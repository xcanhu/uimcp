#!/usr/bin/env python3
"""
ScreenCoder MCP 工具安装和配置脚本
"""

import os
import sys
import json
import shutil
from pathlib import Path
import subprocess

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✅ Python版本: {sys.version}")

def install_dependencies():
    """安装依赖包"""
    print("📦 安装依赖包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_mcp.txt"], check=True)
        print("✅ 依赖包安装完成")
    except subprocess.CalledProcessError:
        print("❌ 依赖包安装失败")
        sys.exit(1)

def setup_config_directory():
    """设置配置目录"""
    config_dir = Path.home() / ".screencoder"
    config_dir.mkdir(exist_ok=True)
    print(f"✅ 配置目录: {config_dir}")
    return config_dir

def create_mcp_config(config_dir):
    """创建MCP配置文件示例"""
    mcp_config = {
        "mcpServers": {
            "screencoder": {
                "command": "python",
                "args": [str(Path(__file__).parent / "mcp_server_v4_local_path.py")],
                "env": {}
            }
        }
    }
    
    config_file = config_dir / "mcp_config_example.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(mcp_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ MCP配置示例: {config_file}")
    return config_file

def setup_api_keys(config_dir):
    """设置API密钥"""
    print("🔑 API密钥配置")
    print("请选择要配置的模型:")
    print("1. Doubao (字节跳动)")
    print("2. Qwen (阿里巴巴)")
    print("3. GPT (OpenAI)")
    print("4. Gemini (Google)")
    print("5. 跳过配置")
    
    choice = input("请选择 (1-5): ").strip()
    
    model_map = {
        "1": "doubao",
        "2": "qwen", 
        "3": "gpt",
        "4": "gemini"
    }
    
    if choice in model_map:
        model = model_map[choice]
        api_key = input(f"请输入{model.upper()} API密钥: ").strip()
        
        if api_key:
            api_key_file = config_dir / f"{model}_api.txt"
            api_key_file.write_text(api_key)
            print(f"✅ {model.upper()} API密钥已保存")
        else:
            print("⚠️ 未输入API密钥，跳过配置")
    else:
        print("⚠️ 跳过API密钥配置")

def test_installation():
    """测试安装"""
    print("\n🧪 测试安装...")
    try:
        # 测试导入核心模块
        from screencoder_core import ScreenCoderPipeline, ScreenCoderConfig
        from config_manager import config_manager
        from error_handler import task_manager
        print("✅ 核心模块导入成功")
        
        # 测试配置管理
        available_models = config_manager.get_available_models()
        print(f"✅ 可用模型: {available_models if available_models else '无 (需要配置API密钥)'}")
        
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def print_usage_instructions():
    """打印使用说明"""
    print("\n" + "="*50)
    print("🎉 ScreenCoder MCP 工具安装完成!")
    print("="*50)
    
    print("\n📖 使用方法:")
    print("1. 在你的MCP客户端配置文件中添加服务器配置")
    print("2. 重启MCP客户端")
    print("3. 通过AI助手使用以下命令:")
    print("   - '将这张截图转换为HTML代码'")
    print("   - '分析这张截图的布局'")
    print("   - '为这个组件生成代码'")
    
    print("\n⚙️ 配置文件位置:")
    print(f"   配置目录: {Path.home() / '.screencoder'}")
    print(f"   MCP配置示例: {Path.home() / '.screencoder' / 'mcp_config_example.json'}")
    
    print("\n🔧 如需配置更多API密钥，运行:")
    print("   python -c \"from config_manager import config_manager; config_manager.set_api_key('model_name', 'your_api_key')\"")
    
    print("\n📚 详细文档: README_MCP.md")

def main():
    """主安装流程"""
    print("🚀 ScreenCoder MCP 工具安装程序")
    print("="*40)
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖
    install_dependencies()
    
    # 设置配置目录
    config_dir = setup_config_directory()
    
    # 创建MCP配置示例
    create_mcp_config(config_dir)
    
    # 设置API密钥
    setup_api_keys(config_dir)
    
    # 测试安装
    if test_installation():
        print_usage_instructions()
    else:
        print("❌ 安装测试失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
