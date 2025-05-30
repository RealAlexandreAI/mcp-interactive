#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
互動式回饋收集 Web UI
=====================

基於 FastAPI 的 Web 用戶介面，專為 SSH 遠端開發環境設計。
支援文字輸入、圖片上傳、命令執行等功能。

作者: Minidoracat  
靈感來源: dotcursorrules.com
增強功能: 圖片支援和現代化界面設計
"""

import os
import sys
import json
import uuid
import asyncio
import webbrowser
import threading
import subprocess
import psutil
import time
import base64
import tempfile
from typing import Dict, Optional, List
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# ===== 常數定義 =====
MAX_IMAGE_SIZE = 1 * 1024 * 1024  # 1MB 圖片大小限制
SUPPORTED_IMAGE_TYPES = {'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'}
TEMP_DIR = Path.home() / ".cache" / "interactive-feedback-mcp-web"


# ===== Web 回饋會話類 =====
class WebFeedbackSession:
    """Web 回饋會話管理"""
    
    def __init__(self, session_id: str, project_directory: str, summary: str):
        self.session_id = session_id
        self.project_directory = project_directory
        self.summary = summary
        self.websocket: Optional[WebSocket] = None
        self.feedback_result: Optional[str] = None
        self.images: List[dict] = []
        self.feedback_completed = threading.Event()
        self.process: Optional[subprocess.Popen] = None
        self.command_logs = []
        
        # 確保臨時目錄存在
        TEMP_DIR.mkdir(parents=True, exist_ok=True)

    async def wait_for_feedback(self, timeout: int = 600) -> dict:
        """
        等待用戶回饋，包含圖片
        
        Args:
            timeout: 超時時間（秒）
            
        Returns:
            dict: 回饋結果
        """
        loop = asyncio.get_event_loop()
        
        def wait_in_thread():
            return self.feedback_completed.wait(timeout)
        
        completed = await loop.run_in_executor(None, wait_in_thread)
        
        if completed:
            return {
                "logs": "\n".join(self.command_logs),
                "interactive_feedback": self.feedback_result or "",
                "images": self.images
            }
        else:
            raise TimeoutError("等待用戶回饋超時")

    async def submit_feedback(self, feedback: str, images: List[dict]):
        """
        提交回饋和圖片
        
        Args:
            feedback: 文字回饋
            images: 圖片列表
        """
        self.feedback_result = feedback
        self.images = self._process_images(images)
        self.feedback_completed.set()
        
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
    
    def _process_images(self, images: List[dict]) -> List[dict]:
        """
        處理圖片數據，轉換為統一格式
        
        Args:
            images: 原始圖片數據列表
            
        Returns:
            List[dict]: 處理後的圖片數據
        """
        processed_images = []
        
        for img in images:
            try:
                if not all(key in img for key in ["name", "data", "size"]):
                    continue
                
                # 檢查文件大小
                if img["size"] > MAX_IMAGE_SIZE:
                    debug_log(f"圖片 {img['name']} 超過大小限制，跳過")
                    continue
                
                # 解碼 base64 數據
                if isinstance(img["data"], str):
                    try:
                        image_bytes = base64.b64decode(img["data"])
                    except Exception as e:
                        debug_log(f"圖片 {img['name']} base64 解碼失敗: {e}")
                        continue
                else:
                    image_bytes = img["data"]
                
                if len(image_bytes) == 0:
                    debug_log(f"圖片 {img['name']} 數據為空，跳過")
                    continue
                
                processed_images.append({
                    "name": img["name"],
                    "data": image_bytes,  # 保存原始 bytes 數據
                    "size": len(image_bytes)
                })
                
                debug_log(f"圖片 {img['name']} 處理成功，大小: {len(image_bytes)} bytes")
                
            except Exception as e:
                debug_log(f"圖片處理錯誤: {e}")
                continue
        
        return processed_images

    def add_log(self, log_entry: str):
        """添加命令日誌"""
        self.command_logs.append(log_entry)

    async def run_command(self, command: str):
        """執行命令並透過 WebSocket 發送輸出"""
        if self.process:
            # 終止現有進程
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None

        try:
            self.process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.project_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # 在背景線程中讀取輸出
            def read_output():
                try:
                    for line in iter(self.process.stdout.readline, ''):
                        self.add_log(line.rstrip())
                        if self.websocket:
                            asyncio.run_coroutine_threadsafe(
                                self.websocket.send_json({
                                    "type": "command_output",
                                    "output": line
                                }),
                                asyncio.get_event_loop()
                            )
                    
                    # 等待進程完成
                    exit_code = self.process.wait()
                    if self.websocket:
                        asyncio.run_coroutine_threadsafe(
                            self.websocket.send_json({
                                "type": "command_finished",
                                "exit_code": exit_code
                            }),
                            asyncio.get_event_loop()
                        )
                
                except Exception as e:
                    debug_log(f"命令執行錯誤: {e}")
                finally:
                    self.process = None

            thread = threading.Thread(target=read_output, daemon=True)
            thread.start()

        except Exception as e:
            error_msg = f"命令執行失敗: {str(e)}\n"
            self.add_log(error_msg)
            if self.websocket:
                await self.websocket.send_json({
                    "type": "command_output",
                    "output": error_msg
                })


# ===== Web UI 管理器 =====
class WebUIManager:
    """Web UI 管理器"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.app = FastAPI(title="Interactive Feedback MCP Web UI")
        self.sessions: Dict[str, WebFeedbackSession] = {}
        self.server_thread: Optional[threading.Thread] = None
        self.setup_routes()

    def setup_routes(self):
        """設置路由"""
        
        # 確保靜態文件目錄存在（相對於套件位置）
        package_dir = Path(__file__).parent
        static_dir = package_dir / "static"
        templates_dir = package_dir / "templates"
        
        # 靜態文件
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # 模板
        templates = Jinja2Templates(directory=str(templates_dir)) if templates_dir.exists() else None

        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            """首頁"""
            if templates:
                return templates.TemplateResponse("index.html", {"request": request})
            else:
                return HTMLResponse(self._get_simple_index_html())

        @self.app.get("/session/{session_id}", response_class=HTMLResponse)
        async def feedback_session(request: Request, session_id: str):
            """回饋會話頁面"""
            session = self.sessions.get(session_id)
            if not session:
                return HTMLResponse("會話不存在", status_code=404)
            
            if templates:
                return templates.TemplateResponse("feedback.html", {
                    "request": request,
                    "session_id": session_id,
                    "project_directory": session.project_directory,
                    "summary": session.summary
                })
            else:
                return HTMLResponse(self._get_simple_feedback_html(session_id, session))

        @self.app.websocket("/ws/{session_id}")
        async def websocket_endpoint(websocket: WebSocket, session_id: str):
            """WebSocket 連接處理"""
            session = self.sessions.get(session_id)
            if not session:
                await websocket.close(code=4004, reason="會話不存在")
                return

            await websocket.accept()
            session.websocket = websocket

            try:
                while True:
                    data = await websocket.receive_json()
                    await self.handle_websocket_message(session, data)
                    
            except WebSocketDisconnect:
                debug_log(f"WebSocket 斷開連接: {session_id}")
            except Exception as e:
                debug_log(f"WebSocket 錯誤: {e}")
            finally:
                session.websocket = None

    async def handle_websocket_message(self, session: WebFeedbackSession, data: dict):
        """處理 WebSocket 消息"""
        message_type = data.get("type")
        
        if message_type == "run_command":
            command = data.get("command", "").strip()
            if command:
                await session.run_command(command)
                
        elif message_type == "submit_feedback":
            feedback = data.get("feedback", "")
            images = data.get("images", [])
            await session.submit_feedback(feedback, images)
            
        elif message_type == "stop_command":
            if session.process:
                try:
                    session.process.terminate()
                except:
                    pass

    def create_session(self, project_directory: str, summary: str) -> str:
        """創建新的回饋會話"""
        session_id = str(uuid.uuid4())
        session = WebFeedbackSession(session_id, project_directory, summary)
        self.sessions[session_id] = session
        return session_id

    def get_session(self, session_id: str) -> Optional[WebFeedbackSession]:
        """獲取會話"""
        return self.sessions.get(session_id)

    def remove_session(self, session_id: str):
        """移除會話"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if session.process:
                try:
                    session.process.terminate()
                except:
                    pass
            del self.sessions[session_id]

    def start_server(self):
        """啟動伺服器"""
        def run_server():
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="error",
                access_log=False
            )

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 等待伺服器啟動
        time.sleep(2)

    def open_browser(self, url: str):
        """開啟瀏覽器"""
        try:
            webbrowser.open(url)
        except Exception as e:
            debug_log(f"無法開啟瀏覽器: {e}")
    
    def _get_simple_index_html(self) -> str:
        """簡單的首頁 HTML"""
        return """
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <title>Interactive Feedback MCP</title>
        </head>
        <body>
            <h1>Interactive Feedback MCP Web UI</h1>
            <p>服務器運行中...</p>
        </body>
        </html>
        """
    
    def _get_simple_feedback_html(self, session_id: str, session: WebFeedbackSession) -> str:
        """簡單的回饋頁面 HTML"""
        return f"""
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <title>回饋收集</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #1e1e1e; color: white; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                textarea {{ width: 100%; height: 200px; background: #2d2d30; color: white; border: 1px solid #464647; }}
                button {{ background: #007acc; color: white; padding: 10px 20px; border: none; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>回饋收集</h1>
                <div>
                    <h3>AI 工作摘要:</h3>
                    <p>{session.summary}</p>
                </div>
                <div>
                    <h3>您的回饋:</h3>
                    <textarea id="feedback" placeholder="請輸入您的回饋..."></textarea>
                </div>
                <button onclick="submitFeedback()">提交回饋</button>
            </div>
            <script>
                const ws = new WebSocket('ws://localhost:{self.port}/ws/{session_id}');
                function submitFeedback() {{
                    const feedback = document.getElementById('feedback').value;
                    ws.send(JSON.stringify({{
                        type: 'submit_feedback',
                        feedback: feedback,
                        images: []
                    }}));
                    alert('回饋已提交！');
                }}
            </script>
        </body>
        </html>
        """


# ===== 全域管理器 =====
_web_ui_manager: Optional[WebUIManager] = None

def get_web_ui_manager() -> WebUIManager:
    """獲取全域 Web UI 管理器"""
    global _web_ui_manager
    if _web_ui_manager is None:
        _web_ui_manager = WebUIManager()
        _web_ui_manager.start_server()
    return _web_ui_manager

async def launch_web_feedback_ui(project_directory: str, summary: str) -> dict:
    """啟動 Web 回饋 UI 並等待回饋"""
    manager = get_web_ui_manager()
    
    # 創建會話
    session_id = manager.create_session(project_directory, summary)
    session_url = f"http://{manager.host}:{manager.port}/session/{session_id}"
    
    debug_log(f"🌐 Web UI 已啟動: {session_url}")
    
    # 開啟瀏覽器
    manager.open_browser(session_url)
    
    try:
        # 等待用戶回饋
        session = manager.get_session(session_id)
        if not session:
            raise RuntimeError("會話創建失敗")
            
        result = await session.wait_for_feedback(timeout=600)  # 10分鐘超時
        return result
        
    except TimeoutError:
        debug_log("⏰ 等待用戶回饋超時")
        return {
            "logs": "",
            "interactive_feedback": "回饋超時",
            "images": []
        }
    except Exception as e:
        debug_log(f"❌ Web UI 錯誤: {e}")
        return {
            "logs": "",
            "interactive_feedback": f"錯誤: {str(e)}",
            "images": []
        }
    finally:
        # 清理會話
        manager.remove_session(session_id)

def stop_web_ui():
    """停止 Web UI"""
    global _web_ui_manager
    if _web_ui_manager:
        # 清理所有會話
        for session_id in list(_web_ui_manager.sessions.keys()):
            _web_ui_manager.remove_session(session_id)
        _web_ui_manager = None


# ===== 主程式入口 =====
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="啟動 Interactive Feedback MCP Web UI")
    parser.add_argument("--host", default="127.0.0.1", help="主機地址")
    parser.add_argument("--port", type=int, default=8765, help="端口")
    parser.add_argument("--project-directory", default=os.getcwd(), help="專案目錄")
    parser.add_argument("--summary", default="測試 Web UI 功能", help="任務摘要")
    
    args = parser.parse_args()
    
    async def main():
        manager = WebUIManager(args.host, args.port)
        manager.start_server()
        
        session_id = manager.create_session(args.project_directory, args.summary)
        session_url = f"http://{args.host}:{args.port}/session/{session_id}"
        
        debug_log(f"🌐 Web UI 已啟動: {session_url}")
        manager.open_browser(session_url)
        
        try:
            # 保持運行
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            debug_log("\n👋 Web UI 已停止")
    
    asyncio.run(main()) 

# === 工具函數 ===
def debug_log(message: str) -> None:
    """輸出調試訊息到標準錯誤，避免污染標準輸出"""
    # 只在啟用調試模式時才輸出，避免干擾 MCP 通信
    if not os.getenv("MCP_DEBUG", "").lower() in ("true", "1", "yes", "on"):
        return
        
    try:
        print(f"[WEB_UI] {message}", file=sys.stderr, flush=True)
    except Exception:
        # 靜默失敗，不影響主程序
        pass 