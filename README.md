 # Interactive Feedback MCP

**🌐 Language / 語言切換:** **English** | [繁體中文](README.zh-TW.md)

**Original Author:** [Fábio Ferreira](https://x.com/fabiomlferreira)  
**Enhanced Fork:** [Minidoracat](https://github.com/Minidoracat)  
**UI Design Reference:** [sanshao85/mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector) - Thanks for modern interface design inspiration  
**Related Resources:** [dotcursorrules.com](https://dotcursorrules.com/) for more AI development workflow tools

A simple [MCP server](https://modelcontextprotocol.io/) for implementing human-in-the-loop workflows in AI-assisted development tools (like [Cursor](https://www.cursor.com)). This server allows you to execute commands, view output, and provide text feedback and images directly to the AI. Also supports [Cline](https://cline.bot) and [Windsurf](https://windsurf.com).

## ✨ New Features

### 🌐 Full SSH Remote Support
- **Automatic Environment Detection**: Intelligently detects runtime environment and selects appropriate interface
- **Local Environment**: Uses original Qt GUI interface
- **SSH Remote Environment**: Automatically switches to modern Web UI
- **Real-time Communication**: WebSocket-based real-time command output and feedback
- **Dark Theme**: Provides modern dark theme interface

### 🖼️ Image Upload Support
- **Multi-format Support**: PNG, JPG, JPEG, GIF, BMP, WebP
- **Drag & Drop Upload**: Support for dragging files to interface
- **Clipboard Support**: Direct paste from clipboard
- **Auto Compression**: Smart compression for large images to meet 1MB limit
- **MCP Integration**: Images automatically converted to MCP Image objects

### 🛡️ Stability Improvements
- **Encoding Fix**: Complete resolution of Chinese character garbled text issues
- **Debug Control**: Controllable debug output, avoiding JSON parsing errors
- **Error Handling**: Enhanced error handling ensuring stable program operation
- **Output Isolation**: Strict isolation of debug output from MCP communication

## 🖥️ Interface Preview

### Qt GUI Interface (Local Environment)
![Qt GUI Interface](docs/images/qt-gui-interface.png)

### Web UI Interface (SSH Remote Environment)
![Web UI Interface](docs/images/web-ui-interface.jpeg)

Both interfaces support:
- 💬 Text feedback input
- 🖼️ Image upload (supports drag & drop, clipboard paste)
- ⚡ Real-time command execution
- 🎨 Modern dark theme
- 📱 Responsive design (Web UI)

## 🎯 Why Use This Tool?

By guiding AI assistants to confirm with users rather than making speculative high-cost tool calls, this module can significantly reduce the number of paid requests on platforms like Cursor. In some cases, it can consolidate up to 25 tool calls into a single feedback-oriented request, saving resources and improving performance.

## 📝 Prompt Engineering Setup

For best results, add the following custom prompts to your AI assistant (e.g., in Cursor's rules or prompts):

### Basic Prompt
> Whenever you want to ask a question, be sure to call MCP `mcp-feedback-enhanced`.  
> Whenever you're about to complete a user request, call MCP `mcp-feedback-enhanced` instead of ending the process directly.  
> Continue calling MCP until the user's feedback is empty, then end the request.

### Complete Rules Example
```
# MCP Interactive Feedback Rules

1. During any process, task, or conversation, whether asking, responding, or completing stage tasks, must call MCP mcp-feedback-enhanced.
2. When receiving user feedback, if feedback content is not empty, must call MCP mcp-feedback-enhanced again and adjust behavior based on feedback.
3. Only when user explicitly indicates "end" or "no more interaction needed" can you stop calling MCP mcp-feedback-enhanced, then the process is complete.
4. Unless receiving end command, all steps must repeatedly call MCP mcp-feedback-enhanced.
```

This ensures your AI assistant uses this MCP server to request user feedback before marking tasks as complete.

## 🚀 Installation

### Method 1: uvx Installation (Recommended)

**This is the simplest method, no need to manually manage dependencies or virtual environments:**

1. **Install uv** (if not already installed)
   ```bash
   # Windows
   pip install uv

   # Linux/Mac
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Test Installation**
   ```bash
   # View version info (recommend using @latest for latest version)
   uvx mcp-feedback-enhanced@latest version

   # Run tests
   uvx mcp-feedback-enhanced@latest test

   # Persistent test mode (can actually test in browser)
   uvx mcp-feedback-enhanced@latest test --persistent
   ```

### Method 2: Install from Source (Developers)

Suitable for users who need to modify code or contribute to development:

1. **Get the Code**
   ```bash
   git clone https://github.com/Minidoracat/mcp-feedback-enhanced.git
   cd mcp-feedback-enhanced
   ```

2. **Install Dependencies**
   ```bash
   uv sync
   ```

3. **Test Installation**
   ```bash
   # Basic functionality test
   uv run python -m mcp_feedback_enhanced test
   
   # Persistent test mode (can actually test in browser)
   uv run python -m mcp_feedback_enhanced test --persistent
   ```

4. **Run MCP Server**
   ```bash
   uv run python -m mcp_feedback_enhanced
   ```

## ⚙️ AI Assistant Configuration

### Recommended Configuration (using uvx)

Configure custom MCP server in Cursor settings, or manually edit `mcp.json`:

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

### Alternative Configuration (running from source)

If you need to use source version or want to customize environment variables:

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

**Remember to modify the path to your actual project directory!**

## 🧪 Testing and Development

### Testing with uvx
```bash
# Complete functionality test (recommended)
uvx mcp-feedback-enhanced@latest test

# Qt GUI specific test
uvx mcp-feedback-enhanced@latest test --gui

# Web UI specific test
uvx mcp-feedback-enhanced@latest test --web

# Persistent test mode (doesn't close after test, allows interactive testing)
uvx mcp-feedback-enhanced@latest test --persistent

# View version
uvx mcp-feedback-enhanced@latest version

# Enable debug mode testing
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

## 🛠️ Environment Variables

### Core Environment Variables

| Environment Variable | Purpose | Available Values | Default |
|---------------------|---------|------------------|---------|
| `FORCE_WEB` | Force use Web UI | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |
| `MCP_DEBUG` | Enable debug mode | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |
| `INCLUDE_BASE64_DETAIL` | Include full Base64 in image feedback | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |

## 🐛 Troubleshooting

### Common Issues

**Q: Getting "Unexpected token 'D'" error**  
A: This is usually caused by debug output interference. Ensure `MCP_DEBUG=false` is set in production environment or don't set this environment variable.

**Q: Chinese characters display as garbled text**  
A: Completely fixed in v2.0.3. If still having issues, please update to latest version: `uvx mcp-feedback-enhanced@latest`

**Q: Image upload fails**  
A: Check if image size exceeds 1MB limit and ensure format is supported (PNG, JPG, JPEG, GIF, BMP, WebP).

**Q: Web UI won't start**  
A: Ensure firewall allows local port access, or try setting `FORCE_WEB=true` environment variable.

## 🙏 Acknowledgments & Contact

### Original Author
**Fábio Ferreira** - [X @fabiomlferreira](https://x.com/fabiomlferreira)  
If you find Interactive Feedback MCP useful, the best way to support is by following the original author's X account.

### UI Design Inspiration
**sanshao85** - [mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)  
Thanks for providing modern interface design inspiration, making this project's UI more beautiful and user-friendly.

### Fork Maintainer
For questions about Web UI functionality, image support, or other issues, please submit at [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues).

### Community Support
Join our Discord community for real-time assistance and discussions:
**Discord Community:** [https://discord.gg/Gur2V67](https://discord.gg/Gur2V67)  
Feel free to ask any questions in the community!

### Related Resources
- [dotcursorrules.com](https://dotcursorrules.com/) - More AI-assisted development workflow resources
- [Model Context Protocol](https://modelcontextprotocol.io/) - Official MCP documentation

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

**🌟 Welcome to Star this project and share it with more developers!**