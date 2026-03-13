#!/usr/bin/env python3
"""
Settings persistence service for web routes.
"""

import json
import time
from pathlib import Path
from typing import Any


class SettingsService:
    """Encapsulates local config/settings file operations."""

    def __init__(self, config_dir: Path | None = None):
        self.config_dir = config_dir or (Path.home() / ".config" / "mcp-feedback-enhanced")

    @property
    def settings_file(self) -> Path:
        return self.config_dir / "ui_settings.json"

    @property
    def history_file(self) -> Path:
        return self.config_dir / "session_history.json"

    def ensure_config_dir(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_layout_mode(self, default: str = "combined-horizontal") -> str:
        if not self.settings_file.exists():
            return default
        with open(self.settings_file, encoding="utf-8") as f:
            settings = json.load(f)
        return str(settings.get("layoutMode", default))

    def save_settings(
        self, data: dict[str, Any], allowed_keys: set[str]
    ) -> dict[str, Any]:
        sanitized = {k: v for k, v in data.items() if k in allowed_keys}
        self.ensure_config_dir()
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(sanitized, f, ensure_ascii=False, indent=2)
        return sanitized

    def load_settings(self) -> dict[str, Any]:
        if not self.settings_file.exists():
            return {}
        with open(self.settings_file, encoding="utf-8") as f:
            return json.load(f)

    def clear_settings(self) -> bool:
        if self.settings_file.exists():
            self.settings_file.unlink()
            return True
        return False

    def load_session_history(self) -> dict[str, Any]:
        if not self.history_file.exists():
            return {"sessions": [], "lastCleanup": 0}

        with open(self.history_file, encoding="utf-8") as f:
            history_data = json.load(f)

        if isinstance(history_data, dict):
            sessions = history_data.get("sessions", [])
            last_cleanup = history_data.get("lastCleanup", 0)
        else:
            sessions = history_data if isinstance(history_data, list) else []
            last_cleanup = 0

        return {"sessions": sessions, "lastCleanup": last_cleanup}

    def save_session_history(self, data: dict[str, Any]) -> int:
        self.ensure_config_dir()
        history_data = {
            "version": "1.0",
            "sessions": data.get("sessions", []),
            "lastCleanup": data.get("lastCleanup", 0),
            "savedAt": int(time.time() * 1000),
        }
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        return len(history_data["sessions"])

    def get_log_level(self, default: str = "INFO") -> str:
        settings = self.load_settings()
        return str(settings.get("logLevel", default))

    def set_log_level(self, level: str) -> None:
        self.ensure_config_dir()
        settings = {}
        if self.settings_file.exists():
            with open(self.settings_file, encoding="utf-8") as f:
                settings = json.load(f)
        settings["logLevel"] = level
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
