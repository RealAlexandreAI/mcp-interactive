/**
 * 前端國際化支援 - 新架構版本
 * =============================
 * 
 * 提供 Web UI 的多語系支援，支援繁體中文、英文、簡體中文。
 * 新特性：
 * - 支援從 API 動態載入翻譯檔案
 * - 巢狀翻譯鍵值支援
 * - 舊格式兼容
 * - 自動偵測瀏覽器語言
 */

class I18nManager {
    constructor() {
        this.currentLanguage = null;
        this.translations = {};
        this.supportedLanguages = ['zh-TW', 'en', 'zh-CN'];
        this.fallbackLanguage = 'en';
        this.isLoaded = false;
        
        // 內嵌的備用翻譯（防止 API 載入失敗）
        this.fallbackTranslations = this._getEmbeddedTranslations();
        
        // 初始化語言設定
        this.currentLanguage = this.detectLanguage();
    }
    
    /**
     * 獲取內嵌的備用翻譯
     */
    _getEmbeddedTranslations() {
        return {
            'zh-TW': {
                app: {
                    title: 'Interactive Feedback MCP',
                    projectDirectory: '專案目錄',
                    language: '語言'
                },
                tabs: {
                    feedback: '💬 回饋',
                    command: '⚡ 命令'
                },
                feedback: {
                    title: '💬 您的回饋',
                    description: '請在這裡輸入您的回饋、建議或問題。您的意見將幫助 AI 更好地理解您的需求。',
                    placeholder: '請在這裡輸入您的回饋、建議或問題...\n\n💡 小提示：按 Ctrl+Enter 可快速提交回饋'
                },
                command: {
                    title: '⚡ 命令執行',
                    description: '您可以在此執行系統命令來驗證結果或獲取更多資訊。',
                    placeholder: '輸入要執行的命令...',
                    output: '命令輸出'
                },
                images: {
                    title: '🖼️ 圖片附件（可選）',
                    status: '已選擇 {count} 張圖片',
                    statusWithSize: '已選擇 {count} 張圖片 (總計 {size})',
                    dragHint: '🎯 拖拽圖片到這裡 (PNG、JPG、JPEG、GIF、BMP、WebP)',
                    deleteConfirm: '確定要移除圖片 "{filename}" 嗎？',
                    deleteTitle: '確認刪除'
                },
                buttons: {
                    selectFiles: '📁 選擇文件',
                    pasteClipboard: '📋 剪貼板',
                    clearAll: '✕ 清除',
                    runCommand: '▶️ 執行',
                    submitFeedback: '✅ 提交回饋',
                    cancel: '❌ 取消'
                },
                status: {
                    uploading: '上傳中...',
                    uploadSuccess: '上傳成功',
                    uploadFailed: '上傳失敗',
                    commandRunning: '命令執行中...',
                    commandFinished: '命令執行完成',
                    pasteSuccess: '已從剪貼板貼上圖片',
                    pasteFailed: '無法從剪貼板獲取圖片',
                    invalidFileType: '不支援的文件類型',
                    fileTooLarge: '文件過大（最大 1MB）'
                },
                aiSummary: '📋 AI 工作摘要',
                languageSelector: '🌐 語言選擇',
                languageNames: {
                    zhTw: '繁體中文',
                    en: 'English',
                    zhCn: '简体中文'
                }
            },
            
            'en': {
                app: {
                    title: 'Interactive Feedback MCP',
                    projectDirectory: 'Project Directory',
                    language: 'Language'
                },
                tabs: {
                    feedback: '💬 Feedback',
                    command: '⚡ Commands'
                },
                feedback: {
                    title: '💬 Your Feedback',
                    description: 'Please enter your feedback, suggestions, or questions here. Your input helps AI better understand your needs.',
                    placeholder: 'Please enter your feedback, suggestions, or questions here...\n\n💡 Tip: Press Ctrl+Enter to submit quickly'
                },
                command: {
                    title: '⚡ Command Execution',
                    description: 'You can execute system commands here to verify results or get additional information.',
                    placeholder: 'Enter command to execute...',
                    output: 'Command Output'
                },
                images: {
                    title: '🖼️ Image Attachments (Optional)',
                    status: '{count} images selected',
                    statusWithSize: '{count} images selected (Total {size})',
                    dragHint: '🎯 Drag images here (PNG, JPG, JPEG, GIF, BMP, WebP)',
                    deleteConfirm: 'Are you sure you want to remove image "{filename}"?',
                    deleteTitle: 'Confirm Delete'
                },
                buttons: {
                    selectFiles: '📁 Select Files',
                    pasteClipboard: '📋 Clipboard',
                    clearAll: '✕ Clear',
                    runCommand: '▶️ Run',
                    submitFeedback: '✅ Submit Feedback',
                    cancel: '❌ Cancel'
                },
                status: {
                    uploading: 'Uploading...',
                    uploadSuccess: 'Upload successful',
                    uploadFailed: 'Upload failed',
                    commandRunning: 'Command running...',
                    commandFinished: 'Command finished',
                    pasteSuccess: 'Image pasted from clipboard',
                    pasteFailed: 'Failed to get image from clipboard',
                    invalidFileType: 'Unsupported file type',
                    fileTooLarge: 'File too large (max 1MB)'
                },
                aiSummary: '📋 AI Work Summary',
                languageSelector: '🌐 Language',
                languageNames: {
                    zhTw: '繁體中文',
                    en: 'English',
                    zhCn: '简体中文'
                }
            },
            
            'zh-CN': {
                app: {
                    title: 'Interactive Feedback MCP',
                    projectDirectory: '项目目录',
                    language: '语言'
                },
                tabs: {
                    feedback: '💬 反馈',
                    command: '⚡ 命令'
                },
                feedback: {
                    title: '💬 您的反馈',
                    description: '请在这里输入您的反馈、建议或问题。您的意见将帮助 AI 更好地理解您的需求。',
                    placeholder: '请在这里输入您的反馈、建议或问题...\n\n💡 小提示：按 Ctrl+Enter 可快速提交反馈'
                },
                command: {
                    title: '⚡ 命令执行',
                    description: '您可以在此执行系统命令来验证结果或获取更多信息。',
                    placeholder: '输入要执行的命令...',
                    output: '命令输出'
                },
                images: {
                    title: '🖼️ 图片附件（可选）',
                    status: '已选择 {count} 张图片',
                    statusWithSize: '已选择 {count} 张图片 (总计 {size})',
                    dragHint: '🎯 拖拽图片到这里 (PNG、JPG、JPEG、GIF、BMP、WebP)',
                    deleteConfirm: '确定要移除图片 "{filename}" 吗？',
                    deleteTitle: '确认删除'
                },
                buttons: {
                    selectFiles: '📁 选择文件',
                    pasteClipboard: '📋 剪贴板',
                    clearAll: '✕ 清除',
                    runCommand: '▶️ 执行',
                    submitFeedback: '✅ 提交反馈',
                    cancel: '❌ 取消'
                },
                status: {
                    uploading: '上传中...',
                    uploadSuccess: '上传成功',
                    uploadFailed: '上传失败',
                    commandRunning: '命令执行中...',
                    commandFinished: '命令执行完成',
                    pasteSuccess: '已从剪贴板粘贴图片',
                    pasteFailed: '无法从剪贴板获取图片',
                    invalidFileType: '不支持的文件类型',
                    fileTooLarge: '文件过大（最大 1MB）'
                },
                aiSummary: '📋 AI 工作摘要',
                languageSelector: '🌐 语言选择',
                languageNames: {
                    zhTw: '繁體中文',
                    en: 'English',
                    zhCn: '简体中文'
                }
            }
        };
    }
    
