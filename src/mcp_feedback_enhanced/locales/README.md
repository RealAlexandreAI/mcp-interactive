# 多語系檔案結構說明

## 📁 檔案結構

```
locales/
├── README.md           # 此說明檔案
├── zh-TW/              # 繁體中文
│   └── translations.json
├── en/                 # 英文
│   └── translations.json
└── zh-CN/              # 簡體中文
    └── translations.json
```

## 🌐 翻譯檔案格式

每個語言的 `translations.json` 檔案都包含以下結構：

### 1. 元資料區塊 (meta)
```json
{
  "meta": {
    "language": "zh-TW",
    "displayName": "繁體中文",
    "author": "作者名稱",
    "version": "1.0.0",
    "lastUpdate": "2025-01-31"
  }
}
```

### 2. 應用程式區塊 (app)
```json
{
  "app": {
    "title": "應用程式標題",
    "projectDirectory": "專案目錄",
    "language": "語言",
    "settings": "設定"
  }
}
```

### 3. 分頁區塊 (tabs)
```json
{
  "tabs": {
    "feedback": "💬 回饋",
    "command": "⚡ 命令",
    "images": "🖼️ 圖片"
  }
}
```

### 4. 其他功能區塊
- `feedback`: 回饋相關文字
- `command`: 命令執行相關文字
- `images`: 圖片上傳相關文字
- `buttons`: 按鈕文字
- `status`: 狀態訊息
- `aiSummary`: AI 摘要標題
- `languageSelector`: 語言選擇器標題
- `languageNames`: 語言顯示名稱

## 🔧 新增新語言步驟

### 1. 建立語言目錄
```bash
mkdir src/mcp_feedback_enhanced/locales/[語言代碼]
```

### 2. 複製翻譯檔案
```bash
cp src/mcp_feedback_enhanced/locales/en/translations.json \
   src/mcp_feedback_enhanced/locales/[語言代碼]/translations.json
```

### 3. 修改元資料
```json
{
  "meta": {
    "language": "[語言代碼]",
    "displayName": "[語言顯示名稱]",
    "author": "[翻譯者姓名]",
    "version": "1.0.0",
    "lastUpdate": "[日期]"
  }
}
```

### 4. 翻譯內容
逐一翻譯各個區塊的內容，保持 JSON 結構不變。

### 5. 註冊新語言
在 `i18n.py` 中將新語言代碼加入支援列表：
```python
self._supported_languages = ['zh-TW', 'en', 'zh-CN', '[新語言代碼]']
```

在 `i18n.js` 中也要加入：
```javascript
this.supportedLanguages = ['zh-TW', 'en', 'zh-CN', '[新語言代碼]'];
```

## 🎯 使用方式

### Python 後端
```python
from .i18n import t

# 新格式（建議）
title = t('app.title')
button_text = t('buttons.submitFeedback')

# 舊格式（兼容）
title = t('app_title')
button_text = t('btn_submit_feedback')
```

### JavaScript 前端
```javascript
// 新格式（建議）
const title = t('app.title');
const buttonText = t('buttons.submitFeedback');

// 舊格式（兼容）
const title = t('app_title');
const buttonText = t('btn_submit_feedback');
```

## 📋 翻譯檢查清單

建議在新增或修改翻譯時檢查：

- [ ] JSON 格式正確，沒有語法錯誤
- [ ] 所有必要的鍵值都存在
- [ ] 佔位符 `{param}` 格式正確
- [ ] 特殊字符和 Emoji 顯示正常
- [ ] 文字長度適合 UI 顯示
- [ ] 語言顯示名稱在 `languageNames` 中正確設定

## 🔄 向後兼容

新的多語系系統完全向後兼容舊的鍵值格式：

| 舊格式 | 新格式 |
|--------|--------|
| `app_title` | `app.title` |
| `btn_submit_feedback` | `buttons.submitFeedback` |
| `images_status` | `images.status` |
| `command_output` | `command.output` |

## 🚀 優勢特色

1. **結構化組織**：按功能區域分組，易於維護
2. **元資料支援**：包含版本、作者等資訊
3. **巢狀鍵值**：更清晰的命名空間
4. **動態載入**：前端支援從 API 載入翻譯
5. **向後兼容**：舊程式碼無需修改
6. **易於擴充**：新增語言非常簡單

## 📝 貢獻指南

歡迎貢獻新的語言翻譯：

1. Fork 專案
2. 按照上述步驟新增語言
3. 測試翻譯是否正確顯示
4. 提交 Pull Request

需要幫助可以參考現有的翻譯檔案作為範本。 