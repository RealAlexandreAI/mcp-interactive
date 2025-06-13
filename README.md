# MCP Feedback Enhanced

**🌐 Language / 語言切換:** **English** | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

**Original Author:** [Fábio Ferreira](https://x.com/fabiomlferreira) | [Original Project](https://github.com/noopstudios/interactive-feedback-mcp) ⭐
**Enhanced Fork:** [Minidoracat](https://github.com/Minidoracat)
**UI Design Reference:** [sanshao85/mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

## 🎯 Core Concept

This is an [MCP server](https://modelcontextprotocol.io/) that establishes **feedback-oriented development workflows**, adopting a **pure Web UI architecture**, perfectly adapting to local, **SSH Remote environments** (Cursor SSH Remote, VS Code Remote SSH), and **WSL (Windows Subsystem for Linux) environments**. By guiding AI to confirm with users rather than making speculative operations, it can consolidate multiple tool calls into a single feedback-oriented request, dramatically reducing platform costs and improving development efficiency.

**🌐 Web-Only Architecture Advantages:**
- 🚀 **Simplified Deployment**: No GUI dependencies, lighter installation
- 🌍 **Cross-Platform Compatibility**: Supports all operating systems and environments
- 🔧 **Easy Maintenance**: Unified Web interface, reduced complexity
- 📦 **Compact Size**: Removed heavy GUI libraries, significantly smaller installation package

**Supported Platforms:** [Cursor](https://www.cursor.com) | [Cline](https://cline.bot) | [Windsurf](https://windsurf.com) | [Augment](https://www.augmentcode.com) | [Trae](https://www.trae.ai)

### 🔄 Workflow
1. **AI Call** → `mcp-feedback-enhanced` tool
2. **Web UI Launch** → Auto-open browser interface (pure Web architecture)
3. **Smart Interaction** → Prompt selection, text input, image upload, auto-submit
4. **Real-time Feedback** → WebSocket connection delivers information to AI instantly
5. **Session Tracking** → Auto-record session history and statistics
6. **Process Continuation** → AI adjusts behavior or ends task based on feedback

## 🌟 Key Features

### 🌐 Pure Web UI Architecture System
- **Web-Only Design**: Completely removed desktop GUI dependencies, adopting pure Web interface
- **Universal Compatibility**: Supports local, SSH Remote, and WSL environments
- **Auto Adaptation**: Intelligent environment detection and optimal configuration
- **Lightweight Deployment**: No complex GUI environment configuration required

### 📝 Smart Prompt Management System (v2.4.0 New Feature)
- **CRUD Operations**: Create, edit, delete, and use common prompts
- **Usage Statistics**: Track usage frequency with intelligent sorting
- **Quick Application**: One-click selection and application of prompts
- **Auto-Submit Integration**: Support auto-submit marking and priority display

### ⏰ Auto-Timed Submit Feature (v2.4.0 New Feature)
- **Flexible Timing**: Configurable countdown timer from 1-86400 seconds
- **Visual Display**: Real-time countdown display and status indicators
- **Deep Integration**: Seamless integration with prompt management system
- **Complete Control**: Support pause, resume, and cancel operations

### 📊 Session Management & Tracking (v2.4.0 New Feature)
- **Real-time Status**: Current session status display in real-time
- **History Records**: Complete session history and statistical analysis
- **Data Statistics**: Today's session count and average duration statistics
- **Detail Management**: Session detail viewing and management functions

### 🔗 Connection Monitoring System (v2.4.0 New Feature)
- **Real-time Monitoring**: WebSocket connection status monitoring in real-time
- **Quality Indicators**: Latency measurement and connection quality indicators
- **Auto Reconnection**: Smart reconnection mechanism and error handling
- **Detailed Statistics**: Complete connection statistical information

### 🎨 Modern Interface Design
- **Modular Architecture**: JavaScript completely modularized refactoring
- **Responsive Design**: Adapts to different screen sizes and window dimensions
- **Unified Style**: Consistent design language and visual experience
- **Session Panel**: New left session management panel with collapse/expand support

### 🖼️ Image Support
- **Format Support**: PNG, JPG, JPEG, GIF, BMP, WebP
- **Upload Methods**: Drag & drop files + clipboard paste (Ctrl+V)
- **Unlimited Upload**: Support image files of any size with automatic smart processing

### 🌏 Multi-language
- **Three Languages**: English, Traditional Chinese, Simplified Chinese
- **Smart Detection**: Auto-select based on system language
- **Live Switching**: Change language directly within interface

### ✨ WSL Environment Support (v2.2.5)
- **Auto Detection**: Intelligently identifies WSL (Windows Subsystem for Linux) environments
- **Browser Integration**: Automatically launches Windows browser in WSL environments
- **Multiple Launch Methods**: Supports `cmd.exe`, `powershell.exe`, `wslview` and other browser launch methods
- **Seamless Experience**: WSL users can directly use Web UI without additional configuration

### 🌐 SSH Remote Environment Support (v2.3.0 New Feature)
- **Smart Detection**: Automatically identifies SSH Remote environments (Cursor SSH Remote, VS Code Remote SSH, etc.)
- **Browser Launch Guidance**: Provides clear solutions when browser cannot launch automatically
- **Port Forwarding Support**: Complete port forwarding setup guidance and troubleshooting
- **MCP Integration Optimization**: Improved integration with MCP system for more stable connection experience
- **Detailed Documentation**: [SSH Remote Environment Usage Guide](docs/en/ssh-remote/browser-launch-issues.md)
- 🎯 **Auto-focus Input Box**: Automatically focus on feedback input box when window opens, improving user experience (Thanks @penn201500)

## 🌐 Interface Preview

### Web UI Interface (v2.4.0 - Web-Only Architecture)

<div align="center">
  <img src="docs/en/images/web1.jpeg" width="400" alt="Web UI Main Interface - Prompt Management & Auto-Submit" />
</div>

<details>
<summary>📱 Click to view complete interface screenshots</summary>

<div align="center">
  <img src="docs/en/images/web2.jpeg" width="800" alt="Web UI Complete Interface - Session Management & Settings" />
</div>

</details>

*Web UI Interface - Pure Web architecture, supporting prompt management, auto-submit, session tracking and other smart features*

**Keyboard Shortcuts**
- `Ctrl+Enter` (Windows/Linux) / `Cmd+Enter` (macOS): Submit feedback (supports both main keyboard and numpad)
- `Ctrl+V` (Windows/Linux) / `Cmd+V` (macOS): Directly paste clipboard images
- `Ctrl+I` (Windows/Linux) / `Cmd+I` (macOS): Quick focus input box (Thanks @penn201500)

## 🚀 Quick Start

### 1. Installation & Testing
```bash
# Install uv (if not already installed)
pip install uv

# Quick test
uvx mcp-feedback-enhanced@latest test
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
        "MCP_DEBUG": "false",
        "MCP_WEB_PORT": "8765"
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
5. Before completing the task, use the MCP mcp-feedback-enhanced to ask the user for feedback.
```

## ⚙️ Advanced Settings

### Environment Variables
| Variable | Purpose | Values | Default |
|----------|---------|--------|---------|
| `MCP_DEBUG` | Debug mode | `true`/`false` | `false` |
| `MCP_WEB_PORT` | Web UI port | `1024-65535` | `8765` |

### Testing Options
```bash
# Version check
uvx mcp-feedback-enhanced@latest version       # Check version

# Interface testing
uvx mcp-feedback-enhanced@latest test --web    # Test Web UI (auto continuous running)
uvx mcp-feedback-enhanced@latest test --enhanced # Enhanced test suite

# Debug mode
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

### Developer Installation
```bash
git clone https://github.com/Minidoracat/mcp-feedback-enhanced.git
cd mcp-feedback-enhanced
uv sync
```

**Local Testing Methods**
```bash
# Functional Testing
uv run python -m mcp_feedback_enhanced test              # Standard functional testing
uvx --with-editable . mcp-feedback-enhanced test --web   # Web UI testing (continuous running)

# Unit Testing
make test                                                # Run all unit tests
make test-fast                                          # Fast testing (skip slow tests)
make test-cov                                           # Testing with coverage report

# Code Quality Checks
make check                                              # Complete code quality checks
make quick-check                                        # Quick check with auto-fix
```

**Testing Descriptions**
- **Functional Testing**: Test complete MCP tool functionality workflow
- **Unit Testing**: Test individual module functionality
- **Coverage Testing**: Generate HTML coverage report to `htmlcov/` directory
- **Quality Checks**: Include linting, formatting, type checking

## 🆕 Version History

📋 **Complete Version History:** [RELEASE_NOTES/CHANGELOG.en.md](RELEASE_NOTES/CHANGELOG.en.md)

### Latest Version Highlights (v2.4.0)
- 🏗️ **Web-Only Architecture Refactoring**: Completely removed PyQt6 GUI dependencies, transitioned to pure Web UI architecture, dramatically simplifying deployment
- 📝 **Smart Prompt Management**: Added complete prompt CRUD system with usage statistics and intelligent sorting
- ⏰ **Auto-Timed Submit**: Configurable countdown timer with deep integration with prompt management system
- 📊 **Session Management System**: Real-time session status, history records, and statistical analysis features
- 🔗 **Enhanced Connection Monitoring**: WebSocket connection status monitoring, latency measurement, and auto-reconnection
- 🎨 **Comprehensive UI/UX Optimization**: New session panel, responsive design, unified visual style
- 🌐 **Enhanced Multi-language System**: Optimized language switching mechanism, improved localization coverage
- 🛠️ **Technical Architecture Upgrade**: JavaScript modular refactoring, adopting modern development patterns

## 🐛 Common Issues

### 🌐 SSH Remote Environment Issues
**Q: Browser cannot launch in SSH Remote environment**
A: This is normal behavior. SSH Remote environments have no graphical interface, requiring manual opening in local browser. For detailed solutions, see: [SSH Remote Environment Usage Guide](docs/en/ssh-remote/browser-launch-issues.md)

**Q: Why am I not receiving new MCP feedback?**
A: There might be a WebSocket connection issue. **Solution**: Simply refresh the browser page.

**Q: Why isn't MCP being called?**
A: Please confirm the MCP tool status shows green light. **Solution**: Toggle the MCP tool on/off repeatedly, wait a few seconds for system reconnection.

**Q: Augment cannot start MCP**
A: **Solution**: Completely close and restart VS Code or Cursor, then reopen the project.

### 🔧 General Issues
**Q: How to use the legacy GUI interface?**
A: v2.4.0 has completely removed PyQt6 GUI dependencies and transitioned to a pure Web UI architecture. To use the legacy GUI, please specify v2.3.0 or earlier versions:
```bash
# Use v2.3.0 (last version supporting GUI)
uvx mcp-feedback-enhanced@2.3.0

# Or specify version in MCP configuration
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@2.3.0"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```
**Note**: Legacy versions do not include v2.4.0 new features (prompt management, auto-submit, session management, etc.).

**Q: Getting "Unexpected token 'D'" error**
A: Debug output interference. Set `MCP_DEBUG=false` or remove the environment variable.

**Q: Chinese character garbled text**
A: Fixed in v2.0.3. Update to latest version: `uvx mcp-feedback-enhanced@latest`

**Q: Multi-screen window disappearing or positioning errors**
A: Fixed in v2.1.1. Go to "⚙️ Settings" tab, check "Always show window at primary screen center" to resolve. Especially useful for T-shaped screen arrangements and other complex multi-monitor configurations.

**Q: Image upload fails**
A: Check file format (PNG/JPG/JPEG/GIF/BMP/WebP). System supports image files of any size.

**Q: Web UI won't start**
A: Check firewall settings or try using a different port.

**Q: UV Cache taking up too much disk space**
A: Due to frequent use of `uvx` commands, cache may accumulate to tens of GB. Regular cleanup is recommended:
```bash
# Check cache size and detailed information
python scripts/cleanup_cache.py --size

# Preview cleanup content (without actually cleaning)
python scripts/cleanup_cache.py --dry-run

# Execute standard cleanup
python scripts/cleanup_cache.py --clean

# Force cleanup (attempts to close related processes, solves Windows file lock issues)
python scripts/cleanup_cache.py --force

# Or use uv command directly
uv cache clean
```
For detailed instructions, see: [Cache Management Guide](docs/en/cache-management.md)

**Q: AI models cannot parse images**
A: Various AI models (including Gemini Pro 2.5, Claude, etc.) may have instability in image parsing, sometimes correctly identifying and sometimes unable to parse uploaded image content. This is a known limitation of AI visual understanding technology. Recommendations:
1. Ensure good image quality (high contrast, clear text)
2. Try uploading multiple times, retries usually succeed
3. If parsing continues to fail, try adjusting image size or format

## 🙏 Acknowledgments

### 🌟 Support Original Author
**Fábio Ferreira** - [X @fabiomlferreira](https://x.com/fabiomlferreira)
**Original Project:** [noopstudios/interactive-feedback-mcp](https://github.com/noopstudios/interactive-feedback-mcp)

If you find this useful, please:
- ⭐ [Star the original project](https://github.com/noopstudios/interactive-feedback-mcp)
- 📱 [Follow the original author](https://x.com/fabiomlferreira)

### Design Inspiration
**sanshao85** - [mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

### Contributors
**penn201500** - [GitHub @penn201500](https://github.com/penn201500)
- 🎯 Auto-focus input box feature ([PR #39](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/39))

### Community Support
- **Discord:** [https://discord.gg/Gur2V67](https://discord.gg/Gur2V67)
- **Issues:** [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---
**🌟 Welcome to Star and share with more developers!**
