# Interactive Feedback MCP（互動回饋 MCP）

**原作者：** [Fábio Ferreira](https://x.com/fabiomlferreira)  
**分支版本：** [Minidoracat](https://github.com/Minidoracat)  
**相關資源：** [dotcursorrules.com](https://dotcursorrules.com/) 提供更多 AI 開發增強工具

這是一個簡單的 [MCP 伺服器](https://modelcontextprotocol.io/)，用於在 AI 輔助開發工具（如 [Cursor](https://www.cursor.com)）中實現人在回路（human-in-the-loop）的工作流程。該伺服器允許您執行命令、查看輸出並直接向 AI 提供文字回饋。同時支援 [Cline](https://cline.bot) 和 [Windsurf](https://windsurf.com)。

## ✨ 新功能：Web UI 支援

**🌐 支援 SSH Remote 開發環境**  
此分支版本新增了 Web UI 功能，完美解決了 SSH remote 開發環境中無法使用 GUI 的問題：

- **自動環境檢測**：系統會自動檢測運行環境
- **本地環境**：使用原有的 Qt GUI 介面
- **SSH Remote 環境**：自動切換到現代化 Web UI
- **即時通訊**：基於 WebSocket 的即時命令輸出和回饋
- **深色主題**：提供現代化的深色主題界面

![Interactive Feedback Web UI](https://raw.githubusercontent.com/Minidoracat/interactive-feedback-mcp/main/.github/web_ui_preview.jpg)

## 🎯 為什麼使用這個工具？

透過引導 AI 助手與用戶進行確認，而非進行推測性的高成本工具調用，此模組可以大幅減少平台（如 Cursor）上的付費請求次數。在某些情況下，它可以將多達 25 次工具調用合併為單次回饋導向的請求，節省資源並提升效能。

## 📝 提示工程設定

為了獲得最佳效果，請在您的 AI 助手中添加以下自訂提示（例如在 Cursor 的規則或提示中）：

> 每當你想要詢問問題時，請務必調用 MCP `interactive_feedback`。  
> 每當你即將完成用戶請求時，請調用 MCP `interactive_feedback` 而不是直接結束流程。  
> 持續調用 MCP 直到用戶的回饋為空，然後才結束請求。

這將確保您的 AI 助手在標記任務完成前使用此 MCP 伺服器請求用戶回饋。

## 🔧 環境檢測與配置

系統會自動檢測運行環境並選擇適當的介面：

### Qt GUI（本地環境）
- 使用 Qt 的 `QSettings` 按專案基礎儲存配置
- 包含命令設定、自動執行選項、視窗幾何狀態等
- 設定通常儲存在平台特定位置（Windows 登錄檔、macOS plist 檔案、Linux 配置目錄）

### Web UI（SSH Remote 環境）
- 基於 FastAPI 和 WebSocket 的現代化界面
- 支援即時命令執行和輸出顯示
- 自動瀏覽器啟動和會話管理
- 深色主題和響應式設計

## 🚀 安裝說明

### 系統需求
- Python 3.11 或更新版本
- [uv](https://github.com/astral-sh/uv) 套件管理器
  - Windows: `pip install uv`
  - Linux/Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 安裝步驟

1. **取得程式碼**
   ```bash
   git clone https://github.com/Minidoracat/interactive-feedback-mcp.git
   cd interactive-feedback-mcp
   ```

2. **安裝依賴項**
   ```bash
   uv sync
   ```

3. **測試安裝**
   ```bash
   # 基本功能測試
   uv run python test_web_ui.py
   
   # 持久化測試模式（可在瀏覽器中實際測試）
   uv run python test_web_ui.py --persistent
   ```

4. **運行 MCP 伺服器**
   ```bash
   uv run server.py
   ```

## ⚙️ AI 助手配置

### Cursor 配置

在 Cursor 的設定中配置自訂 MCP 伺服器，或手動編輯 `mcp.json`：

```json
{
  "mcpServers": {
    "interactive-feedback-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/interactive-feedback-mcp",
        "run",
        "server.py"
      ],
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

**記得將路徑修改為您實際的專案目錄！**

### Cline / Windsurf 配置

類似的設定原則：在各工具的 MCP 設定中配置伺服器命令，使用 `interactive-feedback-mcp` 作為伺服器識別符。

## 🧪 測試和開發

### 測試 Web UI 功能
```bash
# 快速功能測試
uv run python test_web_ui.py

# 互動式測試模式（持久化運行）
uv run python test_web_ui.py --persistent
```

### 開發模式
使用 FastMCP 開發模式運行伺服器並開啟測試界面：
```bash
uv run fastmcp dev server.py
```

## 🌟 功能特色

### 🖥️ 雙介面支援
- **Qt GUI**：適用於本地開發環境
- **Web UI**：適用於 SSH remote 開發環境

### 🔍 智慧環境檢測
- 自動檢測 SSH 連線環境變數
- 檢測 DISPLAY 設定（Linux）
- 檢測 VSCode Remote 開發環境
- 自動選擇最適合的介面

### 💻 命令執行功能
- 即時命令執行和輸出顯示
- 支援命令中斷和程序樹終止
- 自動工作目錄設定
- 命令歷史記錄

### 🎨 現代化介面
- 深色主題設計
- 響應式佈局（支援手機瀏覽器）
- WebSocket 即時通訊
- 載入動畫和視覺回饋

## 📖 使用範例

AI 助手會如此調用 `interactive_feedback` 工具：

```xml
<use_mcp_tool>
  <server_name>interactive-feedback-mcp</server_name>
  <tool_name>interactive_feedback</tool_name>
  <arguments>
    {
      "project_directory": "/path/to/your/project",
      "summary": "我已經實現了您請求的更改並重構了主模組。"
    }
  </arguments>
</use_mcp_tool>
```

## 🔄 工作流程

1. **AI 助手調用** - AI 完成任務後調用 `interactive_feedback`
2. **環境檢測** - 系統自動檢測運行環境
3. **介面啟動** - 根據環境啟動 Qt GUI 或 Web UI
4. **用戶互動** - 用戶可以執行命令、查看輸出、提供回饋
5. **回饋傳遞** - 用戶回饋傳回給 AI 助手
6. **流程繼續** - AI 根據回饋繼續或結束任務

## 🆕 版本更新

### v2.0 - Web UI 支援
- ✅ 新增 Web UI 介面支援 SSH remote 開發
- ✅ 自動環境檢測和介面選擇
- ✅ WebSocket 即時通訊
- ✅ 現代化深色主題
- ✅ 響應式設計支援
- ✅ 持久化測試模式

### v1.0 - 基礎版本（原作者）
- ✅ Qt GUI 介面
- ✅ 命令執行功能
- ✅ MCP 協議支援
- ✅ 多平台支援

## 🙏 致謝與聯繫

### 原作者
**Fábio Ferreira** - [X @fabiomlferreira](https://x.com/fabiomlferreira)  
如果您覺得 Interactive Feedback MCP 有用，最好的支持方式是關注原作者的 X 帳號。

### 分支維護者
如有關於 Web UI 功能的問題或建議，歡迎在 [GitHub Issues](https://github.com/Minidoracat/interactive-feedback-mcp/issues) 中提出。

### 相關資源
- [dotcursorrules.com](https://dotcursorrules.com/) - 更多 AI 輔助開發工作流程資源
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 官方文件

## 📄 授權條款

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 檔案。

---

**🌟 歡迎 Star 此專案並分享給更多開發者！**