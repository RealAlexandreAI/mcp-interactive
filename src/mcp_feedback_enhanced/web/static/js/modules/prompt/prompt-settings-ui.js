/**
 * MCP Feedback Enhanced - 提示詞設定 UI 模組
 * =========================================
 * 
 * 處理設定頁籤中的提示詞管理介面
 */

(function() {
    'use strict';

    // 確保命名空間存在
    window.MCPFeedback = window.MCPFeedback || {};
    window.MCPFeedback.Prompt = window.MCPFeedback.Prompt || {};

    const Utils = window.MCPFeedback.Utils;

    /**
     * 提示詞設定 UI 管理器
     */
    function PromptSettingsUI(options) {
        options = options || {};

        // 依賴注入
        this.promptManager = options.promptManager || null;
        this.promptModal = options.promptModal || null;

        // UI 元素
        this.container = null;
        this.promptList = null;
        this.addButton = null;

        // 狀態
        this.isInitialized = false;

        console.log('🎨 PromptSettingsUI 初始化完成');
    }

    /**
     * 初始化設定 UI
     */
    PromptSettingsUI.prototype.init = function(containerSelector) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            console.error('❌ 找不到提示詞設定容器:', containerSelector);
            return false;
        }

        // 創建 UI 結構
        this.createUI();

        // 設置事件監聽器
        this.setupEventListeners();

        // 載入提示詞列表
        this.refreshPromptList();

        this.isInitialized = true;
        console.log('✅ PromptSettingsUI 初始化完成');
        return true;
    };

    /**
     * 創建 UI 結構
     */
    PromptSettingsUI.prototype.createUI = function() {
        const html = `
            <div class="prompt-management-section">
                <div class="prompt-management-header">
                    <h4 class="prompt-management-title" data-i18n="prompts.management.title">
                        📝 常用提示詞管理
                    </h4>
                    <button type="button" class="btn btn-primary prompt-add-btn" id="promptAddBtn">
                        <span data-i18n="prompts.management.addNew">新增提示詞</span>
                    </button>
                </div>
                <div class="prompt-management-description" data-i18n="prompts.management.description">
                    管理您的常用提示詞模板，可在回饋輸入時快速選用
                </div>
                <div class="prompt-settings-list" id="promptSettingsList">
                    <!-- 提示詞列表將在這裡動態生成 -->
                </div>
            </div>
        `;

        this.container.insertAdjacentHTML('beforeend', html);

        // 獲取 UI 元素引用
        this.promptList = this.container.querySelector('#promptSettingsList');
        this.addButton = this.container.querySelector('#promptAddBtn');
    };

    /**
     * 設置事件監聽器
     */
    PromptSettingsUI.prototype.setupEventListeners = function() {
        const self = this;

        // 新增按鈕事件
        if (this.addButton) {
            this.addButton.addEventListener('click', function() {
                self.handleAddPrompt();
            });
        }

        // 設置提示詞管理器回調
        if (this.promptManager) {
            this.promptManager.addPromptsChangeCallback(function(prompts) {
                console.log('🎨 提示詞列表變更，重新渲染 UI');
                self.refreshPromptList();
            });
        }

        // 設置彈窗回調
        if (this.promptModal) {
            this.promptModal.onSave = function(promptData, type) {
                self.handlePromptSave(promptData, type);
            };
        }
    };

    /**
     * 刷新提示詞列表
     */
    PromptSettingsUI.prototype.refreshPromptList = function() {
        if (!this.promptList || !this.promptManager) {
            return;
        }

        const prompts = this.promptManager.getAllPrompts();
        
        if (prompts.length === 0) {
            this.promptList.innerHTML = this.createEmptyStateHTML();
        } else {
            this.promptList.innerHTML = prompts.map(prompt => 
                this.createPromptItemHTML(prompt)
            ).join('');
            
            // 設置項目事件監聽器
            this.setupPromptItemEvents();
        }

        // 更新翻譯
        this.updateTranslations();
    };

    /**
     * 創建空狀態 HTML
     */
    PromptSettingsUI.prototype.createEmptyStateHTML = function() {
        return `
            <div class="empty-state">
                <div style="font-size: 48px; margin-bottom: 12px;">📝</div>
                <div data-i18n="prompts.management.emptyState">
                    尚未建立任何常用提示詞
                </div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 8px;" data-i18n="prompts.management.emptyHint">
                    點擊上方「新增提示詞」按鈕開始建立您的第一個提示詞模板
                </div>
            </div>
        `;
    };

    /**
     * 創建提示詞項目 HTML
     */
    PromptSettingsUI.prototype.createPromptItemHTML = function(prompt) {
        const createdDate = this.formatDate(prompt.createdAt);
        const lastUsedDate = prompt.lastUsedAt ? this.formatDate(prompt.lastUsedAt) : null;
        const truncatedContent = this.truncateText(prompt.content, 80);

        return `
            <div class="prompt-settings-item" data-prompt-id="${prompt.id}">
                <div class="prompt-settings-info">
                    <div class="prompt-settings-name">${Utils.escapeHtml(prompt.name)}</div>
                    <div class="prompt-settings-content">${Utils.escapeHtml(truncatedContent)}</div>
                    <div class="prompt-settings-meta">
                        <span data-i18n="prompts.management.created">建立於</span>: ${createdDate}
                        ${lastUsedDate ? `| <span data-i18n="prompts.management.lastUsed">最近使用</span>: ${lastUsedDate}` : ''}
                    </div>
                </div>
                <div class="prompt-settings-actions">
                    <button type="button" class="prompt-action-btn edit-btn" data-prompt-id="${prompt.id}" data-i18n="prompts.management.edit">
                        編輯
                    </button>
                    <button type="button" class="prompt-action-btn delete-btn delete" data-prompt-id="${prompt.id}" data-i18n="prompts.management.delete">
                        刪除
                    </button>
                </div>
            </div>
        `;
    };

    /**
     * 設置提示詞項目事件監聽器
     */
    PromptSettingsUI.prototype.setupPromptItemEvents = function() {
        const self = this;

        // 編輯按鈕事件
        const editButtons = this.promptList.querySelectorAll('.edit-btn');
        editButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                const promptId = button.getAttribute('data-prompt-id');
                self.handleEditPrompt(promptId);
            });
        });

        // 刪除按鈕事件
        const deleteButtons = this.promptList.querySelectorAll('.delete-btn');
        deleteButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                const promptId = button.getAttribute('data-prompt-id');
                self.handleDeletePrompt(promptId);
            });
        });
    };

    /**
     * 處理新增提示詞
     */
    PromptSettingsUI.prototype.handleAddPrompt = function() {
        if (!this.promptModal) {
            console.error('❌ PromptModal 未設定');
            return;
        }

        this.promptModal.showAddModal();
    };

    /**
     * 處理編輯提示詞
     */
    PromptSettingsUI.prototype.handleEditPrompt = function(promptId) {
        if (!this.promptManager || !this.promptModal) {
            console.error('❌ PromptManager 或 PromptModal 未設定');
            return;
        }

        const prompt = this.promptManager.getPromptById(promptId);
        if (!prompt) {
            this.showError(this.t('prompts.management.notFound', '找不到指定的提示詞'));
            return;
        }

        this.promptModal.showEditModal(prompt);
    };

    /**
     * 處理刪除提示詞
     */
    PromptSettingsUI.prototype.handleDeletePrompt = function(promptId) {
        if (!this.promptManager) {
            console.error('❌ PromptManager 未設定');
            return;
        }

        const prompt = this.promptManager.getPromptById(promptId);
        if (!prompt) {
            this.showError(this.t('prompts.management.notFound', '找不到指定的提示詞'));
            return;
        }

        const confirmMessage = this.t('prompts.management.confirmDelete', '確定要刪除此提示詞嗎？') + 
                              '\n\n' + prompt.name;

        if (confirm(confirmMessage)) {
            try {
                this.promptManager.deletePrompt(promptId);
                this.showSuccess(this.t('prompts.management.deleteSuccess', '提示詞已刪除'));
            } catch (error) {
                this.showError(error.message);
            }
        }
    };

    /**
     * 處理提示詞保存
     */
    PromptSettingsUI.prototype.handlePromptSave = function(promptData, type) {
        if (!this.promptManager) {
            console.error('❌ PromptManager 未設定');
            return;
        }

        try {
            if (type === 'add') {
                this.promptManager.addPrompt(promptData.name, promptData.content);
                this.showSuccess(this.t('prompts.management.addSuccess', '提示詞已新增'));
            } else if (type === 'edit') {
                this.promptManager.updatePrompt(promptData.id, promptData.name, promptData.content);
                this.showSuccess(this.t('prompts.management.updateSuccess', '提示詞已更新'));
            }
        } catch (error) {
            throw error; // 重新拋出錯誤，讓彈窗處理
        }
    };

    /**
     * 更新翻譯
     */
    PromptSettingsUI.prototype.updateTranslations = function() {
        if (window.i18nManager && typeof window.i18nManager.applyTranslations === 'function') {
            window.i18nManager.applyTranslations();
        }
    };

    /**
     * 顯示成功訊息
     */
    PromptSettingsUI.prototype.showSuccess = function(message) {
        if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
            window.MCPFeedback.Utils.showMessage(message, 'success');
        } else {
            console.log('✅', message);
        }
    };

    /**
     * 顯示錯誤訊息
     */
    PromptSettingsUI.prototype.showError = function(message) {
        if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
            window.MCPFeedback.Utils.showMessage(message, 'error');
        } else {
            alert(message);
        }
    };

    /**
     * 翻譯函數
     */
    PromptSettingsUI.prototype.t = function(key, fallback) {
        if (window.i18nManager && typeof window.i18nManager.t === 'function') {
            return window.i18nManager.t(key, fallback);
        }
        return fallback || key;
    };

    /**
     * 格式化日期
     */
    PromptSettingsUI.prototype.formatDate = function(dateString) {
        if (!dateString) return '';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        } catch (error) {
            return dateString;
        }
    };

    /**
     * 截斷文字
     */
    PromptSettingsUI.prototype.truncateText = function(text, maxLength) {
        if (!text || text.length <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength) + '...';
    };

    // 將 PromptSettingsUI 加入命名空間
    window.MCPFeedback.Prompt.PromptSettingsUI = PromptSettingsUI;

    console.log('✅ PromptSettingsUI 模組載入完成');

})();
