# Release v2.2.5 - WSL Environment Support & Cross-Platform Enhancement

## 🌟 Highlights
This version introduces comprehensive support for WSL (Windows Subsystem for Linux) environments, enabling WSL users to seamlessly use this tool with automatic Windows browser launching, significantly improving cross-platform development experience.

## ✨ New Features
- 🐧 **WSL Environment Detection**: Automatically identifies WSL environments and provides specialized support logic
- 🌐 **Smart Browser Launching**: Automatically invokes Windows browser in WSL environments with multiple launch methods
- 🔧 **Cross-Platform Testing Enhancement**: Test functionality integrates WSL detection for improved test coverage

## 🚀 Improvements
- 🎯 **Environment Detection Optimization**: Improved remote environment detection logic, WSL no longer misidentified as remote environment
- 📊 **System Information Enhancement**: System information tool now displays WSL environment status
- 🧪 **Testing Experience Improvement**: Test mode automatically attempts browser launching for better testing experience

## 📦 Installation & Update
```bash
# Quick test latest version
uvx mcp-feedback-enhanced@latest test --gui

# Update to specific version
uvx mcp-feedback-enhanced@v2.2.5 test
```

## 🔗 Related Links
- Full Documentation: [README.md](../../README.md)
- Issue Reports: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)
- Project Homepage: [GitHub Repository](https://github.com/Minidoracat/mcp-feedback-enhanced)
