# Interactive Feedback MCP

**🌐 Language / 語言切換:** **English** | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

**Original Author:** [Fábio Ferreira](https://x.com/fabiomlferreira) | [Original Project](https://github.com/noopstudios/interactive-feedback-mcp) ⭐  
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

### 🌏 Multi-language Support
- **Full Internationalization**: Complete multi-language support with structured JSON translation files
- **Supported Languages**: Traditional Chinese, English, Simplified Chinese
- **Smart Detection**: Automatic language detection based on system locale
- **Easy Extension**: Simple JSON-based translation system for adding new languages
- **Legacy Compatibility**: Fully backward compatible with existing code

## 🖥️ Interface Preview

### Qt GUI Interface (Local Environment)
![Qt GUI Interface - English](docs/images/gui-en.png)

### Web UI Interface (SSH Remote Environment)
![Web UI Interface - English](docs/images/web-en.png)

Both interfaces support:
- 💬 Text feedback input
- 🖼️ Image upload (supports drag & drop, clipboard paste)
- ⚡ Real-time command execution
- ⌨️ **Keyboard Shortcuts**:
  - Ctrl+Enter for quick feedback submission (supports main keyboard and numpad)
  - Ctrl+V to paste images directly in feedback dialog
- 🎨 Modern dark theme
- 📱 Responsive design (Web UI)
- 🌐 Multi-language support (Traditional Chinese, English, Simplified Chinese)

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

## 🔧 Environment Detection & Configuration

The system automatically detects the runtime environment and selects the appropriate interface:

### Qt GUI (Local Environment)
- Uses Qt's `QSettings` for project-based configuration storage
- Includes command settings, auto-execution options, window geometry states, etc.
- Settings are typically stored in platform-specific locations (Windows Registry, macOS plist files, Linux config directories)

### Web UI (SSH Remote Environment)
- Modern interface based on FastAPI and WebSocket
- Supports real-time command execution and output display
- Automatic browser launch and session management
- Dark theme and responsive design

### Debug Mode Control
- **Production Mode**: Default off for all debug output, ensuring perfect compatibility with MCP clients
- **Debug Mode**: Set `MCP_DEBUG=true` to enable detailed debug information
- **Output Isolation**: All debug information outputs to stderr, not interfering with MCP communication

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

### Cline / Windsurf Configuration

Similar configuration principles: Configure server commands in the MCP settings of each tool, using `mcp-feedback-enhanced` as the server identifier.

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
uvx mcp-feedback-enhanced@latest test --gui --persistent
uvx mcp-feedback-enhanced@latest test --web --persistent

# View version
uvx mcp-feedback-enhanced@latest version

# Enable debug mode testing
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

### Testing from Source
```bash
# Complete functionality test
uv run python -m mcp_feedback_enhanced test

# Qt GUI specific test
uv run python -m mcp_feedback_enhanced test --gui

# Web UI specific test
uv run python -m mcp_feedback_enhanced test --web

# Persistent test mode
uv run python -m mcp_feedback_enhanced test --persistent

# Enable debug mode
MCP_DEBUG=true uv run python -m mcp_feedback_enhanced test
```

### Development Mode
Run server with FastMCP development mode and open test interface:
```bash
# From source
uv run fastmcp dev src/mcp_feedback_enhanced/server.py
```

### Test Options Description
- **No parameter `test`**: Execute complete test suite (environment detection, parameter validation, MCP integration, Web UI)
- **`--gui`**: Specifically test Qt GUI functionality and interface
- **`--web`**: Specifically test Web UI functionality and WebSocket communication
- **`--persistent`**: Persistent mode, keeps running after test completion for interactive testing

## 🌟 Feature Highlights

### 🖥️ Dual Interface Support
- **Qt GUI**: Suitable for local development environments, providing native experience
- **Web UI**: Suitable for SSH remote development environments, modern interface

### 🔍 Smart Environment Detection
- Auto-detect SSH connection environment variables
- Detect DISPLAY settings (Linux)
- Detect VSCode Remote development environment
- Automatically select the most suitable interface

### 💻 Command Execution Features
- Real-time command execution and output display
- Support command interruption and process tree termination
- Automatic working directory setup
- Command history recording

### 🎨 Modern Interface
- Dark theme design
- Responsive layout (supports mobile browsers)
- WebSocket real-time communication
- Loading animations and visual feedback

### 🖼️ Image Processing Features
- Support multiple image formats (PNG, JPG, JPEG, GIF, BMP, WebP)
- Smart file size detection and compression
- Drag & drop upload and clipboard support
- Automatic conversion to MCP Image objects
- Base64 encoding and preview

## 🛠️ Environment Variables

### Core Environment Variables

| Environment Variable | Purpose | Available Values | Default |
|---------------------|---------|------------------|---------|
| `FORCE_WEB` | Force use Web UI | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |
| `MCP_DEBUG` | Enable debug mode | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |
| `INCLUDE_BASE64_DETAIL` | Include full Base64 in image feedback | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` | `false` |

### Usage Examples

**In MCP configuration**:
```json
"env": {
  "FORCE_WEB": "true",           // Force use Web UI
  "MCP_DEBUG": "false",          // Turn off debug output (recommended for production)
  "INCLUDE_BASE64_DETAIL": "true" // Include full image Base64 data
}
```

**In command line**:
```bash
# Enable debug mode testing
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

## 📖 Usage Examples

### 1. **Recommended MCP Configuration (uvx)**

Simple configuration using uvx:
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

### 2. **Custom Environment Variable Configuration**

If you need custom environment variables (e.g., force Web UI):
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

### 3. **Tool Call Example**

AI assistant will call the `mcp-feedback-enhanced` tool like this:

```xml
<use_mcp_tool>
  <server_name>mcp-feedback-enhanced</server_name>
  <tool_name>interactive_feedback</tool_name>
  <arguments>
    {
      "project_directory": "/path/to/your/project",
      "summary": "I have implemented your requested changes and refactored the main module. Please review the results and provide feedback."
    }
  </arguments>
</use_mcp_tool>
```

## 🔄 Workflow

1. **AI Assistant Call** - AI calls `mcp-feedback-enhanced` after completing tasks
2. **Environment Detection** - System automatically detects runtime environment
3. **Interface Launch** - Launches Qt GUI or Web UI based on environment
4. **User Interaction** - Users can:
   - Execute commands and view output
   - Provide text feedback (supports Ctrl+Enter quick submission, compatible with main keyboard and numpad)
   - Upload images (drag & drop, clipboard paste Ctrl+V)
   - Use multi-language interface switching
5. **Feedback Delivery** - User feedback (including images) is sent back to AI assistant
6. **Process Continuation** - AI continues or ends task based on feedback

## 🆕 Version Updates

### v2.0.14 - Enhanced Keyboard Shortcuts (Latest)
- ⌨️ **Numpad Support**: Ctrl+Enter shortcut now supports both main keyboard and numpad Enter keys
- 🖼️ **Smart Image Pasting**: Ctrl+V can directly paste clipboard images in feedback dialog without additional upload steps
- 🎮 **Dual Shortcut Mechanism**: GUI uses dual QShortcut setup ensuring full compatibility
- 🌐 **Web UI Shortcut Enhancement**: Uses key/code dual detection mechanism supporting all Enter key variants
- 💡 **User Experience Improvements**: Updated trilingual hint texts clearly indicating numpad support and image pasting functionality
- 🔧 **API Simplification**: Removed `force_web_ui` parameter, simplified API design with only environment variable control
- 📝 **Documentation Updates**: Updated all related documentation, removed redundant examples

### v2.0.9 - Multi-language Architecture Enhancement
- 🌏 **Complete Multi-language Architecture Restructuring**: Migrated from embedded translations to structured JSON-based system
- 📁 **Organized Language Files**: Separated language files into `src/mcp_feedback_enhanced/locales/` directory structure
- 🔧 **Enhanced Internationalization**: Dynamic loading with nested key structure and browser language detection
- 📚 **Comprehensive Documentation**: Added detailed README for translation contributors with examples and guidelines
- 🔄 **Backward Compatibility**: Maintained full compatibility with existing code while enabling modern features
- 🖼️ **Interface Screenshots Update**: Added comprehensive screenshots showcasing both English and Traditional Chinese interfaces
- 📝 **Documentation Enhancement**: Updated README files with multi-language screenshots and feature descriptions
- 🛡️ **Enhanced Error Handling**: Improved stability and error recovery mechanisms
- 🚀 **Performance Optimizations**: Faster startup times and improved resource management
- 🔧 **Bug Fixes**: Various minor fixes and improvements
- 📦 **Package Optimization**: Better dependency management and build process
- 🎨 **Visual Improvements**: Enhanced button visibility and color consistency
- 🖱️ **Interaction Fixes**: Improved drag-and-drop indicators and empty state hints
- 📱 **Responsive Design**: Better layout adaptation for different screen sizes
- 🌐 **Language Switching**: Fixed Qt GUI language switching with proper checkmarks

### v2.0.3 - Encoding and Communication Fix
- 🛡️ **Complete Chinese Character Encoding Fix**: Perfect Chinese character display support
- 🔧 **JSON Parsing Error Resolution**: Fixed MCP client "Unexpected token" errors
- 🎛️ **Controllable Debug Mode**: Debug output control via `MCP_DEBUG` environment variable
- 🖼️ **Enhanced Image Support**: Improved image processing and Base64 encoding
- 🚀 **Output Isolation**: Strict separation of debug output from MCP communication
- 📦 **Package Optimization**: Improved uvx installation experience and dependency management

### v2.0.0 - Web UI and Remote Support
- ✅ **Web UI Interface**: Added Web UI support for SSH remote development environments
- ✅ **Automatic Environment Detection**: Smart interface selection based on environment
- ✅ **WebSocket Real-time Communication**: Live command execution and feedback
- ✅ **Modern Dark Theme**: Beautiful dark theme with responsive design
- ✅ **Persistent Testing Mode**: Enhanced testing capabilities

### v1.0.0 - Foundation (Original Author)
- ✅ **Qt GUI Interface**: Native desktop interface
- ✅ **Command Execution**: Real-time command execution and output
- ✅ **MCP Protocol Support**: Full Model Context Protocol implementation
- ✅ **Cross-platform Support**: Windows, macOS, and Linux compatibility

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

### Debug Mode

For detailed debug information, please enable debug mode:
```bash
# Set debug environment variable
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

## 🙏 Acknowledgments & Contact

### Original Author
**Fábio Ferreira** - [X @fabiomlferreira](https://x.com/fabiomlferreira)  
**Original Project:** [noopstudios/interactive-feedback-mcp](https://github.com/noopstudios/interactive-feedback-mcp)  

If you find Interactive Feedback MCP useful, the best ways to show support are:
- 🌟 **Star the original project**: [Click here to star the original repo](https://github.com/noopstudios/interactive-feedback-mcp) ⭐
- 📱 **Follow the original author**: [@fabiomlferreira](https://x.com/fabiomlferreira) on X

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
- [Model Context Protocol](https://modelcontextprotocol.io/) - Official MCP documentation

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

**🌟 Welcome to Star this project and share it with more developers!**