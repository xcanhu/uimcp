"""
ScreenCoder 配置管理系统
管理 API 密钥、模型配置和用户设置
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """AI模型配置"""
    name: str
    api_key_file: Optional[str] = None
    model_id: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.1
    enabled: bool = True

@dataclass
class ScreenCoderSettings:
    """ScreenCoder 全局设置"""
    default_model: str = "doubao"
    output_format: str = "html"
    include_images_by_default: bool = True
    max_concurrent_requests: int = 3
    request_timeout: int = 300  # 5分钟
    auto_cleanup: bool = True
    debug_mode: bool = False

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".screencoder"
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        self.models_file = self.config_dir / "models.json"
        
        self.settings = self._load_settings()
        self.models = self._load_models()
    
    def _load_settings(self) -> ScreenCoderSettings:
        """加载全局设置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return ScreenCoderSettings(**data)
            except Exception as e:
                logger.warning(f"Failed to load settings: {e}, using defaults")
        
        return ScreenCoderSettings()
    
    def _load_models(self) -> Dict[str, ModelConfig]:
        """加载模型配置"""
        default_models = {
            "doubao": ModelConfig(
                name="doubao",
                model_id="doubao-1.5-thinking-vision-pro-250428",
                api_key_file="doubao_api.txt"
            ),
            "qwen": ModelConfig(
                name="qwen",
                model_id="qwen2.5-vl-72b-instruct",
                api_key_file="qwen_api.txt"
            ),
            "gpt": ModelConfig(
                name="gpt",
                model_id="gpt-4o",
                api_key_file="gpt_api.txt"
            ),
            "gemini": ModelConfig(
                name="gemini",
                model_id="gemini-1.5-flash-latest",
                api_key_file="gemini_api.txt"
            )
        }
        
        if self.models_file.exists():
            try:
                with open(self.models_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                models = {}
                for name, config_data in data.items():
                    models[name] = ModelConfig(**config_data)
                
                # 合并默认配置
                for name, default_config in default_models.items():
                    if name not in models:
                        models[name] = default_config
                
                return models
            except Exception as e:
                logger.warning(f"Failed to load models config: {e}, using defaults")
        
        return default_models
    
    def save_settings(self):
        """保存设置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def save_models(self):
        """保存模型配置"""
        try:
            data = {name: asdict(config) for name, config in self.models.items()}
            with open(self.models_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save models config: {e}")
    
    def set_api_key(self, model_name: str, api_key: str) -> bool:
        """设置API密钥"""
        try:
            if model_name not in self.models:
                logger.error(f"Unknown model: {model_name}")
                return False
            
            # 保存API密钥到文件
            api_key_file = self.config_dir / f"{model_name}_api.txt"
            api_key_file.write_text(api_key.strip())
            
            # 更新模型配置
            self.models[model_name].api_key_file = str(api_key_file)
            self.models[model_name].enabled = True
            
            self.save_models()
            logger.info(f"API key set for {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set API key for {model_name}: {e}")
            return False
    
    def get_api_key(self, model_name: str) -> Optional[str]:
        """获取API密钥"""
        if model_name not in self.models:
            return None
        
        model_config = self.models[model_name]
        if not model_config.api_key_file:
            return None
        
        api_key_path = Path(model_config.api_key_file)
        if not api_key_path.is_absolute():
            api_key_path = self.config_dir / api_key_path
        
        if api_key_path.exists():
            try:
                return api_key_path.read_text().strip()
            except Exception as e:
                logger.error(f"Failed to read API key for {model_name}: {e}")
        
        return None
    
    def is_model_available(self, model_name: str) -> bool:
        """检查模型是否可用"""
        if model_name not in self.models:
            return False
        
        model_config = self.models[model_name]
        if not model_config.enabled:
            return False
        
        # 检查API密钥是否存在
        return self.get_api_key(model_name) is not None
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return [name for name in self.models.keys() if self.is_model_available(name)]
    
    def update_model_config(self, model_name: str, **kwargs):
        """更新模型配置"""
        if model_name not in self.models:
            logger.error(f"Unknown model: {model_name}")
            return False
        
        try:
            for key, value in kwargs.items():
                if hasattr(self.models[model_name], key):
                    setattr(self.models[model_name], key, value)
            
            self.save_models()
            return True
        except Exception as e:
            logger.error(f"Failed to update model config for {model_name}: {e}")
            return False
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """获取模型配置"""
        return self.models.get(model_name)
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.settings = ScreenCoderSettings()
        self.models = self._load_models()  # 重新加载默认模型配置
        self.save_settings()
        self.save_models()

# 全局配置管理器实例
config_manager = ConfigManager()
