# MCP Feedback Enhanced（互動回饋 MCP）

**🌐 語言切換 / Language:** [English](README.md) | **繁體中文** | [简体中文](README.zh-CN.md)

**原作者：** [Fábio Ferreira](https://x.com/fabiomlferreira) | [原始專案](https://github.com/noopstudios/interactive-feedback-mcp) ⭐
**分支版本：** [Minidoracat](https://github.com/Minidoracat)
**UI 設計參考：** [sanshao85/mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

## 🎯 核心概念

這是一個 [MCP 伺服器](https://modelcontextprotocol.io/)，建立**回饋導向的開發工作流程**，完美適配本地、**SSH 遠端開發環境**與 **WSL (Windows Subsystem for Linux) 環境**。透過引導 AI 與用戶確認而非進行推測性操作，可將多次工具調用合併為單次回饋導向請求，大幅節省平台成本並提升開發效率。

**支援平台：** [Cursor](https://www.cursor.com) | [Cline](https://cline.bot) | [Windsurf](https://windsurf.com) | [Augment](https://www.augmentcode.com) | [Trae](https://www.trae.ai)

### 🔄 工作流程
1. **AI 調用** → `mcp-feedback-enhanced`
2. **環境檢測** → 自動選擇合適介面
3. **用戶互動** → 命令執行、文字回饋、圖片上傳
4. **回饋傳遞** → 資訊返回 AI
5. **流程繼續** → 根據回饋調整或結束

## 🌟 主要功能

### 🖥️ 雙介面系統
- **Qt GUI**：本地環境原生體驗，模組化重構設計
- **Web UI**：遠端 SSH 環境與 WSL 環境現代化界面，全新架構
- **智能切換**：自動檢測環境（本地/遠端/WSL）並選擇最適介面

### 🎨 全新界面設計（v2.1.0）
- **模組化架構**：GUI 和 Web UI 均採用模組化設計
- **集中管理**：資料夾結構重新組織，維護更容易
- **現代化主題**：改進的視覺設計和用戶體驗
- **響應式布局**：適應不同螢幕尺寸和視窗大小

### 🖼️ 圖片支援
- **格式支援**：PNG、JPG、JPEG、GIF、BMP、WebP
- **上傳方式**：拖拽檔案 + 剪貼板粘貼（Ctrl+V）
- **自動處理**：智能壓縮確保符合 1MB 限制

### 🌏 多語言
- **三語支援**：繁體中文、英文、簡體中文
- **智能偵測**：根據系統語言自動選擇
- **即時切換**：介面內可直接切換語言

### ✨ WSL 環境支援（v2.2.5 新功能）
- **自動檢測**：智能識別 WSL (Windows Subsystem for Linux) 環境
- **瀏覽器整合**：WSL 環境下自動啟動 Windows 瀏覽器
- **多種啟動方式**：支援 `cmd.exe`、`powershell.exe`、`wslview` 等多種瀏覽器啟動方法
- **無縫體驗**：WSL 用戶可直接使用 Web UI，無需額外配置

## 🖥️ 介面預覽

### Qt GUI 介面（重構版）
<div align="center">
  <img src="docs/zh-TW/images/gui1.png" width="400" alt="Qt GUI 主介面" />
  <img src="docs/zh-TW/images/gui2.png" width="400" alt="Qt GUI 設定介面" />
</div>

*Qt GUI 介面 - 模組化重構，支援本地環境*

### Web UI 介面（重構版）
<div align="center">
  <img src="docs/zh-TW/images/web1.png" width="400" alt="Web UI 主介面" />
  <img src="docs/zh-TW/images/web2.png" width="400" alt="Web UI 設定介面" />
</div>

*Web UI 介面 - 全新架構，適合 SSH Remote 環境*

**快捷鍵支援**
- `Ctrl+Enter`（Windows/Linux）/ `Cmd+Enter`（macOS）：提交回饋（主鍵盤與數字鍵盤皆支援）
- `Ctrl+V`（Windows/Linux）/ `Cmd+V`（macOS）：直接粘貼剪貼板圖片

## 🚀 快速開始

### 1. 安裝與測試
```bash
# 安裝 uv（如果尚未安裝）
pip install uv

# 快速測試
uvx mcp-feedback-enhanced@latest test
```

### 2. 配置 MCP
**基本配置**（適合大多數用戶）：
```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@latest"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

**進階配置**（需要自訂環境）：
```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@latest"],
      "timeout": 600,
      "env": {
        "FORCE_WEB": "true",
        "MCP_DEBUG": "false"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

### 3. 設定提示工程
為了獲得最佳效果，請在 AI 助手中添加以下規則：

```
# MCP Interactive Feedback 規則

1. 在任何流程、任務、對話進行時，無論是詢問、回覆、或完成階段性任務，皆必須呼叫 MCP mcp-feedback-enhanced。
2. 每當收到使用者回饋，若回饋內容非空，必須再次呼叫 MCP mcp-feedback-enhanced，並根據回饋內容調整行為。
3. 僅當使用者明確表示「結束」或「不再需要互動」時，才可停止呼叫 MCP mcp-feedback-enhanced，流程才算結束。
4. 除非收到結束指令，否則所有步驟都必須重複呼叫 MCP mcp-feedback-enhanced。
5. 完成任務前，必須使用 MCP mcp-feedback-enhanced 工具向使用者詢問回饋。
```

## ⚙️ 進階設定

### 環境變數
| 變數 | 用途 | 值 | 默認 |
|------|------|-----|------|
| `FORCE_WEB` | 強制使用 Web UI | `true`/`false` | `false` |
| `MCP_DEBUG` | 調試模式 | `true`/`false` | `false` |

### 測試選項
```bash
# 版本查詢
uvx mcp-feedback-enhanced@latest version       # 檢查版本

# 指定介面測試
uvx mcp-feedback-enhanced@latest test --gui    # 快速測試 Qt GUI
uvx mcp-feedback-enhanced@latest test --web    # 測試 Web UI (自動持續運行)

# 調試模式
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

### 開發者安裝
```bash
git clone https://github.com/Minidoracat/mcp-feedback-enhanced.git
cd mcp-feedback-enhanced
uv sync
```

**本地測試方式**
```bash
# 方式一：標準測試（推薦）
uv run python -m mcp_feedback_enhanced test

# 方式二：完整測試套件（macOS 和 windows 通用開發環境）
uvx --with-editable . mcp-feedback-enhanced test

# 方式三：指定介面測試
uvx --with-editable . mcp-feedback-enhanced test --gui    # 快速測試 Qt GUI
uvx --with-editable . mcp-feedback-enhanced test --web    # 測試 Web UI (自動持續運行)
```

**測試說明**
- **標準測試**：執行完整的功能檢查，適合日常開發驗證
- **完整測試**：包含所有組件的深度測試，適合發布前驗證
- **Qt GUI 測試**：快速啟動並測試本地圖形界面
- **Web UI 測試**：啟動 Web 服務器並保持運行，便於完整測試 Web 功能

## 🆕 版本更新記錄

📋 **完整版本更新記錄：** [RELEASE_NOTES/CHANGELOG.zh-TW.md](RELEASE_NOTES/CHANGELOG.zh-TW.md)

### 最新版本亮點（v2.2.5）
- ✨ **WSL 環境支援**: 新增 WSL (Windows Subsystem for Linux) 環境的完整支援
- 🌐 **智能瀏覽器啟動**: WSL 環境下自動調用 Windows 瀏覽器，支援多種啟動方式
- 🎯 **環境檢測優化**: 改進遠端環境檢測邏輯，WSL 不再被誤判為遠端環境
- 🧪 **測試體驗提升**: 測試模式下自動嘗試啟動瀏覽器，提供更好的測試體驗

## 🐛 常見問題

**Q: 出現 "Unexpected token 'D'" 錯誤**
A: 調試輸出干擾。設置 `MCP_DEBUG=false` 或移除該環境變數。

**Q: 中文字符亂碼**
A: 已在 v2.0.3 修復。更新到最新版本：`uvx mcp-feedback-enhanced@latest`

**Q: 多螢幕環境下視窗消失或定位錯誤**
A: 已在 v2.1.1 修復。進入「⚙️ 設定」分頁，勾選「總是在主螢幕中心顯示視窗」即可解決。特別適用於 T 字型螢幕排列等複雜多螢幕配置。

**Q: 圖片上傳失敗**
A: 檢查檔案大小（≤1MB）和格式（PNG/JPG/GIF/BMP/WebP）。

**Q: Web UI 無法啟動**
A: 設置 `FORCE_WEB=true` 或檢查防火牆設定。

**Q: UV Cache 佔用過多磁碟空間**
A: 由於頻繁使用 `uvx` 命令，cache 可能會累積到數十 GB。建議定期清理：
```bash
# 查看 cache 大小和詳細資訊
python scripts/cleanup_cache.py --size

# 預覽清理內容（不實際清理）
python scripts/cleanup_cache.py --dry-run

# 執行標準清理
python scripts/cleanup_cache.py --clean

# 強制清理（會嘗試關閉相關程序，解決 Windows 檔案佔用問題）
python scripts/cleanup_cache.py --force

# 或直接使用 uv 命令
uv cache clean
```
詳細說明請參考：[Cache 管理指南](docs/zh-TW/cache-management.md)

**Q: AI 模型無法解析圖片**
A: 各種 AI 模型（包括 Gemini Pro 2.5、Claude 等）在圖片解析上可能存在不穩定性，表現為有時能正確識別、有時無法解析上傳的圖片內容。這是 AI 視覺理解技術的已知限制。建議：
1. 確保圖片品質良好（高對比度、清晰文字）
2. 多嘗試幾次上傳，通常重試可以成功
3. 如持續無法解析，可嘗試調整圖片大小或格式

## 🙏 致謝

### 🌟 支持原作者
**Fábio Ferreira** - [X @fabiomlferreira](https://x.com/fabiomlferreira)
**原始專案：** [noopstudios/interactive-feedback-mcp](https://github.com/noopstudios/interactive-feedback-mcp)

如果您覺得有用，請：
- ⭐ [為原專案按星星](https://github.com/noopstudios/interactive-feedback-mcp)
- 📱 [關注原作者](https://x.com/fabiomlferreira)

### 設計靈感
**sanshao85** - [mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

### 社群支援
- **Discord：** [https://discord.gg/Gur2V67](https://discord.gg/Gur2V67)
- **Issues：** [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)

## 📄 授權

MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

---
**🌟 歡迎 Star 並分享給更多開發者！**