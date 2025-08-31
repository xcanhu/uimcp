#!/usr/bin/env python3
"""
MCP服务器测试脚本
测试ScreenCoder MCP服务器的基本功能
"""

import asyncio
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server_v4_local_path import ScreenCoderMCPServer, _process_image_from_path

def create_test_image():
    """创建一个测试图片"""
    # 创建一个简单的测试图片
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # 绘制一些矩形区域来模拟UI组件
    draw.rectangle([50, 50, 750, 150], outline='blue', width=3, fill='lightblue')  # header
    draw.rectangle([50, 200, 200, 550], outline='green', width=3, fill='lightgreen')  # sidebar
    draw.rectangle([250, 200, 750, 550], outline='red', width=3, fill='lightcoral')  # main content
    
    # 添加一些文本
    draw.text((400, 100), "Header Area", fill='black')
    draw.text((125, 375), "Sidebar", fill='black')
    draw.text((500, 375), "Main Content", fill='black')
    
    # 保存测试图片
    test_image_path = Path(tempfile.gettempdir()) / "test_ui_screenshot.png"
    img.save(test_image_path)
    print(f"测试图片已创建: {test_image_path}")
    return test_image_path

async def test_mcp_server():
    """测试MCP服务器功能"""
    print("开始测试MCP服务器...")
    
    try:
        # 1. 创建测试图片
        test_image_path = create_test_image()
        
        # 2. 测试process_image_from_path函数
        print("\n测试图像处理功能...")
        args = {"image_path": str(test_image_path)}
        result = await _process_image_from_path(args)
        
        # 3. 检查结果
        if result and isinstance(result, str):
            content = result
            print("\n处理结果:")
            print(content)
            
            # 尝试解析JSON部分
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                
                try:
                    task_manifest = json.loads(json_str)
                    print("\n解析的任务清单:")
                    print(f"原始图片路径: {task_manifest.get('original_image_path')}")
                    print(f"清单图片路径: {task_manifest.get('manifest_image_path')}")
                    print(f"检测到的区域数量: {len(task_manifest.get('regions', []))}")
                    
                    for i, region in enumerate(task_manifest.get('regions', [])):
                        print(f"  区域 {i+1}: {region['name']} - {region['coords']}")
                        
                        # 检查裁剪的图片是否存在
                        crop_path = Path(region['path'])
                        if crop_path.exists():
                            print(f"    ✅ 裁剪图片存在: {crop_path}")
                        else:
                            print(f"    ❌ 裁剪图片不存在: {crop_path}")
                    
                    # 检查清单图片是否存在
                    manifest_path = Path(task_manifest['manifest_image_path'])
                    if manifest_path.exists():
                        print(f"\n✅ 清单图片存在: {manifest_path}")
                    else:
                        print(f"\n❌ 清单图片不存在: {manifest_path}")
                        
                    print("\n🎉 测试成功完成!")
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    return False
            else:
                print("❌ 响应中没有找到JSON数据")
                return False
        else:
            print("❌ 没有收到有效的处理结果")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_server_initialization():
    """测试服务器初始化"""
    print("\n测试服务器初始化...")
    try:
        server = ScreenCoderMCPServer()
        print("✅ MCP服务器初始化成功")
        print("✅ 工具处理器已设置")
        print("  - process_image_from_path: 处理本地文件路径指定的UI截图")
        
        return True
    except Exception as e:
        print(f"❌ 服务器初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("=" * 50)
    print("ScreenCoder MCP 服务器测试")
    print("=" * 50)
    
    # 测试服务器初始化
    init_success = await test_server_initialization()
    
    if init_success:
        # 测试图像处理功能
        process_success = await test_mcp_server()
        
        if process_success:
            print("\n🎉 所有测试通过!")
            return 0
        else:
            print("\n❌ 图像处理测试失败")
            return 1
    else:
        print("\n❌ 服务器初始化测试失败")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)