# Release v2.2.5 - WSL 环境支持与跨平台增强

## 🌟 亮点
本版本新增了 WSL (Windows Subsystem for Linux) 环境的完整支持，让 WSL 用户能够无缝使用本工具并自动启动 Windows 浏览器，大幅提升跨平台开发体验。

## ✨ 新功能
- 🐧 **WSL 环境检测**: 自动识别 WSL 环境，提供专门的支持逻辑
- 🌐 **智能浏览器启动**: WSL 环境下自动调用 Windows 浏览器，支持多种启动方式
- 🔧 **跨平台测试增强**: 测试功能整合 WSL 检测，提升测试覆盖率

## 🚀 改进功能
- 🎯 **环境检测优化**: 改进远程环境检测逻辑，WSL 不再被误判为远程环境
- 📊 **系统信息增强**: 系统信息工具新增 WSL 环境状态显示
- 🧪 **测试体验提升**: 测试模式下自动尝试启动浏览器，提供更好的测试体验

## 📦 安装与更新
```bash
# 快速测试最新版本
uvx mcp-feedback-enhanced@latest test --gui

# 更新到特定版本
uvx mcp-feedback-enhanced@v2.2.5 test
```

## 🔗 相关链接
- 完整文档: [README.zh-CN.md](../../README.zh-CN.md)
- 问题报告: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)
- 项目首页: [GitHub Repository](https://github.com/Minidoracat/mcp-feedback-enhanced)
