#!/usr/bin/env python3
"""
ScreenCoder MCP Server - V4 最终版 (本地文件路径工作流)
通过接收本地文件路径，彻底解决"输出过长"的上下文限制问题。
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

# MCP 相关导入
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    Tool,
    TextContent,
    ServerCapabilities,
    ToolsCapability
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建一个全局的工作目录 - 使用项目目录而不是临时目录
PROJECT_ROOT = Path(__file__).parent
WORK_DIR = PROJECT_ROOT / "data" / "output"
WORK_DIR.mkdir(parents=True, exist_ok=True)
logger.info(f"工作目录已创建: {WORK_DIR}")

class ScreenCoderMCPServer:
    def __init__(self):
        self.server = Server("screencoder")
        self.setup_handlers()
    
    def setup_handlers(self):
        """设置 MCP 服务器的处理器"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """列出所有可用的 ScreenCoder 工具"""
            return [
                    Tool(
                        name="process_image_from_path",
                        description="处理本地文件路径指定的UI截图，分析布局，裁剪区域，并返回一个包含所有文件路径的任务清单。",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "image_path": {
                                    "type": "string",
                                    "description": "要处理的图片的本地绝对文件路径。例如: 'C:\\Users\\Test\\Desktop\\screenshot.png'"
                                }
                            },
                            "required": ["image_path"]
                        }
                    )
                ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
            """处理工具调用请求"""
            try:
                if name == "process_image_from_path":
                    result = await _process_image_from_path(arguments)
                    return CallToolResult(
                        content=[TextContent(type="text", text=result)]
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")
            
            except Exception as e:
                logger.error(f"Error calling tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

async def _process_image_from_path(args: Dict[str, Any]) -> str:
    """一次性完成所有图像处理，并返回任务清单"""
    try:
        # 1. 从本地路径加载图片
        image_path = Path(args["image_path"])
        if not image_path.exists() or not image_path.is_file():
            raise FileNotFoundError(f"指定的图片路径不存在或不是一个文件: {image_path}")
        
        original_image = Image.open(image_path)
        logger.info(f"成功从路径加载图片: {image_path}")

        # 2. 分析布局
        width, height = original_image.size
        cv_image = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        potential_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h > (width * height * 0.01) and w > 50 and h > 50:
                potential_regions.append({"x": x, "y": y, "width": w, "height": h})
        
        potential_regions.sort(key=lambda p: p['width'] * p['height'], reverse=True)
        detected_regions = potential_regions[:5] # 只取最大的5个区域

        # 3. 为这次处理创建唯一的子目录
        import time
        session_id = f"session_{int(time.time())}"
        session_dir = WORK_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        # 4. 裁剪区域并保存
        crop_dir = session_dir / "cropped_regions"
        crop_dir.mkdir(exist_ok=True)
        cropped_info = []
        for i, region in enumerate(detected_regions):
            name = f"region_{i+1}"
            x, y, w, h = region['x'], region['y'], region['width'], region['height']
            
            cropped = original_image.crop((x, y, x + w, y + h))
            crop_path = crop_dir / f"{name}.png"
            cropped.save(crop_path)
            
            cropped_info.append({"name": name, "path": str(crop_path), "coords": f"{x},{y},{w},{h}"})

        # 5. 创建并保存清单图片 (Manifest Image)
        manifest_image = original_image.copy()
        draw = ImageDraw.Draw(manifest_image)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()

        for i, region in enumerate(cropped_info):
            name = region["name"]
            coords = list(map(int, region["coords"].split(',')))
            x, y, w, h = coords[0], coords[1], coords[2], coords[3]
            draw.rectangle([x, y, x + w, y + h], outline="red", width=5)
            draw.text((x + 10, y + 10), name, fill="red", font=font)

        manifest_image_path = session_dir / "layout_manifest.png"
        manifest_image.save(manifest_image_path)
        logger.info(f"清单图片已保存到: {manifest_image_path}")

        # 6. 构建并返回最终的JSON任务清单
        task_manifest = {
            "manifest_image_path": str(manifest_image_path),
            "original_image_path": str(image_path),
            "regions": cropped_info
        }
        response_json = json.dumps(task_manifest, indent=2)

        return f"图像处理完成。AI，请使用这个任务清单来生成代码。\n```json\n{response_json}\n```"

    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return f"处理失败: {str(e)}"

async def main():
    """启动MCP服务器"""
    server_instance = ScreenCoderMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        capabilities = ServerCapabilities(tools=ToolsCapability(listChanged=False))
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="screencoder",
                server_version="4.0.0-local-path",
                capabilities=capabilities
            )
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务器已关闭。")
