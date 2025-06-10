# 交互流程文檔

## 🔄 AI 助手與 MCP 服務完整交互流程

本文檔詳細描述 AI 助手調用 MCP Feedback Enhanced 服務的完整流程，包括首次調用和多次循環調用的機制。

## 📋 流程概覽

### 整體交互時序圖

```mermaid
sequenceDiagram
    participant AI as AI 助手
    participant MCP as MCP 服務
    participant WM as WebUIManager
    participant WS as WebSocket
    participant UI as Web UI
    participant User as 用戶
    
    Note over AI,User: 第一次調用流程
    AI->>MCP: interactive_feedback(summary, timeout)
    MCP->>WM: launch_web_feedback_ui()
    WM->>WM: 創建新會話
    WM->>WS: 啟動 Web 服務器
    WM->>User: 智能開啟瀏覽器
    User->>UI: 訪問回饋頁面
    UI->>WS: 建立 WebSocket 連接
    WS->>UI: connection_established
    
    Note over AI,User: 用戶回饋流程
    User->>UI: 填寫回饋內容
    UI->>WS: submit_feedback
    WS->>WM: 處理回饋數據
    WM->>MCP: 設置回饋完成
    MCP->>AI: 返回回饋結果
    
    Note over AI,User: 第二次調用流程
    AI->>MCP: interactive_feedback(new_summary, timeout)
    MCP->>WM: 更新現有會話
    WM->>WS: session_updated 通知
    WS->>UI: 會話更新訊息
    UI->>UI: 局部更新內容
    User->>UI: 提交新回饋
    UI->>WS: submit_feedback
    WS->>WM: 處理新回饋
    WM->>MCP: 設置回饋完成
    MCP->>AI: 返回新回饋結果
```

## 🚀 第一次調用詳細流程

### 1. AI 助手發起調用

```python
# AI 助手調用示例
result = await interactive_feedback(
    project_directory="./my-project",
    summary="我已完成了功能 X 的實現，請檢查代碼品質和邏輯正確性",
    timeout=600
)
```

### 2. MCP 服務處理流程

```mermaid
flowchart TD
    START[AI 調用 interactive_feedback] --> VALIDATE[參數驗證]
    VALIDATE --> ENV[環境檢測]
    ENV --> LAUNCH[調用 launch_web_feedback_ui]
    LAUNCH --> SESSION[創建新會話]
    SESSION --> SERVER[啟動 Web 服務器]
    SERVER --> BROWSER[智能開啟瀏覽器]
    BROWSER --> WAIT[等待用戶回饋]
    WAIT --> TIMEOUT{檢查超時}
    TIMEOUT -->|未超時| FEEDBACK[接收回饋]
    TIMEOUT -->|超時| ERROR[返回超時錯誤]
    FEEDBACK --> RETURN[返回結果給 AI]
    ERROR --> RETURN
```

**關鍵步驟說明**:

#### 2.1 環境檢測
```python
def detect_environment():
    if os.environ.get('SSH_CLIENT') or os.environ.get('SSH_TTY'):
        return "ssh"
    elif 'microsoft' in platform.uname().release.lower():
        return "wsl"
    else:
        return "local"
```

#### 2.2 會話創建
```python
async def create_session(self, summary: str, project_dir: str):
    # 保存舊會話的 WebSocket 連接
    old_websockets = []
    if self.current_session:
        old_websockets = list(self.current_session.websockets)
    
    # 創建新會話
    session_id = str(uuid.uuid4())
    self.current_session = WebFeedbackSession(
        session_id=session_id,
        summary=summary,
        project_directory=project_dir
    )
    
    # 繼承 WebSocket 連接
    for ws in old_websockets:
        self.current_session.add_websocket(ws)
    
    # 標記需要發送會話更新
    self._pending_session_update = True
```

### 3. Web UI 連接建立

```mermaid
sequenceDiagram
    participant Browser as 瀏覽器
    participant UI as Web UI
    participant WS as WebSocket
    participant Session as 會話管理
    
    Browser->>UI: 訪問 /feedback
    UI->>WS: 建立 WebSocket 連接
    WS->>Session: 註冊連接
    Session->>WS: connection_established
    WS->>UI: 發送連接確認
    
    alt 有待處理的會話更新
        Session->>WS: session_updated
        WS->>UI: 會話更新訊息
        UI->>UI: 更新頁面內容
    end
```

## 🔄 多次循環調用機制

### 持久化會話架構

MCP Feedback Enhanced 的核心創新在於**持久化會話架構**，支援 AI 助手進行多次循環調用而無需重新建立連接。

