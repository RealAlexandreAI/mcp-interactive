/**
 * MCP Feedback Enhanced - UI Manager
 * Handles UI state updates, status indicators, and connection status.
 * Tab-related logic has been removed (single-view layout).
 */

(function() {
    'use strict';

    window.MCPFeedback = window.MCPFeedback || {};
    var Utils = window.MCPFeedback.Utils;

    /**
     * UI Manager constructor
     */
    function UIManager(options) {
        options = options || {};

        // State
        this.feedbackState = Utils.CONSTANTS.FEEDBACK_WAITING;
        this.layoutMode = options.layoutMode || 'combined-horizontal';
        this.lastSubmissionTime = null;

        // UI elements
        this.connectionIndicator = null;
        this.connectionText = null;
        this.submitBtn = null;

        // Callbacks
        this.onLayoutModeChange = options.onLayoutModeChange || null;
        this.onFeedbackStateChange = options.onFeedbackStateChange || null;

        // Initialize debounce handlers
        this.initDebounceHandlers();
        this.initUIElements();
    }

    /**
     * Initialize debounce handlers
     */
    UIManager.prototype.initDebounceHandlers = function() {
        this._debouncedUpdateStatusIndicator = Utils.DOM.debounce(
            this._originalUpdateStatusIndicator.bind(this),
            100,
            false
        );

        this._debouncedUpdateStatusIndicatorElement = Utils.DOM.debounce(
            this._originalUpdateStatusIndicatorElement.bind(this),
            50,
            false
        );
    };

    /**
     * Initialize UI elements
     */
    UIManager.prototype.initUIElements = function() {
        this.connectionIndicator = Utils.safeQuerySelector('#connectionIndicator');
        this.connectionText = Utils.safeQuerySelector('#connectionText');
        this.submitBtn = Utils.safeQuerySelector('#submitBtn');
        console.log('UIManager: UI elements initialized');
    };

    /**
     * Set feedback state
     */
    UIManager.prototype.setFeedbackState = function(state, sessionId) {
        var previousState = this.feedbackState;
        this.feedbackState = state;

        if (sessionId) {
            console.log('Session: ' + sessionId.substring(0, 8) + '...');
        }

        console.log('State: ' + previousState + ' -> ' + state);
        this.updateUIState();
        this.updateStatusIndicator();

        // Notify app to update status ring
        if (this.onFeedbackStateChange) {
            this.onFeedbackStateChange(state);
        }
    };

    /**
     * Update UI state
     */
    UIManager.prototype.updateUIState = function() {
        this.updateSubmitButton();
        this.updateFeedbackInputs();
        this.updateImageUploadAreas();
    };

    /**
     * Update submit button state.
     * Uses textContent and className for safe DOM updates.
     */
    UIManager.prototype.updateSubmitButton = function() {
        var button = Utils.safeQuerySelector('#submitBtn');
        if (!button) return;

        var self = this;
        switch (self.feedbackState) {
            case Utils.CONSTANTS.FEEDBACK_WAITING:
                button.textContent = window.i18nManager ? window.i18nManager.t('buttons.submit') : 'Submit';
                button.className = 'btn btn-primary btn-full btn-submit';
                button.disabled = false;
                break;
            case Utils.CONSTANTS.FEEDBACK_PROCESSING:
                button.textContent = window.i18nManager ? window.i18nManager.t('buttons.processing') : 'Processing...';
                button.className = 'btn btn-secondary btn-full btn-submit';
                button.disabled = true;
                break;
            case Utils.CONSTANTS.FEEDBACK_SUBMITTED:
                button.textContent = window.i18nManager ? window.i18nManager.t('buttons.submitted') : 'Submitted';
                button.className = 'btn btn-success btn-full btn-submit';
                button.disabled = true;
                break;
        }
    };

    /**
     * Update feedback input state
     */
    UIManager.prototype.updateFeedbackInputs = function() {
        var feedbackInput = Utils.safeQuerySelector('#combinedFeedbackText');
        var canInput = this.feedbackState === Utils.CONSTANTS.FEEDBACK_WAITING;
        if (feedbackInput) {
            feedbackInput.disabled = !canInput;
        }
    };

    /**
     * Update image upload area state
     */
    UIManager.prototype.updateImageUploadAreas = function() {
        var uploadAreas = [
            Utils.safeQuerySelector('#feedbackImageUploadArea'),
            Utils.safeQuerySelector('#combinedImageUploadArea')
        ].filter(function(area) { return area !== null; });

        var canUpload = this.feedbackState === Utils.CONSTANTS.FEEDBACK_WAITING;
        uploadAreas.forEach(function(area) {
            if (canUpload) {
                area.classList.remove('disabled');
            } else {
                area.classList.add('disabled');
            }
        });
    };

    /**
     * Update status indicator (original, for debounce)
     */
    UIManager.prototype._originalUpdateStatusIndicator = function() {
        var combinedStatusIndicator = Utils.safeQuerySelector('#combinedFeedbackStatusIndicator');
        var statusInfo = this.getStatusInfo();

        if (combinedStatusIndicator) {
            this._originalUpdateStatusIndicatorElement(combinedStatusIndicator, statusInfo);
        }
    };

    /**
     * Update status indicator (debounced)
     */
    UIManager.prototype.updateStatusIndicator = function() {
        if (this._debouncedUpdateStatusIndicator) {
            this._debouncedUpdateStatusIndicator();
        } else {
            this._originalUpdateStatusIndicator();
        }
    };

    /**
     * Get status info
     */
    UIManager.prototype.getStatusInfo = function() {
        var title, message, status;

        switch (this.feedbackState) {
            case Utils.CONSTANTS.FEEDBACK_WAITING:
                title = window.i18nManager ? window.i18nManager.t('status.waiting.title') : 'Waiting for feedback';
                message = window.i18nManager ? window.i18nManager.t('status.waiting.message') : 'Please provide your feedback';
                status = 'waiting';
                break;

            case Utils.CONSTANTS.FEEDBACK_PROCESSING:
                title = window.i18nManager ? window.i18nManager.t('status.processing.title') : 'Processing';
                message = window.i18nManager ? window.i18nManager.t('status.processing.message') : 'Submitting your feedback...';
                status = 'processing';
                break;

            case Utils.CONSTANTS.FEEDBACK_SUBMITTED:
                var timeStr = this.lastSubmissionTime ?
                    new Date(this.lastSubmissionTime).toLocaleTimeString() : '';
                title = window.i18nManager ? window.i18nManager.t('status.submitted.title') : 'Submitted';
                message = window.i18nManager ? window.i18nManager.t('status.submitted.message') : 'Waiting for next MCP call';
                if (timeStr) { message += ' (' + timeStr + ')'; }
                status = 'submitted';
                break;

            default:
                title = window.i18nManager ? window.i18nManager.t('status.waiting.title') : 'Waiting for feedback';
                message = window.i18nManager ? window.i18nManager.t('status.waiting.message') : 'Please provide your feedback';
                status = 'waiting';
        }

        return { title: title, message: message, status: status };
    };

    /**
     * Update status indicator element (original, for debounce)
     */
    UIManager.prototype._originalUpdateStatusIndicatorElement = function(element, statusInfo) {
        if (!element) return;
        element.className = 'feedback-status-indicator status-' + statusInfo.status;
    };

    /**
     * Update status indicator element (debounced)
     */
    UIManager.prototype.updateStatusIndicatorElement = function(element, statusInfo) {
        if (this._debouncedUpdateStatusIndicatorElement) {
            this._debouncedUpdateStatusIndicatorElement(element, statusInfo);
        } else {
            this._originalUpdateStatusIndicatorElement(element, statusInfo);
        }
    };

    /**
     * Update connection status across all UI elements
     */
    UIManager.prototype.updateConnectionStatus = function(status, text) {
        // Update connection dot in session card
        var dot = document.getElementById('connectionDot');
        if (dot) {
            dot.className = 'status-dot ' + status;
        }

        // Update sidebar status badge
        var badge = document.getElementById('sidebarStatusBadge');
        if (badge) {
            badge.className = 'status-badge ' + status;
            badge.textContent = text;
        }

        // Legacy indicators
        if (this.connectionIndicator) {
            this.connectionIndicator.className = 'connection-indicator ' + status;
        }
        if (this.connectionText) {
            this.connectionText.textContent = text;
        }
    };

    /**
     * Safely render Markdown content using marked + DOMPurify
     */
    UIManager.prototype.renderMarkdownSafely = function(content) {
        try {
            if (typeof window.marked === 'undefined' || typeof window.DOMPurify === 'undefined') {
                return this.escapeHtml(content);
            }

            var rawHtml = window.marked.parse(content);
            // Sanitize with DOMPurify to prevent XSS
            var cleanHtml = window.DOMPurify.sanitize(rawHtml, {
                ALLOWED_TAGS: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'strong', 'em', 'code', 'pre', 'ul', 'ol', 'li', 'blockquote', 'a', 'hr', 'del', 's', 'table', 'thead', 'tbody', 'tr', 'td', 'th'],
                ALLOWED_ATTR: ['href', 'title', 'class', 'align', 'style'],
                ALLOW_DATA_ATTR: false
            });

            return cleanHtml;
        } catch (error) {
            console.error('Markdown render failed:', error);
            return this.escapeHtml(content);
        }
    };

    /**
     * HTML escape
     */
    UIManager.prototype.escapeHtml = function(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.textContent;
    };

    /**
     * Update AI summary content with sanitized Markdown rendering
     */
    UIManager.prototype.updateAISummaryContent = function(summary) {
        var renderedContent = this.renderMarkdownSafely(summary);

        var combinedSummaryContent = Utils.safeQuerySelector('#combinedSummaryContent');
        if (combinedSummaryContent) {
            // Safe: content is sanitized by DOMPurify in renderMarkdownSafely
            combinedSummaryContent.textContent = '';
            var wrapper = document.createElement('div');
            wrapper.textContent = '';
            // Use DOMPurify-sanitized content via trusted assignment
            var tempDiv = document.createElement('div');
            tempDiv.insertAdjacentHTML('afterbegin', renderedContent);
            while (tempDiv.firstChild) {
                combinedSummaryContent.appendChild(tempDiv.firstChild);
            }
        }

        // Re-render Lucide icons in case dynamic content was added
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    };

    /**
     * Reset feedback form
     * @param {boolean} clearText - Whether to clear text, default false
     */
    UIManager.prototype.resetFeedbackForm = function(clearText) {
        var feedbackInput = Utils.safeQuerySelector('#combinedFeedbackText');
        if (feedbackInput) {
            if (clearText === true) {
                feedbackInput.value = '';
            }
            var canInput = this.feedbackState === Utils.CONSTANTS.FEEDBACK_WAITING;
            feedbackInput.disabled = !canInput;
        }

        var button = Utils.safeQuerySelector('#submitBtn');
        if (button) {
            button.disabled = false;
        }
    };

    /**
     * Apply layout mode
     */
    UIManager.prototype.applyLayoutMode = function(layoutMode) {
        this.layoutMode = layoutMode;
        if (this.onLayoutModeChange) {
            this.onLayoutModeChange(layoutMode);
        }
    };

    /**
     * Get current feedback state
     */
    UIManager.prototype.getFeedbackState = function() {
        return this.feedbackState;
    };

    /**
     * Set last submission time
     */
    UIManager.prototype.setLastSubmissionTime = function(timestamp) {
        this.lastSubmissionTime = timestamp;
        this.updateStatusIndicator();
    };

    // Legacy compatibility stubs (called from other modules)
    UIManager.prototype.initTabs = function() {};
    UIManager.prototype.switchTab = function() {};
    UIManager.prototype.updateTabVisibility = function() {};
    UIManager.prototype.getCurrentTab = function() { return 'combined'; };
    UIManager.prototype.handleCombinedMode = function() {};

    // Register module
    window.MCPFeedback.UIManager = UIManager;

    console.log('UIManager module loaded');
})();
