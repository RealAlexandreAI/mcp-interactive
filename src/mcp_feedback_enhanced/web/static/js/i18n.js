/**
 * 國際化（i18n）模組
 * =================
 * 
 * 處理多語言支援和界面文字翻譯
 * 從後端 /api/translations 載入翻譯數據
 */

class I18nManager {
    constructor() {
        this.currentLanguage = 'zh-TW';
        this.translations = {};
        this.loadingPromise = null;
    }

    async init() {
        // 從 localStorage 載入語言偏好
        const savedLanguage = localStorage.getItem('language');
        if (savedLanguage) {
            this.currentLanguage = savedLanguage;
        }

        // 載入翻譯數據
        await this.loadTranslations();
        
        // 應用翻譯
        this.applyTranslations();
        
        // 設置語言選擇器
        this.setupLanguageSelectors();
        
        // 延遲一點再更新動態內容，確保應用程式已初始化
        setTimeout(() => {
            this.updateDynamicContent();
        }, 100);
    }

    async loadTranslations() {
        if (this.loadingPromise) {
            return this.loadingPromise;
        }

        this.loadingPromise = fetch('/api/translations')
            .then(response => response.json())
            .then(data => {
                this.translations = data;
                console.log('翻譯數據載入完成:', Object.keys(this.translations));
                
                // 檢查當前語言是否有翻譯數據
                if (!this.translations[this.currentLanguage] || Object.keys(this.translations[this.currentLanguage]).length === 0) {
                    console.warn(`當前語言 ${this.currentLanguage} 沒有翻譯數據，回退到 zh-TW`);
                    this.currentLanguage = 'zh-TW';
                }
            })
            .catch(error => {
                console.error('載入翻譯數據失敗:', error);
                // 使用最小的回退翻譯
                this.translations = this.getMinimalFallbackTranslations();
            });

        return this.loadingPromise;
    }

    getMinimalFallbackTranslations() {
        // 最小的回退翻譯，只包含關鍵項目
        return {
            'zh-TW': {
                'app': {
                    'title': 'Interactive Feedback MCP',
                    'projectDirectory': '專案目錄'
                },
                'tabs': {
                    'feedback': '💬 回饋',
                    'summary': '📋 AI 摘要',
                    'command': '⚡ 命令',
                    'settings': '⚙️ 設定'
                },
                'buttons': {
                    'cancel': '❌ 取消',
                    'submit': '✅ 提交回饋'
                },
                'settings': {
                    'language': '語言'
                }
            }
        };
    }

    // 支援巢狀鍵值的翻譯函數
    t(key, defaultValue = '') {
        const langData = this.translations[this.currentLanguage] || {};
        return this.getNestedValue(langData, key) || defaultValue || key;
    }

    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            return current && current[key] !== undefined ? current[key] : null;
        }, obj);
    }

    setLanguage(language) {
        if (this.translations[language]) {
            this.currentLanguage = language;
            localStorage.setItem('language', language);
            this.applyTranslations();
            
            // 更新語言選擇器（只更新設定頁面的）
            const selector = document.getElementById('settingsLanguageSelect');
            if (selector) {
                selector.value = language;
            }

            // 更新 HTML lang 屬性
            document.documentElement.lang = language;
            
            console.log('語言已切換到:', language);
        } else {
            console.warn('不支援的語言:', language);
        }
    }

    applyTranslations() {
        // 翻譯所有有 data-i18n 屬性的元素
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);
            if (translation && translation !== key) {
                element.textContent = translation;
            }
        });

        // 翻譯有 data-i18n-placeholder 屬性的元素
        const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
        placeholderElements.forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            const translation = this.t(key);
            if (translation && translation !== key) {
                element.placeholder = translation;
            }
        });

        // 更新動態內容
        this.updateDynamicContent();

        console.log('翻譯已應用:', this.currentLanguage);
    }

    updateDynamicContent() {
        // 只更新終端歡迎信息，不要覆蓋 AI 摘要
        this.updateTerminalWelcome();
    }

    updateTerminalWelcome() {
        const commandOutput = document.getElementById('commandOutput');
        if (commandOutput && window.feedbackApp) {
            const welcomeTemplate = this.t('dynamic.terminalWelcome');
            if (welcomeTemplate && welcomeTemplate !== 'dynamic.terminalWelcome') {
                const welcomeMessage = welcomeTemplate.replace('{sessionId}', window.feedbackApp.sessionId || 'unknown');
                commandOutput.textContent = welcomeMessage;
            }
        }
    }

    setupLanguageSelectors() {
        // 舊版下拉選擇器（兼容性保留）
        const selector = document.getElementById('settingsLanguageSelect');
        if (selector) {
            // 設置當前值
            selector.value = this.currentLanguage;
            
            // 添加事件監聽器
            selector.addEventListener('change', (e) => {
                this.setLanguage(e.target.value);
            });
        }

        // 新版現代化語言選擇器
        const languageOptions = document.querySelectorAll('.language-option');
        if (languageOptions.length > 0) {
            // 設置當前語言的活躍狀態
            languageOptions.forEach(option => {
                const lang = option.getAttribute('data-lang');
                if (lang === this.currentLanguage) {
                    option.classList.add('active');
                } else {
                    option.classList.remove('active');
                }
            });
        }
    }

    getCurrentLanguage() {
        return this.currentLanguage;
    }

    getAvailableLanguages() {
        return Object.keys(this.translations);
    }
}

// 創建全域實例
window.i18nManager = new I18nManager(); 