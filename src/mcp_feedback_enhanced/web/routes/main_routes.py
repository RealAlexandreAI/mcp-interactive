#!/usr/bin/env python3
"""
主要路由處理
============

設置 Web UI 的主要路由和處理邏輯。
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

from ... import __version__
from ...debug import web_debug_log as debug_log
from ..constants import get_message_code as get_msg_code
from ..services import SessionService, SettingsService, handle_session_message


if TYPE_CHECKING:
    from ..main import WebUIManager

# Translation data cached at module level to avoid per-request disk reads.
# Cache is populated on first access and never invalidated (translations
# don't change at runtime).
_translations_cache: dict | None = None


def _load_translations() -> dict:
    """Load translation data from JSON files (cached after first call)."""
    global _translations_cache
    if _translations_cache is not None:
        return _translations_cache

    translations = {}
    web_locales_dir = Path(__file__).parent.parent / "locales"
    supported_languages = ["zh-CN", "en"]

    for lang_code in supported_languages:
        lang_dir = web_locales_dir / lang_code
        translation_file = lang_dir / "translation.json"
        try:
            if translation_file.exists():
                with open(translation_file, encoding="utf-8") as f:
                    translations[lang_code] = json.load(f)
                    debug_log(f"成功載入 Web 翻譯: {lang_code}")
            else:
                debug_log(f"Web 翻譯檔案不存在: {translation_file}")
                translations[lang_code] = {}
        except Exception as e:
            debug_log(f"載入 Web 翻譯檔案失敗 {lang_code}: {e}")
            translations[lang_code] = {}

    _translations_cache = translations
    return translations


# 使用統一的訊息代碼系統
# 從 ..constants 導入的 get_msg_code 函數會處理所有訊息代碼
# 舊的 key 會自動映射到新的常量


def setup_routes(manager: "WebUIManager"):
    """設置路由"""
    settings_service = SettingsService()
    session_service = SessionService()

    @manager.app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """統一回饋頁面 - 重構後的主頁面"""
        # 獲取當前活躍會話
        current_session = manager.get_current_session()

        if not current_session:
            # 沒有活躍會話時顯示等待頁面
            return manager.templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "title": "MCP Feedback Enhanced",
                    "has_session": False,
                    "version": __version__,
                },
            )

        # 有活躍會話時顯示回饋頁面
        # 載入用戶的佈局模式設定
        try:
            layout_mode = settings_service.load_layout_mode()
            debug_log(f"從設定檔案載入佈局模式: {layout_mode}")
        except Exception as e:
            debug_log(f"載入佈局設定失敗: {e}，使用預設佈局模式: combined-horizontal")
            layout_mode = "combined-horizontal"

        return manager.templates.TemplateResponse(
            "feedback.html",
            {
                "request": request,
                "project_directory": current_session.project_directory,
                "summary": current_session.summary,
                "title": "Interactive Feedback - 回饋收集",
                "version": __version__,
                "has_session": True,
                "layout_mode": layout_mode,
            },
        )

    @manager.app.get("/api/translations")
    async def get_translations():
        """獲取翻譯數據 - 從緩存返回"""
        translations = _load_translations()
        return JSONResponse(content=translations)

    @manager.app.get("/api/session-status")
    async def get_session_status(request: Request):
        """獲取當前會話狀態"""
        current_session = manager.get_current_session()

        if not current_session:
            return JSONResponse(
                content={
                    "has_session": False,
                    "status": "no_session",
                    "messageCode": get_msg_code("no_active_session"),
                }
            )

        return JSONResponse(content=session_service.build_session_status_payload(current_session))

    @manager.app.get("/api/current-session")
    async def get_current_session(request: Request):
        """獲取當前會話詳細信息"""
        current_session = manager.get_current_session()

        if not current_session:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "No active session",
                    "messageCode": get_msg_code("no_active_session"),
                },
            )

        return JSONResponse(
            content=session_service.build_current_session_payload(current_session)
        )

    @manager.app.get("/api/all-sessions")
    async def get_all_sessions(request: Request):
        """獲取所有會話的實時狀態"""

        try:
            payload = session_service.build_all_sessions_payload(manager)
            debug_log(f"返回 {len(payload['sessions'])} 個會話的實時狀態")
            return JSONResponse(content=payload)

        except Exception as e:
            debug_log(f"獲取所有會話狀態失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": f"Failed to get sessions: {e!s}",
                    "messageCode": get_msg_code("get_sessions_failed"),
                },
            )

    @manager.app.post("/api/add-user-message")
    async def add_user_message(request: Request):
        """添加用戶消息到當前會話"""

        try:
            data = await request.json()
            current_session = manager.get_current_session()

            if not current_session:
                return JSONResponse(
                    status_code=404,
                    content={
                        "error": "No active session",
                        "messageCode": get_msg_code("no_active_session"),
                    },
                )

            # 添加用戶消息到會話
            current_session.add_user_message(data)

            debug_log(f"用戶消息已添加到會話 {current_session.session_id}")
            return JSONResponse(
                content={
                    "status": "success",
                    "messageCode": get_msg_code("user_message_recorded"),
                }
            )

        except Exception as e:
            debug_log(f"添加用戶消息失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": f"Failed to add user message: {e!s}",
                    "messageCode": get_msg_code("add_user_message_failed"),
                },
            )

    @manager.app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket, lang: str = "zh-CN"):
        """WebSocket 端點 - 重構後移除 session_id 依賴"""
        # 獲取當前活躍會話
        session = manager.get_current_session()
        if not session:
            await websocket.close(code=4004, reason="No active session")
            return

        await websocket.accept()

        # 語言由前端處理，不需要在後端設置
        debug_log(f"WebSocket 連接建立，語言由前端處理: {lang}")

        # 檢查會話是否已有 WebSocket 連接
        if session.websocket and session.websocket != websocket:
            debug_log("會話已有 WebSocket 連接，替換為新連接")

        session.websocket = websocket
        debug_log(f"WebSocket 連接建立: 當前活躍會話 {session.session_id}")

        # 發送連接成功消息
        try:
            await websocket.send_json(
                {
                    "type": "connection_established",
                    "messageCode": get_msg_code("websocket_connected"),
                }
            )

            # 檢查是否有待發送的會話更新
            if getattr(manager, "_pending_session_update", False):
                debug_log("檢測到待發送的會話更新，準備發送通知")
                await websocket.send_json(
                    {
                        "type": "session_updated",
                        "action": "new_session_created",
                        "messageCode": get_msg_code("new_session_created"),
                        "session_info": {
                            "project_directory": session.project_directory,
                            "summary": session.summary,
                            "session_id": session.session_id,
                        },
                    }
                )
                manager._pending_session_update = False
                debug_log("✅ 已發送會話更新通知到前端")
            else:
                # 發送當前會話狀態
                await websocket.send_json(
                    {"type": "status_update", "status_info": session.get_status_info()}
                )
                debug_log("已發送當前會話狀態到前端")

        except Exception as e:
            debug_log(f"發送連接確認失敗: {e}")

        try:
            while True:
                data = await websocket.receive_text()

                # Enforce message size limit (50 MB) to prevent memory exhaustion
                if len(data) > 50 * 1024 * 1024:
                    await websocket.close(code=1009, reason="Message too large")
                    debug_log("WebSocket message exceeds 50 MB limit, closing connection")
                    return

                message = json.loads(data)

                # 重新獲取當前會話，以防會話已切換
                current_session = manager.get_current_session()
                if current_session and current_session.websocket == websocket:
                    await handle_websocket_message(manager, current_session, message)
                else:
                    debug_log("會話已切換或 WebSocket 連接不匹配，忽略消息")
                    break

        except WebSocketDisconnect:
            debug_log("WebSocket 連接正常斷開")
        except ConnectionResetError:
            debug_log("WebSocket 連接被重置")
        except Exception as e:
            debug_log(f"WebSocket 錯誤: {e}")
        finally:
            # 安全清理 WebSocket 連接
            current_session = manager.get_current_session()
            if current_session and current_session.websocket == websocket:
                current_session.websocket = None
                debug_log("已清理會話中的 WebSocket 連接")

    @manager.app.post("/api/save-settings")
    async def save_settings(request: Request):
        """保存設定到檔案"""

        # Allowed top-level setting keys (whitelist)
        _ALLOWED_SETTINGS_KEYS = {
            "layoutMode", "language", "logLevel", "theme",
            "notificationEnabled", "notificationVolume", "notificationSound",
            "autoSubmit", "autoSubmitDelay", "showTimestamp",
            "sessionHistoryRetention", "imageQuality",
            "fontSize", "fontFamily", "promptTemplates",
            "sessionTimeout", "sessionTimeoutEnabled",
        }

        try:
            data = await request.json()

            if not isinstance(data, dict):
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "message": "Invalid settings format"},
                )

            settings_service.save_settings(data, _ALLOWED_SETTINGS_KEYS)
            debug_log(f"設定已保存到: {settings_service.settings_file}")

            return JSONResponse(
                content={
                    "status": "success",
                    "messageCode": get_msg_code("settings_saved"),
                }
            )

        except Exception as e:
            debug_log(f"保存設定失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Save failed: {e!s}",
                    "messageCode": get_msg_code("save_failed"),
                },
            )

    @manager.app.get("/api/load-settings")
    async def load_settings(request: Request):
        """從檔案載入設定"""

        try:
            settings = settings_service.load_settings()
            if settings:
                debug_log(f"設定已從檔案載入: {settings_service.settings_file}")
                return JSONResponse(content=settings)
            debug_log("設定檔案不存在，返回空設定")
            return JSONResponse(content={})

        except Exception as e:
            debug_log(f"載入設定失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Load failed: {e!s}",
                    "messageCode": get_msg_code("load_failed"),
                },
            )

    @manager.app.post("/api/clear-settings")
    async def clear_settings(request: Request):
        """清除設定檔案"""

        try:
            if settings_service.clear_settings():
                debug_log(f"設定檔案已刪除: {settings_service.settings_file}")
            else:
                debug_log("設定檔案不存在，無需刪除")

            return JSONResponse(
                content={
                    "status": "success",
                    "messageCode": get_msg_code("settings_cleared"),
                }
            )

        except Exception as e:
            debug_log(f"清除設定失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Clear failed: {e!s}",
                    "messageCode": get_msg_code("clear_failed"),
                },
            )

    @manager.app.get("/api/load-session-history")
    async def load_session_history(request: Request):
        """從檔案載入會話歷史"""

        try:
            payload = settings_service.load_session_history()
            if payload["sessions"] or payload["lastCleanup"] != 0:
                debug_log(f"會話歷史已從檔案載入: {settings_service.history_file}")
            else:
                debug_log("會話歷史檔案不存在，返回空歷史")
            return JSONResponse(content=payload)

        except Exception as e:
            debug_log(f"載入會話歷史失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Load failed: {e!s}",
                    "messageCode": get_msg_code("load_failed"),
                },
            )

    @manager.app.post("/api/save-session-history")
    async def save_session_history(request: Request):
        """保存會話歷史到檔案"""

        try:
            data = await request.json()

            session_count = settings_service.save_session_history(data)
            debug_log(f"會話歷史已保存到: {settings_service.history_file}")
            debug_log(f"保存了 {session_count} 個會話記錄")

            return JSONResponse(
                content={
                    "status": "success",
                    "messageCode": get_msg_code("session_history_saved"),
                    "params": {"count": session_count},
                }
            )

        except Exception as e:
            debug_log(f"保存會話歷史失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Save failed: {e!s}",
                    "messageCode": get_msg_code("save_failed"),
                },
            )

    @manager.app.get("/api/log-level")
    async def get_log_level(request: Request):
        """獲取日誌等級設定"""

        try:
            log_level = settings_service.get_log_level("INFO")
            debug_log(f"從設定檔案載入日誌等級: {log_level}")
            return JSONResponse(content={"logLevel": log_level})

        except Exception as e:
            debug_log(f"獲取日誌等級失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": f"Failed to get log level: {e!s}",
                    "messageCode": get_msg_code("get_log_level_failed"),
                },
            )

    @manager.app.post("/api/log-level")
    async def set_log_level(request: Request):
        """設定日誌等級"""

        try:
            data = await request.json()
            log_level = data.get("logLevel")

            if not log_level or log_level not in ["DEBUG", "INFO", "WARN", "ERROR"]:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Invalid log level",
                        "messageCode": get_msg_code("invalid_log_level"),
                    },
                )

            settings_service.set_log_level(log_level)
            debug_log(f"日誌等級已設定為: {log_level}")

            return JSONResponse(
                content={
                    "status": "success",
                    "logLevel": log_level,
                    "messageCode": get_msg_code("log_level_updated"),
                }
            )

        except Exception as e:
            debug_log(f"設定日誌等級失敗: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Set failed: {e!s}",
                    "messageCode": get_msg_code("set_failed"),
                },
            )


async def handle_websocket_message(manager: "WebUIManager", session, data: dict):
    """處理 WebSocket 消息"""
    _ = manager  # keep signature for backward compatibility
    await handle_session_message(session, data)


async def _delayed_server_stop(manager: "WebUIManager"):
    """延遲停止服務器"""
    import asyncio

    await asyncio.sleep(5)  # 等待 5 秒讓前端有時間關閉
    from ..main import stop_web_ui

    stop_web_ui()
    debug_log("Web UI 服務器已因用戶超時而停止")
