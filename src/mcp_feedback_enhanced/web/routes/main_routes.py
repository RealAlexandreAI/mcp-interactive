#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主要路由處理
============

設置 Web UI 的主要路由和處理邏輯。
"""

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

from ...debug import web_debug_log as debug_log
from ... import __version__

if TYPE_CHECKING:
    from ..main import WebUIManager


def setup_routes(manager: 'WebUIManager'):
    """設置路由"""
    
    @manager.app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """首頁"""
        return manager.templates.TemplateResponse("index.html", {
            "request": request,
            "title": "Interactive Feedback MCP"
        })

    @manager.app.get("/session/{session_id}", response_class=HTMLResponse)
    async def feedback_session(request: Request, session_id: str):
        """回饋會話頁面"""
        session = manager.get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={"error": "會話不存在"}
            )
        
        return manager.templates.TemplateResponse("feedback.html", {
            "request": request,
            "session_id": session_id,
            "project_directory": session.project_directory,
            "summary": session.summary,
            "title": "Interactive Feedback - 回饋收集",
            "version": __version__
        })

    @manager.app.get("/api/translations")
    async def get_translations():
        """獲取翻譯數據 - 從 Web 專用翻譯檔案載入"""
        translations = {}
        
        # 獲取 Web 翻譯檔案目錄
        web_locales_dir = Path(__file__).parent.parent / "locales"
        supported_languages = ["zh-TW", "zh-CN", "en"]
        
        for lang_code in supported_languages:
            lang_dir = web_locales_dir / lang_code
            translation_file = lang_dir / "translation.json"
            
            try:
                if translation_file.exists():
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        lang_data = json.load(f)
                        translations[lang_code] = lang_data
                        debug_log(f"成功載入 Web 翻譯: {lang_code}")
                else:
                    debug_log(f"Web 翻譯檔案不存在: {translation_file}")
                    translations[lang_code] = {}
            except Exception as e:
                debug_log(f"載入 Web 翻譯檔案失敗 {lang_code}: {e}")
                translations[lang_code] = {}
        
        debug_log(f"Web 翻譯 API 返回 {len(translations)} 種語言的數據")
        return JSONResponse(content=translations)

    @manager.app.websocket("/ws/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str):
        """WebSocket 端點"""
        session = manager.get_session(session_id)
        if not session:
            await websocket.close(code=4004, reason="會話不存在")
            return
        
        await websocket.accept()
        session.websocket = websocket
        
        debug_log(f"WebSocket 連接建立: {session_id}")
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                await handle_websocket_message(manager, session, message)
                
        except WebSocketDisconnect:
            debug_log(f"WebSocket 連接斷開: {session_id}")
        except Exception as e:
            debug_log(f"WebSocket 錯誤: {e}")
        finally:
            session.websocket = None

    @manager.app.post("/api/save-settings")
    async def save_settings(request: Request):
        """保存設定到檔案"""
        try:
            data = await request.json()
            
            # 構建設定檔案路徑
            settings_file = Path.cwd() / ".mcp_feedback_settings.json"
            
            # 保存設定到檔案
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            debug_log(f"設定已保存到: {settings_file}")
            
            return JSONResponse(content={"status": "success", "message": "設定已保存"})
            
        except Exception as e:
            debug_log(f"保存設定失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": f"保存失敗: {str(e)}"}
            )

    @manager.app.get("/api/load-settings")
    async def load_settings():
        """從檔案載入設定"""
        try:
            settings_file = Path.cwd() / ".mcp_feedback_settings.json"
            
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                debug_log(f"設定已從檔案載入: {settings_file}")
                return JSONResponse(content=settings)
            else:
                debug_log("設定檔案不存在，返回空設定")
                return JSONResponse(content={})
                
        except Exception as e:
            debug_log(f"載入設定失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": f"載入失敗: {str(e)}"}
            )

    @manager.app.post("/api/clear-settings")
    async def clear_settings():
        """清除設定檔案"""
        try:
            settings_file = Path.cwd() / ".mcp_feedback_settings.json"
            
            if settings_file.exists():
                settings_file.unlink()
                debug_log(f"設定檔案已刪除: {settings_file}")
            else:
                debug_log("設定檔案不存在，無需刪除")
            
            return JSONResponse(content={"status": "success", "message": "設定已清除"})
            
        except Exception as e:
            debug_log(f"清除設定失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": f"清除失敗: {str(e)}"}
            )


async def handle_websocket_message(manager: 'WebUIManager', session, data: dict):
    """處理 WebSocket 消息"""
    message_type = data.get("type")
    
    if message_type == "submit_feedback":
        # 提交回饋
        feedback = data.get("feedback", "")
        images = data.get("images", [])
        await session.submit_feedback(feedback, images)
        
    elif message_type == "run_command":
        # 執行命令
        command = data.get("command", "")
        if command.strip():
            await session.run_command(command)
        
    else:
        debug_log(f"未知的消息類型: {message_type}") 