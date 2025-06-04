# Release v2.2.3 - Timeout Control & Image Settings Enhancement

## 🌟 Highlights
This version introduces user-controllable timeout settings and flexible image upload configuration options, while improving UV Cache management tools to enhance the overall user experience.

## ✨ New Features
- ⏰ **User Timeout Control**: Added customizable timeout settings with flexible range from 30 seconds to 2 hours
- ⏱️ **Countdown Timer**: Real-time countdown timer display at the top of the interface for visual time reminders
- 🖼️ **Image Size Limits**: Added image upload size limit settings (unlimited/1MB/3MB/5MB)
- 🔧 **Base64 Compatibility Mode**: Added Base64 detail mode to improve image recognition compatibility with AI models 
- 🧹 **UV Cache Management Tool**: Added `cleanup_cache.py` script to help manage and clean UV cache space

## 🚀 Improvements
- 📚 **Documentation Structure Optimization**: Reorganized documentation directory structure, moved images to `docs/{language}/images/` paths
- 📖 **Cache Management Guide**: Added detailed UV Cache management guide with automated cleanup solutions
- 🎯 **Smart Compatibility Hints**: Automatically display Base64 compatibility mode suggestions when image upload fails
- 🔄 **Settings Sync Mechanism**: Improved image settings synchronization between different interface modes

## 🐛 Bug Fixes
- 🛡️ **Timeout Handling Optimization**: Improved coordination between user-defined timeout and MCP system timeout
- 🖥️ **Interface Auto-close**: Fixed interface auto-close and resource cleanup logic after timeout
- 📱 **Responsive Layout**: Optimized timeout control component display on small screen devices

## 🔧 Technical Improvements
- 🎛️ **Timeout Control Architecture**: Implemented separated design for frontend countdown timer and backend timeout handling
- 📊 **Image Processing Optimization**: Improved image upload size checking and format validation mechanisms
- 🗂️ **Settings Persistence**: Enhanced settings saving mechanism to ensure correct saving and loading of user preferences
- 🧰 **Tool Script Enhancement**: Added cross-platform cache cleanup tool with support for force cleanup and preview modes

## 📦 Installation & Update
```bash
# Quick test latest version
uvx mcp-feedback-enhanced@latest test --gui

# Update to specific version
uvx mcp-feedback-enhanced@v2.2.3 test
```

## 🔗 Related Links
- Full Documentation: [README.md](../../README.md)
- Issue Reporting: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)
- Related PRs: #22 (Timeout Control Feature), #19 (Image Settings Feature)
