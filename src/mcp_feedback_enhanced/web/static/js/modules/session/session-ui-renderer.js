/**
 * MCP Feedback Enhanced - 會話 UI 渲染模組
 * =======================================
 * 
 * 負責會話相關的 UI 渲染和更新
 */

(function() {
    'use strict';

    // 確保命名空間存在
    window.MCPFeedback = window.MCPFeedback || {};
    window.MCPFeedback.Session = window.MCPFeedback.Session || {};

    const DOMUtils = window.MCPFeedback.Utils.DOM;
    const TimeUtils = window.MCPFeedback.Utils.Time;
    const StatusUtils = window.MCPFeedback.Utils.Status;

    /**
     * 會話 UI 渲染器
     */
    function SessionUIRenderer(options) {
        options = options || {};

        // UI 元素引用
        this.currentSessionCard = null;
        this.historyList = null;
        this.statsElements = {};

        // 渲染選項
        this.showFullSessionId = options.showFullSessionId || false;
        this.enableAnimations = options.enableAnimations !== false;

        // 活躍時間定時器
        this.activeTimeTimer = null;
        this.currentSessionData = null;

        this.initializeElements();
        this.startActiveTimeTimer();

        console.log('🎨 SessionUIRenderer 初始化完成');
    }

    /**
     * 初始化 UI 元素
     */
    SessionUIRenderer.prototype.initializeElements = function() {
        this.currentSessionCard = DOMUtils.safeQuerySelector('#currentSessionCard');
        this.historyList = DOMUtils.safeQuerySelector('#sessionHistoryList');

        // 統計元素
        this.statsElements = {
            todayCount: DOMUtils.safeQuerySelector('.stat-today-count'),
            averageDuration: DOMUtils.safeQuerySelector('.stat-average-duration'),
            totalSessions: DOMUtils.safeQuerySelector('.stat-total-sessions')
        };
    };

    /**
     * 渲染當前會話
     */
    SessionUIRenderer.prototype.renderCurrentSession = function(sessionData) {
        if (!this.currentSessionCard || !sessionData) return;

        console.log('🎨 渲染當前會話:', sessionData);

        // 檢查是否是新會話（會話 ID 變更）
        const isNewSession = !this.currentSessionData ||
                            this.currentSessionData.session_id !== sessionData.session_id;

        // 更新當前會話數據
        this.currentSessionData = sessionData;

        // 如果是新會話，重置活躍時間定時器
        if (isNewSession) {
            console.log('🎨 檢測到新會話，重置活躍時間定時器');
            this.resetActiveTimeTimer();
        }

        // 更新會話 ID
        this.updateSessionId(sessionData);

        // 更新狀態徽章
        this.updateStatusBadge(sessionData);

        // 更新時間資訊
        this.updateTimeInfo(sessionData);

        // 更新專案資訊
        this.updateProjectInfo(sessionData);

        // 更新摘要
        this.updateSummary(sessionData);

        // 更新會話狀態列
        this.updateSessionStatusBar(sessionData);
    };

    /**
     * 更新會話 ID 顯示
     */
    SessionUIRenderer.prototype.updateSessionId = function(sessionData) {
        const sessionIdElement = this.currentSessionCard.querySelector('.session-id');
        if (sessionIdElement && sessionData.session_id) {
            const displayId = this.showFullSessionId ?
                sessionData.session_id :
                sessionData.session_id.substring(0, 8) + '...';
            const sessionIdLabel = window.i18nManager ? window.i18nManager.t('sessionManagement.sessionId') : '會話 ID';
            DOMUtils.safeSetTextContent(sessionIdElement, sessionIdLabel + ': ' + displayId);
        }
    };

    /**
     * 更新狀態徽章
     */
    SessionUIRenderer.prototype.updateStatusBadge = function(sessionData) {
        const statusBadge = this.currentSessionCard.querySelector('.status-badge');
        if (statusBadge && sessionData.status) {
            StatusUtils.updateStatusIndicator(statusBadge, sessionData.status, {
                updateText: true,
                updateColor: false, // 使用 CSS 類控制顏色
                updateClass: true
            });
        }
    };

    /**
     * 更新時間資訊
     */
    SessionUIRenderer.prototype.updateTimeInfo = function(sessionData) {
        const timeElement = this.currentSessionCard.querySelector('.session-time');
        if (timeElement && sessionData.created_at) {
            const timeText = TimeUtils.formatTimestamp(sessionData.created_at, { format: 'time' });
            const createdTimeLabel = window.i18nManager ? window.i18nManager.t('sessionManagement.createdTime') : '建立時間';
            DOMUtils.safeSetTextContent(timeElement, createdTimeLabel + ': ' + timeText);
        }
    };

    /**
     * 更新專案資訊
     */
    SessionUIRenderer.prototype.updateProjectInfo = function(sessionData) {
        const projectElement = this.currentSessionCard.querySelector('.session-project');
        if (projectElement) {
            const projectDir = sessionData.project_directory || './';
            const projectLabel = window.i18nManager ? window.i18nManager.t('sessionManagement.project') : '專案';
            DOMUtils.safeSetTextContent(projectElement, projectLabel + ': ' + projectDir);
        }
    };

    /**
     * 更新摘要
     */
    SessionUIRenderer.prototype.updateSummary = function(sessionData) {
        const summaryElement = this.currentSessionCard.querySelector('.session-summary');
        if (summaryElement) {
            const noSummaryText = window.i18nManager ? window.i18nManager.t('sessionManagement.noSummary') : '無摘要';
            const summary = sessionData.summary || noSummaryText;
            const summaryLabel = window.i18nManager ? window.i18nManager.t('sessionManagement.aiSummary') : 'AI 摘要';
            DOMUtils.safeSetTextContent(summaryElement, summaryLabel + ': ' + summary);
        }
    };

    /**
     * 更新會話狀態列
     */
    SessionUIRenderer.prototype.updateSessionStatusBar = function(sessionData) {
        if (!sessionData) return;

        console.log('🎨 更新會話狀態列:', sessionData);

        // 更新當前會話 ID - 顯示完整 session ID
        const currentSessionElement = document.getElementById('currentSessionId');
        if (currentSessionElement && sessionData.session_id) {
            DOMUtils.safeSetTextContent(currentSessionElement, sessionData.session_id);
        }

        // 立即更新活躍時間（定時器會持續更新）
        this.updateActiveTime();
    };

    /**
     * 渲染會話歷史列表
     */
    SessionUIRenderer.prototype.renderSessionHistory = function(sessionHistory) {
        if (!this.historyList) return;

        console.log('🎨 渲染會話歷史:', sessionHistory.length, '個會話');

        // 清空現有內容
        DOMUtils.clearElement(this.historyList);

        if (sessionHistory.length === 0) {
            this.renderEmptyHistory();
            return;
        }

        // 渲染歷史會話
        const fragment = document.createDocumentFragment();
        sessionHistory.forEach((session) => {
            const card = this.createSessionCard(session, true);
            fragment.appendChild(card);
        });

        this.historyList.appendChild(fragment);
    };

    /**
     * 渲染空歷史狀態
     */
    SessionUIRenderer.prototype.renderEmptyHistory = function() {
        const noHistoryText = window.i18nManager ? window.i18nManager.t('sessionManagement.noHistory') : '暫無歷史會話';
        const emptyElement = DOMUtils.createElement('div', {
            className: 'no-sessions',
            textContent: noHistoryText
        });
        this.historyList.appendChild(emptyElement);
    };

    /**
     * 創建會話卡片
     */
    SessionUIRenderer.prototype.createSessionCard = function(sessionData, isHistory) {
        const card = DOMUtils.createElement('div', {
            className: 'session-card' + (isHistory ? ' history' : ''),
            attributes: {
                'data-session-id': sessionData.session_id
            }
        });

        // 創建卡片內容
        const header = this.createSessionHeader(sessionData);
        const info = this.createSessionInfo(sessionData, isHistory);
        const actions = this.createSessionActions(sessionData, isHistory);

        card.appendChild(header);
        card.appendChild(info);
        card.appendChild(actions);

        return card;
    };

    /**
     * 創建會話卡片標題
     */
    SessionUIRenderer.prototype.createSessionHeader = function(sessionData) {
        const header = DOMUtils.createElement('div', { className: 'session-header' });

        // 會話 ID
        const sessionIdLabel = window.i18nManager ? window.i18nManager.t('sessionManagement.sessionId') : '會話 ID';
        const sessionId = DOMUtils.createElement('div', {
            className: 'session-id',
            textContent: sessionIdLabel + ': ' + (sessionData.session_id || '').substring(0, 8) + '...'
        });

        // 狀態徽章
        const statusContainer = DOMUtils.createElement('div', { className: 'session-status' });
        const statusBadge = DOMUtils.createElement('span', {
            className: 'status-badge ' + (sessionData.status || 'waiting'),
            textContent: StatusUtils.getStatusText(sessionData.status)
        });

        statusContainer.appendChild(statusBadge);
        header.appendChild(sessionId);
        header.appendChild(statusContainer);

        return header;
    };

    /**
     * 創建會話資訊區域
     */
    SessionUIRenderer.prototype.createSessionInfo = function(sessionData, isHistory) {
        const info = DOMUtils.createElement('div', { className: 'session-info' });

        // 時間資訊
        const timeText = sessionData.created_at ?
            TimeUtils.formatTimestamp(sessionData.created_at, { format: 'time' }) :
            '--:--:--';

        const timeLabel = isHistory ?
            (window.i18nManager ? window.i18nManager.t('sessionManagement.sessionDetails.duration') : '完成時間') :
            (window.i18nManager ? window.i18nManager.t('sessionManagement.createdTime') : '建立時間');

        const timeElement = DOMUtils.createElement('div', {
            className: 'session-time',
            textContent: timeLabel + ': ' + timeText
        });

        info.appendChild(timeElement);

        // 歷史會話顯示持續時間
        if (isHistory) {
            const duration = this.calculateDisplayDuration(sessionData);
            const durationLabel = window.i18nManager ? window.i18nManager.t('sessionManagement.sessionDetails.duration') : '持續時間';
            const durationElement = DOMUtils.createElement('div', {
                className: 'session-duration',
                textContent: durationLabel + ': ' + duration
            });
            info.appendChild(durationElement);
        }

        return info;
    };

    /**
     * 計算顯示用的持續時間
     */
    SessionUIRenderer.prototype.calculateDisplayDuration = function(sessionData) {
        if (sessionData.duration && sessionData.duration > 0) {
            return TimeUtils.formatDuration(sessionData.duration);
        } else if (sessionData.created_at && sessionData.completed_at) {
            const duration = sessionData.completed_at - sessionData.created_at;
            return TimeUtils.formatDuration(duration);
        } else if (sessionData.created_at) {
            return TimeUtils.estimateSessionDuration(sessionData);
        }
        return window.i18nManager ? window.i18nManager.t('sessionManagement.sessionDetails.unknown') : '未知';
    };

    /**
     * 創建會話操作區域
     */
    SessionUIRenderer.prototype.createSessionActions = function(sessionData, isHistory) {
        const actions = DOMUtils.createElement('div', { className: 'session-actions' });

        const buttonText = isHistory ?
            (window.i18nManager ? window.i18nManager.t('sessionManagement.viewDetails') : '查看') :
            (window.i18nManager ? window.i18nManager.t('sessionManagement.viewDetails') : '詳細資訊');

        const button = DOMUtils.createElement('button', {
            className: 'btn-small',
            textContent: buttonText
        });

        // 添加點擊事件
        DOMUtils.addEventListener(button, 'click', function() {
            if (window.MCPFeedback && window.MCPFeedback.SessionManager) {
                window.MCPFeedback.SessionManager.viewSessionDetails(sessionData.session_id);
            }
        });

        actions.appendChild(button);
        return actions;
    };

    /**
     * 渲染統計資訊
     */
    SessionUIRenderer.prototype.renderStats = function(stats) {
        console.log('🎨 渲染統計資訊:', stats);
        console.log('🎨 統計元素狀態:', {
            todayCount: !!this.statsElements.todayCount,
            averageDuration: !!this.statsElements.averageDuration,
            totalSessions: !!this.statsElements.totalSessions
        });

        // 更新今日會話數
        if (this.statsElements.todayCount) {
            DOMUtils.safeSetTextContent(this.statsElements.todayCount, stats.todayCount.toString());
            console.log('🎨 已更新今日會話數:', stats.todayCount);
        } else {
            console.warn('🎨 找不到今日會話數元素 (.stat-today-count)');
        }

        // 更新平均時長
        if (this.statsElements.averageDuration) {
            const durationText = TimeUtils.formatDuration(stats.averageDuration);
            DOMUtils.safeSetTextContent(this.statsElements.averageDuration, durationText);
            console.log('🎨 已更新平均時長:', durationText);
        } else {
            console.warn('🎨 找不到平均時長元素 (.stat-average-duration)');
        }

        // 更新總會話數
        if (this.statsElements.totalSessions) {
            DOMUtils.safeSetTextContent(this.statsElements.totalSessions, stats.totalSessions.toString());
            console.log('🎨 已更新總會話數:', stats.totalSessions);
        } else {
            console.warn('🎨 找不到總會話數元素 (.stat-total-sessions)');
        }
    };

    /**
     * 添加載入動畫
     */
    SessionUIRenderer.prototype.showLoading = function(element) {
        if (element && this.enableAnimations) {
            DOMUtils.safeAddClass(element, 'loading');
        }
    };

    /**
     * 移除載入動畫
     */
    SessionUIRenderer.prototype.hideLoading = function(element) {
        if (element && this.enableAnimations) {
            DOMUtils.safeRemoveClass(element, 'loading');
        }
    };

    /**
     * 啟動活躍時間定時器
     */
    SessionUIRenderer.prototype.startActiveTimeTimer = function() {
        const self = this;

        // 清除現有定時器
        if (this.activeTimeTimer) {
            clearInterval(this.activeTimeTimer);
        }

        // 每秒更新活躍時間
        this.activeTimeTimer = setInterval(function() {
            self.updateActiveTime();
        }, 1000);

        console.log('🎨 活躍時間定時器已啟動');
    };

    /**
     * 停止活躍時間定時器
     */
    SessionUIRenderer.prototype.stopActiveTimeTimer = function() {
        if (this.activeTimeTimer) {
            clearInterval(this.activeTimeTimer);
            this.activeTimeTimer = null;
            console.log('🎨 活躍時間定時器已停止');
        }
    };

    /**
     * 重置活躍時間定時器
     */
    SessionUIRenderer.prototype.resetActiveTimeTimer = function() {
        this.stopActiveTimeTimer();
        this.startActiveTimeTimer();
    };

    /**
     * 更新活躍時間顯示
     */
    SessionUIRenderer.prototype.updateActiveTime = function() {
        if (!this.currentSessionData || !this.currentSessionData.created_at) {
            return;
        }

        const activeTimeElement = document.getElementById('sessionAge');
        if (activeTimeElement) {
            const timeText = TimeUtils.formatElapsedTime(this.currentSessionData.created_at);
            DOMUtils.safeSetTextContent(activeTimeElement, timeText);
        }
    };

    /**
     * 清理資源
     */
    SessionUIRenderer.prototype.cleanup = function() {
        // 停止定時器
        this.stopActiveTimeTimer();

        // 清理引用
        this.currentSessionCard = null;
        this.historyList = null;
        this.statsElements = {};
        this.currentSessionData = null;

        console.log('🎨 SessionUIRenderer 清理完成');
    };

    // 將 SessionUIRenderer 加入命名空間
    window.MCPFeedback.Session.UIRenderer = SessionUIRenderer;

    console.log('✅ SessionUIRenderer 模組載入完成');

})();
