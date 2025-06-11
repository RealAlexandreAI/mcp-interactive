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

import asyncio
import os
import sys
import time
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
    啟動桌面應用收集回饋（優化版本，支援並行啟動）

    Args:
        project_dir: 專案目錄路徑
        summary: AI 工作摘要
        timeout: 超時時間（秒）

    Returns:
        dict: 收集到的回饋資料
    """
    debug_log("啟動桌面應用（並行優化版本）...")
    start_time = time.time()

    try:
        # 並行任務1：創建 Electron 管理器和依賴檢查
        async def init_electron_manager():
            from .electron_manager import ElectronManager

            manager = ElectronManager()
            # 預先檢查依賴（如果實現了異步版本）
            if hasattr(manager, "ensure_dependencies_async"):
                await manager.ensure_dependencies_async()
            return manager

        # 並行任務2：初始化 Web 管理器和會話
        async def init_web_manager():
            from ..web import get_web_ui_manager

            web_manager = get_web_ui_manager()

            # 確保異步初始化完成
            if hasattr(web_manager, "_init_async_components"):
                await web_manager._init_async_components()

            # 創建會話
            web_manager.create_session(project_dir, summary)
            session = web_manager.get_current_session()

            if not session:
                raise RuntimeError("無法創建回饋會話")

            return web_manager, session

        # 並行執行初始化任務
        debug_log("並行執行初始化任務...")
        init_results = await asyncio.gather(
            init_electron_manager(), init_web_manager(), return_exceptions=True
        )

        # 檢查初始化結果
        if isinstance(init_results[0], Exception):
            raise init_results[0]
        if isinstance(init_results[1], Exception):
            raise init_results[1]

        manager = init_results[0]
        web_result = init_results[1]
        if isinstance(web_result, tuple) and len(web_result) == 2:
            web_manager, session = web_result
        else:
            raise RuntimeError("Web 管理器初始化返回格式錯誤")

        init_time = time.time() - start_time
        debug_log(f"並行初始化完成，耗時: {init_time:.2f}秒")

        # 並行任務3：啟動 Web 服務器
        async def start_web_server():
            if (
                not web_manager.server_thread
                or not web_manager.server_thread.is_alive()
            ):
                debug_log("啟動 Web 服務器...")
                web_manager.start_server()

            # 智能等待服務器啟動（減少固定等待時間）
            await _wait_for_server_startup(web_manager)
            return web_manager.port

        # 並行任務4：準備 Electron 環境
        async def prepare_electron():
            # 如果有預熱方法，在這裡調用
            if hasattr(manager, "preheat_async"):
                await manager.preheat_async()
            return True

        # 並行執行服務器啟動和 Electron 準備
        debug_log("並行啟動 Web 服務器和準備 Electron 環境...")
        startup_results = await asyncio.gather(
            start_web_server(), prepare_electron(), return_exceptions=True
        )

        if isinstance(startup_results[0], Exception):
            raise startup_results[0]
        if isinstance(startup_results[1], Exception):
            debug_log(f"Electron 預熱失敗（非致命）: {startup_results[1]}")

        server_port = startup_results[0]

        # 類型檢查：確保 manager 不是 Exception
        if isinstance(manager, Exception):
            raise manager

        # 設置 Web 服務器端口
        manager.set_web_server_port(server_port)  # type: ignore[union-attr]
        debug_log(f"桌面應用將連接到: http://localhost:{server_port}")

        # 啟動桌面應用
        desktop_success = await manager.launch_desktop_app(summary, project_dir)  # type: ignore[union-attr]

        if desktop_success:
            total_startup_time = time.time() - start_time
            debug_log(
                f"桌面應用啟動成功，總耗時: {total_startup_time:.2f}秒，等待用戶回饋..."
            )
            try:
                # 等待用戶回饋
                result = await session.wait_for_feedback(timeout)
                debug_log("收到桌面應用用戶回饋")
                return result  # type: ignore[no-any-return]
            finally:
                # 確保 Electron 進程被正確清理
                debug_log("清理 Electron 進程...")
                if not isinstance(manager, Exception):
                    await manager.cleanup_async()  # type: ignore[union-attr]
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
            if "manager" in locals() and not isinstance(manager, Exception):
                await manager.cleanup_async()  # type: ignore[union-attr]
        except Exception as cleanup_error:
            debug_log(f"清理 Electron 進程時出錯: {cleanup_error}")

        # 回退到 Web 模式
        from ..web import launch_web_feedback_ui

        return await launch_web_feedback_ui(project_dir, summary, timeout)


async def _wait_for_server_startup(web_manager, max_wait: int = 10) -> bool:
    """智能等待服務器啟動"""
    debug_log("智能等待 Web 服務器啟動...")

    for attempt in range(max_wait):
        if web_manager.server_thread and web_manager.server_thread.is_alive():
            # 嘗試連接測試
            try:
                import aiohttp

                timeout = aiohttp.ClientTimeout(total=1)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(
                        f"http://{web_manager.host}:{web_manager.port}/"
                    ) as response:
                        if response.status == 200:
                            debug_log(
                                f"✅ Web 服務器啟動驗證成功，耗時: {attempt + 1}秒"
                            )
                            return True
            except Exception:
                pass

        await asyncio.sleep(1)
        debug_log(f"等待 Web 服務器啟動... ({attempt + 1}/{max_wait})")

    # 回退到線程檢查
    if web_manager.server_thread and web_manager.server_thread.is_alive():
        debug_log("✅ Web 服務器線程運行正常（回退驗證）")
        return True

    debug_log("❌ Web 服務器啟動失敗")
    return False


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
