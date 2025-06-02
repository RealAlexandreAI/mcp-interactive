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
     * 獲取內嵌的備用翻譯（僅保留基本錯誤訊息）
     */
    _getEmbeddedTranslations() {
        return {
            'zh-TW': {
                app: { title: 'Interactive Feedback MCP' },
                loading: '載入中...',
                error: '載入失敗',
                retry: '重試'
            },
            'en': {
                app: { title: 'Interactive Feedback MCP' },
                loading: 'Loading...',
                error: 'Loading failed',
                retry: 'Retry'
            },
            'zh-CN': {
                app: { title: 'Interactive Feedback MCP' },
                loading: '加载中...',
                error: '加载失败',
                retry: '重试'
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
            'paste_no_image': 'status.paste_no_image',
            'paste_image_from_textarea': 'status.paste_image_from_textarea',
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