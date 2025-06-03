#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web UI 主要管理器
================

基於 FastAPI 的 Web 用戶介面主要管理類，參考 GUI 的設計模式重構。
專為 SSH 遠端開發環境設計，支援現代化界面和多語言。
"""

import asyncio
import json
import logging
import os
import socket
import threading
import time
import webbrowser
from pathlib import Path
from typing import Dict, Optional
import uuid

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from .models import WebFeedbackSession, FeedbackResult
from .routes import setup_routes
from .utils import find_free_port, get_browser_opener
from ..debug import web_debug_log as debug_log
from ..i18n import get_i18n_manager


class WebUIManager:
    """Web UI 管理器"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = None):
        self.host = host
        # 優先使用固定端口 8765，確保 localStorage 的一致性
        self.port = port or find_free_port(preferred_port=8765)
        self.app = FastAPI(title="Interactive Feedback MCP")
        self.sessions: Dict[str, WebFeedbackSession] = {}
        self.server_thread = None
        self.server_process = None
        self.i18n = get_i18n_manager()
        
        # 設置靜態文件和模板
        self._setup_static_files()
        self._setup_templates()
        
        # 設置路由
        setup_routes(self)
        
        debug_log(f"WebUIManager 初始化完成，將在 {self.host}:{self.port} 啟動")

    def _setup_static_files(self):
        """設置靜態文件服務"""
        # Web UI 靜態文件
        web_static_path = Path(__file__).parent / "static"
        if web_static_path.exists():
            self.app.mount("/static", StaticFiles(directory=str(web_static_path)), name="static")
        else:
            raise RuntimeError(f"Static files directory not found: {web_static_path}")

    def _setup_templates(self):
        """設置模板引擎"""
        # Web UI 模板
        web_templates_path = Path(__file__).parent / "templates"
        if web_templates_path.exists():
            self.templates = Jinja2Templates(directory=str(web_templates_path))
        else:
            raise RuntimeError(f"Templates directory not found: {web_templates_path}")

    def create_session(self, project_directory: str, summary: str) -> str:
        """創建新的回饋會話"""
        session_id = str(uuid.uuid4())
        session = WebFeedbackSession(session_id, project_directory, summary)
        self.sessions[session_id] = session
        debug_log(f"創建回饋會話: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[WebFeedbackSession]:
        """獲取回饋會話"""
        return self.sessions.get(session_id)

    def remove_session(self, session_id: str):
        """移除回饋會話"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.cleanup()
            del self.sessions[session_id]
            debug_log(f"移除回饋會話: {session_id}")

    def start_server(self):
        """啟動 Web 伺服器"""
        def run_server_with_retry():
            max_retries = 5
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    debug_log(f"嘗試啟動伺服器在 {self.host}:{self.port} (嘗試 {retry_count + 1}/{max_retries})")
                    
                    config = uvicorn.Config(
                        app=self.app,
                        host=self.host,
                        port=self.port,
                        log_level="warning",
                        access_log=False
                    )
                    
                    server = uvicorn.Server(config)
                    asyncio.run(server.serve())
                    break
                    
                except OSError as e:
                    if e.errno == 10048:  # Windows: 位址已在使用中
                        retry_count += 1
                        if retry_count < max_retries:
                            debug_log(f"端口 {self.port} 被占用，嘗試下一個端口")
                            self.port = find_free_port(self.port + 1)
                        else:
                            debug_log("已達到最大重試次數，無法啟動伺服器")
                            break
                    else:
                        debug_log(f"伺服器啟動錯誤: {e}")
                        break
                except Exception as e:
                    debug_log(f"伺服器運行錯誤: {e}")
                    break

        # 在新線程中啟動伺服器
        self.server_thread = threading.Thread(target=run_server_with_retry, daemon=True)
        self.server_thread.start()
        
        # 等待伺服器啟動
        time.sleep(2)

    def open_browser(self, url: str):
        """開啟瀏覽器"""
        try:
            browser_opener = get_browser_opener()
            browser_opener(url)
            debug_log(f"已開啟瀏覽器：{url}")
        except Exception as e:
            debug_log(f"無法開啟瀏覽器: {e}")

    def get_server_url(self) -> str:
        """獲取伺服器 URL"""
        return f"http://{self.host}:{self.port}"

    def stop(self):
        """停止 Web UI 服務"""
        # 清理所有會話
        for session in list(self.sessions.values()):
            session.cleanup()
        self.sessions.clear()
        
        # 停止伺服器（注意：uvicorn 的 graceful shutdown 需要額外處理）
        if self.server_thread and self.server_thread.is_alive():
            debug_log("正在停止 Web UI 服務")


# 全域實例
_web_ui_manager: Optional[WebUIManager] = None


def get_web_ui_manager() -> WebUIManager:
    """獲取 Web UI 管理器實例"""
    global _web_ui_manager
    if _web_ui_manager is None:
        _web_ui_manager = WebUIManager()
    return _web_ui_manager


async def launch_web_feedback_ui(project_directory: str, summary: str) -> dict:
    """
    啟動 Web 回饋介面並等待用戶回饋
    
    Args:
        project_directory: 專案目錄路徑
        summary: AI 工作摘要
        
    Returns:
        dict: 回饋結果，包含 logs、interactive_feedback 和 images
    """
    manager = get_web_ui_manager()
    
    # 創建會話
    session_id = manager.create_session(project_directory, summary)
    session = manager.get_session(session_id)
    
    if not session:
        raise RuntimeError("無法創建回饋會話")
    
    # 啟動伺服器（如果尚未啟動）
    if not manager.server_thread or not manager.server_thread.is_alive():
        manager.start_server()
    
    # 構建完整 URL 並開啟瀏覽器
    feedback_url = f"{manager.get_server_url()}/session/{session_id}"
    manager.open_browser(feedback_url)
    
    try:
        # 等待用戶回饋
        result = await session.wait_for_feedback()
        debug_log(f"收到用戶回饋，會話: {session_id}")
        return result
    finally:
        # 清理會話
        manager.remove_session(session_id)


def stop_web_ui():
    """停止 Web UI 服務"""
    global _web_ui_manager
    if _web_ui_manager:
        _web_ui_manager.stop()
        _web_ui_manager = None
        debug_log("Web UI 服務已停止")


# 測試用主函數
if __name__ == "__main__":
    async def main():
        try:
            project_dir = os.getcwd()
            summary = "這是一個測試摘要，用於驗證 Web UI 功能。"
            
            print(f"啟動 Web UI 測試...")
            print(f"專案目錄: {project_dir}")
            print("等待用戶回饋...")
            
            result = await launch_web_feedback_ui(project_dir, summary)
            
            print("收到回饋結果:")
            print(f"命令日誌: {result.get('logs', '')}")
            print(f"互動回饋: {result.get('interactive_feedback', '')}")
            print(f"圖片數量: {len(result.get('images', []))}")
            
        except KeyboardInterrupt:
            print("\n用戶取消操作")
        except Exception as e:
            print(f"錯誤: {e}")
        finally:
            stop_web_ui()

    asyncio.run(main()) 