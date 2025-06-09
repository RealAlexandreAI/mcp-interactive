/**
 * MCP Feedback Enhanced - 自動刷新管理模組
 * =======================================
 * 
 * 處理自動檢測會話更新和頁面內容刷新
 */

(function() {
    'use strict';

    // 確保命名空間和依賴存在
    window.MCPFeedback = window.MCPFeedback || {};
    const Utils = window.MCPFeedback.Utils;

    /**
     * 自動刷新管理器建構函數
     */
    function AutoRefreshManager(options) {
        options = options || {};
        
        // 設定
        this.autoRefreshEnabled = options.autoRefreshEnabled || false;
        this.autoRefreshInterval = options.autoRefreshInterval || 5; // 秒
        this.lastKnownSessionId = options.lastKnownSessionId || null;
        
        // 定時器
        this.autoRefreshTimer = null;
        
        // UI 元素
        this.autoRefreshCheckbox = null;
        this.autoRefreshIntervalInput = null;
        this.refreshStatusIndicator = null;
        this.refreshStatusText = null;
        
        // 回調函數
        this.onSessionUpdate = options.onSessionUpdate || null;
        this.onSettingsChange = options.onSettingsChange || null;
        
        this.initUIElements();
    }

    /**
     * 初始化 UI 元素
     */
    AutoRefreshManager.prototype.initUIElements = function() {
        this.autoRefreshCheckbox = Utils.safeQuerySelector('#autoRefreshEnabled');
        this.autoRefreshIntervalInput = Utils.safeQuerySelector('#autoRefreshInterval');
        this.refreshStatusIndicator = Utils.safeQuerySelector('#refreshStatusIndicator');
        this.refreshStatusText = Utils.safeQuerySelector('#refreshStatusText');
        
        console.log('🔄 自動刷新 UI 元素初始化完成');
    };

    /**
     * 初始化自動刷新功能
     */
    AutoRefreshManager.prototype.init = function() {
        console.log('🔄 初始化自動刷新功能...');

        if (!this.autoRefreshCheckbox || !this.autoRefreshIntervalInput) {
            console.warn('⚠️ 自動刷新元素不存在，跳過初始化');
            return;
        }

        this.setupEventListeners();
        this.applySettings();
        
        // 延遲更新狀態指示器，確保 i18n 已完全載入
        const self = this;
        setTimeout(function() {
            self.updateAutoRefreshStatus();
            
            if (self.autoRefreshEnabled) {
                console.log('🔄 自動刷新已啟用，啟動自動檢測...');
                self.startAutoRefresh();
            }
        }, 100);

        console.log('✅ 自動刷新功能初始化完成');
    };

    /**
     * 設置事件監聽器
     */
    AutoRefreshManager.prototype.setupEventListeners = function() {
        const self = this;
        
        // 設置開關事件監聽器
        this.autoRefreshCheckbox.addEventListener('change', function(e) {
            self.autoRefreshEnabled = e.target.checked;
            self.handleAutoRefreshToggle();
            if (self.onSettingsChange) {
                self.onSettingsChange();
            }
        });

        // 設置間隔輸入事件監聽器
        this.autoRefreshIntervalInput.addEventListener('change', function(e) {
            const newInterval = parseInt(e.target.value);
            if (newInterval >= 5 && newInterval <= 300) {
                self.autoRefreshInterval = newInterval;
                if (self.onSettingsChange) {
                    self.onSettingsChange();
                }

                // 如果自動刷新已啟用，重新啟動定時器
                if (self.autoRefreshEnabled) {
                    self.stopAutoRefresh();
                    self.startAutoRefresh();
                }
            }
        });
    };

    /**
     * 應用設定
     */
    AutoRefreshManager.prototype.applySettings = function() {
        if (this.autoRefreshCheckbox) {
            this.autoRefreshCheckbox.checked = this.autoRefreshEnabled;
        }
        if (this.autoRefreshIntervalInput) {
            this.autoRefreshIntervalInput.value = this.autoRefreshInterval;
        }
    };

    /**
     * 處理自動刷新開關切換
     */
    AutoRefreshManager.prototype.handleAutoRefreshToggle = function() {
        if (this.autoRefreshEnabled) {
            this.startAutoRefresh();
        } else {
            this.stopAutoRefresh();
        }
        this.updateAutoRefreshStatus();
    };

    /**
     * 啟動自動刷新
     */
    AutoRefreshManager.prototype.startAutoRefresh = function() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
        }

        const self = this;
        this.autoRefreshTimer = setInterval(function() {
            self.checkForSessionUpdate();
        }, this.autoRefreshInterval * 1000);

        console.log('🔄 自動刷新已啟動，間隔: ' + this.autoRefreshInterval + '秒');
    };

    /**
     * 停止自動刷新
     */
    AutoRefreshManager.prototype.stopAutoRefresh = function() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
            this.autoRefreshTimer = null;
        }
        console.log('⏸️ 自動刷新已停止');
    };

    /**
     * 檢查會話更新
     */
    AutoRefreshManager.prototype.checkForSessionUpdate = function() {
        const self = this;
        
        this.updateAutoRefreshStatus('checking');

        fetch('/api/current-session')
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('API 請求失敗: ' + response.status);
                }
                return response.json();
            })
            .then(function(sessionData) {
                // 檢查會話 ID 是否變化
                if (sessionData.session_id && sessionData.session_id !== self.lastKnownSessionId) {
                    console.log('🔄 檢測到新會話: ' + self.lastKnownSessionId + ' -> ' + sessionData.session_id);

                    // 更新記錄的會話 ID
                    self.lastKnownSessionId = sessionData.session_id;

                    // 觸發會話更新回調
                    if (self.onSessionUpdate) {
                        self.onSessionUpdate(sessionData);
                    }

                    self.updateAutoRefreshStatus('detected');

                    // 短暫顯示檢測成功狀態，然後恢復為檢測中
                    setTimeout(function() {
                        if (self.autoRefreshEnabled) {
                            self.updateAutoRefreshStatus('enabled');
                        }
                    }, 2000);
                } else {
                    self.updateAutoRefreshStatus('enabled');
                }
            })
            .catch(function(error) {
                console.error('❌ 自動刷新檢測失敗:', error);
                self.updateAutoRefreshStatus('error');

                // 短暫顯示錯誤狀態，然後恢復
                setTimeout(function() {
                    if (self.autoRefreshEnabled) {
                        self.updateAutoRefreshStatus('enabled');
                    }
                }, 3000);
            });
    };

    /**
     * 更新自動刷新狀態指示器
     */
    AutoRefreshManager.prototype.updateAutoRefreshStatus = function(status) {
        status = status || (this.autoRefreshEnabled ? 'enabled' : 'disabled');

        console.log('🔧 updateAutoRefreshStatus 被調用，status: ' + status);
        console.log('🔧 refreshStatusIndicator: ' + (this.refreshStatusIndicator ? 'found' : 'null'));
        console.log('🔧 refreshStatusText: ' + (this.refreshStatusText ? 'found' : 'null'));

        if (!this.refreshStatusIndicator || !this.refreshStatusText) {
            console.log('⚠️ 自動檢測狀態元素未找到，跳過更新');
            return;
        }

        let indicator = '⏸️';
        let textKey = 'autoRefresh.disabled';

        switch (status) {
            case 'enabled':
                indicator = '🔄';
                textKey = 'autoRefresh.enabled';
                break;
            case 'checking':
                indicator = '🔍';
                textKey = 'autoRefresh.checking';
                break;
            case 'detected':
                indicator = '✅';
                textKey = 'autoRefresh.detected';
                break;
            case 'error':
                indicator = '❌';
                textKey = 'autoRefresh.error';
                break;
            case 'disabled':
            default:
                indicator = '⏸️';
                textKey = 'autoRefresh.disabled';
                break;
        }

        this.refreshStatusIndicator.textContent = indicator;

        // 使用多語系翻譯
        if (window.i18nManager) {
            const translatedText = window.i18nManager.t(textKey);
            console.log('🔄 自動檢測狀態翻譯: ' + textKey + ' -> ' + translatedText + ' (語言: ' + window.i18nManager.currentLanguage + ')');
            this.refreshStatusText.textContent = translatedText;
        } else {
            // 備用翻譯
            const fallbackTexts = {
                'autoRefresh.enabled': '已啟用',
                'autoRefresh.checking': '檢測中...',
                'autoRefresh.detected': '檢測到更新',
                'autoRefresh.error': '檢測錯誤',
                'autoRefresh.disabled': '已停用'
            };
            this.refreshStatusText.textContent = fallbackTexts[textKey] || '未知狀態';
        }
    };

    /**
     * 更新設定
     */
    AutoRefreshManager.prototype.updateSettings = function(settings) {
        if (settings.autoRefreshEnabled !== undefined) {
            this.autoRefreshEnabled = settings.autoRefreshEnabled;
        }
        if (settings.autoRefreshInterval !== undefined) {
            this.autoRefreshInterval = settings.autoRefreshInterval;
        }
        
        this.applySettings();
        
        // 根據新設定調整自動刷新狀態
        if (this.autoRefreshEnabled && !this.autoRefreshTimer) {
            this.startAutoRefresh();
        } else if (!this.autoRefreshEnabled && this.autoRefreshTimer) {
            this.stopAutoRefresh();
        }
        
        this.updateAutoRefreshStatus();
    };

    /**
     * 設置最後已知會話 ID
     */
    AutoRefreshManager.prototype.setLastKnownSessionId = function(sessionId) {
        this.lastKnownSessionId = sessionId;
    };

    /**
     * 獲取當前設定
     */
    AutoRefreshManager.prototype.getSettings = function() {
        return {
            autoRefreshEnabled: this.autoRefreshEnabled,
            autoRefreshInterval: this.autoRefreshInterval
        };
    };

    /**
     * 檢查是否已啟用
     */
    AutoRefreshManager.prototype.isEnabled = function() {
        return this.autoRefreshEnabled;
    };

    /**
     * 手動觸發檢查
     */
    AutoRefreshManager.prototype.manualCheck = function() {
        if (!this.autoRefreshEnabled) {
            console.log('🔄 手動觸發會話檢查...');
            this.checkForSessionUpdate();
        }
    };

    /**
     * 清理資源
     */
    AutoRefreshManager.prototype.cleanup = function() {
        this.stopAutoRefresh();
        console.log('🧹 自動刷新管理器已清理');
    };

    // 將 AutoRefreshManager 加入命名空間
    window.MCPFeedback.AutoRefreshManager = AutoRefreshManager;

    console.log('✅ AutoRefreshManager 模組載入完成');

})();
