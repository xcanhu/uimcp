# ScreenCoder MCP 工具

将 ScreenCoder 改造为 MCP (Model Context Protocol) 工具，让前端开发人员可以通过 AI 助手直接使用截图生成 HTML/CSS 代码的功能。

## 功能特性

- 🖼️ **截图转HTML**: 将UI截图转换为完整的HTML/CSS代码
- 🔍 **布局分析**: 智能分析截图的布局结构
- 🧩 **组件生成**: 为特定UI组件生成代码
- 🎨 **真实图片**: 支持提取真实图片或使用占位符
- 🤖 **多模型支持**: 支持 Doubao、Qwen、GPT、Gemini 等模型
- ⚙️ **配置管理**: 简单的API密钥和模型配置

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements_mcp.txt
```

### 2. 配置 MCP 服务器

在你的 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "screencoder": {
      "command": "python",
      "args": ["path/to/screencoder/mcp_server.py"],
      "env": {}
    }
  }
}
```

### 3. 配置 API 密钥

首次使用时，需要配置AI模型的API密钥：

```python
# 通过MCP工具配置
configure_api_keys(model="doubao", api_key="your_api_key_here")
```

## 使用方法

### 通过 AI 助手使用

一旦配置完成，你就可以通过支持MCP的AI助手（如Claude Desktop）直接使用这些功能：

#### 1. 截图转HTML

```
请帮我将这张UI截图转换为HTML代码
[上传截图]
```

AI助手会调用 `screenshot_to_html` 工具，返回完整的HTML/CSS代码。

#### 2. 布局分析

```
请分析这张截图的布局结构
[上传截图]
```

AI助手会调用 `analyze_layout` 工具，返回布局区域信息。

#### 3. 组件代码生成

```
请为这个导航栏组件生成HTML代码
[上传组件截图]
```

AI助手会调用 `generate_component_code` 工具生成特定组件的代码。

### 可用的MCP工具

#### `screenshot_to_html`
将完整的UI截图转换为HTML/CSS代码

**参数:**
- `image` (必需): Base64编码的截图
- `model` (可选): AI模型选择 (doubao/qwen/gpt/gemini)
- `include_images` (可选): 是否包含真实图片
- `custom_instructions` (可选): 各区域的自定义指令

**示例:**
```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "model": "doubao",
  "include_images": true,
  "custom_instructions": {
    "header": "使用深色主题",
    "sidebar": "添加搜索功能"
  }
}
```

#### `analyze_layout`
分析UI截图的布局结构

**参数:**
- `image` (必需): Base64编码的截图
- `model` (可选): AI模型选择

#### `generate_component_code`
为特定UI组件生成代码

**参数:**
- `image` (必需): Base64编码的组件截图
- `component_type` (必需): 组件类型 (header/sidebar/navigation/main_content/custom)
- `custom_instruction` (可选): 自定义生成指令
- `model` (可选): AI模型选择

#### `configure_api_keys`
配置AI模型的API密钥

**参数:**
- `model` (必需): 模型名称 (doubao/qwen/gpt/gemini)
- `api_key` (必需): API密钥

## 使用示例

### 示例1: 完整网页生成

```
用户: "请帮我将这张电商网站的截图转换为HTML代码，要求使用响应式设计"

AI助手会:
1. 调用 screenshot_to_html 工具
2. 分析截图布局 (header, navigation, main content, sidebar)
3. 为每个区域生成HTML/CSS代码
4. 提取真实图片并替换占位符
5. 返回完整的HTML文件
```

### 示例2: 组件级别生成

```
用户: "这是一个导航栏的截图，请生成对应的HTML代码，要求添加下拉菜单功能"

AI助手会:
1. 调用 generate_component_code 工具
2. 传入 component_type="navigation"
3. 传入 custom_instruction="添加下拉菜单功能"
4. 返回导航栏的HTML/CSS代码
```

### 示例3: 布局分析

```
用户: "请分析这张网页截图的布局结构"

AI助手会:
1. 调用 analyze_layout 工具
2. 返回检测到的区域信息:
   - Header: 顶部导航区域
   - Sidebar: 左侧边栏
   - Main Content: 主内容区域
   - Navigation: 面包屑导航
```

## 配置选项

### 模型配置

支持的AI模型及其特点：

- **Doubao** (默认): 字节跳动的多模态模型，中文支持好
- **Qwen**: 阿里巴巴的Qwen视觉语言模型
- **GPT**: OpenAI的GPT-4V模型
- **Gemini**: Google的Gemini视觉模型

### 自定义指令

可以为不同区域添加自定义指令：

```json
{
  "custom_instructions": {
    "header": "使用深色主题，添加用户头像",
    "sidebar": "添加搜索框和过滤器",
    "navigation": "使用面包屑导航",
    "main_content": "使用卡片布局展示内容"
  }
}
```

## 输出格式

### HTML结构

生成的HTML包含：
- 完整的HTML5文档结构
- Tailwind CSS样式
- 响应式设计
- 真实图片（如果启用）

### 文件组织

```
output/
├── final.html          # 最终HTML文件
├── cropped_images/     # 提取的图片
│   ├── ph0.png
│   ├── ph1.png
│   └── ...
└── debug/              # 调试文件
    ├── layout_analysis.png
    └── bbox_overlay.png
```

## 错误处理

工具包含完整的错误处理机制：

- **API错误**: 模型调用失败
- **网络错误**: 连接问题
- **验证错误**: 输入参数错误
- **处理错误**: 图片处理失败
- **超时错误**: 处理时间过长

## 性能优化

- **异步处理**: 支持并发处理多个请求
- **缓存机制**: 避免重复的模型调用
- **资源管理**: 自动清理临时文件
- **超时控制**: 防止长时间阻塞

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   Error: API key file not found for doubao
   ```
   解决: 使用 `configure_api_keys` 工具设置正确的API密钥

2. **图片格式不支持**
   ```
   Error: Could not decode image
   ```
   解决: 确保上传的是PNG、JPG或其他支持的图片格式

3. **模型调用失败**
   ```
   Error: API request failed
   ```
   解决: 检查网络连接和API密钥是否有效

### 调试模式

启用调试模式获取更多信息：

```python
# 在配置中启用调试
config = ScreenCoderConfig(debug_mode=True)
```

## 开发和扩展

### 添加新模型

1. 在 `config_manager.py` 中添加模型配置
2. 在 `screencoder_core.py` 中实现模型客户端
3. 更新 `utils.py` 中的模型类

### 自定义处理流程

可以继承 `ScreenCoderPipeline` 类来自定义处理流程：

```python
class CustomPipeline(ScreenCoderPipeline):
    async def _analyze_layout(self, image_path):
        # 自定义布局分析逻辑
        pass
```

## 许可证

本项目基于原始 ScreenCoder 项目，遵循相同的开源许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个MCP工具。

## 更新日志

### v1.0.0
- 初始MCP工具实现
- 支持完整的截图转HTML功能
- 多模型支持
- 配置管理系统
- 错误处理和状态管理
