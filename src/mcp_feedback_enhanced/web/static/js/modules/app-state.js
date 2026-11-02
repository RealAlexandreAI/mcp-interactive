/**
 * Lightweight app state container for MCP Feedback.
 */
(function() {
    'use strict';

    window.MCPFeedback = window.MCPFeedback || {};

    function AppState(initialState) {
        this._state = initialState || {
            connection: { status: 'disconnected', text: '' },
            session: { id: null, status: 'unknown' }
        };
        this._listeners = [];
    }

    AppState.prototype.getState = function() {
        return JSON.parse(JSON.stringify(this._state));
    };

    AppState.prototype.get = function(path, defaultValue) {
        var parts = (path || '').split('.');
        var current = this._state;
        for (var i = 0; i < parts.length; i++) {
            if (!parts[i]) continue;
            if (current == null || typeof current !== 'object' || !(parts[i] in current)) {
                return defaultValue;
            }
            current = current[parts[i]];
        }
        return current;
    };

    AppState.prototype.patch = function(partialState) {
        this._state = deepMerge(this._state, partialState || {});
        this._emit();
    };

    AppState.prototype.subscribe = function(listener) {
        if (typeof listener !== 'function') return function() {};
        this._listeners.push(listener);
        var self = this;
        return function() {
            self._listeners = self._listeners.filter(function(item) {
                return item !== listener;
            });
        };
    };

    AppState.prototype._emit = function() {
        var snapshot = this.getState();
        this._listeners.forEach(function(listener) {
            try {
                listener(snapshot);
            } catch (error) {
                console.error('AppState listener error:', error);
            }
        });
    };

    function deepMerge(target, source) {
        var output = Array.isArray(target) ? target.slice() : Object.assign({}, target);
        Object.keys(source).forEach(function(key) {
            var sourceValue = source[key];
            if (sourceValue && typeof sourceValue === 'object' && !Array.isArray(sourceValue)) {
                var base = output[key] && typeof output[key] === 'object' ? output[key] : {};
                output[key] = deepMerge(base, sourceValue);
            } else {
                output[key] = sourceValue;
            }
        });
        return output;
    }

    window.MCPFeedback.AppState = AppState;
})();
