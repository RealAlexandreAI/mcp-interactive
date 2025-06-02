# Interactive Feedback MCP（交互反馈 MCP）

**🌐 语言切换 / Language:** [English](README.md) | [繁體中文](README.zh-TW.md) | **简体中文**

**原作者：** [Fábio Ferreira](https://x.com/fabiomlferreira) | [原始项目](https://github.com/noopstudios/interactive-feedback-mcp) ⭐  
**分支版本：** [Minidoracat](https://github.com/Minidoracat)  
**UI 设计参考：** [sanshao85/mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector) - 感谢提供现代化界面设计灵感  
**相关资源：** [dotcursorrules.com](https://dotcursorrules.com/) 提供更多 AI 开发增强工具

这是一个简单的 [MCP 服务器](https://modelcontextprotocol.io/)，用于在 AI 辅助开发工具（如 [Cursor](https://www.cursor.com)）中实现人在回路（human-in-the-loop）的工作流程。该服务器允许您执行命令、查看输出并直接向 AI 提供文字反馈和图片。同时支持 [Cline](https://cline.bot) 和 [Windsurf](https://windsurf.com)。

## ✨ 新功能特色

### 🌐 完整的 SSH Remote 支持
- **自动环境检测**：智能检测运行环境并选择适当界面
- **本地环境**：使用原有的 Qt GUI 界面
- **SSH Remote 环境**：自动切换到现代化 Web UI
- **实时通讯**：基于 WebSocket 的实时命令输出和反馈
- **深色主题**：提供现代化的深色主题界面

### 🖼️ 图片上传支持
- **多格式支持**：PNG、JPG、JPEG、GIF、BMP、WebP
- **拖拽上传**：支持拖拽文件到界面
- **剪贴板支持**：直接从剪贴板粘贴图片
- **自动压缩**：智能压缩大图片以符合 1MB 限制
- **MCP 整合**：图片自动转换为 MCP Image 对象

### 🛡️ 稳定性改善
- **编码修复**：完全解决中文字符乱码问题
- **调试控制**：可控制的调试输出，避免 JSON 解析错误
- **错误处理**：强化错误处理，确保程序稳定运行
- **输出隔离**：严格隔离调试输出与 MCP 通信

### 🌏 多语言支持
- **完整国际化**：采用结构化 JSON 翻译文件的完整多语言支持
- **支持语言**：繁体中文、英文、简体中文
- **智能检测**：根据系统语言环境自动检测
- **易于扩充**：基于 JSON 的简单翻译系统，方便新增语言
- **向后兼容**：与现有程序代码完全向后兼容

## 🖥️ 界面预览

### Qt GUI 界面（本地环境）
![Qt GUI Interface - Traditional Chinese](docs/images/gui-zh-tw.png)

### Web UI 界面（SSH Remote 环境）
![Web UI Interface - Traditional Chinese](docs/images/web-zh-tw.png)

两种界面都支持：
- 💬 文字反馈输入
- 🖼️ 图片上传（支持拖拽、剪贴板粘贴）
- ⚡ 实时命令执行
- ⌨️ **快捷键支持**：
  - Ctrl+Enter 快速提交反馈（支持主键盘和数字键盘）
  - Ctrl+V 直接在反馈对话框中贴上剪贴板图片
- 🎨 现代化深色主题
- 📱 响应式设计（Web UI）
- 🌐 多语言支持（繁体中文、英文、简体中文）

## 🎯 为什么使用这个工具？

通过引导 AI 助手与用户进行确认，而非进行推测性的高成本工具调用，此模块可以大幅减少平台（如 Cursor）上的付费请求次数。在某些情况下，它可以将多达 25 次工具调用合并为单次反馈导向的请求，节省资源并提升性能。

## 📝 提示工程设定

为了获得最佳效果，请在您的 AI 助手中添加以下自定义提示（例如在 Cursor 的规则或提示中）：

### 基本提示
> 每当你想要询问问题时，请务必调用 MCP `mcp-feedback-enhanced`。  
> 每当你即将完成用户请求时，请调用 MCP `mcp-feedback-enhanced` 而不是直接结束流程。  
> 持续调用 MCP 直到用户的反馈为空，然后才结束请求。

### 完整规则范例
```
# MCP Interactive Feedback 规则

1. 在任何流程、任务、对话进行时，无论是询问、回复、或完成阶段性任务，皆必须调用 MCP mcp-feedback-enhanced。
2. 每当收到用户反馈，若反馈内容非空，必须再次调用 MCP mcp-feedback-enhanced，并根据反馈内容调整行为。
3. 仅当用户明确表示「结束」或「不再需要交互」时，才可停止调用 MCP mcp-feedback-enhanced，流程才算结束。
4. 除非收到结束指令，否则所有步骤都必须重复调用 MCP mcp-feedback-enhanced。
```

这将确保您的 AI 助手在标记任务完成前使用此 MCP 服务器请求用户反馈。

## 🔧 环境检测与配置

系统会自动检测运行环境并选择适当的界面：

### Qt GUI（本地环境）
- 使用 Qt 的 `QSettings` 按项目基础存储配置
- 包含命令设定、自动执行选项、窗口几何状态等
- 设定通常存储在平台特定位置（Windows 注册表、macOS plist 文件、Linux 配置目录）

### Web UI（SSH Remote 环境）
- 基于 FastAPI 和 WebSocket 的现代化界面
- 支持实时命令执行和输出显示
- 自动浏览器启动和会话管理
- 深色主题和响应式设计

### 调试模式控制
- **生产模式**：默认关闭所有调试输出，确保与 MCP 客户端完美兼容
- **调试模式**：设置 `MCP_DEBUG=true` 启用详细调试信息
- **输出隔离**：所有调试信息输出到 stderr，不干扰 MCP 通信

## 🚀 安装说明

### 方法 1：uvx 安装（推荐）

**这是最简单的方法，无需手动管理依赖项或虚拟环境：**

1. **安装 uv**（如果尚未安装）
   ```bash
   # Windows
   pip install uv

   # Linux/Mac
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **测试安装**
   ```bash
   # 查看版本信息（推荐使用 @latest 确保最新版本）
   uvx mcp-feedback-enhanced@latest version

   # 执行测试
   uvx mcp-feedback-enhanced@latest test

   # 持久化测试模式（可在浏览器中实际测试）
   uvx mcp-feedback-enhanced@latest test --persistent
   ```

### 方法 2：从源码安装（开发者）

适合需要修改代码或贡献开发的用户：

1. **获取程序代码**
   ```bash
   git clone https://github.com/Minidoracat/mcp-feedback-enhanced.git
   cd mcp-feedback-enhanced
   ```

2. **安装依赖项**
   ```bash
   uv sync
   ```

3. **测试安装**
   ```bash
   # 基本功能测试
   uv run python -m mcp_feedback_enhanced test
   
   # 持久化测试模式（可在浏览器中实际测试）
   uv run python -m mcp_feedback_enhanced test --persistent
   ```

4. **运行 MCP 服务器**
   ```bash
   uv run python -m mcp_feedback_enhanced
   ```

## ⚙️ AI 助手配置

### 推荐配置（使用 uvx）

在 Cursor 的设定中配置自定义 MCP 服务器，或手动编辑 `mcp.json`：

```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": [
        "mcp-feedback-enhanced@latest"
      ],
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

### 替代配置（从源码运行）

如果您需要使用源码版本或想要自定义环境变量：

```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-feedback-enhanced",
        "run",
        "python",
        "-m",
        "mcp_feedback_enhanced"
      ],
      "timeout": 600,
      "env": {
        "FORCE_WEB": "true",
        "MCP_DEBUG": "false"
      },
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

**记得将路径修改为您实际的项目目录！**

### Cline / Windsurf 配置

类似的设定原则：在各工具的 MCP 设定中配置服务器命令，使用 `mcp-feedback-enhanced` 作为服务器标识符。

## 🧪 测试和开发

### 使用 uvx 测试
```bash
# 完整功能测试（推荐）
uvx mcp-feedback-enhanced@latest test

# Qt GUI 专门测试
uvx mcp-feedback-enhanced@latest test --gui

# Web UI 专门测试
uvx mcp-feedback-enhanced@latest test --web

# 持久化测试模式（测试完不关闭，可交互测试）
uvx mcp-feedback-enhanced@latest test --persistent
uvx mcp-feedback-enhanced@latest test --gui --persistent
uvx mcp-feedback-enhanced@latest test --web --persistent

# 查看版本
uvx mcp-feedback-enhanced@latest version

# 启用调试模式测试
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

### 从源码测试
```bash
# 完整功能测试
uv run python -m mcp_feedback_enhanced test

# Qt GUI 专门测试
uv run python -m mcp_feedback_enhanced test --gui

# Web UI 专门测试
uv run python -m mcp_feedback_enhanced test --web

# 持久化测试模式
uv run python -m mcp_feedback_enhanced test --persistent

# 启用调试模式
MCP_DEBUG=true uv run python -m mcp_feedback_enhanced test
```

### 开发模式
使用 FastMCP 开发模式运行服务器并开启测试界面：
```bash
# 从源码
uv run fastmcp dev src/mcp_feedback_enhanced/server.py
```

### 测试选项说明
- **无参数 `test`**：执行完整测试套件（环境检测、参数验证、MCP 整合、Web UI）
- **`--gui`**：专门测试 Qt GUI 功能和界面
- **`--web`**：专门测试 Web UI 功能和 WebSocket 通信
- **`--persistent`**：持久化模式，测试完成后保持运行，方便交互测试

## 🌟 功能特色

### 🖥️ 双界面支持
- **Qt GUI**：适用于本地开发环境，提供原生体验
- **Web UI**：适用于 SSH remote 开发环境，现代化界面

### 🔍 智能环境检测
- 自动检测 SSH 连接环境变量
- 检测 DISPLAY 设定（Linux）
- 检测 VSCode Remote 开发环境
- 自动选择最适合的界面

### 💻 命令执行功能
- 实时命令执行和输出显示
- 支持命令中断和进程树终止
- 自动工作目录设定
- 命令历史记录

### 🎨 现代化界面
- 深色主题设计
- 响应式布局（支持手机浏览器）
- WebSocket 实时通信
- 加载动画和视觉反馈

### 🖼️ 图片处理功能
- 支持多种图片格式（PNG、JPG、JPEG、GIF、BMP、WebP）
- 智能文件大小检测和压缩
- 拖拽上传和剪贴板支持
- 自动转换为 MCP Image 对象
- Base64 编码和预览

## 🛠️ 环境变量配置

### 核心环境变量

| 环境变量 | 用途 | 可用值 | 默认值 |
|---------|------|--------|--------|
| `FORCE_WEB` | 强制使用 Web UI | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |
| `MCP_DEBUG` | 启用调试模式 | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |
| `INCLUDE_BASE64_DETAIL` | 图片反馈包含完整 Base64 | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |

### 使用范例

**在 MCP 配置中设定**：
```json
"env": {
  "FORCE_WEB": "true",           // 强制使用 Web UI
  "MCP_DEBUG": "false",          // 关闭调试输出（推荐生产环境）
  "INCLUDE_BASE64_DETAIL": "true" // 包含完整图片 Base64 数据
}
```

**在命令行中设定**：
```bash
# 启用调试模式测试
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

## 📖 使用范例

### 1. **推荐 MCP 配置（uvx）**

使用 uvx 的简洁配置：
```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": [
        "mcp-feedback-enhanced@latest"
      ],
      "timeout": 600,
      "env": {
        "MCP_DEBUG": "false"
      },
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

### 2. **自定义环境变量配置**

如需要自定义环境变量（例如强制使用 Web UI）：
```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-feedback-enhanced",
        "run",
        "python",
        "-m",
        "mcp_feedback_enhanced"
      ],
      "timeout": 600,
      "env": {
        "FORCE_WEB": "true",
        "MCP_DEBUG": "false",
        "INCLUDE_BASE64_DETAIL": "true"
      },
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

### 3. **工具调用范例**

AI 助手会如此调用 `mcp-feedback-enhanced` 工具：

```xml
<use_mcp_tool>
  <server_name>mcp-feedback-enhanced</server_name>
  <tool_name>interactive_feedback</tool_name>
  <arguments>
    {
      "project_directory": "/path/to/your/project",
      "summary": "我已经实现了您请求的更改并重构了主模块。请查看结果并提供反馈。"
    }
  </arguments>
</use_mcp_tool>
```

## 🔄 工作流程

1. **AI 助手调用** - AI 完成任务后调用 `mcp-feedback-enhanced`
2. **环境检测** - 系统自动检测运行环境
3. **界面启动** - 根据环境启动 Qt GUI 或 Web UI
4. **用户交互** - 用户可以：
   - 执行命令和查看输出
   - 提供文字反馈（支持 Ctrl+Enter 快速提交，兼容主键盘和数字键盘）
   - 上传图片（拖拽、剪贴板粘贴 Ctrl+V）
   - 使用多语言界面切换
5. **反馈传递** - 用户反馈（包括图片）传回给 AI 助手
6. **流程继续** - AI 根据反馈继续或结束任务

## 🆕 版本更新

### v2.0.14 - 增强快捷键支持（最新版）
- ⌨️ **数字键盘支持**：Ctrl+Enter 快捷键现在同时支持主键盘和数字键盘的 Enter 键
- 🖼️ **智能图片贴上**：Ctrl+V 可直接在反馈对话框中贴上剪贴板图片，无需额外上传步骤
- 🎮 **双重快捷键机制**：GUI 使用 QShortcut 双重设定，确保完整兼容性
- 🌐 **Web UI 快捷键增强**：使用 key/code 双重检测机制，支持所有 Enter 键变体
- 💡 **用户体验改善**：更新三语言提示文字，明确标示数字键盘支持和图片贴上功能
- 🔧 **API 简化**：移除 `force_web_ui` 参数，简化 API 设计，只保留环境变量控制
- 📝 **文档更新**：更新所有相关说明文档，移除冗余范例

### v2.0.9 - 多语言架构重构
- 🌏 **完整多语言架构重构**：从嵌入式翻译迁移到结构化 JSON 基础系统
- 📁 **语言文件组织化**：将语言文件分离到 `src/mcp_feedback_enhanced/locales/` 目录结构
- 🔧 **增强国际化功能**：动态加载与嵌套键值结构，支持浏览器语言检测
- 📚 **完整文档说明**：为翻译贡献者新增详细 README，包含范例和指南
- 🔄 **向后兼容性**：在启用现代功能的同时保持与现有程序代码的完全兼容性
- 🖼️ **界面截图更新**：新增完整截图展示英文和繁体中文界面
- 📝 **文档强化**：更新 README 文件，加入多语言截图和功能说明
- 🛡️ **增强错误处理**：改善稳定性和错误恢复机制
- 🚀 **性能优化**：更快的启动时间和改善的资源管理
- 🔧 **错误修复**：各种小型修复和改善
- 📦 **包优化**：更好的依赖管理和构建流程
- 🎨 **视觉改善**：增强按钮可见性和颜色一致性
- 🖱️ **交互修复**：改善拖拽指示器和空状态提示
- 📱 **响应式设计**：更好的不同屏幕尺寸适应
- 🌐 **语言切换**：修复 Qt GUI 语言切换，加入适当的勾选标记

### v2.0.3 - 编码与通信修复
- 🛡️ **完全修复中文字符编码问题**：支持完美的中文显示
- 🔧 **解决 JSON 解析错误**：修复 MCP 客户端的 "Unexpected token" 错误
- 🎛️ **可控调试模式**：通过 `MCP_DEBUG` 环境变量控制调试输出
- 🖼️ **强化图片支持**：改善图片处理和 Base64 编码
- 🚀 **输出隔离**：严格分离调试输出与 MCP 通信
- 📦 **包优化**：改善 uvx 安装体验和依赖管理

### v2.0.0 - Web UI 与远程支持
- ✅ **Web UI 界面**：新增 Web UI 支持 SSH remote 开发环境
- ✅ **自动环境检测**：根据环境智能选择界面
- ✅ **WebSocket 实时通信**：实时命令执行和反馈
- ✅ **现代化深色主题**：美观的深色主题与响应式设计
- ✅ **持久化测试模式**：增强的测试功能

### v1.0.0 - 基础版本（原作者）
- ✅ **Qt GUI 界面**：原生桌面界面
- ✅ **命令执行**：实时命令执行和输出
- ✅ **MCP 协议支持**：完整的模型上下文协议实现
- ✅ **跨平台支持**：Windows、macOS 和 Linux 兼容性

## 🐛 故障排除

### 常见问题

**Q: 出现 "Unexpected token 'D'" 错误**  
A: 这通常是调试输出干扰造成的。确保在生产环境中设置 `MCP_DEBUG=false` 或不设置该环境变量。

**Q: 中文字符显示为乱码**  
A: 已在 v2.0.3 中完全修复。如果仍有问题，请更新到最新版本：`uvx mcp-feedback-enhanced@latest`

**Q: 图片上传失败**  
A: 检查图片大小是否超过 1MB 限制，并确保格式为支持的类型（PNG、JPG、JPEG、GIF、BMP、WebP）。

**Q: Web UI 无法启动**  
A: 确保防火墙允许本地端口访问，或尝试设置 `FORCE_WEB=true` 环境变量。

### 调试模式

如需详细调试信息，请启用调试模式：
```bash
# 设置调试环境变量
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

## 🙏 致谢与联系

### 原作者
**Fábio Ferreira** - [X @fabiomlferreira](https://x.com/fabiomlferreira)  
**原始项目：** [noopstudios/interactive-feedback-mcp](https://github.com/noopstudios/interactive-feedback-mcp)  

如果您觉得 Interactive Feedback MCP 有用，最好的支持方式是：
- 🌟 **为原作者的项目按星星**：[按此前往并按星星](https://github.com/noopstudios/interactive-feedback-mcp) ⭐
- 📱 **关注原作者的 X 账号**：[@fabiomlferreira](https://x.com/fabiomlferreira)

### UI 设计灵感
**sanshao85** - [mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)  
感谢提供现代化界面设计灵感，让本项目的 UI 更加美观和易用。

### 分支维护者
如有关于 Web UI 功能、图片支持或其他问题，欢迎在 [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues) 中提出。

### 社区支持
加入我们的 Discord 社区获得实时协助和讨论：
**Discord 社区：** [https://discord.gg/Gur2V67](https://discord.gg/Gur2V67)  
有任何问题都可以到社区中寻求帮助！

### 相关资源
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 官方文档

## 📄 授权条款

本项目采用 MIT 授权条款。详见 [LICENSE](LICENSE) 文件。

---

**🌟 欢迎 Star 此项目并分享给更多开发者！** 