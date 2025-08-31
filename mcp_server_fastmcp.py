#!/usr/bin/env python3
"""
ScreenCoder MCP Server using FastMCP
使用FastMCP重写的ScreenCoder MCP服务器，避免CallToolResult序列化问题
"""

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

from mcp.server.fastmcp import FastMCP

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建工作目录
WORK_DIR = Path(tempfile.mkdtemp(prefix="screencoder_session_"))
logger.info(f"工作目录已创建: {WORK_DIR}")

# 创建FastMCP服务器
mcp = FastMCP("ScreenCoder")

@mcp.tool()
def process_image_from_path(image_path: str) -> str:
    """
    处理本地文件路径指定的UI截图，分析布局，裁剪区域，并返回一个包含所有文件路径的任务清单。
    
    Args:
        image_path: 要处理的图片的本地绝对文件路径
        
    Returns:
        包含任务清单的JSON字符串
    """
    try:
        # 1. 从本地路径加载图片
        img_path = Path(image_path)
        if not img_path.exists() or not img_path.is_file():
            return f"错误：图片文件不存在: {image_path}"
        
        logger.info(f"开始处理图片: {img_path}")
        
        # 加载图片
        image = cv2.imread(str(img_path))
        if image is None:
            return f"错误：无法加载图片: {image_path}"
        
        height, width = image.shape[:2]
        logger.info(f"图片尺寸: {width}x{height}")
        
        # 2. 图像布局分析 - 简化版本，检测主要区域
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用简单的区域分割
        regions = [
            {"name": "header", "bbox": [0, 0, width, height//6]},
            {"name": "navigation", "bbox": [0, height//6, width//4, height//2]},
            {"name": "main_content", "bbox": [width//4, height//6, width*3//4, height*5//6]},
            {"name": "sidebar", "bbox": [width*3//4, height//6, width, height*5//6]}
        ]
        
        # 3. 裁剪并保存区域图片
        cropped_dir = WORK_DIR / "cropped_images"
        cropped_dir.mkdir(exist_ok=True)
        
        cropped_files = []
        for i, region in enumerate(regions):
            x1, y1, x2, y2 = region["bbox"]
            # 确保坐标在图片范围内
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(width, x2), min(height, y2)
            
            if x2 > x1 and y2 > y1:  # 确保区域有效
                cropped = image[y1:y2, x1:x2]
                crop_filename = f"region_{i}_{region['name']}.png"
                crop_path = cropped_dir / crop_filename
                cv2.imwrite(str(crop_path), cropped)
                
                cropped_files.append({
                    "region_id": i,
                    "name": region["name"],
                    "file_path": str(crop_path),
                    "bbox": [x1, y1, x2, y2]
                })
                logger.info(f"保存裁剪图片: {crop_path}")
        
        # 4. 创建并保存manifest图片（带标注的原图）
        manifest_image = image.copy()
        for i, region in enumerate(regions):
            x1, y1, x2, y2 = region["bbox"]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(width, x2), min(height, y2)
            
            # 绘制边框
            cv2.rectangle(manifest_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # 添加标签
            cv2.putText(manifest_image, f"{i}: {region['name']}", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        manifest_path = WORK_DIR / "layout_manifest.png"
        cv2.imwrite(str(manifest_path), manifest_image)
        logger.info(f"保存manifest图片: {manifest_path}")
        
        # 5. 创建任务清单
        task_manifest = {
            "original_image": str(img_path),
            "manifest_image": str(manifest_path),
            "work_directory": str(WORK_DIR),
            "regions": cropped_files,
            "total_regions": len(cropped_files)
        }
        
        response_json = json.dumps(task_manifest, indent=2)
        return f"图像处理完成。AI，请使用这个任务清单来生成代码。\n```json\n{response_json}\n```"
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return f"处理失败: {str(e)}"

if __name__ == "__main__":
    try:
        # 运行FastMCP服务器
        mcp.run()
    except KeyboardInterrupt:
        logger.info("服务器已关闭。")
        import shutil
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)
            logger.info(f"工作目录 {WORK_DIR} 已清理。")