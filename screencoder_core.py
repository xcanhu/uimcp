"""
ScreenCoder 核心功能模块
将原有脚本重构为可调用的类和函数
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import cv2
import numpy as np
from PIL import Image
import subprocess
import sys
from dataclasses import dataclass

# 导入原有模块
from utils import Doubao, Qwen, GPT, Gemini, encode_image, image_mask
from block_parsor import parse_bboxes, resolve_containment, draw_bboxes, save_bboxes_to_json
from html_generator import generate_html, generate_code_parallel, code_substitution
from image_box_detection import extract_bboxes_from_html
from mapping import load_regions_and_placeholders, load_uied_boxes, find_local_mapping_and_transform
from image_replacer import main as image_replacer_main

@dataclass
class ScreenCoderConfig:
    """ScreenCoder 配置类"""
    model: str = "doubao"
    include_images: bool = True
    custom_instructions: Dict[str, str] = None
    api_key_path: Optional[str] = None
    output_dir: str = "output"
    temp_dir: str = "tmp"
    
    def __post_init__(self):
        if self.custom_instructions is None:
            self.custom_instructions = {}

class ScreenCoderPipeline:
    """ScreenCoder 主处理管道"""
    
    def __init__(self, config: ScreenCoderConfig):
        self.config = config
        self.work_dir = Path(tempfile.mkdtemp(prefix="screencoder_"))
        self.output_dir = self.work_dir / config.output_dir
        self.temp_dir = self.work_dir / config.temp_dir
        
        # 创建工作目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化AI客户端
        self.ai_client = self._init_ai_client()
    
    def _init_ai_client(self):
        """初始化AI客户端"""
        api_key_path = self.config.api_key_path
        if not api_key_path:
            # 尝试从默认位置加载API密钥
            config_dir = Path.home() / ".screencoder"
            api_key_path = config_dir / f"{self.config.model}_api.txt"
            
            if not api_key_path.exists():
                # 尝试项目根目录
                api_key_path = Path(f"{self.config.model}_api.txt")
        
        if not Path(api_key_path).exists():
            raise FileNotFoundError(f"API key file not found for {self.config.model}")
        
        # 根据模型类型创建客户端
        if self.config.model == "doubao":
            return Doubao(str(api_key_path))
        elif self.config.model == "qwen":
            return Qwen(str(api_key_path))
        elif self.config.model == "gpt":
            return GPT(str(api_key_path))
        elif self.config.model == "gemini":
            return Gemini(str(api_key_path))
        else:
            raise ValueError(f"Unsupported model: {self.config.model}")
    
    async def process_screenshot(self, image: Image.Image) -> Dict[str, Any]:
        """处理截图的完整流程"""
        try:
            # 保存输入图片
            image_path = self.temp_dir / "input.png"
            image.save(image_path)
            
            # 步骤1: 布局分析
            layout_result = await self._analyze_layout(image_path)
            
            # 步骤2: 生成初始HTML
            html_result = await self._generate_initial_html(image_path, layout_result)
            
            # 步骤3: 如果需要包含真实图片，进行图片替换
            if self.config.include_images:
                final_result = await self._replace_images(image_path, html_result)
            else:
                final_result = html_result
            
            return {
                "success": True,
                "layout_info": layout_result["summary"],
                "html_path": str(final_result["html_path"]),
                "html_content": final_result["html_content"],
                "work_dir": str(self.work_dir)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "work_dir": str(self.work_dir)
            }
    
    async def analyze_layout_only(self, image: Image.Image) -> Dict[str, Any]:
        """仅分析布局，不生成HTML"""
        image_path = self.temp_dir / "input.png"
        image.save(image_path)
        
        return await self._analyze_layout(image_path)
    
    async def generate_component_code(self, image: Image.Image, component_type: str, custom_instruction: str = "") -> Dict[str, Any]:
        """为单个组件生成代码"""
        try:
            # 更新自定义指令
            if custom_instruction:
                self.config.custom_instructions[component_type] = custom_instruction
            
            # 保存图片
            image_path = self.temp_dir / f"component_{component_type}.png"
            image.save(image_path)
            
            # 生成代码
            code = await self._generate_single_component_code(image_path, component_type)
            
            return {
                "success": True,
                "component_type": component_type,
                "code": code
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_layout(self, image_path: Path) -> Dict[str, Any]:
        """分析图片布局"""
        # 使用原有的block_parsor逻辑
        prompt = "Return the bounding boxes of the sidebar, main content, header, and navigation in this webpage screenshot. Please only return the corresponding bounding boxes. Note: 1. The areas should not overlap; 2. All text information and other content should be framed inside; 3. Try to keep it compact without leaving a lot of blank space; 4. Output a label and the corresponding bounding box for each line."
        
        # 调用AI模型
        bbox_content = self.ai_client.ask(prompt, encode_image(str(image_path)))
        
        # 解析边界框
        bboxes = parse_bboxes(bbox_content, str(image_path))
        bboxes = resolve_containment(bboxes)
        
        if not bboxes:
            raise ValueError("No valid bounding boxes found in layout analysis")
        
        # 保存结果
        json_path = save_bboxes_to_json(bboxes, str(image_path))
        draw_bboxes(str(image_path), bboxes)
        
        # 生成摘要
        regions_summary = f"检测到 {len(bboxes)} 个区域: {', '.join(bboxes.keys())}"
        
        return {
            "bboxes": bboxes,
            "json_path": json_path,
            "summary": regions_summary,
            "regions": bboxes,
            "regions_summary": regions_summary
        }
    
    async def _generate_initial_html(self, image_path: Path, layout_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成初始HTML"""
        bboxes = layout_result["bboxes"]
        
        # 读取图片尺寸
        with Image.open(image_path) as img:
            width, height = img.size
        
        # 创建根节点
        root = {
            "bbox": [0, 0, width, height],
            "children": []
        }
        
        # 添加每个区域作为子节点
        for component_name, norm_bbox in bboxes.items():
            # 转换归一化坐标到像素坐标
            x1 = int(norm_bbox[0] * width / 1000)
            y1 = int(norm_bbox[1] * height / 1000)
            x2 = int(norm_bbox[2] * width / 1000)
            y2 = int(norm_bbox[3] * height / 1000)
            
            child = {
                "bbox": [x1, y1, x2, y2],
                "children": [],
                "type": component_name
            }
            root["children"].append(child)
        
        # 分配ID
        self._assign_ids(root, 0)
        
        # 生成HTML骨架
        html_path = self.temp_dir / "layout.html"
        generate_html(root, str(html_path))
        
        # 生成组件代码
        code_dict = await self._generate_components_code(root, image_path)
        
        # 注入代码
        code_substitution(str(html_path), code_dict)
        
        # 读取生成的HTML内容
        html_content = html_path.read_text()
        
        return {
            "html_path": html_path,
            "html_content": html_content,
            "root": root,
            "code_dict": code_dict
        }
    
    async def _generate_components_code(self, root: Dict[str, Any], image_path: Path) -> Dict[str, str]:
        """生成所有组件的代码"""
        code_dict = {}
        
        def _process_node(node):
            if not node.get("children"):  # 叶子节点
                component_type = node.get("type")
                if component_type:
                    # 裁剪图片
                    with Image.open(image_path) as img:
                        bbox = node["bbox"]
                        cropped_img = img.crop(bbox)
                        
                        # 生成代码
                        code = self._generate_component_code_sync(cropped_img, component_type)
                        code_dict[node["id"]] = code
            else:
                for child in node["children"]:
                    _process_node(child)
        
        _process_node(root)
        return code_dict
    
    def _generate_component_code_sync(self, image: Image.Image, component_type: str) -> str:
        """同步生成组件代码"""
        # 获取自定义指令
        custom_instruction = self.config.custom_instructions.get(component_type, "")
        
        # 构建提示词
        prompts = {
            "sidebar": f"这是一个sidebar的截图。用户要求：{custom_instruction}。请填写完整的HTML和Tailwind CSS代码以准确再现给定的容器。",
            "header": f"这是一个header的截图。用户要求：{custom_instruction}。请填写完整的HTML和Tailwind CSS代码以准确再现给定的容器。",
            "navigation": f"这是一个navigation的截图。用户要求：{custom_instruction}。请填写完整的HTML和Tailwind CSS代码以准确再现给定的容器。",
            "main_content": f"这是一个main content的截图。用户要求：{custom_instruction}。请使用相同大小的纯灰色图像块替换原始截图中的图像。请填写完整的HTML和Tailwind CSS代码。"
        }
        
        prompt = prompts.get(component_type, f"请为这个{component_type}组件生成HTML和Tailwind CSS代码。")
        prompt += "\n\n<div>\nyour code here\n</div>\n\n只需返回<div>和</div>标签内的代码"
        
        # 调用AI模型
        code = self.ai_client.ask(prompt, encode_image(image))
        
        # 清理代码
        code = code.replace("```html", "").replace("```", "").strip()
        
        return code
    
    async def _generate_single_component_code(self, image_path: Path, component_type: str) -> str:
        """为单个组件生成代码"""
        with Image.open(image_path) as image:
            return self._generate_component_code_sync(image, component_type)
    
    async def _replace_images(self, image_path: Path, html_result: Dict[str, Any]) -> Dict[str, Any]:
        """替换HTML中的图片占位符"""
        try:
            # 这里需要实现UIED检测和图片替换逻辑
            # 由于UIED比较复杂，暂时返回原始HTML
            # 在实际实现中，需要调用UIED模块并执行mapping和image_replacer的逻辑
            
            final_html_path = self.output_dir / "final.html"
            final_html_path.write_text(html_result["html_content"])
            
            return {
                "html_path": final_html_path,
                "html_content": html_result["html_content"]
            }
            
        except Exception as e:
            # 如果图片替换失败，返回原始HTML
            return html_result
    
    def _assign_ids(self, node: Dict[str, Any], current_id: int) -> int:
        """为节点分配ID"""
        node["id"] = str(current_id)
        current_id += 1
        
        for child in node.get("children", []):
            current_id = self._assign_ids(child, current_id)
        
        return current_id
    
    def cleanup(self):
        """清理临时文件"""
        import shutil
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)

class ScreenCoderManager:
    """ScreenCoder 管理器，用于管理多个处理实例"""
    
    def __init__(self):
        self.active_pipelines: Dict[str, ScreenCoderPipeline] = {}
    
    def create_pipeline(self, config: ScreenCoderConfig) -> str:
        """创建新的处理管道"""
        pipeline_id = f"pipeline_{len(self.active_pipelines)}"
        self.active_pipelines[pipeline_id] = ScreenCoderPipeline(config)
        return pipeline_id
    
    def get_pipeline(self, pipeline_id: str) -> Optional[ScreenCoderPipeline]:
        """获取处理管道"""
        return self.active_pipelines.get(pipeline_id)
    
    def cleanup_pipeline(self, pipeline_id: str):
        """清理处理管道"""
        if pipeline_id in self.active_pipelines:
            self.active_pipelines[pipeline_id].cleanup()
            del self.active_pipelines[pipeline_id]
    
    def cleanup_all(self):
        """清理所有管道"""
        for pipeline_id in list(self.active_pipelines.keys()):
            self.cleanup_pipeline(pipeline_id)
