/**
 * Electron 預載腳本
 * ==================
 * 
 * 此腳本在渲染進程中運行，但在網頁內容載入之前執行。
 * 它提供了安全的方式讓網頁與主進程通信，同時保持安全性。
 * 
 * 主要功能：
 * - 提供安全的 IPC 通信接口
 * - 擴展現有的 WebSocket 管理器
 * - 添加桌面應用特有的 API
 * - 標記桌面環境
 * 
 * 作者: Augment Agent
 * 版本: 2.3.0
 */

const { contextBridge, ipcRenderer } = require('electron');

/**
 * 桌面 API 接口
 * 通過 contextBridge 安全地暴露給渲染進程
 */
const desktopAPI = {
    // 環境標識
    isDesktop: true,
    platform: process.platform,

    // 視窗控制
    window: {
        minimize: () => ipcRenderer.invoke('window-minimize'),
        maximize: () => ipcRenderer.invoke('window-maximize'),
        close: () => ipcRenderer.invoke('window-close')
    },

    // 系統資訊
    system: {
        getInfo: () => ipcRenderer.invoke('get-system-info'),
        platform: process.platform,
        arch: process.arch
    },

    // 事件監聽
    events: {
        onSessionUpdate: (callback) => {
            const wrappedCallback = (event, ...args) => callback(...args);
            ipcRenderer.on('session-updated', wrappedCallback);
            
            // 返回清理函數
            return () => {
                ipcRenderer.removeListener('session-updated', wrappedCallback);
            };
        },

        onFeedbackRequest: (callback) => {
            const wrappedCallback = (event, ...args) => callback(...args);
            ipcRenderer.on('feedback-request', wrappedCallback);
            
            return () => {
                ipcRenderer.removeListener('feedback-request', wrappedCallback);
            };
        }
    },

    // 回饋處理
    feedback: {
        send: (data) => ipcRenderer.invoke('send-feedback', data),
        cancel: () => ipcRenderer.invoke('cancel-feedback')
    },

    // 開發者工具
    dev: {
        openDevTools: () => ipcRenderer.invoke('open-dev-tools'),
        reload: () => ipcRenderer.invoke('reload-window')
    }
};

/**
 * 擴展現有的 Web UI 功能
 */
const webUIExtensions = {
    // 檢測桌面環境
    isDesktopMode: () => true,

    // 獲取桌面特有的配置
    getDesktopConfig: () => ({
        windowControls: true,
        nativeMenus: process.platform === 'darwin',
        customTitleBar: process.platform !== 'darwin'
    }),

    // 桌面通知
    showNotification: (title, body, options = {}) => {
        if ('Notification' in window && Notification.permission === 'granted') {
            return new Notification(title, { body, ...options });
        }
        return null;
    },

    // 請求通知權限
    requestNotificationPermission: async () => {
        if ('Notification' in window) {
            return await Notification.requestPermission();
        }
        return 'denied';
    }
};

/**
 * 日誌工具
 */
const logger = {
    debug: (...args) => {
        if (process.env.NODE_ENV === 'development') {
            console.log('[Desktop Debug]', ...args);
        }
    },
    info: (...args) => console.log('[Desktop Info]', ...args),
    warn: (...args) => console.warn('[Desktop Warn]', ...args),
    error: (...args) => console.error('[Desktop Error]', ...args)
};

// 暴露 API 到渲染進程
try {
    // 主要的桌面 API
    contextBridge.exposeInMainWorld('electronAPI', desktopAPI);
    
    // Web UI 擴展
    contextBridge.exposeInMainWorld('desktopExtensions', webUIExtensions);
    
    // 日誌工具
    contextBridge.exposeInMainWorld('desktopLogger', logger);
    
    // 標記桌面環境（向後兼容）
    contextBridge.exposeInMainWorld('MCP_DESKTOP_MODE', true);
    
    logger.info('桌面 API 已成功暴露到渲染進程');
    
} catch (error) {
    console.error('暴露桌面 API 失敗:', error);
}

/**
 * DOM 載入完成後的初始化
 */
window.addEventListener('DOMContentLoaded', () => {
    logger.debug('DOM 載入完成，開始桌面環境初始化');
    
    // 添加桌面環境樣式類
    document.body.classList.add('desktop-mode');
    document.body.classList.add(`platform-${process.platform}`);
    
    // 設置桌面環境變數
    document.documentElement.style.setProperty('--is-desktop', '1');
    
    // 如果是 macOS，添加特殊樣式
    if (process.platform === 'darwin') {
        document.body.classList.add('macos-titlebar');
    }
    
    // 監聽鍵盤快捷鍵
    document.addEventListener('keydown', (event) => {
        // Ctrl/Cmd + R: 重新載入
        if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
            if (process.env.NODE_ENV === 'development') {
                event.preventDefault();
                location.reload();
            }
        }
        
        // F12: 開發者工具
        if (event.key === 'F12' && process.env.NODE_ENV === 'development') {
            event.preventDefault();
            desktopAPI.dev.openDevTools();
        }
        
        // Escape: 最小化視窗
        if (event.key === 'Escape' && event.ctrlKey) {
            event.preventDefault();
            desktopAPI.window.minimize();
        }
    });
    
    logger.debug('桌面環境初始化完成');
});

/**
 * 錯誤處理
 */
window.addEventListener('error', (event) => {
    logger.error('渲染進程錯誤:', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
    });
});

window.addEventListener('unhandledrejection', (event) => {
    logger.error('未處理的 Promise 拒絕:', event.reason);
});

logger.info('預載腳本載入完成');
