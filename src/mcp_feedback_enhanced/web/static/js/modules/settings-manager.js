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
            sessionPanelCollapsed: false,
            // 自動定時提交設定
            autoSubmitEnabled: false,
            autoSubmitTimeout: 30,
            autoSubmitPromptId: null
        };
        
        // 當前設定
        this.currentSettings = Utils.deepClone(this.defaultSettings);
        
        // 回調函數
        this.onSettingsChange = options.onSettingsChange || null;
        this.onLanguageChange = options.onLanguageChange || null;
        this.onAutoSubmitStateChange = options.onAutoSubmitStateChange || null;
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
     * 驗證自動提交設定
     */
    SettingsManager.prototype.validateAutoSubmitSettings = function(settings) {
        const errors = [];

        // 驗證超時時間
        if (settings.autoSubmitTimeout !== undefined) {
            const timeout = parseInt(settings.autoSubmitTimeout);
            if (isNaN(timeout) || timeout < 1) {
                errors.push('自動提交時間必須大於等於 1 秒');
            } else if (timeout > 86400) { // 24 小時
                errors.push('自動提交時間不能超過 24 小時');
            }
        }

        // 驗證提示詞 ID
        if (settings.autoSubmitEnabled && !settings.autoSubmitPromptId) {
            errors.push('啟用自動提交時必須選擇一個提示詞');
        }

        return errors;
    };

    /**
     * 設定自動提交功能
     */
    SettingsManager.prototype.setAutoSubmitSettings = function(enabled, timeout, promptId) {
        const newSettings = {
            autoSubmitEnabled: Boolean(enabled),
            autoSubmitTimeout: parseInt(timeout) || 30,
            autoSubmitPromptId: promptId || null
        };

        // 驗證設定
        const errors = this.validateAutoSubmitSettings(newSettings);
        if (errors.length > 0) {
            throw new Error(errors.join('; '));
        }

        // 如果停用自動提交，清除提示詞 ID
        if (!newSettings.autoSubmitEnabled) {
            newSettings.autoSubmitPromptId = null;
        }

        // 更新設定
        this.set('autoSubmitEnabled', newSettings.autoSubmitEnabled);
        this.set('autoSubmitTimeout', newSettings.autoSubmitTimeout);
        this.set('autoSubmitPromptId', newSettings.autoSubmitPromptId);

        console.log('自動提交設定已更新:', newSettings);
        return newSettings;
    };

    /**
     * 獲取自動提交設定
     */
    SettingsManager.prototype.getAutoSubmitSettings = function() {
        return {
            enabled: this.get('autoSubmitEnabled'),
            timeout: this.get('autoSubmitTimeout'),
            promptId: this.get('autoSubmitPromptId')
        };
    };

    /**
     * 觸發自動提交狀態變更事件
     */
    SettingsManager.prototype.triggerAutoSubmitStateChange = function(enabled) {
        if (this.onAutoSubmitStateChange) {
            const settings = this.getAutoSubmitSettings();
            this.onAutoSubmitStateChange(enabled, settings);
        }

        console.log('自動提交狀態變更:', enabled ? '啟用' : '停用');
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

        // 應用自動提交設定
        this.applyAutoSubmitSettingsToUI();
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
        // 更新所有圖片大小限制選擇器（包括設定頁籤中的）
        const imageSizeLimitSelects = document.querySelectorAll('[id$="ImageSizeLimit"]');
        imageSizeLimitSelects.forEach(function(select) {
            select.value = this.currentSettings.imageSizeLimit.toString();
        }.bind(this));

        // 更新所有 Base64 相容模式複選框（包括設定頁籤中的）
        const enableBase64DetailCheckboxes = document.querySelectorAll('[id$="EnableBase64Detail"]');
        enableBase64DetailCheckboxes.forEach(function(checkbox) {
            checkbox.checked = this.currentSettings.enableBase64Detail;
        }.bind(this));

        console.log('圖片設定已應用到 UI:', {
            imageSizeLimit: this.currentSettings.imageSizeLimit,
            enableBase64Detail: this.currentSettings.enableBase64Detail
        });
    };

    /**
     * 應用自動提交設定到 UI
     */
    SettingsManager.prototype.applyAutoSubmitSettingsToUI = function() {
        // 更新自動提交啟用開關
        const autoSubmitToggle = Utils.safeQuerySelector('#autoSubmitToggle');
        if (autoSubmitToggle) {
            autoSubmitToggle.classList.toggle('active', this.currentSettings.autoSubmitEnabled);
        }

        // 更新自動提交超時時間輸入框
        const autoSubmitTimeoutInput = Utils.safeQuerySelector('#autoSubmitTimeout');
        if (autoSubmitTimeoutInput) {
            autoSubmitTimeoutInput.value = this.currentSettings.autoSubmitTimeout;
        }

        // 更新自動提交提示詞選擇下拉選單
        const autoSubmitPromptSelect = Utils.safeQuerySelector('#autoSubmitPromptSelect');
        if (autoSubmitPromptSelect) {
            autoSubmitPromptSelect.value = this.currentSettings.autoSubmitPromptId || '';
        }

        // 更新自動提交狀態顯示
        this.updateAutoSubmitStatusDisplay();

        console.log('自動提交設定已應用到 UI:', {
            enabled: this.currentSettings.autoSubmitEnabled,
            timeout: this.currentSettings.autoSubmitTimeout,
            promptId: this.currentSettings.autoSubmitPromptId
        });
    };

    /**
     * 更新自動提交狀態顯示
     */
    SettingsManager.prototype.updateAutoSubmitStatusDisplay = function() {
        const statusElement = Utils.safeQuerySelector('#autoSubmitStatus');
        if (!statusElement) return;

        const statusIcon = statusElement.querySelector('span:first-child');
        const statusText = statusElement.querySelector('.button-text');

        if (this.currentSettings.autoSubmitEnabled && this.currentSettings.autoSubmitPromptId) {
            // 直接設定 HTML 內容，就像提示詞按鈕一樣
            if (statusIcon) statusIcon.innerHTML = '⏰';
            if (statusText) {
                const enabledText = window.i18nManager ?
                    window.i18nManager.t('autoSubmit.enabled', '已啟用') :
                    '已啟用';
                statusText.textContent = `${enabledText} (${this.currentSettings.autoSubmitTimeout}秒)`;
            }
            statusElement.className = 'auto-submit-status-btn enabled';
        } else {
            // 直接設定 HTML 內容，就像提示詞按鈕一樣
            if (statusIcon) statusIcon.innerHTML = '⏸️';
            if (statusText) {
                const disabledText = window.i18nManager ?
                    window.i18nManager.t('autoSubmit.disabled', '已停用') :
                    '已停用';
                statusText.textContent = disabledText;
            }
            statusElement.className = 'auto-submit-status-btn disabled';
        }
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

        // 圖片設定 - 大小限制選擇器
        const settingsImageSizeLimit = Utils.safeQuerySelector('#settingsImageSizeLimit');
        if (settingsImageSizeLimit) {
            settingsImageSizeLimit.addEventListener('change', function(e) {
                const value = parseInt(e.target.value);
                self.set('imageSizeLimit', value);
                console.log('圖片大小限制已更新:', value);
            });
        }

        // 圖片設定 - Base64 相容模式切換器
        const settingsEnableBase64Detail = Utils.safeQuerySelector('#settingsEnableBase64Detail');
        if (settingsEnableBase64Detail) {
            settingsEnableBase64Detail.addEventListener('change', function(e) {
                const value = e.target.checked;
                self.set('enableBase64Detail', value);
                console.log('Base64 相容模式已更新:', value);
            });
        }

        // 自動提交功能啟用開關
        const autoSubmitToggle = Utils.safeQuerySelector('#autoSubmitToggle');
        if (autoSubmitToggle) {
            autoSubmitToggle.addEventListener('click', function() {
                const newValue = !self.get('autoSubmitEnabled');
                const currentPromptId = self.get('autoSubmitPromptId');

                console.log('自動提交開關點擊:', {
                    newValue: newValue,
                    currentPromptId: currentPromptId
                });

                try {
                    // 如果要啟用自動提交，檢查是否已選擇提示詞
                    if (newValue && (!currentPromptId || currentPromptId === '')) {
                        Utils.showMessage('請先選擇一個提示詞作為自動提交內容', Utils.CONSTANTS.MESSAGE_WARNING);
                        return;
                    }

                    self.set('autoSubmitEnabled', newValue);
                    autoSubmitToggle.classList.toggle('active', newValue);

                    console.log('自動提交狀態已更新:', newValue);

                    // 觸發自動提交狀態變更事件
                    self.triggerAutoSubmitStateChange(newValue);
                } catch (error) {
                    Utils.showMessage(error.message, Utils.CONSTANTS.MESSAGE_ERROR);
                }
            });
        }

        // 自動提交超時時間設定
        const autoSubmitTimeoutInput = Utils.safeQuerySelector('#autoSubmitTimeout');
        if (autoSubmitTimeoutInput) {
            autoSubmitTimeoutInput.addEventListener('change', function(e) {
                const timeout = parseInt(e.target.value);
                try {
                    self.setAutoSubmitSettings(
                        self.get('autoSubmitEnabled'),
                        timeout,
                        self.get('autoSubmitPromptId')
                    );
                } catch (error) {
                    Utils.showMessage(error.message, Utils.CONSTANTS.MESSAGE_ERROR);
                    // 恢復原值
                    e.target.value = self.get('autoSubmitTimeout');
                }
            });
        }

        // 自動提交提示詞選擇
        const autoSubmitPromptSelect = Utils.safeQuerySelector('#autoSubmitPromptSelect');
        if (autoSubmitPromptSelect) {
            autoSubmitPromptSelect.addEventListener('change', function(e) {
                const promptId = e.target.value || null;
                console.log('自動提交提示詞選擇變更:', promptId);

                try {
                    // 如果選擇了空值，清除自動提交設定
                    if (!promptId || promptId === '') {
                        self.set('autoSubmitPromptId', null);
                        self.set('autoSubmitEnabled', false);
                        console.log('清除自動提交設定');
                    } else {
                        // 設定新的自動提交提示詞
                        self.set('autoSubmitPromptId', promptId);
                        console.log('設定自動提交提示詞 ID:', promptId);
                    }
                } catch (error) {
                    Utils.showMessage(error.message, Utils.CONSTANTS.MESSAGE_ERROR);
                    // 恢復原值
                    e.target.value = self.get('autoSubmitPromptId') || '';
                }
            });
        }

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
