/**
 * Simple event dispatcher with typed-channel handlers.
 */
(function() {
    'use strict';

    window.MCPFeedback = window.MCPFeedback || {};

    function EventDispatcher() {
        this._handlers = {};
    }

    EventDispatcher.prototype.on = function(eventName, handler) {
        if (!eventName || typeof handler !== 'function') return function() {};
        this._handlers[eventName] = this._handlers[eventName] || [];
        this._handlers[eventName].push(handler);
        var self = this;
        return function() {
            self._handlers[eventName] = (self._handlers[eventName] || []).filter(function(item) {
                return item !== handler;
            });
        };
    };

    EventDispatcher.prototype.emit = function(eventName, payload) {
        var handlers = this._handlers[eventName] || [];
        if (!handlers.length) return false;
        handlers.forEach(function(handler) {
            try {
                handler(payload);
            } catch (error) {
                console.error('EventDispatcher handler error:', eventName, error);
            }
        });
        return true;
    };

    window.MCPFeedback.EventDispatcher = EventDispatcher;
})();
