# Changelog (English)

This file documents all version updates for **MCP Feedback Enhanced**.

---

## [v2.2.4] - GUI Experience Optimization & Bug Fixes (2025-01-XX)

### 🐛 Bug Fixes
- 🖼️ **Image Duplicate Paste Fix**: Fixed the issue where Ctrl+V image pasting in GUI would create duplicate images
- 🌐 **Localization Switch Fix**: Fixed image settings area text not translating correctly when switching languages
- 📝 **Font Readability Improvement**: Adjusted font sizes in image settings area for better readability

---

## [v2.2.3] - Timeout Control & Image Settings Enhancement (2025-01-XX)

### ✨ New Features
- ⏰ **User Timeout Control**: Added customizable timeout settings with flexible range from 30 seconds to 2 hours
- ⏱️ **Countdown Timer**: Real-time countdown timer displayed at the top of the interface for visual time reminders
- 🖼️ **Image Size Limit**: Added image upload size limit settings (Unlimited/1MB/3MB/5MB)
- 🔧 **Base64 Compatibility Mode**: Added Base64 verbose mode to improve image recognition compatibility with some AI models
- 🧹 **UV Cache Management Tool**: Added `cleanup_cache.py` script for managing and cleaning UV cache space

### 🚀 Improvements
- 📚 **Documentation Structure Optimization**: Reorganized documentation directory structure, moved images to `docs/{language}/images/` path
- 📖 **Cache Management Guide**: Added detailed UV Cache management guide with automated cleanup solutions
- 🎯 **Smart Compatibility Hints**: Automatically show Base64 compatibility mode suggestions when image upload fails

### 🐛 Bug Fixes
- 🛡️ **Timeout Handling Optimization**: Improved coordination between user-defined timeout and MCP system timeout
- 🖥️ **Interface Auto-close**: Fixed timeout-triggered interface auto-close and resource cleanup logic
- 📱 **Responsive Layout**: Optimized timeout control components display on small screen devices

---

## [v2.2.2] - Timeout Auto-cleanup Fix (2024-12-XX)

### 🐛 Bug Fixes
- 🔄 **Timeout Auto-cleanup**: Fixed GUI/Web UI not auto-closing after MCP session timeout (default 600 seconds)
- 🛡️ **Resource Management Optimization**: Improved timeout handling to ensure proper cleanup and closure of all UI resources
- ⚡ **Timeout Detection Enhancement**: Strengthened timeout detection logic to handle timeout events correctly in all scenarios

---

## [v2.2.1] - Window Optimization & Unified Settings Interface (2024-12-XX)

### 🚀 Improvements
- 🖥️ **Window Size Limit Removal**: Removed GUI main window minimum size limit, reduced from 1000×800 to 400×300
- 💾 **Real-time Window State Saving**: Implemented instant window size and position saving with debounce delay
- ⚙️ **Unified Settings Interface Optimization**: Improved GUI settings panel configuration saving logic to avoid conflicts

### 🐛 Bug Fixes
- 🔧 **Window Size Limitation**: Fixed GUI window unable to resize to small dimensions issue
- 🛡️ **Settings Conflict**: Fixed configuration conflicts that could occur during settings save

---

## [v2.2.0] - Layout & Settings Interface Optimization (2024-12-XX)

### ✨ New Features
- 🎨 **Horizontal Layout Mode**: Added summary and feedback left-right layout option for GUI and Web UI merged mode

### 🚀 Improvements
- 🎨 **Settings Interface Improvement**: Optimized GUI and Web UI settings pages for better layout clarity
- ⌨️ **Hotkey Enhancement**: Submit feedback hotkey now fully supports numpad Enter key

### 🐛 Bug Fixes
- 🔧 **Image Duplicate Paste**: Fixed duplicate image pasting issue when using Ctrl+V in Web UI text input area

---

## [v2.1.1] - Window Positioning Optimization (2024-11-XX)

### ✨ New Features
- 🖥️ **Smart Window Positioning**: Added "Always center window on main screen" setting option
- 🌐 **Multi-screen Support**: Perfect solution for complex multi-screen environments like T-shaped screen arrangements
- 💾 **Position Memory**: Automatic window position saving and restoration with intelligent visibility detection

---

## [v2.1.0] - Complete Refactoring Version (2024-11-XX)

### 🎨 Major Refactoring
- 🏗️ **Complete Refactoring**: GUI and Web UI adopted modular architecture
- 📁 **Centralized Management**: Reorganized folder structure for improved maintainability
- 🖥️ **Interface Optimization**: Modern design and improved user experience

### ✨ New Features
- 🍎 **macOS Interface Optimization**: Specialized improvements for macOS user experience
- ⚙️ **Feature Enhancement**: Added setting options and auto-close page functionality
- ℹ️ **About Page**: Added about page with version info, project links, and acknowledgments

---

## [v2.0.14] - Hotkey & Image Feature Enhancement (2024-10-XX)

### 🚀 Improvements
- ⌨️ **Enhanced Hotkeys**: Ctrl+Enter supports numpad
- 🖼️ **Smart Image Paste**: Ctrl+V directly pastes clipboard images

---

## [v2.0.9] - Multi-language Architecture Refactoring (2024-10-XX)

### 🔄 Refactoring
- 🌏 **Multi-language Architecture Refactoring**: Support for dynamic loading
- 📁 **Language File Modularization**: Modular organization of language files

---

## [v2.0.3] - Encoding Issues Fix (2024-10-XX)

### 🐛 Critical Fixes
- 🛡️ **Complete Chinese Character Encoding Fix**: Resolved all Chinese display related issues
- 🔧 **JSON Parsing Error Fix**: Fixed data parsing errors

---

## [v2.0.0] - Web UI Support (2024-09-XX)

### 🌟 Major Features
- ✅ **Added Web UI Support**: Support for remote environment usage
- ✅ **Automatic Environment Detection**: Automatically choose appropriate interface
- ✅ **WebSocket Real-time Communication**: Implemented real-time bidirectional communication 