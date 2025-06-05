# Release v2.2.5 - WSL 環境支援與跨平台增強

## 🌟 亮點
本版本新增了 WSL (Windows Subsystem for Linux) 環境的完整支援，讓 WSL 用戶能夠無縫使用本工具並自動啟動 Windows 瀏覽器，大幅提升跨平台開發體驗。

## ✨ 新功能
- 🐧 **WSL 環境檢測**: 自動識別 WSL 環境，提供專門的支援邏輯
- 🌐 **智能瀏覽器啟動**: WSL 環境下自動調用 Windows 瀏覽器，支援多種啟動方式
- 🔧 **跨平台測試增強**: 測試功能整合 WSL 檢測，提升測試覆蓋率

## 🚀 改進功能
- 🎯 **環境檢測優化**: 改進遠端環境檢測邏輯，WSL 不再被誤判為遠端環境
- 📊 **系統資訊增強**: 系統資訊工具新增 WSL 環境狀態顯示
- 🧪 **測試體驗提升**: 測試模式下自動嘗試啟動瀏覽器，提供更好的測試體驗

## 📦 安裝與更新
```bash
# 快速測試最新版本
uvx mcp-feedback-enhanced@latest test --gui

# 更新到特定版本
uvx mcp-feedback-enhanced@v2.2.5 test
```

## 🔗 相關連結
- 完整文檔: [README.zh-TW.md](../../README.zh-TW.md)
- 問題回報: [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)
- 專案首頁: [GitHub Repository](https://github.com/Minidoracat/mcp-feedback-enhanced)
