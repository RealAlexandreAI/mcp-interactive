# Changelog (English)

This document records all version updates for **MCP Feedback Enhanced**.

## [v2.2.5] - WSL Environment Support & Cross-Platform Enhancement
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

---

### ✨ New Features
- 🐧 **WSL Environment Detection**: Automatically identifies WSL environments and provides specialized support logic
- 🌐 **Smart Browser Launching**: Automatically invokes Windows browser in WSL environments with multiple launch methods
- 🔧 **Cross-Platform Testing Enhancement**: Test functionality integrates WSL detection for improved test coverage

### 🚀 Improvements
- 🎯 **Environment Detection Optimization**: Improved remote environment detection logic, WSL no longer misidentified as remote environment
- 📊 **System Information Enhancement**: System information tool now displays WSL environment status
- 🧪 **Testing Experience Improvement**: Test mode automatically attempts browser launching for better testing experience

---

## [v2.2.4] - GUI Experience Optimization & Bug Fixes

### 🐛 Bug Fixes
- 🖼️ **Image Duplicate Paste Fix**: Fixed the issue where Ctrl+V image pasting in GUI would create duplicate images
- 🌐 **Localization Switch Fix**: Fixed image settings area text not translating correctly when switching languages
- 📝 **Font Readability Improvement**: Adjusted font sizes in image settings area for better readability

---

## [v2.2.3] - Timeout Control & Image Settings Enhancement

### ✨ New Features
- ⏰ **User Timeout Control**: Added customizable timeout settings with flexible range from 30 seconds to 2 hours
- ⏱️ **Countdown Timer**: Real-time countdown timer display at the top of the interface for visual time reminders
- 🖼️ **Image Size Limits**: Added image upload size limit settings (unlimited/1MB/3MB/5MB)
- 🔧 **Base64 Compatibility Mode**: Added Base64 detail mode to improve image recognition compatibility with AI models
- 🧹 **UV Cache Management Tool**: Added `cleanup_cache.py` script to help manage and clean UV cache space

### 🚀 Improvements
- 📚 **Documentation Structure Optimization**: Reorganized documentation directory structure, moved images to `docs/{language}/images/` paths
- 📖 **Cache Management Guide**: Added detailed UV Cache management guide with automated cleanup solutions
- 🎯 **Smart Compatibility Hints**: Automatically display Base64 compatibility mode suggestions when image upload fails

### 🐛 Bug Fixes
- 🛡️ **Timeout Handling Optimization**: Improved coordination between user-defined timeout and MCP system timeout
- 🖥️ **Interface Auto-close**: Fixed interface auto-close and resource cleanup logic after timeout
- 📱 **Responsive Layout**: Optimized timeout control component display on small screen devices

---

## [v2.2.2] - Timeout Auto-cleanup Fix

### 🐛 Bug Fixes
- 🔄 **Timeout Auto-cleanup**: Fixed GUI/Web UI not automatically closing after MCP session timeout (default 600 seconds)
- 🛡️ **Resource Management Optimization**: Improved timeout handling mechanism to ensure proper cleanup and closure of all UI resources on timeout
- ⚡ **Enhanced Timeout Detection**: Strengthened timeout detection logic to correctly handle timeout events in various scenarios

---

## [v2.2.1] - Window Optimization & Unified Settings Interface

### 🚀 Improvements
- 🖥️ **Window Size Constraint Removal**: Removed GUI main window minimum size limit from 1000×800 to 400×300
- 💾 **Real-time Window State Saving**: Implemented real-time saving mechanism for window size and position changes
- ⚙️ **Unified Settings Interface Optimization**: Improved GUI settings page configuration saving logic to avoid setting conflicts

### 🐛 Bug Fixes
- 🔧 **Window Size Constraint**: Fixed GUI window unable to resize to small dimensions issue
- 🛡️ **Setting Conflicts**: Fixed potential configuration conflicts during settings save operations

---

## [v2.2.0] - Layout & Settings UI Enhancements

### ✨ New Features
- 🎨 **Horizontal Layout Mode**: GUI & Web UI combined mode adds left-right layout option for summary and feedback

### 🚀 Improvements
- 🎨 **Improved Settings Interface**: Optimized the settings page for both GUI and Web UI
- ⌨️ **GUI Shortcut Enhancement**: Submit feedback shortcut now fully supports numeric keypad Enter key

### 🐛 Bug Fixes
- 🔧 **Image Duplication Fix**: Resolved Web UI image pasting duplication issue

---

## [v2.1.1] - Window Positioning Optimization

### ✨ New Features
- 🖥️ **Smart Window Positioning**: Added "Always show window at primary screen center" setting option
- 🌐 **Multi-Monitor Support**: Perfect solution for complex multi-monitor setups like T-shaped screen arrangements
- 💾 **Position Memory**: Auto-save and restore window position with intelligent visibility detection

---

## [v2.1.0] - Complete Refactored Version

### 🎨 Major Refactoring
- 🏗️ **Complete Refactoring**: GUI and Web UI adopt modular architecture
- 📁 **Centralized Management**: Reorganized folder structure, improved maintainability
- 🖥️ **Interface Optimization**: Modern design and improved user experience

### ✨ New Features
- 🍎 **macOS Interface Optimization**: Specialized improvements for macOS user experience
- ⚙️ **Feature Enhancement**: New settings options and auto-close page functionality
- ℹ️ **About Page**: Added about page with version info, project links, and acknowledgments

---

## [v2.0.14] - Shortcut & Image Feature Enhancement

### 🚀 Improvements
- ⌨️ **Enhanced Shortcuts**: Ctrl+Enter supports numeric keypad
- 🖼️ **Smart Image Pasting**: Ctrl+V directly pastes clipboard images

---

## [v2.0.9] - Multi-language Architecture Refactor

### 🔄 Refactoring
- 🌏 **Multi-language Architecture Refactor**: Support for dynamic loading
- 📁 **Modularized Language Files**: Modular organization of language files

---

## [v2.0.3] - Encoding Issues Fix

### 🐛 Critical Fixes
- 🛡️ **Complete Chinese Character Encoding Fix**: Resolved all Chinese display related issues
- 🔧 **JSON Parsing Error Fix**: Fixed data parsing errors

---

## [v2.0.0] - Web UI Support

### 🌟 Major Features
- ✅ **Added Web UI Support**: Support for remote environments
- ✅ **Auto Environment Detection**: Automatically choose appropriate interface
- ✅ **WebSocket Real-time Communication**: Real-time bidirectional communication

---

## Legend

| Icon | Meaning |
|------|---------|
| 🌟 | Version Highlights |
| ✨ | New Features |
| 🚀 | Improvements |
| 🐛 | Bug Fixes |
| 🔄 | Refactoring Changes |
| 🎨 | UI Optimization |
| ⚙️ | Settings Related |
| 🖥️ | Window Related |
| 🌐 | Multi-language/Network Related |
| 📁 | File Structure |
| ⌨️ | Shortcuts |
| 🖼️ | Image Features |

---

**Full Project Info:** [GitHub - mcp-feedback-enhanced](https://github.com/Minidoracat/mcp-feedback-enhanced) 