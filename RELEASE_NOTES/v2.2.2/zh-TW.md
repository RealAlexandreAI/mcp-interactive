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