"""
ScreenCoder 错误处理和状态管理系统
"""

import asyncio
import logging
import traceback
from enum import Enum
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ErrorType(Enum):
    """错误类型枚举"""
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    PROCESSING_ERROR = "processing_error"
    TIMEOUT_ERROR = "timeout_error"
    RESOURCE_ERROR = "resource_error"

@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    error_type: Optional[ErrorType] = None
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None

class ScreenCoderError(Exception):
    """ScreenCoder 基础异常类"""
    def __init__(self, message: str, error_type: ErrorType = ErrorType.PROCESSING_ERROR, details: Optional[Dict] = None):
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}

class APIError(ScreenCoderError):
    """API调用错误"""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict] = None):
        super().__init__(message, ErrorType.API_ERROR, details)
        self.status_code = status_code

class ValidationError(ScreenCoderError):
    """输入验证错误"""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message, ErrorType.VALIDATION_ERROR, details)
        self.field = field

class ProcessingError(ScreenCoderError):
    """处理过程错误"""
    def __init__(self, message: str, stage: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message, ErrorType.PROCESSING_ERROR, details)
        self.stage = stage

class TaskManager:
    """任务管理器"""
    
    def __init__(self, max_concurrent_tasks: int = 3):
        self.tasks: Dict[str, TaskInfo] = {}
        self.max_concurrent_tasks = max_concurrent_tasks
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_counter = 0
        self._lock = asyncio.Lock()
    
    def create_task(self, task_id: Optional[str] = None) -> str:
        """创建新任务"""
        if not task_id:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}"
        
        self.tasks[task_id] = TaskInfo(
            task_id=task_id,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        
        logger.info(f"Created task: {task_id}")
        return task_id
    
    async def start_task(self, task_id: str, coro, timeout: Optional[int] = None):
        """启动任务"""
        async with self._lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
            
            if len(self.running_tasks) >= self.max_concurrent_tasks:
                raise RuntimeError("Too many concurrent tasks")
            
            task_info = self.tasks[task_id]
            task_info.status = TaskStatus.RUNNING
            task_info.started_at = datetime.now()
            
            # 创建异步任务
            async_task = asyncio.create_task(self._run_task_with_timeout(task_id, coro, timeout))
            self.running_tasks[task_id] = async_task
            
            logger.info(f"Started task: {task_id}")
            return async_task
    
    async def _run_task_with_timeout(self, task_id: str, coro, timeout: Optional[int]):
        """运行带超时的任务"""
        try:
            if timeout:
                result = await asyncio.wait_for(coro, timeout=timeout)
            else:
                result = await coro
            
            await self._complete_task(task_id, result)
            return result
            
        except asyncio.TimeoutError:
            await self._fail_task(task_id, "Task timeout", ErrorType.TIMEOUT_ERROR)
            raise ScreenCoderError("Task timeout", ErrorType.TIMEOUT_ERROR)
        except Exception as e:
            await self._fail_task(task_id, str(e), self._get_error_type(e))
            raise
        finally:
            async with self._lock:
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
    
    async def _complete_task(self, task_id: str, result: Any):
        """完成任务"""
        async with self._lock:
            if task_id in self.tasks:
                task_info = self.tasks[task_id]
                task_info.status = TaskStatus.COMPLETED
                task_info.completed_at = datetime.now()
                task_info.progress = 1.0
                task_info.result = result
                
                logger.info(f"Completed task: {task_id}")
    
    async def _fail_task(self, task_id: str, error_message: str, error_type: ErrorType):
        """任务失败"""
        async with self._lock:
            if task_id in self.tasks:
                task_info = self.tasks[task_id]
                task_info.status = TaskStatus.FAILED
                task_info.completed_at = datetime.now()
                task_info.error_message = error_message
                task_info.error_type = error_type
                
                logger.error(f"Failed task {task_id}: {error_message}")
    
    def get_task_status(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.CANCELLED
                self.tasks[task_id].completed_at = datetime.now()
            
            logger.info(f"Cancelled task: {task_id}")
            return True
        
        return False
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for task_id, task_info in self.tasks.items():
            if task_info.created_at < cutoff_time and task_info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
            logger.info(f"Cleaned up old task: {task_id}")
    
    def _get_error_type(self, error: Exception) -> ErrorType:
        """根据异常类型确定错误类型"""
        if isinstance(error, ScreenCoderError):
            return error.error_type
        elif isinstance(error, asyncio.TimeoutError):
            return ErrorType.TIMEOUT_ERROR
        elif isinstance(error, (ConnectionError, OSError)):
            return ErrorType.NETWORK_ERROR
        elif isinstance(error, ValueError):
            return ErrorType.VALIDATION_ERROR
        else:
            return ErrorType.PROCESSING_ERROR

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.error_callbacks: Dict[ErrorType, List[Callable]] = {}
    
    def register_callback(self, error_type: ErrorType, callback: Callable):
        """注册错误回调"""
        if error_type not in self.error_callbacks:
            self.error_callbacks[error_type] = []
        self.error_callbacks[error_type].append(callback)
    
    async def handle_error(self, error: Exception, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理错误"""
        error_info = self._extract_error_info(error, context)
        
        # 记录错误
        logger.error(f"Error occurred: {error_info}")
        
        # 调用回调函数
        error_type = error_info.get("type", ErrorType.PROCESSING_ERROR)
        if error_type in self.error_callbacks:
            for callback in self.error_callbacks[error_type]:
                try:
                    await callback(error_info)
                except Exception as e:
                    logger.error(f"Error in error callback: {e}")
        
        return error_info
    
    def _extract_error_info(self, error: Exception, context: Optional[Dict] = None) -> Dict[str, Any]:
        """提取错误信息"""
        error_info = {
            "message": str(error),
            "type": self._get_error_type(error),
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        
        # 添加特定错误类型的详细信息
        if isinstance(error, ScreenCoderError):
            error_info["details"] = error.details
            if isinstance(error, APIError):
                error_info["status_code"] = error.status_code
            elif isinstance(error, ValidationError):
                error_info["field"] = error.field
            elif isinstance(error, ProcessingError):
                error_info["stage"] = error.stage
        
        return error_info
    
    def _get_error_type(self, error: Exception) -> ErrorType:
        """获取错误类型"""
        if isinstance(error, ScreenCoderError):
            return error.error_type
        elif isinstance(error, asyncio.TimeoutError):
            return ErrorType.TIMEOUT_ERROR
        elif isinstance(error, (ConnectionError, OSError)):
            return ErrorType.NETWORK_ERROR
        elif isinstance(error, ValueError):
            return ErrorType.VALIDATION_ERROR
        else:
            return ErrorType.PROCESSING_ERROR

# 全局实例
task_manager = TaskManager()
error_handler = ErrorHandler()

def handle_errors(func):
    """错误处理装饰器"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_info = await error_handler.handle_error(e, {"function": func.__name__})
            raise ScreenCoderError(
                f"Error in {func.__name__}: {str(e)}",
                error_info.get("type", ErrorType.PROCESSING_ERROR),
                error_info
            )
    return wrapper
