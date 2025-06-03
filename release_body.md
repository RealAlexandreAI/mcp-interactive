## 🌐 Multi-Language Release Notes

### 🇺🇸 English
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
---

### 🇹🇼 繁體中文
# Release v2.2.2 - 超時自動清理修復

## 🌟 亮點
本版本修復了一個重要的資源管理問題：當 MCP session 因超時結束時，GUI/Web UI 介面沒有正確關閉，導致介面持續顯示而無法正常關閉。

## 🐛 問題修復
- 🔄 **超時自動清理**: 修復 GUI/Web UI 在 MCP session timeout (預設 600 秒) 後沒有自動關閉的問題
- 🛡️ **資源管理優化**: 改進超時處理機制，確保在超時時正確清理和關閉所有 UI 資源
- ⚡ **超時檢測增強**: 加強超時檢測邏輯，確保在各種情況下都能正確處理超時事件
- 🔧 **介面回應改進**: 改善 Web UI 前端對 session timeout 事件的處理回應

## 🚀 技術改進
- 📦 **Web Session 管理**: 重構 WebFeedbackSession 的超時處理邏輯
- 🎯 **QTimer 整合**: 在 GUI 中引入精確的 QTimer 超時控制機制
- 🌐 **前端通訊優化**: 改進 Web UI 前端與後端的超時訊息傳遞
- 🧹 **資源清理機制**: 新增 _cleanup_resources_on_timeout 方法確保徹底清理

## 📦 安裝與更新
```bash
# 快速測試最新版本
uvx mcp-feedback-enhanced@latest test --gui

# 更新到特定版本
uvx mcp-feedback-enhanced@v2.2.2 test
```

## 🔗 相關連結
- 完整文檔: [README.zh-TW.md](../../README.zh-TW.md)
- 問題回報: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)
- 解決問題: #5 (GUI/Web UI timeout cleanup) 
---

### 🇨🇳 简体中文
# Release v2.2.2 - 超时自动清理修复

## 🌟 亮点
本版本修复了一个重要的资源管理问题：当 MCP session 因超时结束时，GUI/Web UI 界面没有正确关闭，导致界面持续显示而无法正常关闭。

## 🐛 问题修复
- 🔄 **超时自动清理**: 修复 GUI/Web UI 在 MCP session timeout (默认 600 秒) 后没有自动关闭的问题
- 🛡️ **资源管理优化**: 改进超时处理机制，确保在超时时正确清理和关闭所有 UI 资源
- ⚡ **超时检测增强**: 加强超时检测逻辑，确保在各种情况下都能正确处理超时事件
- 🔧 **界面响应改进**: 改善 Web UI 前端对 session timeout 事件的处理响应

## 🚀 技术改进
- 📦 **Web Session 管理**: 重构 WebFeedbackSession 的超时处理逻辑
- 🎯 **QTimer 整合**: 在 GUI 中引入精确的 QTimer 超时控制机制
- 🌐 **前端通信优化**: 改进 Web UI 前端与后端的超时消息传递
- 🧹 **资源清理机制**: 新增 _cleanup_resources_on_timeout 方法确保彻底清理

## 📦 安装与更新
```bash
# 快速测试最新版本
uvx mcp-feedback-enhanced@latest test --gui

# 更新到特定版本
uvx mcp-feedback-enhanced@v2.2.2 test
```

## 🔗 相关链接
- 完整文档: [README.zh-CN.md](../../README.zh-CN.md)
- 问题报告: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)
- 解决问题: #5 (GUI/Web UI timeout cleanup) 
---

## 📦 Installation & Update

```bash
# Quick test latest version
uvx mcp-feedback-enhanced@latest test

# Update to this specific version
uvx mcp-feedback-enhanced@v2.2.2 test
```

## 🔗 Links
- **Documentation**: [README.md](https://github.com/Minidoracat/mcp-feedback-enhanced/blob/main/README.md)
- **Full Changelog**: [CHANGELOG](https://github.com/Minidoracat/mcp-feedback-enhanced/blob/main/RELEASE_NOTES/)
- **Issues**: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)

---
**Release automatically generated from RELEASE_NOTES system** 🤖
