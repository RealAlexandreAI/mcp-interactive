#!/usr/bin/env python3
"""
WebSocket business-message handling.
"""

import time
from typing import Any

from ...debug import web_debug_log as debug_log


async def handle_session_message(session, data: dict[str, Any]) -> None:
    """Handle one websocket message for the active session."""
    message_type = data.get("type")

    if message_type == "submit_feedback":
        feedback = data.get("feedback", "")
        images = data.get("images", [])
        settings = data.get("settings", {})
        await session.submit_feedback(feedback, images, settings)

    elif message_type == "run_command":
        command = data.get("command", "")
        if command.strip():
            await session.run_command(command)

    elif message_type == "get_status":
        if session.websocket:
            try:
                await session.websocket.send_json(
                    {"type": "status_update", "status_info": session.get_status_info()}
                )
            except Exception as e:
                debug_log(f"發送狀態更新失敗: {e}")

    elif message_type == "heartbeat":
        now = time.time()
        session.last_heartbeat = now
        session.last_activity = now
        if session.websocket:
            try:
                await session.websocket.send_json(
                    {
                        "type": "heartbeat_response",
                        "timestamp": data.get("timestamp", 0),
                    }
                )
            except Exception as e:
                debug_log(f"發送心跳回應失敗: {e}")

    elif message_type == "user_timeout":
        debug_log(f"收到用戶超時通知: {session.session_id}")
        await session._cleanup_resources_on_timeout()

    elif message_type == "pong":
        debug_log(f"收到 pong 回應，時間戳: {data.get('timestamp', 'N/A')}")

    elif message_type == "update_timeout_settings":
        settings = data.get("settings", {})
        debug_log(f"收到超時設定更新: {settings}")
        if settings.get("enabled"):
            session.update_timeout_settings(
                enabled=True, timeout_seconds=settings.get("seconds", 3600)
            )
        else:
            session.update_timeout_settings(enabled=False)

    elif message_type == "pause_timeout":
        debug_log(f"收到暫停超時請求: {session.session_id}")
        session.pause_timeout_timers()
        debug_log("會話超時計時器已暫停（含 MCP 等待超時）")

    elif message_type == "resume_timeout":
        debug_log(f"收到恢復超時請求: {session.session_id}")
        session.resume_timeout_timers()

    else:
        debug_log(f"未知的消息類型: {message_type}")
