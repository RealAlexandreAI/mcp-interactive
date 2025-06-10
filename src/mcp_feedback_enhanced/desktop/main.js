#!/usr/bin/env node
/**
 * Electron 主進程
 * ===============
 * 
 * 此文件是 MCP Feedback Enhanced 桌面應用的主進程入口點。
 * 負責創建和管理 BrowserWindow，以及與現有 Web UI 的整合。
 * 
 * 主要功能：
 * - 創建和管理應用視窗
 * - 載入本地 Web 服務器內容
 * - 處理應用生命週期事件
 * - 提供桌面應用特有的功能
 * 
 * 作者: Augment Agent
 * 版本: 2.3.0
 */

const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const os = require('os');

// 應用配置
const APP_CONFIG = {
    name: 'MCP Feedback Enhanced',
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    defaultPort: 8765
};

// 全局變數
let mainWindow = null;
let webServerPort = APP_CONFIG.defaultPort;

/**
 * Electron 應用類
 */
class ElectronApp {
    constructor() {
        this.mainWindow = null;
        this.webServerPort = APP_CONFIG.defaultPort;
        this.isDevMode = process.argv.includes('--dev');
        
        this.setupEventHandlers();
        this.parseCommandLineArgs();
    }

    /**
     * 解析命令行參數
     */
    parseCommandLineArgs() {
        const args = process.argv;
        const portIndex = args.indexOf('--port');
        
        if (portIndex !== -1 && portIndex + 1 < args.length) {
            const port = parseInt(args[portIndex + 1]);
            if (!isNaN(port) && port > 0 && port < 65536) {
                this.webServerPort = port;
                console.log(`使用指定端口: ${port}`);
            }
        }
    }

    /**
     * 設置事件處理器
     */
    setupEventHandlers() {
        // 應用準備就緒
        app.whenReady().then(() => {
            this.createWindow();
            this.setupIpcHandlers();
        });

        // 所有視窗關閉
        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });

        // 應用激活（macOS）
        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) {
                this.createWindow();
            }
        });

        // 處理證書錯誤（開發模式）
        app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
            if (this.isDevMode && url.startsWith('https://localhost')) {
                event.preventDefault();
                callback(true);
            } else {
                callback(false);
            }
        });
    }

    /**
     * 創建主視窗
     */
    async createWindow() {
        console.log('創建主視窗...');
        console.log(`視窗配置: ${APP_CONFIG.width}x${APP_CONFIG.height}`);

        this.mainWindow = new BrowserWindow({
            width: APP_CONFIG.width,
            height: APP_CONFIG.height,
            minWidth: APP_CONFIG.minWidth,
            minHeight: APP_CONFIG.minHeight,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                preload: path.join(__dirname, 'preload.js'),
                webSecurity: !this.isDevMode
            },
            icon: this.getAppIcon(),
            title: APP_CONFIG.name,
            show: false, // 先隱藏，等載入完成後顯示
            titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
            alwaysOnTop: false, // 不總是置頂，但確保可見
            center: true, // 居中顯示
            resizable: true
        });

        // 載入 Web UI
        await this.loadWebUI();

        // 視窗準備顯示
        this.mainWindow.once('ready-to-show', () => {
            console.log('視窗準備顯示，正在顯示視窗...');
            this.mainWindow.show();
            this.mainWindow.focus(); // 確保視窗獲得焦點

            if (this.isDevMode) {
                this.mainWindow.webContents.openDevTools();
            }
        });

        // 備用顯示機制：如果 ready-to-show 沒有觸發，強制顯示
        setTimeout(() => {
            if (this.mainWindow && !this.mainWindow.isVisible()) {
                console.log('備用顯示機制：強制顯示視窗');
                this.mainWindow.show();
                this.mainWindow.focus();
            }
        }, 3000); // 3秒後強制顯示

        // 處理視窗關閉
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });

        // 處理外部連結
        this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
            shell.openExternal(url);
            return { action: 'deny' };
        });

        console.log('主視窗創建完成');
    }

    /**
     * 載入 Web UI
     */
    async loadWebUI() {
        const webUrl = `http://localhost:${this.webServerPort}`;
        console.log(`載入 Web UI: ${webUrl}`);

        try {
            await this.mainWindow.loadURL(webUrl);
            console.log('Web UI 載入成功');
        } catch (error) {
            console.error('載入 Web UI 失敗:', error);

            // 載入錯誤頁面
            const errorHtml = this.createErrorPage(error);
            await this.mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(errorHtml)}`);

            // 確保錯誤頁面也能顯示視窗
            console.log('載入錯誤頁面，強制顯示視窗');
            this.mainWindow.show();
            this.mainWindow.focus();
        }
    }

    /**
     * 創建錯誤頁面
     */
    createErrorPage(error) {
        return `
        <!DOCTYPE html>
        <html>
        <head>
            <title>連接錯誤 - ${APP_CONFIG.name}</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #f5f5f5;
                    margin: 0;
                    padding: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                }
                .error-container {
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                }
                h1 { color: #e74c3c; margin-bottom: 20px; }
                p { color: #666; line-height: 1.6; }
                .retry-btn {
                    background: #3498db;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-top: 20px;
                }
                .retry-btn:hover { background: #2980b9; }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>無法連接到 Web 服務器</h1>
                <p>桌面應用無法連接到本地 Web 服務器（端口 ${this.webServerPort}）。</p>
                <p>請確保 MCP 服務器正在運行。</p>
                <p><strong>錯誤詳情：</strong> ${error.message}</p>
                <button class="retry-btn" onclick="location.reload()">重試</button>
            </div>
        </body>
        </html>
        `;
    }

    /**
     * 獲取應用圖標
     */
    getAppIcon() {
        const iconPath = path.join(__dirname, 'assets');
        
        if (process.platform === 'win32') {
            return path.join(iconPath, 'icon.ico');
        } else if (process.platform === 'darwin') {
            return path.join(iconPath, 'icon.icns');
        } else {
            return path.join(iconPath, 'icon.png');
        }
    }

    /**
     * 設置 IPC 處理器
     */
    setupIpcHandlers() {
        // 視窗控制
        ipcMain.handle('window-minimize', () => {
            if (this.mainWindow) {
                this.mainWindow.minimize();
            }
        });

        ipcMain.handle('window-maximize', () => {
            if (this.mainWindow) {
                if (this.mainWindow.isMaximized()) {
                    this.mainWindow.unmaximize();
                } else {
                    this.mainWindow.maximize();
                }
            }
        });

        ipcMain.handle('window-close', () => {
            if (this.mainWindow) {
                this.mainWindow.close();
            }
        });

        // 獲取系統資訊
        ipcMain.handle('get-system-info', () => {
            return {
                platform: process.platform,
                arch: process.arch,
                nodeVersion: process.version,
                electronVersion: process.versions.electron,
                chromeVersion: process.versions.chrome
            };
        });

        console.log('IPC 處理器設置完成');
    }
}

// 創建應用實例
const electronApp = new ElectronApp();

// 導出供外部使用
module.exports = electronApp;
