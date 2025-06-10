# API 參考文檔

## 📡 MCP 工具 API

### interactive_feedback

AI 助手與用戶進行交互式回饋的核心 MCP 工具。

#### 函數簽名
```python
async def interactive_feedback(
    project_directory: str,
    summary: str,
    timeout: int = 600
) -> dict
```

#### 參數說明

| 參數 | 類型 | 必需 | 預設值 | 描述 |
|------|------|------|--------|------|
| `project_directory` | `str` | ✅ | - | 專案目錄路徑，用於上下文顯示 |
| `summary` | `str` | ✅ | - | AI 助手的工作摘要，向用戶說明當前狀態 |
| `timeout` | `int` | ❌ | `600` | 等待用戶回饋的超時時間（秒） |

#### 返回值
```python
{
    "command_logs": "",  # 命令執行日誌（保留字段）
    "interactive_feedback": str,  # 用戶回饋內容
    "images": List[str]  # 用戶上傳的圖片（Base64 編碼）
}
```

#### 使用示例
```python
# 基本調用
result = await interactive_feedback(
    project_directory="./my-web-app",
    summary="我已完成登入功能的實現，包括表單驗證和錯誤處理。請檢查代碼品質。"
)

# 自定義超時
result = await interactive_feedback(
    project_directory="./complex-project",
    summary="重構完成，請詳細測試所有功能模組。",
    timeout=1200  # 20分鐘
)
```

#### 錯誤處理
```python
try:
    result = await interactive_feedback(...)
except TimeoutError:
    print("用戶回饋超時")
except ValidationError as e:
    print(f"參數驗證錯誤: {e}")
except EnvironmentError as e:
    print(f"環境檢測錯誤: {e}")
```

## 🌐 Web API

### HTTP 端點

#### GET /
主頁重定向到回饋頁面。

**響應**: `302 Redirect` → `/feedback`

#### GET /feedback
回饋頁面主入口。

**響應**: `200 OK`
```html
<!DOCTYPE html>
<html>
<!-- 回饋頁面 HTML 內容 -->
</html>
```

#### GET /static/{path}
靜態資源服務（CSS、JS、圖片等）。

**參數**:
- `path`: 靜態資源路徑

**響應**: `200 OK` 或 `404 Not Found`

### WebSocket API

#### 連接端點
```
ws://localhost:{port}/ws
```

#### 訊息格式
所有 WebSocket 訊息都使用 JSON 格式：
```json
{
    "type": "message_type",
    "data": { /* 訊息數據 */ },
    "timestamp": "2024-12-XX 10:30:00"
}
```

### 📤 客戶端 → 服務器訊息

#### submit_feedback
提交用戶回饋。

```json
{
    "type": "submit_feedback",
    "data": {
        "feedback": "這個功能很好，但建議增加輸入驗證。",
        "images": [
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
        ],
        "settings": {
            "language": "zh-TW",
            "compress_images": true
        }
    }
}
```

**字段說明**:
- `feedback`: 用戶回饋文字內容
- `images`: 圖片數組（Base64 編碼）
- `settings.language`: 界面語言
- `settings.compress_images`: 是否壓縮圖片

#### heartbeat
心跳檢測訊息。

```json
{
    "type": "heartbeat",
    "data": {
        "timestamp": 1703123456789
    }
}
```

#### language_switch
切換界面語言。

```json
{
    "type": "language_switch",
    "data": {
        "language": "en"
    }
}
```

### 📥 服務器 → 客戶端訊息

#### connection_established
WebSocket 連接建立確認。

```json
{
    "type": "connection_established",
    "data": {
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "server_time": "2024-12-XX 10:30:00"
    }
}
```

#### session_updated
會話更新通知（AI 再次調用時）。

```json
{
    "type": "session_updated",
    "data": {
        "session_id": "new-session-id",
        "summary": "根據您的建議，我已修改了錯誤處理邏輯。",
        "project_directory": "./my-project",
        "timestamp": "2024-12-XX 10:35:00"
    }
}
```

#### feedback_received
回饋接收確認。

```json
{
    "type": "feedback_received",
    "data": {
        "session_id": "session-id",
        "status": "success",
        "message": "回饋已成功接收"
    }
}
```

#### status_update
狀態更新通知。

```json
{
    "type": "status_update",
    "data": {
        "status": "FEEDBACK_PROCESSING",
        "message": "正在處理您的回饋...",
        "progress": 50
    }
}
```

#### error
錯誤訊息。

```json
{
    "type": "error",
    "data": {
        "error_code": "VALIDATION_ERROR",
        "message": "回饋內容不能為空",
        "details": {
            "field": "feedback",
            "value": ""
        }
    }
}
```

## 🔧 內部 API

### WebUIManager API

#### create_session()
```python
async def create_session(
    self,
    summary: str,
    project_directory: str
) -> WebFeedbackSession
```

創建新的回饋會話。

#### smart_open_browser()
```python
async def smart_open_browser(self, url: str) -> bool
```

智能開啟瀏覽器，避免重複開啟。

**返回值**:
- `True`: 檢測到活躍標籤頁，未開啟新視窗
- `False`: 開啟了新瀏覽器視窗

### WebFeedbackSession API

#### submit_feedback()
```python
async def submit_feedback(
    self,
    feedback: str,
    images: List[str],
    settings: dict
) -> None
```

提交用戶回饋到會話。

#### wait_for_feedback()
```python
async def wait_for_feedback(self, timeout: int = 600) -> dict
```

等待用戶回饋完成。

#### add_websocket()
```python
def add_websocket(self, websocket: WebSocket) -> None
```

添加 WebSocket 連接到會話。

## 📊 狀態碼和錯誤碼

### HTTP 狀態碼
- `200 OK`: 請求成功
- `302 Found`: 重定向
- `404 Not Found`: 資源不存在
- `500 Internal Server Error`: 服務器內部錯誤

### WebSocket 錯誤碼
```python
class ErrorCodes:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
```

### 會話狀態
```python
class SessionStatus:
    WAITING = "FEEDBACK_WAITING"
    PROCESSING = "FEEDBACK_PROCESSING"
    SUBMITTED = "FEEDBACK_SUBMITTED"
    ERROR = "ERROR"
```

## 🔒 安全考慮

### 輸入驗證
- 回饋內容長度限制：最大 10,000 字符
- 圖片大小限制：單張最大 5MB
- 圖片數量限制：最多 10 張
- 支援的圖片格式：PNG, JPEG, GIF, WebP

### 資源保護
- WebSocket 連接數限制：每會話最多 5 個連接
- 會話超時自動清理
- 內存使用監控和限制

### 跨域設置
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發環境，生產環境應限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

**下一步**: 查看 [部署指南](./deployment-guide.md) 了解部署配置和運維指南
