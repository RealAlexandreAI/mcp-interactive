# MCP Feedback Enhanced 架構文檔

## 📋 文檔索引

本目錄包含 MCP Feedback Enhanced 專案的完整架構文檔，提供深入的技術分析和設計說明。

### 📚 文檔結構

| 文檔 | 描述 | 適用對象 |
|------|------|----------|
| [系統架構總覽](./system-overview.md) | 整體架構設計、核心概念和技術亮點 | 架構師、技術負責人 |
| [組件詳細說明](./component-details.md) | 各層級組件的詳細功能和實現 | 開發人員、維護人員 |
| [交互流程文檔](./interaction-flows.md) | AI 助手與 MCP 服務的完整交互流程 | 集成開發人員 |
| [API 參考文檔](./api-reference.md) | MCP 工具接口和 WebSocket API 規範 | API 使用者、前端開發 |
| [部署指南](./deployment-guide.md) | 環境配置、部署選項和故障排除 | 運維人員、系統管理員 |

### 🏗️ 架構概覽

MCP Feedback Enhanced 採用**單一活躍會話 + 持久化 Web UI**的創新架構，實現了 AI 助手與用戶之間的無縫交互體驗。

#### 核心特性
- **智能環境檢測**: 自動識別 Local/SSH Remote/WSL 環境
- **單一活躍會話**: 替代傳統多會話管理，提升性能和用戶體驗
- **持久化 Web UI**: 支援多次循環調用，無需重複開啟瀏覽器
- **實時雙向通信**: WebSocket 實現前後端狀態同步
- **智能資源管理**: 自動清理和會話生命週期管理

#### 技術棧
- **後端**: Python 3.11+, FastAPI, FastMCP
- **前端**: HTML5, JavaScript ES6+, WebSocket
- **通信**: WebSocket, HTTP REST API
- **部署**: uvicorn, 跨平台支援

### 🎯 快速導航

- **新手入門**: 從 [系統架構總覽](./system-overview.md) 開始
- **深入理解**: 閱讀 [組件詳細說明](./component-details.md)
- **集成開發**: 參考 [交互流程文檔](./interaction-flows.md) 和 [API 參考文檔](./api-reference.md)
- **部署運維**: 查看 [部署指南](./deployment-guide.md)

### 📊 架構圖表

所有文檔都包含豐富的 Mermaid 圖表，包括：
- 系統整體架構圖
- 組件關係圖
- 交互流程圖
- 會話生命週期圖
- 部署拓撲圖

---

**版本**: 2.3.0  
**最後更新**: 2024年12月  
**維護者**: Minidoracat
