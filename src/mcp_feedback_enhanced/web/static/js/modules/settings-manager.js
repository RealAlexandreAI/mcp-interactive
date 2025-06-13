/**
 * MCP Feedback Enhanced - 設定管理模組
 * ==================================
 * 
 * 處理應用程式設定的載入、保存和同步
 */

(function() {
    'use strict';

    // 確保命名空間和依賴存在
    window.MCPFeedback = window.MCPFeedback || {};
    const Utils = window.MCPFeedback.Utils;

    /**
     * 設定管理器建構函數
     */
    function SettingsManager(options) {
        options = options || {};
        
        // 預設設定
        this.defaultSettings = {
            layoutMode: 'combined-vertical',
            autoClose: false,
            language: 'zh-TW',
            imageSizeLimit: 0,
            enableBase64Detail: false,
            activeTab: 'combined',
            sessionPanelCollapsed: false
        };
        
        // 當前設定
        this.currentSettings = Utils.deepClone(this.defaultSettings);
        
        // 回調函數
        this.onSettingsChange = options.onSettingsChange || null;
        this.onLanguageChange = options.onLanguageChange || null;
    }

    /**
     * 載入設定
     */
    SettingsManager.prototype.loadSettings = function() {
        const self = this;
        
        return new Promise(function(resolve, reject) {
            console.log('開始載入設定...');
            
            // 優先從伺服器端載入設定
            self.loadFromServer()
                .then(function(serverSettings) {
                    if (serverSettings && Object.keys(serverSettings).length > 0) {
                        self.currentSettings = self.mergeSettings(self.defaultSettings, serverSettings);
                        console.log('從伺服器端載入設定成功:', self.currentSettings);
                        
                        // 同步到 localStorage
                        self.saveToLocalStorage();
                        resolve(self.currentSettings);
                    } else {
                        // 回退到 localStorage
                        return self.loadFromLocalStorage();
                    }
                })
                .then(function(localSettings) {
                    if (localSettings) {
                        self.currentSettings = self.mergeSettings(self.defaultSettings, localSettings);
                        console.log('從 localStorage 載入設定:', self.currentSettings);
                    } else {
                        console.log('沒有找到設定，使用預設值');
                    }
                    resolve(self.currentSettings);
                })
                .catch(function(error) {
                    console.error('載入設定失敗:', error);
                    self.currentSettings = Utils.deepClone(self.defaultSettings);
                    resolve(self.currentSettings);
                });
        });
    };

    /**
     * 從伺服器載入設定
     */
    SettingsManager.prototype.loadFromServer = function() {
        return fetch('/api/load-settings')
            .then(function(response) {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('伺服器回應錯誤: ' + response.status);
                }
            })
            .catch(function(error) {
                console.warn('從伺服器端載入設定失敗:', error);
                return null;
            });
    };

    /**
     * 從 localStorage 載入設定
     */
    SettingsManager.prototype.loadFromLocalStorage = function() {
        if (!Utils.isLocalStorageSupported()) {
            return Promise.resolve(null);
        }

        try {
            const localSettings = localStorage.getItem('mcp-feedback-settings');
            if (localSettings) {
                const parsed = Utils.safeJsonParse(localSettings, null);
                console.log('從 localStorage 載入設定:', parsed);
                return Promise.resolve(parsed);
            }
        } catch (error) {
            console.warn('從 localStorage 載入設定失敗:', error);
        }
        
        return Promise.resolve(null);
    };

    /**
     * 保存設定
     */
    SettingsManager.prototype.saveSettings = function(newSettings) {
        if (newSettings) {
            this.currentSettings = this.mergeSettings(this.currentSettings, newSettings);
        }

        console.log('保存設定:', this.currentSettings);

        // 保存到 localStorage
        this.saveToLocalStorage();

        // 同步保存到伺服器端
        this.saveToServer();

        // 觸發回調
        if (this.onSettingsChange) {
            this.onSettingsChange(this.currentSettings);
        }

        return this.currentSettings;
    };

    /**
     * 保存到 localStorage
     */
    SettingsManager.prototype.saveToLocalStorage = function() {
        if (!Utils.isLocalStorageSupported()) {
            return;
        }

        try {
            localStorage.setItem('mcp-feedback-settings', JSON.stringify(this.currentSettings));
        } catch (error) {
            console.error('保存設定到 localStorage 失敗:', error);
        }
    };

    /**
     * 保存到伺服器
     */
    SettingsManager.prototype.saveToServer = function() {
        fetch('/api/save-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(this.currentSettings)
        })
        .then(function(response) {
            if (response.ok) {
                console.log('設定已同步到伺服器端');
            } else {
                console.warn('同步設定到伺服器端失敗:', response.status);
            }
        })
        .catch(function(error) {
            console.warn('同步設定到伺服器端時發生錯誤:', error);
        });
    };

    /**
     * 合併設定
     */
    SettingsManager.prototype.mergeSettings = function(defaultSettings, newSettings) {
        const merged = Utils.deepClone(defaultSettings);
        
        for (const key in newSettings) {
            if (newSettings.hasOwnProperty(key)) {
                merged[key] = newSettings[key];
            }
        }
        
        return merged;
    };

    /**
     * 獲取設定值
     */
    SettingsManager.prototype.get = function(key, defaultValue) {
        if (key in this.currentSettings) {
            return this.currentSettings[key];
        }
        return defaultValue !== undefined ? defaultValue : this.defaultSettings[key];
    };

    /**
     * 設置設定值
     */
    SettingsManager.prototype.set = function(key, value) {
        const oldValue = this.currentSettings[key];
        this.currentSettings[key] = value;
        
        // 特殊處理語言變更
        if (key === 'language' && oldValue !== value) {
            this.handleLanguageChange(value);
        }
        
        this.saveSettings();
        return this;
    };

    /**
     * 批量設置設定
     */
    SettingsManager.prototype.setMultiple = function(settings) {
        let languageChanged = false;
        const oldLanguage = this.currentSettings.language;
        
        for (const key in settings) {
            if (settings.hasOwnProperty(key)) {
                this.currentSettings[key] = settings[key];
                
                if (key === 'language' && oldLanguage !== settings[key]) {
                    languageChanged = true;
                }
            }
        }
        
        if (languageChanged) {
            this.handleLanguageChange(this.currentSettings.language);
        }
        
        this.saveSettings();
        return this;
    };

    /**
     * 處理語言變更
     */
    SettingsManager.prototype.handleLanguageChange = function(newLanguage) {
        console.log('語言設定變更: ' + newLanguage);
        
        // 同步到 localStorage
        if (Utils.isLocalStorageSupported()) {
            localStorage.setItem('language', newLanguage);
        }
        
        // 通知國際化系統
        if (window.i18nManager) {
            window.i18nManager.setLanguage(newLanguage);
        }
        
        // 觸發語言變更回調
        if (this.onLanguageChange) {
            this.onLanguageChange(newLanguage);
        }
    };

    /**
     * 重置設定
     */
    SettingsManager.prototype.resetSettings = function() {
        console.log('重置所有設定');
        
        // 清除 localStorage
        if (Utils.isLocalStorageSupported()) {
            localStorage.removeItem('mcp-feedback-settings');
        }
        
        // 重置為預設值
        this.currentSettings = Utils.deepClone(this.defaultSettings);
        
        // 保存重置後的設定
        this.saveSettings();
        
        return this.currentSettings;
    };

    /**
     * 獲取所有設定
     */
    SettingsManager.prototype.getAllSettings = function() {
        return Utils.deepClone(this.currentSettings);
    };

    /**
     * 應用設定到 UI
     */
    SettingsManager.prototype.applyToUI = function() {
        console.log('應用設定到 UI');
        
        // 應用佈局模式
        this.applyLayoutMode();
        
        // 應用自動關閉設定
        this.applyAutoCloseToggle();
        
        // 應用語言設定
        this.applyLanguageSettings();
        
        // 應用圖片設定
        this.applyImageSettings();
    };

    /**
     * 應用佈局模式
     */
    SettingsManager.prototype.applyLayoutMode = function() {
        const layoutModeInputs = document.querySelectorAll('input[name="layoutMode"]');
        layoutModeInputs.forEach(function(input) {
            input.checked = input.value === this.currentSettings.layoutMode;
        }.bind(this));

        const expectedClassName = 'layout-' + this.currentSettings.layoutMode;
        if (document.body.className !== expectedClassName) {
            console.log('應用佈局模式: ' + this.currentSettings.layoutMode);
            document.body.className = expectedClassName;
        }
    };

    /**
     * 應用自動關閉設定
     */
    SettingsManager.prototype.applyAutoCloseToggle = function() {
        const autoCloseToggle = Utils.safeQuerySelector('#autoCloseToggle');
        if (autoCloseToggle) {
            autoCloseToggle.classList.toggle('active', this.currentSettings.autoClose);
        }
    };

    /**
     * 應用語言設定
     */
    SettingsManager.prototype.applyLanguageSettings = function() {
        if (this.currentSettings.language && window.i18nManager) {
            const currentI18nLanguage = window.i18nManager.getCurrentLanguage();
            if (this.currentSettings.language !== currentI18nLanguage) {
                console.log('應用語言設定: ' + currentI18nLanguage + ' -> ' + this.currentSettings.language);
                window.i18nManager.setLanguage(this.currentSettings.language);
            }
        }

        // 更新下拉選單選項
        const languageSelect = Utils.safeQuerySelector('#settingsLanguageSelect');
        if (languageSelect) {
            languageSelect.value = this.currentSettings.language;
        }

        // 更新語言選項顯示（兼容舊版卡片式選擇器）
        const languageOptions = document.querySelectorAll('.language-option');
        languageOptions.forEach(function(option) {
            option.classList.toggle('active', option.getAttribute('data-lang') === this.currentSettings.language);
        }.bind(this));
    };

    /**
     * 應用圖片設定
     */
    SettingsManager.prototype.applyImageSettings = function() {
        const imageSizeLimitSelects = document.querySelectorAll('[id$="ImageSizeLimit"]');
        imageSizeLimitSelects.forEach(function(select) {
            select.value = this.currentSettings.imageSizeLimit.toString();
        }.bind(this));

        const enableBase64DetailCheckboxes = document.querySelectorAll('[id$="EnableBase64Detail"]');
        enableBase64DetailCheckboxes.forEach(function(checkbox) {
            checkbox.checked = this.currentSettings.enableBase64Detail;
        }.bind(this));
    };



    /**
     * 設置事件監聽器
     */
    SettingsManager.prototype.setupEventListeners = function() {
        const self = this;
        
        // 佈局模式切換
        const layoutModeInputs = document.querySelectorAll('input[name="layoutMode"]');
        layoutModeInputs.forEach(function(input) {
            input.addEventListener('change', function(e) {
                self.set('layoutMode', e.target.value);
            });
        });

        // 自動關閉切換
        const autoCloseToggle = Utils.safeQuerySelector('#autoCloseToggle');
        if (autoCloseToggle) {
            autoCloseToggle.addEventListener('click', function() {
                const newValue = !self.get('autoClose');
                self.set('autoClose', newValue);
                autoCloseToggle.classList.toggle('active', newValue);
            });
        }

        // 語言切換 - 支援下拉選單
        const languageSelect = Utils.safeQuerySelector('#settingsLanguageSelect');
        if (languageSelect) {
            languageSelect.addEventListener('change', function(e) {
                const lang = e.target.value;
                self.set('language', lang);
            });
        }

        // 語言切換 - 兼容舊版卡片式選擇器
        const languageOptions = document.querySelectorAll('.language-option');
        languageOptions.forEach(function(option) {
            option.addEventListener('click', function() {
                const lang = option.getAttribute('data-lang');
                self.set('language', lang);
            });
        });

        // 重置設定
        const resetBtn = Utils.safeQuerySelector('#resetSettingsBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                if (confirm('確定要重置所有設定嗎？')) {
                    self.resetSettings();
                    self.applyToUI();
                }
            });
        }


    };

    // 將 SettingsManager 加入命名空間
    window.MCPFeedback.SettingsManager = SettingsManager;

    console.log('✅ SettingsManager 模組載入完成');

})();
