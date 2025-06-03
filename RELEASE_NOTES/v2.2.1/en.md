# Release v2.2.1 - Window Optimization & Unified Settings Interface

## 🌟 Highlights
This release primarily addresses GUI window size constraints, implements smart window state saving mechanisms, and optimizes the unified settings interface.

## 🚀 Improvements
- 🖥️ **Window Size Constraint Removal**: Removed GUI main window minimum size limit from 1000×800 to 400×300, allowing users to freely adjust window size for different use cases
- 💾 **Real-time Window State Saving**: Implemented real-time saving mechanism for window size and position changes, with debounce delay to avoid excessive I/O operations
- ⚙️ **Unified Settings Interface Optimization**: Improved GUI settings page configuration saving logic to avoid setting conflicts, ensuring correct window positioning and size settings
- 🎯 **Smart Window Size Saving**: In "Always center display" mode, correctly saves window size (but not position); in "Smart positioning" mode, saves complete window state

## 🐛 Bug Fixes
- 🔧 **Window Size Constraint**: Fixed GUI window unable to resize to small dimensions issue (fixes #10 part one)
- 🛡️ **Setting Conflicts**: Fixed potential configuration conflicts during settings save operations

## 📦 Installation & Update
```bash
# Quick test latest version
uvx mcp-feedback-enhanced@latest test --gui

# Update to specific version
uvx mcp-feedback-enhanced@v2.2.1 test
```

## 🔗 Related Links
- Full Documentation: [README.md](../../README.md)
- Issue Reporting: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)
- Issues Addressed: #10 (partially completed) 