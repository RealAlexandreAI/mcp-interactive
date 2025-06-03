# Release v2.2.2 - Timeout Auto-cleanup Fix

## 🌟 Highlights
This version fixes a critical resource management issue where GUI/Web UI interfaces were not properly closed when MCP sessions ended due to timeout, causing the interfaces to remain open and unresponsive.

## 🐛 Bug Fixes
- 🔄 **Timeout Auto-cleanup**: Fixed GUI/Web UI not automatically closing after MCP session timeout (default 600 seconds)
- 🛡️ **Resource Management Optimization**: Improved timeout handling mechanism to ensure proper cleanup and closure of all UI resources on timeout
- ⚡ **Enhanced Timeout Detection**: Strengthened timeout detection logic to correctly handle timeout events in various scenarios
- 🔧 **Interface Response Improvement**: Enhanced Web UI frontend handling of session timeout events

## 🚀 Technical Improvements
- 📦 **Web Session Management**: Refactored WebFeedbackSession timeout handling logic
- 🎯 **QTimer Integration**: Introduced precise QTimer timeout control mechanism in GUI
- 🌐 **Frontend Communication Optimization**: Improved timeout message communication between Web UI frontend and backend
- 🧹 **Resource Cleanup Mechanism**: Added _cleanup_resources_on_timeout method to ensure thorough cleanup

## 📦 Installation & Update
```bash
# Quick test latest version
uvx mcp-feedback-enhanced@latest test --gui

# Update to specific version
uvx mcp-feedback-enhanced@v2.2.2 test
```

## 🔗 Related Links
- Full Documentation: [README.md](../../README.md)
- Issue Reporting: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)
- Fixed Issue: #5 (GUI/Web UI timeout cleanup) 