    /**
     * 從 API 載入翻譯檔案
     */
    async loadTranslations() {
        try {
            // 嘗試從 API 載入翻譯
            const response = await fetch('/api/translations');
            if (response.ok) {
                const data = await response.json();
                this.translations = data;
                this.isLoaded = true;
                console.log('[I18N] 成功從 API 載入翻譯');
                return true;
            }
        } catch (error) {
            console.warn('[I18N] 無法從 API 載入翻譯，使用內嵌翻譯:', error);
        }
        
        // 使用內嵌翻譯作為備用
        this.translations = this.fallbackTranslations;
        this.isLoaded = true;
        console.log('[I18N] 使用內嵌翻譯');
        return false;
    }
    
    /**
     * 自動偵測語言
     */
    detectLanguage() {
        // 1. 先檢查 localStorage
        const savedLang = localStorage.getItem('mcp-feedback-language');
        if (savedLang && this.supportedLanguages.includes(savedLang)) {
            return savedLang;
        }
        
        // 2. 檢查瀏覽器語言設定
        const browserLang = navigator.language || navigator.userLanguage;
        
        // 映射常見的語言代碼
        const langMap = {
            'zh-TW': 'zh-TW',
            'zh-HK': 'zh-TW',
            'zh-MO': 'zh-TW',
            'zh-CN': 'zh-CN',
            'zh-SG': 'zh-CN',
            'zh': 'zh-TW',  // 默認繁體中文
            'en': 'en',
            'en-US': 'en',
            'en-GB': 'en',
            'en-AU': 'en',
            'en-CA': 'en'
        };
        
        if (langMap[browserLang]) {
            return langMap[browserLang];
        }
        
        // 3. 檢查語言前綴
        const prefix = browserLang.split('-')[0];
        if (langMap[prefix]) {
            return langMap[prefix];
        }
        
        // 4. 回退到默認語言
        return this.fallbackLanguage;
    }
    
