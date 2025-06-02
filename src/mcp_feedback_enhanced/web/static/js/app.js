/**
 * 主要前端應用
 * ============
 * 
 * 處理 WebSocket 通信、分頁切換、圖片上傳、命令執行等功能
 */

class FeedbackApp {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.websocket = null;
        this.images = [];
        this.isConnected = false;
        this.combinedMode = false;
        this.autoClose = true; // 預設開啟
        
        this.init();
    }

    async init() {
        // 等待國際化系統加載完成
        if (window.i18nManager) {
            await window.i18nManager.init();
        }

        // 處理動態摘要內容
        this.processDynamicSummaryContent();

        // 設置 WebSocket 連接
        this.setupWebSocket();
        
        // 設置事件監聽器
        this.setupEventListeners();
        
        // 初始化分頁系統
        this.setupTabs();
        
        // 設置圖片上傳
        this.setupImageUpload();
        
        // 設置鍵盤快捷鍵
        this.setupKeyboardShortcuts();
        
        // 載入設定
        this.loadSettings();
        
        // 初始化命令終端
        this.initCommandTerminal();
        
        // 確保合併模式狀態正確
        this.applyCombinedModeState();
        
        console.log('FeedbackApp 初始化完成');
    }

    processDynamicSummaryContent() {
        // 處理所有帶有 data-dynamic-content 屬性的元素
        const dynamicElements = document.querySelectorAll('[data-dynamic-content="aiSummary"]');
        
        dynamicElements.forEach(element => {
            const currentContent = element.textContent || element.innerHTML;
            
            // 檢查是否為測試摘要
            if (this.isTestSummary(currentContent)) {
                // 如果是測試摘要，使用翻譯系統的內容
                if (window.i18nManager) {
                    const translatedSummary = window.i18nManager.t('dynamic.aiSummary');
                    if (translatedSummary && translatedSummary !== 'dynamic.aiSummary') {
                        element.textContent = translatedSummary.trim();
                        console.log('已更新測試摘要為:', window.i18nManager.currentLanguage);
                    }
                }
            } else {
                // 如果不是測試摘要，清理原有內容的前導和尾隨空白
                element.textContent = currentContent.trim();
            }
        });
    }

    isTestSummary(content) {
        // 簡化的測試摘要檢測邏輯 - 檢查是否包含任何測試相關關鍵詞
        const testKeywords = [
            // 標題關鍵詞（任何語言版本）
            '測試 Web UI 功能', 'Test Web UI Functionality', '测试 Web UI 功能',
            '圖片預覽和視窗調整測試', 'Image Preview and Window Adjustment Test', '图片预览和窗口调整测试',
            
            // 功能測試項目關鍵詞
            '功能測試項目', 'Test Items', '功能测试项目',
            
            // 特殊標記
            '🎯 **功能測試項目', '🎯 **Test Items', '🎯 **功能测试项目',
            '📋 測試步驟', '📋 Test Steps', '📋 测试步骤',
            
            // 具體測試功能
            'WebSocket 即時通訊', 'WebSocket real-time communication', 'WebSocket 即时通讯',
            '智能 Ctrl+V', 'Smart Ctrl+V', '智能 Ctrl+V',
            
            // 測試提示詞
            '請測試這些功能', 'Please test these features', '请测试这些功能'
        ];
        
        // 只要包含任何一個測試關鍵詞就認為是測試摘要
        return testKeywords.some(keyword => content.includes(keyword));
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

        try {
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                this.isConnected = true;
                console.log('WebSocket 連接已建立');
                this.updateConnectionStatus(true);
            };

            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.websocket.onclose = () => {
                this.isConnected = false;
                console.log('WebSocket 連接已關閉');
                this.updateConnectionStatus(false);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket 錯誤:', error);
                this.updateConnectionStatus(false);
            };

        } catch (error) {
            console.error('WebSocket 連接失敗:', error);
            this.updateConnectionStatus(false);
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'command_output':
                this.appendCommandOutput(data.output);
                break;
            case 'command_complete':
                this.appendCommandOutput(`\n[命令完成，退出碼: ${data.exit_code}]\n`);
                this.enableCommandInput();
                break;
            case 'command_error':
                this.appendCommandOutput(`\n[錯誤: ${data.error}]\n`);
                this.enableCommandInput();
                break;
            case 'feedback_received':
                console.log('回饋已收到');
                // 顯示成功訊息
                this.showSuccessMessage();
                break;
            default:
                console.log('未知的 WebSocket 消息:', data);
        }
    }

    showSuccessMessage() {
        // 創建成功訊息提示
        const message = document.createElement('div');
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--success-color);
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            font-weight: 500;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease-out;
        `;
        message.textContent = '✅ 回饋提交成功！';
        
        // 添加動畫樣式
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(message);
        
        // 3秒後移除訊息
        setTimeout(() => {
            if (message.parentNode) {
                message.remove();
            }
        }, 3000);
    }

    updateConnectionStatus(connected) {
        // 更新連接狀態指示器
        const elements = document.querySelectorAll('.connection-indicator');
        elements.forEach(el => {
            el.textContent = connected ? '✅ 已連接' : '❌ 未連接';
            el.className = `connection-indicator ${connected ? 'connected' : 'disconnected'}`;
        });

        // 更新命令執行按鈕狀態
        const runCommandBtn = document.getElementById('runCommandBtn');
        if (runCommandBtn) {
            runCommandBtn.disabled = !connected;
            runCommandBtn.textContent = connected ? '▶️ 執行' : '❌ 未連接';
        }
    }

    setupEventListeners() {
        // 提交回饋按鈕
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitFeedback());
        }

        // 取消按鈕
        const cancelBtn = document.getElementById('cancelBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.cancelFeedback());
        }

        // 執行命令按鈕
        const runCommandBtn = document.getElementById('runCommandBtn');
        if (runCommandBtn) {
            runCommandBtn.addEventListener('click', () => this.runCommand());
        }

        // 命令輸入框 Enter 事件 - 修正為使用新的 input 元素
        const commandInput = document.getElementById('commandInput');
        if (commandInput) {
            commandInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.runCommand();
                }
            });
        }

        // 設定切換
        this.setupSettingsListeners();
    }

    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');

                // 移除所有活躍狀態
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));

                // 添加活躍狀態
                button.classList.add('active');
                const targetContent = document.getElementById(`tab-${targetTab}`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }

                // 保存當前分頁
                localStorage.setItem('activeTab', targetTab);
            });
        });

        // 恢復上次的活躍分頁
        const savedTab = localStorage.getItem('activeTab');
        if (savedTab) {
            const savedButton = document.querySelector(`[data-tab="${savedTab}"]`);
            if (savedButton) {
                savedButton.click();
            }
        }
    }

    setupImageUpload() {
        const imageUploadArea = document.getElementById('imageUploadArea');
        const imageInput = document.getElementById('imageInput');
        const imagePreviewContainer = document.getElementById('imagePreviewContainer');

        if (!imageUploadArea || !imageInput || !imagePreviewContainer) {
            return;
        }

        // 原始分頁的圖片上傳
        this.setupImageUploadForArea(imageUploadArea, imageInput, imagePreviewContainer);

        // 合併模式的圖片上傳
        const combinedImageUploadArea = document.getElementById('combinedImageUploadArea');
        const combinedImageInput = document.getElementById('combinedImageInput');
        const combinedImagePreviewContainer = document.getElementById('combinedImagePreviewContainer');

        if (combinedImageUploadArea && combinedImageInput && combinedImagePreviewContainer) {
            this.setupImageUploadForArea(combinedImageUploadArea, combinedImageInput, combinedImagePreviewContainer);
        }
    }

    setupImageUploadForArea(uploadArea, input, previewContainer) {
        // 點擊上傳區域
        uploadArea.addEventListener('click', () => {
            input.click();
        });

        // 文件選擇
        input.addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files);
        });

        // 拖放事件
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFileSelection(e.dataTransfer.files);
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Enter 或 Cmd+Enter 提交回饋
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.submitFeedback();
            }

            // ESC 取消
            if (e.key === 'Escape') {
                this.cancelFeedback();
            }
        });

        // 設置 Ctrl+V 貼上圖片監聽器
        this.setupPasteListener();
    }

    setupPasteListener() {
        document.addEventListener('paste', (e) => {
            // 檢查是否在回饋文字框中
            const feedbackText = document.getElementById('feedbackText');
            const combinedFeedbackText = document.getElementById('combinedFeedbackText');
            
            const isInFeedbackInput = document.activeElement === feedbackText || 
                                    document.activeElement === combinedFeedbackText;
            
            if (isInFeedbackInput) {
                console.log('偵測到在回饋輸入框中貼上');
                this.handlePasteEvent(e);
            }
        });
    }

    handlePasteEvent(e) {
        const clipboardData = e.clipboardData || window.clipboardData;
        if (!clipboardData) return;

        const items = clipboardData.items;
        let hasImages = false;

        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            
            if (item.type.indexOf('image') !== -1) {
                hasImages = true;
                e.preventDefault(); // 防止文字也被貼上
                
                const file = item.getAsFile();
                if (file) {
                    console.log('從剪貼簿貼上圖片:', file.name, file.type);
                    this.addImage(file);
                }
            }
        }

        if (hasImages) {
            console.log('已處理剪貼簿圖片');
        }
    }

    setupSettingsListeners() {
        // 合併模式開關
        const combinedModeToggle = document.getElementById('combinedModeToggle');
        if (combinedModeToggle) {
            combinedModeToggle.addEventListener('click', () => {
                this.toggleCombinedMode();
            });
        }

        // 自動關閉開關
        const autoCloseToggle = document.getElementById('autoCloseToggle');
        if (autoCloseToggle) {
            autoCloseToggle.addEventListener('click', () => {
                this.toggleAutoClose();
            });
        }

        // 語言選擇器
        const languageOptions = document.querySelectorAll('.language-option');
        languageOptions.forEach(option => {
            option.addEventListener('click', () => {
                const language = option.getAttribute('data-lang');
                this.setLanguage(language);
            });
        });
    }

    setLanguage(language) {
        // 更新語言選擇器的活躍狀態
        const languageOptions = document.querySelectorAll('.language-option');
        languageOptions.forEach(option => {
            option.classList.remove('active');
            if (option.getAttribute('data-lang') === language) {
                option.classList.add('active');
            }
        });

        // 調用國際化管理器
        if (window.i18nManager) {
            window.i18nManager.setLanguage(language);
            
            // 語言切換後重新處理動態摘要內容
            setTimeout(() => {
                console.log('語言切換到:', language, '- 重新處理動態內容');
                this.processDynamicSummaryContent();
            }, 200); // 增加延遲時間確保翻譯加載完成
        }
    }

    handleFileSelection(files) {
        for (let file of files) {
            if (file.type.startsWith('image/')) {
                this.addImage(file);
            }
        }
    }

    addImage(file) {
        if (file.size > 1024 * 1024) { // 1MB
            alert('圖片大小不能超過 1MB');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const imageData = {
                name: file.name,
                data: e.target.result.split(',')[1], // 移除 data:image/...;base64, 前綴
                size: file.size,
                type: file.type,
                preview: e.target.result
            };

            this.images.push(imageData);
            this.updateImagePreview();
        };
        reader.readAsDataURL(file);
    }

    updateImagePreview() {
        // 更新原始分頁的圖片預覽
        this.updateImagePreviewForContainer('imagePreviewContainer', 'imageUploadArea');

        // 更新合併模式的圖片預覽
        this.updateImagePreviewForContainer('combinedImagePreviewContainer', 'combinedImageUploadArea');
    }

    updateImagePreviewForContainer(containerId, uploadAreaId) {
        const container = document.getElementById(containerId);
        const uploadArea = document.getElementById(uploadAreaId);
        if (!container || !uploadArea) return;

        container.innerHTML = '';

        // 更新上傳區域的樣式
        if (this.images.length > 0) {
            uploadArea.classList.add('has-images');
        } else {
            uploadArea.classList.remove('has-images');
        }

        this.images.forEach((image, index) => {
            const preview = document.createElement('div');
            preview.className = 'image-preview';
            preview.innerHTML = `
                <img src="${image.preview}" alt="${image.name}">
                <button class="image-remove" onclick="feedbackApp.removeImage(${index})">×</button>
            `;
            container.appendChild(preview);
        });
    }

    removeImage(index) {
        this.images.splice(index, 1);
        this.updateImagePreview();
    }

    runCommand() {
        const commandInput = document.getElementById('commandInput');
        const command = commandInput?.value.trim();

        if (!command) {
            this.appendCommandOutput('⚠️ 請輸入命令\n');
            return;
        }

        if (!this.isConnected) {
            this.appendCommandOutput('❌ WebSocket 未連接，無法執行命令\n');
            return;
        }

        // 禁用輸入和按鈕
        this.disableCommandInput();

        // 顯示執行的命令，使用 terminal 風格
        this.appendCommandOutput(`$ ${command}\n`);

        // 發送命令
        try {
            this.websocket.send(JSON.stringify({
                type: 'run_command',
                command: command
            }));

            // 清空輸入框
            commandInput.value = '';

            // 顯示正在執行的狀態
            this.appendCommandOutput('[正在執行...]\n');

        } catch (error) {
            this.appendCommandOutput(`❌ 發送命令失敗: ${error.message}\n`);
            this.enableCommandInput();
        }
    }

    disableCommandInput() {
        const commandInput = document.getElementById('commandInput');
        const runCommandBtn = document.getElementById('runCommandBtn');

        if (commandInput) {
            commandInput.disabled = true;
            commandInput.style.opacity = '0.6';
        }
        if (runCommandBtn) {
            runCommandBtn.disabled = true;
            runCommandBtn.textContent = '⏳ 執行中...';
        }
    }

    enableCommandInput() {
        const commandInput = document.getElementById('commandInput');
        const runCommandBtn = document.getElementById('runCommandBtn');

        if (commandInput) {
            commandInput.disabled = false;
            commandInput.style.opacity = '1';
            commandInput.focus(); // 自動聚焦到輸入框
        }
        if (runCommandBtn) {
            runCommandBtn.disabled = false;
            runCommandBtn.textContent = '▶️ 執行';
        }
    }

    appendCommandOutput(text) {
        const output = document.getElementById('commandOutput');
        if (output) {
            output.textContent += text;
            output.scrollTop = output.scrollHeight;

            // 添加時間戳（可選）
            if (text.includes('[命令完成') || text.includes('[錯誤:')) {
                const timestamp = new Date().toLocaleTimeString();
                output.textContent += `[${timestamp}]\n`;
            }
        }
    }

    submitFeedback() {
        let feedbackText;

        // 根據當前模式選擇正確的輸入框
        if (this.combinedMode) {
            const combinedFeedbackInput = document.getElementById('combinedFeedbackText');
            feedbackText = combinedFeedbackInput?.value.trim() || '';
        } else {
            const feedbackInput = document.getElementById('feedbackText');
            feedbackText = feedbackInput?.value.trim() || '';
        }

        const feedback = feedbackText;

        if (!feedback && this.images.length === 0) {
            alert('請提供回饋文字或上傳圖片');
            return;
        }

        if (!this.isConnected) {
            alert('WebSocket 未連接');
            return;
        }

        // 準備圖片數據
        const imageData = this.images.map(img => ({
            name: img.name,
            data: img.data,
            size: img.size,
            type: img.type
        }));

        // 發送回饋
        this.websocket.send(JSON.stringify({
            type: 'submit_feedback',
            feedback: feedback,
            images: imageData
        }));

        console.log('回饋已提交');
        
        // 根據設定決定是否自動關閉頁面
        if (this.autoClose) {
            // 稍微延遲一下讓用戶看到提交成功的反饋
            setTimeout(() => {
                window.close();
            }, 1000);
        }
    }

    cancelFeedback() {
        if (confirm('確定要取消回饋嗎？')) {
            window.close();
        }
    }

    toggleCombinedMode() {
        this.combinedMode = !this.combinedMode;

        const toggle = document.getElementById('combinedModeToggle');
        if (toggle) {
            toggle.classList.toggle('active', this.combinedMode);
        }

        // 顯示/隱藏分頁
        const feedbackTab = document.querySelector('[data-tab="feedback"]');
        const summaryTab = document.querySelector('[data-tab="summary"]');
        const combinedTab = document.querySelector('[data-tab="combined"]');

        if (this.combinedMode) {
            // 啟用合併模式：隱藏原本的回饋和摘要分頁，顯示合併分頁
            if (feedbackTab) feedbackTab.classList.add('hidden');
            if (summaryTab) summaryTab.classList.add('hidden');
            if (combinedTab) {
                combinedTab.classList.remove('hidden');
                // 如果合併分頁顯示，並且當前在回饋或摘要分頁，則將合併分頁設為活躍
                const currentActiveTab = document.querySelector('.tab-button.active');
                if (currentActiveTab && (currentActiveTab.getAttribute('data-tab') === 'feedback' || currentActiveTab.getAttribute('data-tab') === 'summary')) {
                    combinedTab.classList.add('active');
                    currentActiveTab.classList.remove('active');

                    // 顯示對應的分頁內容
                    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                    document.getElementById('tab-combined').classList.add('active');
                }
            }

            // 同步數據到合併模式
            this.syncDataToCombinedMode();

        } else {
            // 停用合併模式：顯示原本的分頁，隱藏合併分頁
            if (feedbackTab) feedbackTab.classList.remove('hidden');
            if (summaryTab) summaryTab.classList.remove('hidden');
            if (combinedTab) {
                combinedTab.classList.add('hidden');
                // 如果當前在合併分頁，則切換到回饋分頁
                if (combinedTab.classList.contains('active')) {
                    combinedTab.classList.remove('active');
                    if (feedbackTab) {
                        feedbackTab.classList.add('active');
                        // 顯示對應的分頁內容
                        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                        document.getElementById('tab-feedback').classList.add('active');
                    }
                }
            }

            // 同步數據回原始分頁
            this.syncDataFromCombinedMode();
        }

        localStorage.setItem('combinedMode', this.combinedMode.toString());

        console.log('合併模式已', this.combinedMode ? '啟用' : '停用');
    }

    toggleAutoClose() {
        this.autoClose = !this.autoClose;

        const toggle = document.getElementById('autoCloseToggle');
        if (toggle) {
            toggle.classList.toggle('active', this.autoClose);
        }

        localStorage.setItem('autoClose', this.autoClose.toString());

        console.log('自動關閉頁面已', this.autoClose ? '啟用' : '停用');
    }

    syncDataToCombinedMode() {
        // 同步回饋文字
        const feedbackText = document.getElementById('feedbackText');
        const combinedFeedbackText = document.getElementById('combinedFeedbackText');
        if (feedbackText && combinedFeedbackText) {
            combinedFeedbackText.value = feedbackText.value;
        }

        // 同步摘要內容
        const summaryContent = document.getElementById('summaryContent');
        const combinedSummaryContent = document.getElementById('combinedSummaryContent');
        if (summaryContent && combinedSummaryContent) {
            combinedSummaryContent.textContent = summaryContent.textContent;
        }
    }

    syncDataFromCombinedMode() {
        // 同步回饋文字
        const feedbackText = document.getElementById('feedbackText');
        const combinedFeedbackText = document.getElementById('combinedFeedbackText');
        if (feedbackText && combinedFeedbackText) {
            feedbackText.value = combinedFeedbackText.value;
        }
    }

    loadSettings() {
        // 載入合併模式設定
        const savedCombinedMode = localStorage.getItem('combinedMode');
        if (savedCombinedMode === 'true') {
            this.combinedMode = true;
            const toggle = document.getElementById('combinedModeToggle');
            if (toggle) {
                toggle.classList.add('active');
            }

            // 應用合併模式設定
            this.applyCombinedModeState();
        }

        // 載入自動關閉設定
        const savedAutoClose = localStorage.getItem('autoClose');
        if (savedAutoClose !== null) {
            this.autoClose = savedAutoClose === 'true';
        } else {
            // 如果沒有保存的設定，使用預設值（true）
            this.autoClose = true;
        }
        
        // 更新自動關閉開關狀態
        const autoCloseToggle = document.getElementById('autoCloseToggle');
        if (autoCloseToggle) {
            autoCloseToggle.classList.toggle('active', this.autoClose);
        }
    }

    applyCombinedModeState() {
        const feedbackTab = document.querySelector('[data-tab="feedback"]');
        const summaryTab = document.querySelector('[data-tab="summary"]');
        const combinedTab = document.querySelector('[data-tab="combined"]');

        if (this.combinedMode) {
            // 隱藏原本的回饋和摘要分頁，顯示合併分頁
            if (feedbackTab) feedbackTab.classList.add('hidden');
            if (summaryTab) summaryTab.classList.add('hidden');
            if (combinedTab) combinedTab.classList.remove('hidden');
        } else {
            // 顯示原本的分頁，隱藏合併分頁
            if (feedbackTab) feedbackTab.classList.remove('hidden');
            if (summaryTab) summaryTab.classList.remove('hidden');
            if (combinedTab) combinedTab.classList.add('hidden');
        }
    }

    initCommandTerminal() {
        // 使用翻譯的歡迎信息
        if (window.i18nManager) {
            const welcomeTemplate = window.i18nManager.t('dynamic.terminalWelcome');
            if (welcomeTemplate && welcomeTemplate !== 'dynamic.terminalWelcome') {
                const welcomeMessage = welcomeTemplate.replace('{sessionId}', this.sessionId);
                this.appendCommandOutput(welcomeMessage);
                return;
            }
        }

        // 回退到預設歡迎信息（如果翻譯不可用）
        const welcomeMessage = `Welcome to Interactive Feedback Terminal
========================================
Project Directory: ${this.sessionId}
Enter commands and press Enter or click Execute button
Supported commands: ls, dir, pwd, cat, type, etc.

$ `;
        this.appendCommandOutput(welcomeMessage);
    }
}

// 全域函數，供 HTML 中的 onclick 使用
window.feedbackApp = null; 