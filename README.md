# Interactive Feedback MCP

**🌐 Language / 語言切換:** **English** | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

**Original Author:** [Fábio Ferreira](https://x.com/fabiomlferreira) | [Original Project](https://github.com/noopstudios/interactive-feedback-mcp) ⭐  
**Enhanced Fork:** [Minidoracat](https://github.com/Minidoracat)  
**UI Design Reference:** [sanshao85/mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

## 🎯 Core Concept

This is an [MCP server](https://modelcontextprotocol.io/) that implements **human-in-the-loop** workflows in AI-assisted development tools. By guiding AI to confirm with users rather than making speculative operations, it can consolidate up to 25 tool calls into a single feedback-oriented request, dramatically reducing platform costs.

**Supported Platforms:** [Cursor](https://www.cursor.com) | [Cline](https://cline.bot) | [Windsurf](https://windsurf.com)

### 🔄 Workflow
1. **AI Call** → `mcp-feedback-enhanced`
2. **Environment Detection** → Auto-select appropriate interface
3. **User Interaction** → Command execution, text feedback, image upload
4. **Feedback Delivery** → Information returns to AI
5. **Process Continuation** → Adjust or end based on feedback

## 🌟 Key Features

### 🖥️ Dual Interface System
- **Qt GUI**: Native experience for local environments
- **Web UI**: Modern interface for remote SSH environments
- **Smart Switching**: Auto-detect environment and choose optimal interface

### 🖼️ Image Support
- **Format Support**: PNG, JPG, JPEG, GIF, BMP, WebP
- **Upload Methods**: Drag & drop files + clipboard paste (Ctrl+V)
- **Auto Processing**: Smart compression to ensure 1MB limit compliance

### 🌏 Multi-language
- **Three Languages**: Traditional Chinese, English, Simplified Chinese
- **Smart Detection**: Auto-select based on system language
- **Live Switching**: Change language directly within interface

## 🖥️ Interface Preview

![Qt GUI Interface](docs/images/gui-en.png)  
*Qt GUI Interface - Local Environment*

![Web UI Interface](docs/images/web-en.png)  
*Web UI Interface - SSH Remote Environment*

**Keyboard Shortcuts**
- `Ctrl+Enter`: Submit feedback (supports both main keyboard and numpad)
- `Ctrl+V`: Directly paste clipboard images

## 🚀 Quick Start

### 1. Installation & Testing
```bash
# Install uv (if not already installed)
pip install uv

# Quick test
uvx mcp-feedback-enhanced@latest test

# Interactive test
uvx mcp-feedback-enhanced@latest test --persistent
```

### 2. MCP Configuration
**Basic Configuration** (suitable for most users):
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

**Advanced Configuration** (custom environment needed):
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

### 3. Prompt Engineering Setup
For best results, add these rules to your AI assistant:

```
# MCP Interactive Feedback Rules

1. During any process, task, or conversation, whether asking, responding, or completing stage tasks, must call MCP mcp-feedback-enhanced.
2. When receiving user feedback, if feedback content is not empty, must call MCP mcp-feedback-enhanced again and adjust behavior based on feedback.
3. Only when user explicitly indicates "end" or "no more interaction needed" can you stop calling MCP mcp-feedback-enhanced, then the process is complete.
4. Unless receiving end command, all steps must repeatedly call MCP mcp-feedback-enhanced.
```

## ⚙️ Advanced Settings

### Environment Variables
| Variable | Purpose | Values | Default |
|----------|---------|--------|---------|
| `FORCE_WEB` | Force use Web UI | `true`/`false` | `false` |
| `MCP_DEBUG` | Debug mode | `true`/`false` | `false` |
| `INCLUDE_BASE64_DETAIL` | Full Base64 for images | `true`/`false` | `false` |

### Testing Options
```bash
# Interface-specific testing
uvx mcp-feedback-enhanced@latest test --gui    # Qt GUI only
uvx mcp-feedback-enhanced@latest test --web    # Web UI only

# Debug mode
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

### Developer Installation
```bash
git clone https://github.com/Minidoracat/mcp-feedback-enhanced.git
cd mcp-feedback-enhanced
uv sync
uv run python -m mcp_feedback_enhanced test
```

## 🆕 Version Highlights

### v2.0.14 (Latest)
- ⌨️ Enhanced Shortcuts: Ctrl+Enter supports numpad
- 🖼️ Smart Image Pasting: Ctrl+V directly pastes clipboard images

### v2.0.9
- 🌏 Multi-language architecture refactor with dynamic loading
- 📁 Modularized language file organization

### v2.0.3
- 🛡️ Complete fix for Chinese character encoding issues
- 🔧 Resolved JSON parsing errors

### v2.0.0
- ✅ Added Web UI support for remote environments
- ✅ Auto environment detection and interface selection
- ✅ WebSocket real-time communication

## 🐛 Common Issues

**Q: Getting "Unexpected token 'D'" error**  
A: Debug output interference. Set `MCP_DEBUG=false` or remove the environment variable.

**Q: Chinese character garbled text**  
A: Fixed in v2.0.3. Update to latest version: `uvx mcp-feedback-enhanced@latest`

**Q: Image upload fails**  
A: Check file size (≤1MB) and format (PNG/JPG/GIF/BMP/WebP).

**Q: Web UI won't start**  
A: Set `FORCE_WEB=true` or check firewall settings.

## 🙏 Acknowledgments

### 🌟 Support Original Author
**Fábio Ferreira** - [X @fabiomlferreira](https://x.com/fabiomlferreira)  
**Original Project:** [noopstudios/interactive-feedback-mcp](https://github.com/noopstudios/interactive-feedback-mcp)

If you find this useful, please:
- ⭐ [Star the original project](https://github.com/noopstudios/interactive-feedback-mcp)
- 📱 [Follow the original author](https://x.com/fabiomlferreira)

### Design Inspiration
**sanshao85** - [mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

### Community Support
- **Discord:** [https://discord.gg/Gur2V67](https://discord.gg/Gur2V67)
- **Issues:** [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---
**🌟 Welcome to Star and share with more developers!**