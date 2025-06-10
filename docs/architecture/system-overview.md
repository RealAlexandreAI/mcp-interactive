# 系統架構總覽

## 🏗️ 整體架構設計

MCP Feedback Enhanced 採用**單一活躍會話 + 持久化 Web UI**的創新架構設計，實現 AI 助手與用戶之間的高效、無縫交互體驗。

### 系統整體架構圖

```mermaid
graph TB
    subgraph "AI 助手環境"
        AI[AI 助手<br/>Claude/GPT等]
    end
    
    subgraph "MCP Feedback Enhanced"
        subgraph "MCP 服務層"
            MCP[MCP Server<br/>server.py]
            TOOL[interactive_feedback<br/>工具]
        end
        
        subgraph "Web UI 管理層"
            WM[WebUIManager<br/>單例模式]
            SESSION[WebFeedbackSession<br/>會話管理]
        end
        
        subgraph "Web 服務層"
            API[FastAPI<br/>HTTP/WebSocket]
            ROUTES[路由處理<br/>main_routes.py]
        end
        
        subgraph "前端交互層"
            UI[Web UI<br/>HTML/JS]
            WS[WebSocket<br/>實時通信]
        end
        
        subgraph "工具層"
            ENV[環境檢測]
            BROWSER[智能瀏覽器開啟]
            RESOURCE[資源管理]
        end
    end
    
    subgraph "用戶環境"
        USER[用戶瀏覽器]
        FILES[專案文件]
    end
    
    AI -->|調用 MCP 工具| MCP
    MCP --> TOOL
    TOOL --> WM
    WM --> SESSION
    WM --> API
    API --> ROUTES
    ROUTES --> UI
    UI --> WS
    WS --> USER
    
    ENV --> MCP
    BROWSER --> USER
    RESOURCE --> SESSION
    
    USER -->|回饋提交| WS
    FILES -->|專案內容| TOOL
```

## 🎯 核心設計理念

### 1. 單一活躍會話模式
```mermaid
stateDiagram-v2
    [*] --> NoSession: 系統啟動
    NoSession --> ActiveSession: AI 首次調用
    ActiveSession --> SessionUpdated: AI 再次調用
    SessionUpdated --> ActiveSession: 會話切換完成
    ActiveSession --> Cleanup: 超時或手動清理
    Cleanup --> NoSession: 資源釋放
    
    note right of ActiveSession
        只維護一個活躍會話
        提升性能和用戶體驗
    end note
```

### 2. 持久化 Web UI 架構
- **瀏覽器標籤頁保持**: 避免重複開啟瀏覽器
- **WebSocket 連接復用**: 減少連接建立開銷
- **狀態無縫切換**: 從 SUBMITTED → WAITING
- **內容局部更新**: 只更新必要的 UI 元素

### 3. 智能環境檢測
```mermaid
flowchart TD
    START[啟動檢測] --> LOCAL{本地環境?}
    LOCAL -->|是| DIRECT[直接開啟瀏覽器]
    LOCAL -->|否| REMOTE{SSH 遠程?}
    REMOTE -->|是| TUNNEL[建立 SSH 隧道]
    REMOTE -->|否| WSL{WSL 環境?}
    WSL -->|是| WSLOPEN[WSL 瀏覽器開啟]
    WSL -->|否| FALLBACK[回退模式]
    
    DIRECT --> SUCCESS[成功啟動]
    TUNNEL --> SUCCESS
    WSLOPEN --> SUCCESS
    FALLBACK --> SUCCESS
```

## 🔧 技術亮點

### 1. 創新的會話管理
```python
# 傳統多會話設計 (已棄用)
self.sessions: Dict[str, WebFeedbackSession] = {}

# 創新單一活躍會話設計
self.current_session: Optional[WebFeedbackSession] = None
self.global_active_tabs: Dict[str, dict] = {}  # 全局標籤頁狀態
```

### 2. 智能瀏覽器開啟機制
- **活躍標籤頁檢測**: 避免重複開啟瀏覽器視窗
- **跨平台支援**: Windows, macOS, Linux 自動適配
- **環境感知**: SSH/WSL 環境特殊處理

### 3. 實時狀態同步
- **WebSocket 雙向通信**: 前後端狀態實時同步
- **會話更新通知**: 立即推送會話變更
- **錯誤處理機制**: 連接斷線自動重連

## 📊 性能特性

### 資源使用優化
- **內存佔用**: 單一會話模式減少 60% 內存使用
- **連接復用**: WebSocket 連接保持，減少建立開銷
- **智能清理**: 自動資源回收和會話超時處理

### 用戶體驗提升
- **零等待切換**: 會話更新無需重新載入頁面
- **連續交互**: 支援 AI 助手多次循環調用
- **視覺反饋**: 實時狀態指示和進度顯示

## 🔄 核心工作流程

### AI 助手調用流程
```mermaid
sequenceDiagram
    participant AI as AI 助手
    participant MCP as MCP 服務
    participant WM as WebUIManager
    participant UI as Web UI
    participant User as 用戶
    
    AI->>MCP: interactive_feedback()
    MCP->>WM: 創建/更新會話
    WM->>UI: 啟動 Web 服務
    WM->>User: 智能開啟瀏覽器
    User->>UI: 提交回饋
    UI->>WM: WebSocket 傳送
    WM->>MCP: 回饋完成
    MCP->>AI: 返回結果
```

### 多次循環調用
```mermaid
graph LR
    A[AI 首次調用] --> B[用戶回饋]
    B --> C[AI 處理回饋]
    C --> D[AI 再次調用]
    D --> E[會話無縫更新]
    E --> F[用戶再次回饋]
    F --> G[持續循環...]
    
    style D fill:#e1f5fe
    style E fill:#e8f5e8
```

---

**下一步**: 查看 [組件詳細說明](./component-details.md) 了解各組件的具體實現
