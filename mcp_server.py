#!/usr/bin/env python3
"""
ScreenCoder MCP Server
将 ScreenCoder 功能暴露为 MCP 工具，供前端开发人员通过 AI 助手使用
"""

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
import base64
from io import BytesIO
from PIL import Image

# MCP 相关导入
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

# ScreenCoder 核心模块导入
from screencoder_core import ScreenCoderPipeline, ScreenCoderConfig

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScreenCoderMCPServer:
    def __init__(self):
        self.server = Server("screencoder")
        self.pipeline = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """设置 MCP 服务器的处理器"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """列出所有可用的 ScreenCoder 工具"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="screenshot_to_html",
                        description="将UI截图转换为完整的HTML/CSS代码",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "image": {
                                    "type": "string",
                                    "description": "Base64编码的截图图片"
                                },
                                "include_images": {
                                    "type": "boolean",
                                    "description": "是否包含真实图片 (否则使用灰色占位符)",
                                    "default": True
                                },
                                "custom_instructions": {
                                    "type": "object",
                                    "description": "各区域的自定义指令",
                                    "properties": {
                                        "header": {"type": "string"},
                                        "sidebar": {"type": "string"},
                                        "navigation": {"type": "string"},
                                        "main_content": {"type": "string"}
                                    }
                                }
                            },
                            "required": ["image"]
                        }
                    ),
                    Tool(
                        name="analyze_layout",
                        description="分析UI截图的布局结构，返回主要区域信息",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "image": {
                                    "type": "string",
                                    "description": "Base64编码的截图图片"
                                }
                            },
                            "required": ["image"]
                        }
                    ),
                    Tool(
                        name="generate_component_code",
                        description="为特定UI组件生成HTML/CSS代码",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "image": {
                                    "type": "string",
                                    "description": "Base64编码的组件截图"
                                },
                                "component_type": {
                                    "type": "string",
                                    "enum": ["header", "sidebar", "navigation", "main_content", "custom"],
                                    "description": "组件类型"
                                },
                                "custom_instruction": {
                                    "type": "string",
                                    "description": "自定义生成指令"
                                }
                            },
                            "required": ["image", "component_type"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """处理工具调用请求"""
            try:
                if request.name == "screenshot_to_html":
                    return await self._screenshot_to_html(request.arguments)
                elif request.name == "analyze_layout":
                    return await self._analyze_layout(request.arguments)
                elif request.name == "generate_component_code":
                    return await self._generate_component_code(request.arguments)
                else:
                    raise ValueError(f"Unknown tool: {request.name}")
            
            except Exception as e:
                logger.error(f"Error calling tool {request.name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    async def _screenshot_to_html(self, args: Dict[str, Any]) -> CallToolResult:
        """将截图转换为HTML代码"""
        try:
            # 解码图片
            image_data = base64.b64decode(args["image"])
            image = Image.open(BytesIO(image_data))
            
            # 配置参数 - 不再需要指定模型
            config = ScreenCoderConfig(
                include_images=args.get("include_images", True),
                custom_instructions=args.get("custom_instructions", {})
            )
            
            # 初始化管道
            if not self.pipeline:
                self.pipeline = ScreenCoderPipeline(config)
            
            # 执行转换
            result = await self.pipeline.process_screenshot(image)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", 
                        text=f"✅ 成功生成HTML代码！\n\n**布局分析结果:**\n{result['layout_info']}\n\n**生成的HTML文件:** {result['html_path']}"
                    ),
                    TextContent(
                        type="text",
                        text=f"```html\n{result['html_content']}\n```"
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"Screenshot to HTML error: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ 转换失败: {str(e)}")]
            )
    
    async def _analyze_layout(self, args: Dict[str, Any]) -> CallToolResult:
        """分析截图布局"""
        try:
            # 解码图片
            image_data = base64.b64decode(args["image"])
            image = Image.open(BytesIO(image_data))
            
            # 配置参数
            config = ScreenCoderConfig(model=args.get("model", "doubao"))
            
            # 初始化管道
            if not self.pipeline:
                self.pipeline = ScreenCoderPipeline(config)
            
            # 执行布局分析
            layout_result = await self.pipeline.analyze_layout_only(image)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"🔍 **布局分析完成**\n\n**检测到的区域:**\n{layout_result['regions_summary']}\n\n**区域详情:**\n```json\n{json.dumps(layout_result['regions'], indent=2, ensure_ascii=False)}\n```"
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"Layout analysis error: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ 布局分析失败: {str(e)}")]
            )
    
    async def _generate_component_code(self, args: Dict[str, Any]) -> CallToolResult:
        """为特定组件生成代码"""
        try:
            # 解码图片
            image_data = base64.b64decode(args["image"])
            image = Image.open(BytesIO(image_data))
            
            # 配置参数
            config = ScreenCoderConfig(model=args.get("model", "doubao"))
            
            # 初始化管道
            if not self.pipeline:
                self.pipeline = ScreenCoderPipeline(config)
            
            # 生成组件代码
            component_result = await self.pipeline.generate_component_code(
                image, 
                args["component_type"],
                args.get("custom_instruction", "")
            )
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"[object Object]args['component_type']} 组件代码生成完成**"
                    ),
                    TextContent(
                        type="text",
                        text=f"```html\n{component_result['code']}\n```"
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"Component code generation error: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ 组件代码生成失败: {str(e)}")]
            )
    
    async def _configure_api_keys(self, args: Dict[str, Any]) -> CallToolResult:
        """配置API密钥"""
        try:
            model = args["model"]
            api_key = args["api_key"]
            
            # 保存API密钥到配置文件
            config_dir = Path.home() / ".screencoder"
            config_dir.mkdir(exist_ok=True)
            
            api_key_file = config_dir / f"{model}_api.txt"
            api_key_file.write_text(api_key)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"✅ {model.upper()} API密钥配置成功！"
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"API key configuration error: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ API密钥配置失败: {str(e)}")]
            )

async def main():
    """启动MCP服务器"""
    server_instance = ScreenCoderMCPServer()
    
    # 使用stdio运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="screencoder",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
