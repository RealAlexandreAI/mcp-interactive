/**
 * MCP Feedback Enhanced - 主應用程式
 * =================================
 *
 * 模組化重構版本，整合所有功能模組
 * 依賴模組載入順序：utils -> tab-manager -> websocket-manager -> image-handler ->
 *                  settings-manager -> ui-manager -> auto-refresh-manager -> app
 */

(function() {
    'use strict';

    // 確保命名空間存在
    window.MCPFeedback = window.MCPFeedback || {};
    const Utils = window.MCPFeedback.Utils;

    /**
     * 主應用程式建構函數
     */
    function FeedbackApp(sessionId) {
        // 會話信息
        this.sessionId = sessionId;
        this.currentSessionId = null;

        // 模組管理器
        this.tabManager = null;
        this.webSocketManager = null;
        this.imageHandler = null;
        this.settingsManager = null;
        this.uiManager = null;
        this.autoRefreshManager = null;

        // 應用程式狀態
        this.isInitialized = false;
        this.pendingSubmission = null;

        console.log('🚀 FeedbackApp 建構函數初始化完成');
    }

    /**
     * 初始化應用程式
     */
    FeedbackApp.prototype.init = function() {
        const self = this;

        console.log('🚀 初始化 MCP Feedback Enhanced 應用程式');

        return new Promise(function(resolve, reject) {
            try {
                // 等待國際化系統
                self.waitForI18n()
                    .then(function() {
                        return self.initializeManagers();
                    })
                    .then(function() {
                        return self.setupEventListeners();
                    })
                    .then(function() {
                        return self.setupCleanupHandlers();
                    })
                    .then(function() {
                        self.isInitialized = true;
                        console.log('✅ MCP Feedback Enhanced 應用程式初始化完成');
                        resolve();
                    })
                    .catch(function(error) {
                        console.error('❌ 應用程式初始化失敗:', error);
                        reject(error);
                    });
            } catch (error) {
                console.error('❌ 應用程式初始化異常:', error);
                reject(error);
            }
        });
    };

    /**
     * 等待國際化系統載入
     */
    FeedbackApp.prototype.waitForI18n = function() {
        return new Promise(function(resolve) {
            if (window.i18nManager) {
                window.i18nManager.init().then(resolve).catch(resolve);
            } else {
                resolve();
            }
        });
    };

    /**
     * 初始化所有管理器
     */
    FeedbackApp.prototype.initializeManagers = function() {
        const self = this;

        return new Promise(function(resolve, reject) {
            try {
                console.log('🔧 初始化管理器...');

                // 1. 初始化設定管理器
                self.settingsManager = new window.MCPFeedback.SettingsManager({
                    onSettingsChange: function(settings) {
                        self.handleSettingsChange(settings);
                    },
                    onLanguageChange: function(language) {
                        self.handleLanguageChange(language);
                    }
                });

                // 2. 載入設定
                self.settingsManager.loadSettings()
                    .then(function(settings) {
                        console.log('📋 設定載入完成:', settings);

                        // 3. 初始化 UI 管理器
                        self.uiManager = new window.MCPFeedback.UIManager({
                            currentTab: settings.activeTab,
                            layoutMode: settings.layoutMode,
                            onTabChange: function(tabName) {
                                self.handleTabChange(tabName);
                            },
                            onLayoutModeChange: function(layoutMode) {
                                self.handleLayoutModeChange(layoutMode);
                            }
                        });

                        // 4. 初始化標籤頁管理器
                        self.tabManager = new window.MCPFeedback.TabManager();

                        // 5. 初始化 WebSocket 管理器
                        self.webSocketManager = new window.MCPFeedback.WebSocketManager({
                            tabManager: self.tabManager,
                            onOpen: function() {
                                self.handleWebSocketOpen();
                            },
                            onMessage: function(data) {
                                self.handleWebSocketMessage(data);
                            },
                            onClose: function(event) {
                                self.handleWebSocketClose(event);
                            },
                            onConnectionStatusChange: function(status, text) {
                                self.uiManager.updateConnectionStatus(status, text);
                            }
                        });

                        // 6. 初始化圖片處理器
                        self.imageHandler = new window.MCPFeedback.ImageHandler({
                            imageSizeLimit: settings.imageSizeLimit,
                            enableBase64Detail: settings.enableBase64Detail,
                            layoutMode: settings.layoutMode,
                            onSettingsChange: function() {
                                self.saveImageSettings();
                            }
                        });

                        // 7. 初始化自動刷新管理器
                        self.autoRefreshManager = new window.MCPFeedback.AutoRefreshManager({
                            autoRefreshEnabled: settings.autoRefreshEnabled,
                            autoRefreshInterval: settings.autoRefreshInterval,
                            lastKnownSessionId: self.currentSessionId,
                            onSessionUpdate: function(sessionData) {
                                self.handleSessionUpdate(sessionData);
                            },
                            onSettingsChange: function() {
                                self.saveAutoRefreshSettings();
                            }
                        });

                        // 8. 應用設定到 UI
                        self.settingsManager.applyToUI();

                        // 9. 初始化各個管理器
                        self.uiManager.initTabs();
                        self.imageHandler.init();
                        self.autoRefreshManager.init();

                        // 10. 建立 WebSocket 連接
                        self.webSocketManager.connect();

                        resolve();
                    })
                    .catch(reject);
            } catch (error) {
                reject(error);
            }
        });
    };

    /**
     * 設置事件監聽器
     */
    FeedbackApp.prototype.setupEventListeners = function() {
        const self = this;

        return new Promise(function(resolve) {
            // 提交按鈕事件
            const submitButtons = [
                window.MCPFeedback.Utils.safeQuerySelector('#submitBtn'),
                window.MCPFeedback.Utils.safeQuerySelector('#combinedSubmitBtn')
            ].filter(function(btn) { return btn !== null; });

            submitButtons.forEach(function(button) {
                button.addEventListener('click', function() {
                    self.submitFeedback();
                });
            });

            // 取消按鈕事件
            const cancelButtons = [
                window.MCPFeedback.Utils.safeQuerySelector('#cancelBtn'),
                window.MCPFeedback.Utils.safeQuerySelector('#combinedCancelBtn')
            ].filter(function(btn) { return btn !== null; });

            cancelButtons.forEach(function(button) {
                button.addEventListener('click', function() {
                    self.cancelFeedback();
                });
            });

            // 命令執行事件
            const runCommandBtn = window.MCPFeedback.Utils.safeQuerySelector('#runCommandBtn');
            if (runCommandBtn) {
                runCommandBtn.addEventListener('click', function() {
                    self.runCommand();
                });
            }

            const commandInput = window.MCPFeedback.Utils.safeQuerySelector('#commandInput');
            if (commandInput) {
                commandInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        self.runCommand();
                    }
                });
            }

            // 快捷鍵
            document.addEventListener('keydown', function(e) {
                // Ctrl+Enter 提交回饋
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    e.preventDefault();
                    self.submitFeedback();
                }

                // Esc 取消
                if (e.key === 'Escape') {
                    self.cancelFeedback();
                }
            });

            // 設置設定管理器的事件監聽器
            self.settingsManager.setupEventListeners();

            console.log('✅ 事件監聽器設置完成');
            resolve();
        });
    };

    /**
     * 設置清理處理器
     */
    FeedbackApp.prototype.setupCleanupHandlers = function() {
        const self = this;

        return new Promise(function(resolve) {
            window.addEventListener('beforeunload', function() {
                self.cleanup();
            });

            console.log('✅ 清理處理器設置完成');
            resolve();
        });
    };

    /**
     * 處理設定變更
     */
    FeedbackApp.prototype.handleSettingsChange = function(settings) {
        console.log('🔧 處理設定變更:', settings);

        // 更新圖片處理器設定
        if (this.imageHandler) {
            this.imageHandler.updateSettings(settings);
        }

        // 更新自動刷新管理器設定
        if (this.autoRefreshManager) {
            this.autoRefreshManager.updateSettings(settings);
        }

        // 更新 UI 管理器佈局模式
        if (this.uiManager && settings.layoutMode) {
            this.uiManager.applyLayoutMode(settings.layoutMode);
        }
    };

    /**
     * 處理語言變更
     */
    FeedbackApp.prototype.handleLanguageChange = function(language) {
        console.log('🌐 處理語言變更:', language);

        // 更新 UI 顯示
        if (this.uiManager) {
            this.uiManager.updateStatusIndicator();
        }

        if (this.autoRefreshManager) {
            this.autoRefreshManager.updateAutoRefreshStatus();
        }
    };

    /**
     * 處理頁籤變更
     */
    FeedbackApp.prototype.handleTabChange = function(tabName) {
        console.log('📋 處理頁籤變更:', tabName);

        // 重新初始化圖片處理器（確保使用正確的佈局模式元素）
        if (this.imageHandler) {
            const layoutMode = this.settingsManager.get('layoutMode');
            this.imageHandler.reinitialize(layoutMode);
        }

        // 保存當前頁籤設定
        this.settingsManager.set('activeTab', tabName);
    };

    /**
     * 處理佈局模式變更
     */
    FeedbackApp.prototype.handleLayoutModeChange = function(layoutMode) {
        console.log('🎨 處理佈局模式變更:', layoutMode);

        // 重新初始化圖片處理器
        if (this.imageHandler) {
            this.imageHandler.reinitialize(layoutMode);
        }
    };

    /**
     * 保存圖片設定
     */
    FeedbackApp.prototype.saveImageSettings = function() {
        if (this.imageHandler && this.settingsManager) {
            this.settingsManager.setMultiple({
                imageSizeLimit: this.imageHandler.imageSizeLimit,
                enableBase64Detail: this.imageHandler.enableBase64Detail
            });
        }
    };

    /**
     * 保存自動刷新設定
     */
    FeedbackApp.prototype.saveAutoRefreshSettings = function() {
        if (this.autoRefreshManager && this.settingsManager) {
            const settings = this.autoRefreshManager.getSettings();
            this.settingsManager.setMultiple(settings);
        }
    };

    /**
     * 處理 WebSocket 開啟
     */
    FeedbackApp.prototype.handleWebSocketOpen = function() {
        console.log('🔗 WebSocket 連接已開啟');

        // 如果有待處理的提交，處理它
        if (this.pendingSubmission) {
            console.log('🔄 處理待提交的回饋');
            this.submitFeedbackInternal(this.pendingSubmission);
            this.pendingSubmission = null;
        }
    };

    /**
     * 處理 WebSocket 訊息
     */
    FeedbackApp.prototype.handleWebSocketMessage = function(data) {
        console.log('📨 處理 WebSocket 訊息:', data);

        switch (data.type) {
            case 'command_output':
                this.appendCommandOutput(data.output);
                break;
            case 'command_complete':
                this.appendCommandOutput('\n[命令完成，退出碼: ' + data.exit_code + ']\n');
                this.enableCommandInput();
                break;
            case 'command_error':
                this.appendCommandOutput('\n[錯誤: ' + data.error + ']\n');
                this.enableCommandInput();
                break;
            case 'feedback_received':
                console.log('回饋已收到');
                this.handleFeedbackReceived(data);
                break;
            case 'status_update':
                console.log('狀態更新:', data.status_info);
                this.handleStatusUpdate(data.status_info);
                break;
            case 'session_updated':
                console.log('🔄 收到會話更新訊息:', data.session_info);
                this.handleSessionUpdated(data);
                break;
        }
    };

    /**
     * 處理 WebSocket 關閉
     */
    FeedbackApp.prototype.handleWebSocketClose = function(event) {
        console.log('🔗 WebSocket 連接已關閉');

        // 重置回饋狀態，避免卡在處理狀態
        if (this.uiManager && this.uiManager.getFeedbackState() === window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_PROCESSING) {
            console.log('🔄 WebSocket 斷開，重置處理狀態');
            this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING);
        }
    };

    /**
     * 處理回饋接收
     */
    FeedbackApp.prototype.handleFeedbackReceived = function(data) {
        // 使用 UI 管理器設置狀態
        this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_SUBMITTED);
        this.uiManager.setLastSubmissionTime(Date.now());

        // 顯示成功訊息
        window.MCPFeedback.Utils.showMessage(data.message || '回饋提交成功！', window.MCPFeedback.Utils.CONSTANTS.MESSAGE_SUCCESS);

        // 更新 AI 摘要區域顯示「已送出反饋」狀態
        this.updateSummaryStatus('已送出反饋，等待下次 MCP 調用...');

        console.log('反饋已提交，頁面保持開啟狀態');
    };

    /**
     * 處理會話更新
     */
    FeedbackApp.prototype.handleSessionUpdated = function(data) {
        console.log('🔄 處理會話更新:', data.session_info);

        // 顯示更新通知
        window.MCPFeedback.Utils.showMessage(data.message || '會話已更新，正在局部更新內容...', window.MCPFeedback.Utils.CONSTANTS.MESSAGE_SUCCESS);

        // 更新會話信息
        if (data.session_info) {
            const newSessionId = data.session_info.session_id;
            console.log('📋 會話 ID 更新: ' + this.currentSessionId + ' -> ' + newSessionId);

            // 重置回饋狀態為等待新回饋
            this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING, newSessionId);
            this.currentSessionId = newSessionId;

            // 更新自動刷新管理器的會話 ID
            if (this.autoRefreshManager) {
                this.autoRefreshManager.setLastKnownSessionId(newSessionId);
            }

            // 更新頁面標題
            if (data.session_info.project_directory) {
                const projectName = data.session_info.project_directory.split(/[/\\]/).pop();
                document.title = 'MCP Feedback - ' + projectName;
            }

            // 使用局部更新替代整頁刷新
            this.refreshPageContent();
        } else {
            console.log('⚠️ 會話更新沒有包含會話信息，僅重置狀態');
            this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING);
        }

        console.log('✅ 會話更新處理完成');
    };

    /**
     * 處理狀態更新
     */
    FeedbackApp.prototype.handleStatusUpdate = function(statusInfo) {
        console.log('處理狀態更新:', statusInfo);

        // 更新頁面標題顯示會話信息
        if (statusInfo.project_directory) {
            const projectName = statusInfo.project_directory.split(/[/\\]/).pop();
            document.title = 'MCP Feedback - ' + projectName;
        }

        // 提取會話 ID
        const sessionId = statusInfo.session_id || this.currentSessionId;

        // 根據狀態更新 UI
        switch (statusInfo.status) {
            case 'feedback_submitted':
                this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_SUBMITTED, sessionId);
                this.updateSummaryStatus('已送出反饋，等待下次 MCP 調用...');
                break;

            case 'active':
            case 'waiting':
                // 檢查是否是新會話
                if (sessionId && sessionId !== this.currentSessionId) {
                    this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING, sessionId);
                } else if (this.uiManager.getFeedbackState() !== window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_SUBMITTED) {
                    this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING, sessionId);
                }

                if (statusInfo.status === 'waiting') {
                    this.updateSummaryStatus('等待用戶回饋...');
                }
                break;
        }
    };

    /**
     * 提交回饋
     */
    FeedbackApp.prototype.submitFeedback = function() {
        console.log('📤 嘗試提交回饋...');

        // 檢查是否可以提交回饋
        if (!this.canSubmitFeedback()) {
            console.log('⚠️ 無法提交回饋');
            this.handleSubmitError();
            return;
        }

        // 收集回饋數據並提交
        const feedbackData = this.collectFeedbackData();
        if (!feedbackData) {
            return;
        }

        this.submitFeedbackInternal(feedbackData);
    };

    /**
     * 檢查是否可以提交回饋
     */
    FeedbackApp.prototype.canSubmitFeedback = function() {
        return this.webSocketManager &&
               this.webSocketManager.isReady() &&
               this.uiManager &&
               this.uiManager.getFeedbackState() === window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING;
    };

    /**
     * 處理提交錯誤
     */
    FeedbackApp.prototype.handleSubmitError = function() {
        const feedbackState = this.uiManager ? this.uiManager.getFeedbackState() : null;

        if (feedbackState === window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_SUBMITTED) {
            window.MCPFeedback.Utils.showMessage('回饋已提交，請等待下次 MCP 調用', window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING);
        } else if (feedbackState === window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_PROCESSING) {
            window.MCPFeedback.Utils.showMessage('正在處理中，請稍候', window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING);
        } else if (!this.webSocketManager || !this.webSocketManager.isReady()) {
            // 收集回饋數據，等待連接就緒後提交
            const feedbackData = this.collectFeedbackData();
            if (feedbackData) {
                this.pendingSubmission = feedbackData;
                window.MCPFeedback.Utils.showMessage('WebSocket 連接中，回饋將在連接就緒後自動提交...', window.MCPFeedback.Utils.CONSTANTS.MESSAGE_INFO);
            }
        } else {
            window.MCPFeedback.Utils.showMessage('當前狀態不允許提交: ' + feedbackState, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING);
        }
    };

    /**
     * 收集回饋數據
     */
    FeedbackApp.prototype.collectFeedbackData = function() {
        // 根據當前佈局模式獲取回饋內容
        let feedback = '';
        const layoutMode = this.settingsManager ? this.settingsManager.get('layoutMode') : 'combined-vertical';

        if (layoutMode.startsWith('combined')) {
            const combinedFeedbackInput = window.MCPFeedback.Utils.safeQuerySelector('#combinedFeedbackText');
            feedback = combinedFeedbackInput ? combinedFeedbackInput.value.trim() : '';
        } else {
            const feedbackInput = window.MCPFeedback.Utils.safeQuerySelector('#feedbackText');
            feedback = feedbackInput ? feedbackInput.value.trim() : '';
        }

        const images = this.imageHandler ? this.imageHandler.getImages() : [];

        if (!feedback && images.length === 0) {
            window.MCPFeedback.Utils.showMessage('請提供回饋文字或上傳圖片', window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING);
            return null;
        }

        return {
            feedback: feedback,
            images: images,
            settings: {
                image_size_limit: this.imageHandler ? this.imageHandler.imageSizeLimit : 0,
                enable_base64_detail: this.imageHandler ? this.imageHandler.enableBase64Detail : false
            }
        };
    };

    /**
     * 內部提交回饋方法
     */
    FeedbackApp.prototype.submitFeedbackInternal = function(feedbackData) {
        console.log('📤 內部提交回饋...');

        // 設置處理狀態
        if (this.uiManager) {
            this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_PROCESSING);
        }

        try {
            // 發送回饋
            const success = this.webSocketManager.send({
                type: 'submit_feedback',
                feedback: feedbackData.feedback,
                images: feedbackData.images,
                settings: feedbackData.settings
            });

            if (success) {
                // 清空表單
                this.clearFeedback();
                console.log('📤 回饋已發送，等待服務器確認...');
            } else {
                throw new Error('WebSocket 發送失敗');
            }

        } catch (error) {
            console.error('❌ 發送回饋失敗:', error);
            window.MCPFeedback.Utils.showMessage('發送失敗，請重試', window.MCPFeedback.Utils.CONSTANTS.MESSAGE_ERROR);

            // 恢復到等待狀態
            if (this.uiManager) {
                this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING);
            }
        }
    };

    /**
     * 清空回饋內容
     */
    FeedbackApp.prototype.clearFeedback = function() {
        console.log('🧹 清空回饋內容...');

        // 使用 UI 管理器重置表單
        if (this.uiManager) {
            this.uiManager.resetFeedbackForm();
        }

        // 清空圖片數據
        if (this.imageHandler) {
            this.imageHandler.clearImages();
        }

        console.log('✅ 回饋內容清空完成');
    };

    /**
     * 取消回饋
     */
    FeedbackApp.prototype.cancelFeedback = function() {
        console.log('❌ 取消回饋');
        this.clearFeedback();
    };

    /**
     * 執行命令
     */
    FeedbackApp.prototype.runCommand = function() {
        const commandInput = window.MCPFeedback.Utils.safeQuerySelector('#commandInput');
        const command = commandInput ? commandInput.value.trim() : '';

        if (!command) {
            this.appendCommandOutput('⚠️ 請輸入命令\n');
            return;
        }

        if (!this.webSocketManager || !this.webSocketManager.isConnected) {
            this.appendCommandOutput('❌ WebSocket 未連接，無法執行命令\n');
            return;
        }

        // 顯示執行的命令
        this.appendCommandOutput('$ ' + command + '\n');

        // 發送命令
        try {
            const success = this.webSocketManager.send({
                type: 'run_command',
                command: command
            });

            if (success) {
                // 清空輸入框
                commandInput.value = '';
                this.appendCommandOutput('[正在執行...]\n');
            } else {
                this.appendCommandOutput('❌ 發送命令失敗\n');
            }

        } catch (error) {
            this.appendCommandOutput('❌ 發送命令失敗: ' + error.message + '\n');
        }
    };

    /**
     * 添加命令輸出
     */
    FeedbackApp.prototype.appendCommandOutput = function(output) {
        const commandOutput = window.MCPFeedback.Utils.safeQuerySelector('#commandOutput');
        if (commandOutput) {
            commandOutput.textContent += output;
            commandOutput.scrollTop = commandOutput.scrollHeight;
        }
    };

    /**
     * 啟用命令輸入
     */
    FeedbackApp.prototype.enableCommandInput = function() {
        const commandInput = window.MCPFeedback.Utils.safeQuerySelector('#commandInput');
        const runCommandBtn = window.MCPFeedback.Utils.safeQuerySelector('#runCommandBtn');

        if (commandInput) commandInput.disabled = false;
        if (runCommandBtn) {
            runCommandBtn.disabled = false;
            runCommandBtn.textContent = '▶️ 執行';
        }
    };

    /**
     * 更新摘要狀態
     */
    FeedbackApp.prototype.updateSummaryStatus = function(message) {
        const summaryElements = document.querySelectorAll('.ai-summary-content');
        summaryElements.forEach(function(element) {
            element.innerHTML = '<div style="padding: 16px; background: var(--success-color); color: white; border-radius: 6px; text-align: center;">✅ ' + message + '</div>';
        });
    };

    /**
     * 處理會話更新（來自自動刷新）
     */
    FeedbackApp.prototype.handleSessionUpdate = function(sessionData) {
        console.log('🔄 處理自動檢測到的會話更新:', sessionData);

        // 更新當前會話 ID
        this.currentSessionId = sessionData.session_id;

        // 重置回饋狀態
        if (this.uiManager) {
            this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING, sessionData.session_id);
        }

        // 局部更新頁面內容
        this.refreshPageContent();
    };

    /**
     * 刷新頁面內容
     */
    FeedbackApp.prototype.refreshPageContent = function() {
        console.log('🔄 局部更新頁面內容...');

        const self = this;

        fetch('/api/current-session')
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('API 請求失敗: ' + response.status);
                }
                return response.json();
            })
            .then(function(sessionData) {
                console.log('📥 獲取到最新會話資料:', sessionData);

                // 重置回饋狀態
                if (sessionData.session_id && self.uiManager) {
                    self.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING, sessionData.session_id);
                }

                // 更新 AI 摘要內容
                if (self.uiManager) {
                    self.uiManager.updateAISummaryContent(sessionData.summary);
                    self.uiManager.resetFeedbackForm();
                    self.uiManager.updateStatusIndicator();
                }

                // 更新頁面標題
                if (sessionData.project_directory) {
                    const projectName = sessionData.project_directory.split(/[/\\]/).pop();
                    document.title = 'MCP Feedback - ' + projectName;
                }

                console.log('✅ 局部更新完成');
            })
            .catch(function(error) {
                console.error('❌ 局部更新失敗:', error);
                window.MCPFeedback.Utils.showMessage('更新內容失敗，請手動刷新頁面以查看新的 AI 工作摘要', window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING);
            });
    };

    /**
     * 清理資源
     */
    FeedbackApp.prototype.cleanup = function() {
        console.log('🧹 清理應用程式資源...');

        if (this.tabManager) {
            this.tabManager.cleanup();
        }

        if (this.webSocketManager) {
            this.webSocketManager.close();
        }

        if (this.imageHandler) {
            this.imageHandler.cleanup();
        }

        if (this.autoRefreshManager) {
            this.autoRefreshManager.cleanup();
        }

        console.log('✅ 應用程式資源清理完成');
    };

    // 將 FeedbackApp 加入命名空間
    window.MCPFeedback.FeedbackApp = FeedbackApp;

    console.log('✅ FeedbackApp 主模組載入完成');

})();