    /**
     * 設定語言
     */
    setLanguage(language) {
        if (!this.supportedLanguages.includes(language)) {
            console.warn(`Unsupported language: ${language}`);
            return false;
        }
        
        this.currentLanguage = language;
        localStorage.setItem('mcp-feedback-language', language);
        
        // 觸發語言變更事件
        document.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { language: language }
        }));
        
        return true;
    }
    
    /**
     * 從巢狀物件中獲取值
     */
    _getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            return current && current[key] !== undefined ? current[key] : null;
        }, obj);
    }
    
    /**
     * 舊鍵到新鍵的映射
     */
    _getLegacyMapping() {
        return {
            // 應用程式標題
            'app_title': 'app.title',
            'project_directory': 'app.projectDirectory',
            'language_selector': 'languageSelector',
            
            // 語言名稱
            'lang_zh_tw': 'languageNames.zhTw',
            'lang_en': 'languageNames.en',
            'lang_zh_cn': 'languageNames.zhCn',
            
            // AI 摘要區域
            'ai_summary': 'aiSummary',
            
            // 分頁標籤
            'feedback_tab': 'tabs.feedback',
            'command_tab': 'tabs.command',
            
            // 回饋區域
            'feedback_title': 'feedback.title',
            'feedback_description': 'feedback.description',
            'feedback_placeholder': 'feedback.placeholder',
            
            // 命令區域
            'command_title': 'command.title',
            'command_description': 'command.description',
            'command_placeholder': 'command.placeholder',
            'command_output': 'command.output',
            
            // 圖片區域
            'images_title': 'images.title',
            'images_select': 'images.select',
            'images_paste': 'images.paste',
            'images_clear': 'images.clear',
            'images_status': 'images.status',
            'images_status_with_size': 'images.statusWithSize',
            'images_drag_hint': 'images.dragHint',
            'images_delete_confirm': 'images.deleteConfirm',
            'images_delete_title': 'images.deleteTitle',
            'images_size_warning': 'images.sizeWarning',
            'images_format_error': 'images.formatError',
            
            // 按鈕
            'btn_select_files': 'buttons.selectFiles',
            'btn_paste_clipboard': 'buttons.pasteClipboard',
            'btn_clear_all': 'buttons.clearAll',
            'btn_run_command': 'buttons.runCommand',
            'btn_submit_feedback': 'buttons.submitFeedback',
            'btn_cancel': 'buttons.cancel',
            
            // 狀態消息
            'uploading': 'status.uploading',
            'upload_success': 'status.uploadSuccess',
            'upload_failed': 'status.uploadFailed',
            'command_running': 'status.commandRunning',
            'command_finished': 'status.commandFinished',
            'paste_success': 'status.pasteSuccess',
            'paste_failed': 'status.pasteFailed',
            'invalid_file_type': 'status.invalidFileType',
            'file_too_large': 'status.fileTooLarge'
        };
    }
    
    /**
     * 獲取翻譯文字
     */
    t(key, params = {}) {
        // 確保翻譯已載入
        if (!this.isLoaded) {
            // 如果還沒載入，先嘗試從備用翻譯獲取
            this.translations = this.fallbackTranslations;
        }
        
        const currentTranslations = this.translations[this.currentLanguage] || {};
        
        // 嘗試新格式（巢狀鍵）
        let translation = this._getNestedValue(currentTranslations, key);
        
        // 如果沒有找到，嘗試舊格式映射
        if (translation === null) {
            const legacyMapping = this._getLegacyMapping();
            const newKey = legacyMapping[key];
            if (newKey) {
                translation = this._getNestedValue(currentTranslations, newKey);
            }
        }
        
        // 如果還是沒有找到，嘗試回退語言
        if (translation === null) {
            const fallbackTranslations = this.translations[this.fallbackLanguage] || {};
            translation = this._getNestedValue(fallbackTranslations, key);
            
            if (translation === null) {
                const legacyMapping = this._getLegacyMapping();
                const newKey = legacyMapping[key];
                if (newKey) {
                    translation = this._getNestedValue(fallbackTranslations, newKey);
                }
            }
        }
        
        // 最後回退到鍵本身
        if (translation === null) {
            translation = key;
        }
        
        // 替換參數
        if (typeof translation === 'string') {
            translation = translation.replace(/{(\w+)}/g, (match, param) => {
                return params[param] !== undefined ? params[param] : match;
            });
        }
        
        return translation;
    }
    
    /**
     * 獲取語言顯示名稱
     */
    getLanguageDisplayName(languageCode) {
        const key = `languageNames.${languageCode.toLowerCase().replace('-', '')}`;
        if (languageCode === 'zh-TW') {
            return this.t('languageNames.zhTw');
        } else if (languageCode === 'zh-CN') {
            return this.t('languageNames.zhCn');
        } else if (languageCode === 'en') {
            return this.t('languageNames.en');
        }
        return this.t(key);
    }
    
    /**
     * 獲取當前語言
     */
    getCurrentLanguage() {
        return this.currentLanguage;
    }
    
    /**
     * 獲取支援的語言列表
     */
    getSupportedLanguages() {
        return [...this.supportedLanguages];
    }
    
    /**
     * 初始化（載入翻譯）
     */
    async init() {
        await this.loadTranslations();
        return this.isLoaded;
    }
}

// 創建全域實例
window.i18n = new I18nManager();

// 翻譯函數的全域快捷方式
window.t = function(key, params = {}) {
    return window.i18n.t(key, params);
};

// 初始化函數
window.initI18n = async function() {
    await window.i18n.init();
    return window.i18n.isLoaded;
}; 