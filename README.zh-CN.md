# Interactive Feedback MCP（交互反馈 MCP）

**🌐 语言切换 / Language:** [English](README.md) | [繁體中文](README.zh-TW.md) | **简体中文**

**原作者：** [Fábio Ferreira](https://x.com/fabiomlferreira) | [原始项目](https://github.com/noopstudios/interactive-feedback-mcp) ⭐  
**分支版本：** [Minidoracat](https://github.com/Minidoracat)  
**UI 设计参考：** [sanshao85/mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

## 🎯 核心概念

这是一个 [MCP 服务器](https://modelcontextprotocol.io/)，在 AI 辅助开发工具中实现**人在回路（human-in-the-loop）**的工作流程。通过引导 AI 与用户确认而非进行推测性操作，可将多达 25 次工具调用合并为单次反馈导向请求，大幅节省平台成本。

**支持平台：** [Cursor](https://www.cursor.com) | [Cline](https://cline.bot) | [Windsurf](https://windsurf.com)

### 🔄 工作流程
1. **AI 调用** → `mcp-feedback-enhanced`
2. **环境检测** → 自动选择合适界面
3. **用户交互** → 命令执行、文字反馈、图片上传
4. **反馈传递** → 信息返回 AI
5. **流程继续** → 根据反馈调整或结束

## 🌟 主要功能

### 🖥️ 双界面系统
- **Qt GUI**：本地环境原生体验，模块化重构设计
- **Web UI**：远程 SSH 环境现代化界面，全新架构
- **智能切换**：自动检测环境并选择最适界面

### 🎨 全新界面设计（v2.1.0）
- **模块化架构**：GUI 和 Web UI 均采用模块化设计
- **集中管理**：文件夹结构重新组织，维护更容易
- **现代化主题**：改进的视觉设计和用户体验
- **响应式布局**：适应不同屏幕尺寸和窗口大小

### 🖼️ 图片支持
- **格式支持**：PNG、JPG、JPEG、GIF、BMP、WebP
- **上传方式**：拖拽文件 + 剪贴板粘贴（Ctrl+V）
- **自动处理**：智能压缩确保符合 1MB 限制

### 🌏 多语言
- **三语支持**：简体中文、英文、繁体中文
- **智能检测**：根据系统语言自动选择
- **即时切换**：界面内可直接切换语言

## 🖥️ 界面预览

### Qt GUI 界面（重构版）
<div align="center">
  <img src="docs/images/zh-TW/gui1.png" width="400" alt="Qt GUI 主界面" />
  <img src="docs/images/zh-TW/gui2.png" width="400" alt="Qt GUI 设置界面" />
</div>

*Qt GUI 界面 - 模块化重构，支持本地环境*

### Web UI 界面（重构版）
<div align="center">
  <img src="docs/images/zh-TW/web1.png" width="400" alt="Web UI 主界面" />
  <img src="docs/images/zh-TW/web2.png" width="400" alt="Web UI 设置界面" />
</div>

*Web UI 界面 - 全新架构，适合 SSH Remote 环境*

**快捷键支持**
- `Ctrl+Enter`：提交反馈（主键盘与数字键盘皆支持）
- `Ctrl+V`：直接粘贴剪贴板图片

## 🚀 快速开始

### 1. 安装与测试
```bash
# 安装 uv（如果尚未安装）
pip install uv

# 快速测试
uvx mcp-feedback-enhanced@latest test
```

### 2. 配置 MCP
**基本配置**（适合大多数用户）：
```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@latest"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

**进阶配置**（需要自定义环境）：
```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@latest"],
      "timeout": 600,
      "env": {
        "FORCE_WEB": "true",
        "MCP_DEBUG": "false"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

### 3. 设定提示工程
为了获得最佳效果，请在 AI 助手中添加以下规则：

```
# MCP Interactive Feedback 规则

1. 在任何流程、任务、对话进行时，无论是询问、回复、或完成阶段性任务，皆必须调用 MCP mcp-feedback-enhanced。
2. 每当收到用户反馈，若反馈内容非空，必须再次调用 MCP mcp-feedback-enhanced，并根据反馈内容调整行为。
3. 仅当用户明确表示「结束」或「不再需要交互」时，才可停止调用 MCP mcp-feedback-enhanced，流程才算结束。
4. 除非收到结束指令，否则所有步骤都必须重复调用 MCP mcp-feedback-enhanced。
```

## ⚙️ 进阶设定

### 环境变量
| 变量 | 用途 | 值 | 默认 |
|------|------|-----|------|
| `FORCE_WEB` | 强制使用 Web UI | `true`/`false` | `false` |
| `MCP_DEBUG` | 调试模式 | `true`/`false` | `false` |
| `INCLUDE_BASE64_DETAIL` | 图片完整 Base64 | `true`/`false` | `false` |

### 测试选项
```bash
# 版本查询
uvx mcp-feedback-enhanced@latest version       # 检查版本

# 指定界面测试
uvx mcp-feedback-enhanced@latest test --gui    # 快速测试 Qt GUI
uvx mcp-feedback-enhanced@latest test --web    # 测试 Web UI (自动持续运行)

# 调试模式
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

### 开发者安装
```bash
git clone https://github.com/Minidoracat/mcp-feedback-enhanced.git
cd mcp-feedback-enhanced
uv sync
```

**本地测试方式**
```bash
# 方式一：标准测试（推荐）
uv run python -m mcp_feedback_enhanced test

# 方式二：完整测试套件（macOS 和 Windows 通用开发环境）
uvx --with-editable . mcp-feedback-enhanced test

# 方式三：指定界面测试
uvx --with-editable . mcp-feedback-enhanced test --gui    # 快速测试 Qt GUI
uvx --with-editable . mcp-feedback-enhanced test --web    # 测试 Web UI (自动持续运行)
```

**测试说明**
- **标准测试**：执行完整的功能检查，适合日常开发验证
- **完整测试**：包含所有组件的深度测试，适合发布前验证
- **Qt GUI 测试**：快速启动并测试本地图形界面
- **Web UI 测试**：启动 Web 服务器并保持运行，便于完整测试 Web 功能

## 🆕 版本亮点

### v2.2.0 (布局与设置界面优化)
- ✨ **界面布局增强**：GUI 与 Web UI 的合并模式新增摘要与反馈的左右布局（水平分割）选项，提供更灵活的查看方式 (实现 [Issue #1](https://github.com/Minidoracat/mcp-feedback-enhanced/issues/1))。
- 🎨 **设置界面改进**：优化了 GUI 与 Web UI 的设置页面，提升布局清晰度与用户操作体验。
- ⌨️ **快捷键完善 (GUI)**：提交反馈快捷键 (Ctrl+Enter / Cmd+Enter) 现已完整支持数字键盘(九宫格)的 Enter 键。
- 🐞 **问题修复 (Web UI)**：解决了在文本输入区使用 Ctrl+V 粘贴图片时，可能导致图片重复粘贴的问题。

### v2.1.1（窗口定位优化）
- 🖥️ **智能窗口定位**：新增「总是在主屏幕中心显示窗口」设置选项
- 🌐 **多屏幕支持**：完美解决 T 字型屏幕排列等复杂多屏幕环境的窗口定位问题
- 💾 **位置记忆**：自动保存和恢复窗口位置，智能检测窗口可见性
- ⚙️ **用户选择**：提供智能定位（默认）和强制中心显示两种模式

### v2.1.0（最新重构版）
- 🎨 **全面重构**：GUI 和 Web UI 采用模块化架构
- 📁 **集中管理**：重新组织文件夹结构，提升维护性
- 🖥️ **界面优化**：现代化设计和改进的用户体验
- 🍎 **macOS 界面优化**：针对 macOS 用户体验进行专项改进
- ⚙️ **功能增强**：新增设置选项和自动关闭页面功能
- 🌐 **语言切换**：修复 Web UI 语言切换时内容更新问题
- ℹ️ **关于页面**：新增关于页面，包含版本信息、项目链接和致谢内容

### v2.0.14
- ⌨️ 增强快捷键：Ctrl+Enter 支持数字键盘
- 🖼️ 智能图片粘贴：Ctrl+V 直接粘贴剪贴板图片

### v2.0.9
- 🌏 多语言架构重构，支持动态载入
- 📁 语言文件模块化组织

### v2.0.3
- 🛡️ 完全修复中文字符编码问题
- 🔧 解决 JSON 解析错误

### v2.0.0
- ✅ 新增 Web UI 支持远程环境
- ✅ 自动环境检测与界面选择
- ✅ WebSocket 即时通讯

## 🐛 常见问题

**Q: 出现 "Unexpected token 'D'" 错误**  
A: 调试输出干扰。设置 `MCP_DEBUG=false` 或移除该环境变量。

**Q: 中文字符乱码**  
A: 已在 v2.0.3 修复。更新到最新版本：`uvx mcp-feedback-enhanced@latest`

**Q: 图片上传失败**  
A: 检查文件大小（≤1MB）和格式（PNG/JPG/GIF/BMP/WebP）。

**Q: Web UI 无法启动**  
A: 设置 `FORCE_WEB=true` 或检查防火墙设定。

**Q: Gemini Pro 2.5 无法解析图片**  
A: 已知问题，Gemini Pro 2.5 可能无法正确解析上传的图片内容。实测 Claude-4-Sonnet 可以正常解析图片。建议使用 Claude 模型获得更好的图片理解能力。

**Q: 多屏幕视窗定位问题**  
A: 已在 v2.1.1 修复。进入「⚙️ 设置」标签页，勾选「总是在主屏幕中心显示窗口」即可解决窗口定位问题。特别适用于 T 字型屏幕排列等复杂多屏幕配置。

## 🙏 致谢

### 🌟 支持原作者
**Fábio Ferreira** - [X @fabiomlferreira](https://x.com/fabiomlferreira)  
**原始项目：** [noopstudios/interactive-feedback-mcp](https://github.com/noopstudios/interactive-feedback-mcp)

如果您觉得有用，请：
- ⭐ [为原项目按星星](https://github.com/noopstudios/interactive-feedback-mcp)
- 📱 [关注原作者](https://x.com/fabiomlferreira)

### 设计灵感
**sanshao85** - [mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

### 社群支援
- **Discord：** [https://discord.gg/Gur2V67](https://discord.gg/Gur2V67)
- **Issues：** [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)

## 📄 授权

MIT 授权条款 - 详见 [LICENSE](LICENSE) 档案

---
**🌟 欢迎 Star 并分享给更多开发者！**