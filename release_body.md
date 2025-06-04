## 🌐 Multi-Language Release Notes

### 🇺🇸 English
# Release v2.2.3 - Timeout Control & Image Settings Enhancement

## 🌟 Highlights
This version introduces user-controllable timeout settings and flexible image upload configuration options, while improving UV Cache management tools to enhance the overall user experience.

## ✨ New Features
- ⏰ **User Timeout Control**: Added customizable timeout settings with flexible range from 30 seconds to 2 hours
- ⏱️ **Countdown Timer**: Real-time countdown timer display at the top of the interface for visual time reminders
- 🖼️ **Image Size Limits**: Added image upload size limit settings (unlimited/1MB/3MB/5MB)
- 🔧 **Base64 Compatibility Mode**: Added Base64 detail mode to improve image recognition compatibility with AI models like Gemini
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

---

### 🇹🇼 繁體中文
# Release v2.2.3 - 超時控制與圖片設定增強

## 🌟 亮點
本版本新增了用戶可控制的超時設定功能，以及靈活的圖片上傳設定選項，同時完善了 UV Cache 管理工具，提升整體使用體驗。

## ✨ 新功能
- ⏰ **用戶超時控制**: 新增可自訂的超時設定功能，支援 30 秒至 2 小時的彈性設定
- ⏱️ **倒數計時器**: 介面頂部顯示即時倒數計時器，提供視覺化的時間提醒
- 🖼️ **圖片大小限制**: 新增圖片上傳大小限制設定（無限制/1MB/3MB/5MB）
- 🔧 **Base64 相容模式**: 新增 Base64 詳細模式，提升與 Gemini 等 AI 模型的圖片識別相容性
- 🧹 **UV Cache 管理工具**: 新增 `cleanup_cache.py` 腳本，協助管理和清理 UV cache 空間

## 🚀 改進功能
- 📚 **文檔結構優化**: 重新整理文檔目錄結構，將圖片移至 `docs/{語言}/images/` 路徑
- 📖 **Cache 管理指南**: 新增詳細的 UV Cache 管理指南，包含自動化清理方案
- 🎯 **智能相容性提示**: 當圖片上傳失敗時自動顯示 Base64 相容模式建議
- 🔄 **設定同步機制**: 改進圖片設定在不同介面模式間的同步機制

## 🐛 問題修復
- 🛡️ **超時處理優化**: 改進用戶自訂超時與 MCP 系統超時的協調機制
- 🖥️ **介面自動關閉**: 修復超時後介面自動關閉和資源清理邏輯
- 📱 **響應式佈局**: 優化超時控制元件在小螢幕設備上的顯示效果

## 🔧 技術改進
- 🎛️ **超時控制架構**: 實現前端倒數計時器與後端超時處理的分離設計
- 📊 **圖片處理優化**: 改進圖片上傳的大小檢查和格式驗證機制
- 🗂️ **設定持久化**: 增強設定保存機制，確保用戶偏好的正確保存和載入
- 🧰 **工具腳本增強**: 新增跨平台的 cache 清理工具，支援強制清理和預覽模式

## 📦 安裝與更新
```bash
# 快速測試最新版本
uvx mcp-feedback-enhanced@latest test --gui

# 更新到特定版本
uvx mcp-feedback-enhanced@v2.2.3 test
```

## 🔗 相關連結
- 完整文檔: [README.zh-TW.md](../../README.zh-TW.md)
- 問題回報: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)
- 相關 PR: #22 (超時控制功能), #19 (圖片設定功能)

---

### 🇨🇳 简体中文
# Release v2.2.3 - 超时控制与图片设置增强

## 🌟 亮点
本版本新增了用户可控制的超时设置功能，以及灵活的图片上传设置选项，同时完善了 UV Cache 管理工具，提升整体使用体验。

## ✨ 新功能
- ⏰ **用户超时控制**: 新增可自定义的超时设置功能，支持 30 秒至 2 小时的弹性设置
- ⏱️ **倒数计时器**: 界面顶部显示实时倒数计时器，提供可视化的时间提醒
- 🖼️ **图片大小限制**: 新增图片上传大小限制设置（无限制/1MB/3MB/5MB）
- 🔧 **Base64 兼容模式**: 新增 Base64 详细模式，提升与 Gemini 等 AI 模型的图片识别兼容性
- 🧹 **UV Cache 管理工具**: 新增 `cleanup_cache.py` 脚本，协助管理和清理 UV cache 空间

## 🚀 改进功能
- 📚 **文档结构优化**: 重新整理文档目录结构，将图片移至 `docs/{语言}/images/` 路径
- 📖 **Cache 管理指南**: 新增详细的 UV Cache 管理指南，包含自动化清理方案
- 🎯 **智能兼容性提示**: 当图片上传失败时自动显示 Base64 兼容模式建议
- 🔄 **设置同步机制**: 改进图片设置在不同界面模式间的同步机制

## 🐛 问题修复
- 🛡️ **超时处理优化**: 改进用户自定义超时与 MCP 系统超时的协调机制
- 🖥️ **界面自动关闭**: 修复超时后界面自动关闭和资源清理逻辑
- 📱 **响应式布局**: 优化超时控制组件在小屏幕设备上的显示效果

## 🔧 技术改进
- 🎛️ **超时控制架构**: 实现前端倒数计时器与后端超时处理的分离设计
- 📊 **图片处理优化**: 改进图片上传的大小检查和格式验证机制
- 🗂️ **设置持久化**: 增强设置保存机制，确保用户偏好的正确保存和载入
- 🧰 **工具脚本增强**: 新增跨平台的 cache 清理工具，支持强制清理和预览模式

## 📦 安装与更新
```bash
# 快速测试最新版本
uvx mcp-feedback-enhanced@latest test --gui

# 更新到特定版本
uvx mcp-feedback-enhanced@v2.2.3 test
```

## 🔗 相关链接
- 完整文档: [README.zh-CN.md](../../README.zh-CN.md)
- 问题报告: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)
- 相关 PR: #22 (超时控制功能), #19 (图片设置功能)

---

## 📦 Installation & Update

```bash
# Quick test latest version
uvx mcp-feedback-enhanced@latest test

# Update to this specific version
uvx mcp-feedback-enhanced@v2.2.3 test
```

## 🔗 Links
- **Documentation**: [README.md](https://github.com/Minidoracat/mcp-feedback-enhanced/blob/main/README.md)
- **Full Changelog**: [CHANGELOG](https://github.com/Minidoracat/mcp-feedback-enhanced/blob/main/RELEASE_NOTES/)
- **Issues**: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)

---
**Release automatically generated from RELEASE_NOTES system** 🤖
