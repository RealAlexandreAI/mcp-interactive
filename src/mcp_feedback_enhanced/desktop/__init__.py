#!/usr/bin/env python3
"""
桌面應用模組
===========

此模組提供 Electron 桌面應用整合功能，實現零前端改動的桌面化方案。

主要功能：
- Electron 進程管理
- 與現有 Web UI 的無縫整合
- 跨平台桌面應用支援
- 環境變數控制

作者: Augment Agent
版本: 2.3.0
"""

import os
import sys
from typing import Optional

from ..debug import web_debug_log as debug_log


def is_desktop_available() -> bool:
    """
    檢測桌面環境是否可用

    Returns:
        bool: True 表示桌面環境可用
    """
    try:
        # 檢查是否有 Node.js 環境
        import subprocess

        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode != 0:
            debug_log("Node.js 不可用，桌面模式不可用")
            return False

        # 檢查是否為遠程環境
        from ..server import is_remote_environment

        if is_remote_environment():
            debug_log("檢測到遠程環境，桌面模式不適用")
            return False

        debug_log("桌面環境檢測通過")
        return True

    except (subprocess.TimeoutExpired, FileNotFoundError, ImportError) as e:
        debug_log(f"桌面環境檢測失敗: {e}")
        return False
    except Exception as e:
        debug_log(f"桌面環境檢測出現未預期錯誤: {e}")
        return False


async def launch_desktop_app(project_dir: str, summary: str, timeout: int) -> dict:
    """
    啟動桌面應用收集回饋

    Args:
        project_dir: 專案目錄路徑
        summary: AI 工作摘要
        timeout: 超時時間（秒）

    Returns:
        dict: 收集到的回饋資料
    """
    debug_log("啟動桌面應用...")

    try:
        # 創建 Electron 管理器
        from .electron_manager import ElectronManager

        manager = ElectronManager()

        # 首先啟動 Web 服務器（桌面應用需要載入 Web UI）
        from ..web import get_web_ui_manager

        web_manager = get_web_ui_manager()

        # 創建會話
        web_manager.create_session(project_dir, summary)
        session = web_manager.get_current_session()

        if not session:
            raise RuntimeError("無法創建回饋會話")

        # 啟動 Web 服務器（如果尚未啟動）
        if not web_manager.server_thread or not web_manager.server_thread.is_alive():
            debug_log("啟動 Web 服務器...")
            web_manager.start_server()

        # 等待 Web 服務器完全啟動
        import time

        debug_log("等待 Web 服務器啟動...")
        time.sleep(5)  # 增加等待時間

        # 驗證 Web 服務器是否正常運行
        if web_manager.server_thread and web_manager.server_thread.is_alive():
            debug_log(f"✅ Web 服務器成功啟動在端口: {web_manager.port}")
        else:
            raise RuntimeError("Web 服務器啟動失敗")

        # 設置 Web 服務器端口
        manager.set_web_server_port(web_manager.port)
        debug_log(f"桌面應用將連接到: http://localhost:{web_manager.port}")

        # 啟動桌面應用
        desktop_success = await manager.launch_desktop_app(summary, project_dir)

        if desktop_success:
            debug_log("桌面應用啟動成功，等待用戶回饋...")
            try:
                # 等待用戶回饋
                result = await session.wait_for_feedback(timeout)
                debug_log("收到桌面應用用戶回饋")
                return result
            finally:
                # 確保 Electron 進程被正確清理
                debug_log("清理 Electron 進程...")
                await manager.cleanup_async()
                debug_log("Electron 進程清理完成")
        else:
            debug_log("桌面應用啟動失敗，回退到 Web 模式")
            # 回退到 Web 模式
            from ..web import launch_web_feedback_ui

            return await launch_web_feedback_ui(project_dir, summary, timeout)

    except Exception as e:
        debug_log(f"桌面應用啟動過程中出錯: {e}")
        debug_log("回退到 Web 模式")
        # 確保清理 Electron 進程
        try:
            if "manager" in locals():
                await manager.cleanup_async()
        except Exception as cleanup_error:
            debug_log(f"清理 Electron 進程時出錯: {cleanup_error}")

        # 回退到 Web 模式
        from ..web import launch_web_feedback_ui

        return await launch_web_feedback_ui(project_dir, summary, timeout)


class ElectronManager:
    """Electron 管理器 - 預留接口"""

    def __init__(self):
        """初始化 Electron 管理器"""
        self.electron_process = None
        self.web_server_port = None
        debug_log("ElectronManager 初始化（預留實現）")

    async def launch_desktop_app(self, summary: str, project_dir: str) -> bool:
        """
        啟動桌面應用

        Args:
            summary: AI 工作摘要
            project_dir: 專案目錄

        Returns:
            bool: 啟動是否成功
        """
        debug_log("桌面應用啟動功能尚未實現")
        debug_log("此功能將在階段 2 中實現")
        return False

    def is_available(self) -> bool:
        """檢查桌面管理器是否可用"""
        return is_desktop_available()


# 主要導出介面
__all__ = ["ElectronManager", "is_desktop_available", "launch_desktop_app"]