```mermaid
stateDiagram-v2
    [*] --> FirstCall: AI 首次調用
    FirstCall --> SessionActive: 會話建立
    SessionActive --> UserFeedback: 等待用戶回饋
    UserFeedback --> FeedbackSubmitted: 回饋提交
    FeedbackSubmitted --> AIProcessing: AI 處理回饋
    AIProcessing --> SecondCall: AI 再次調用
    SecondCall --> SessionUpdated: 會話更新
    SessionUpdated --> UserFeedback: 等待新回饋
    
    note right of SessionActive
        Web 服務器持續運行
        瀏覽器標籤頁保持開啟
        WebSocket 連接維持
    end note
    
    note right of SessionUpdated
        無需重新開啟瀏覽器
        局部更新頁面內容
        狀態無縫切換
    end note
```

### 第二次調用流程

#### 1. AI 助手再次調用
```python
# AI 根據用戶回饋進行調整後再次調用
result = await interactive_feedback(
    project_directory="./my-project",
    summary="根據您的建議，我已修改了錯誤處理邏輯，請再次確認",
    timeout=600
)
```

#### 2. 智能會話切換
```mermaid
flowchart TD
    CALL[AI 再次調用] --> CHECK[檢查現有會話]
    CHECK --> ACTIVE{有活躍會話?}
    ACTIVE -->|是| UPDATE[更新會話內容]
    ACTIVE -->|否| CREATE[創建新會話]
    UPDATE --> PRESERVE[保存 WebSocket 連接]
    CREATE --> PRESERVE
    PRESERVE --> NOTIFY[發送會話更新通知]
    NOTIFY --> FRONTEND[前端接收更新]
    FRONTEND --> REFRESH[局部刷新內容]
```

#### 3. 前端無縫更新
```javascript
// 處理會話更新訊息
function handleSessionUpdated(data) {
    // 顯示會話更新通知
    showNotification('會話已更新', 'info');
    
    // 重置回饋狀態
    feedbackState = 'FEEDBACK_WAITING';
    
    // 局部更新 AI 摘要
    updateAISummary(data.summary);
    
    // 清空回饋表單
    clearFeedbackForm();
    
    // 更新會話 ID
    currentSessionId = data.session_id;
    
    // 保持 WebSocket 連接不變
    // 無需重新建立連接
}
```

## 📊 狀態同步機制

### WebSocket 訊息類型

```mermaid
graph LR
    subgraph "服務器 → 客戶端"
        CE[connection_established<br/>連接建立]
        SU[session_updated<br/>會話更新]
        FR[feedback_received<br/>回饋確認]
        ST[status_update<br/>狀態更新]
    end
    
    subgraph "客戶端 → 服務器"
        SF[submit_feedback<br/>提交回饋]
        HB[heartbeat<br/>心跳檢測]
        LS[language_switch<br/>語言切換]
    end
```

### 狀態轉換圖

```mermaid
stateDiagram-v2
    [*] --> WAITING: 會話創建/更新
    WAITING --> FEEDBACK_PROCESSING: 用戶提交回饋
    FEEDBACK_PROCESSING --> FEEDBACK_SUBMITTED: 處理完成
    FEEDBACK_SUBMITTED --> WAITING: 新會話更新
    FEEDBACK_SUBMITTED --> [*]: 會話結束
    
    WAITING --> ERROR: 連接錯誤
    FEEDBACK_PROCESSING --> ERROR: 處理錯誤
    ERROR --> WAITING: 錯誤恢復
    ERROR --> [*]: 致命錯誤
```

## 🛡️ 錯誤處理和恢復

### 連接斷線處理
```javascript
// WebSocket 重連機制
function handleWebSocketClose() {
    console.log('WebSocket 連接已關閉，嘗試重連...');
    
    setTimeout(() => {
        initWebSocket();
    }, 3000); // 3秒後重連
}

// 心跳檢測
setInterval(() => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
            type: 'heartbeat',
            timestamp: Date.now()
        }));
    }
}, 30000); // 每30秒發送心跳
```

### 超時處理
```python
async def wait_for_feedback(self, timeout: int = 600):
    try:
        await asyncio.wait_for(
            self.feedback_completed.wait(),
            timeout=timeout
        )
        return self.get_feedback_result()
    except asyncio.TimeoutError:
        raise TimeoutError(f"等待用戶回饋超時 ({timeout}秒)")
```

## 🎯 性能優化

### 連接復用
- **WebSocket 連接保持**: 避免重複建立連接
- **會話狀態繼承**: 新會話繼承舊會話的連接
- **智能瀏覽器開啟**: 檢測活躍標籤頁，避免重複開啟

### 資源管理
- **自動清理機制**: 超時會話自動清理
- **內存優化**: 單一活躍會話模式
- **進程管理**: 優雅的進程啟動和關閉

---

**下一步**: 查看 [API 參考文檔](./api-reference.md) 了解詳細的 API 規範
