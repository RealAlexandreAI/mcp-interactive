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