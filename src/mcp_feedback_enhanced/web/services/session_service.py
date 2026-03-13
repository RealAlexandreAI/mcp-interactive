#!/usr/bin/env python3
"""
Session shaping helpers for API route responses.
"""

from typing import Any


class SessionService:
    """Builds API response payloads from session objects."""

    @staticmethod
    def build_session_status_payload(current_session) -> dict[str, Any]:
        if not current_session:
            return {
                "has_session": False,
                "status": "no_session",
            }

        return {
            "has_session": True,
            "status": "active",
            "session_info": {
                "project_directory": current_session.project_directory,
                "summary": current_session.summary,
                "feedback_completed": current_session.feedback_completed.is_set(),
            },
        }

    @staticmethod
    def build_current_session_payload(current_session) -> dict[str, Any]:
        return {
            "session_id": current_session.session_id,
            "project_directory": current_session.project_directory,
            "summary": current_session.summary,
            "feedback_completed": current_session.feedback_completed.is_set(),
            "command_logs": list(current_session.command_logs),
            "images_count": len(current_session.images),
        }

    @staticmethod
    def build_all_sessions_payload(manager) -> dict[str, Any]:
        sessions_data = []
        for session in manager.sessions.values():
            sessions_data.append(
                {
                    "session_id": session.session_id,
                    "project_directory": session.project_directory,
                    "summary": session.summary,
                    "status": session.status.value,
                    "status_message": session.status_message,
                    "created_at": int(session.created_at * 1000),
                    "last_activity": int(session.last_activity * 1000),
                    "feedback_completed": session.feedback_completed.is_set(),
                    "has_websocket": session.websocket is not None,
                    "is_current": session == manager.current_session,
                    "user_messages": list(session.user_messages),
                }
            )

        sessions_data.sort(key=lambda x: x["created_at"], reverse=True)
        return {"sessions": sessions_data}
