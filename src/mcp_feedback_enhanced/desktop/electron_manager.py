#!/usr/bin/env python3
"""
Electron 管理器
==============

此模組負責管理 Electron 進程的生命週期，包括：
- Electron 應用啟動和停止
- 與 Web 服務器的整合
- 依賴檢測和自動安裝
- 進程管理和錯誤處理

此文件為階段 1 的預留實現，完整功能將在階段 2 中實現。

作者: Augment Agent
版本: 2.3.0
"""

import asyncio
import os
import platform
import signal
import subprocess
import warnings
from pathlib import Path

from ..debug import web_debug_log as debug_log
from ..utils.error_handler import ErrorHandler, ErrorType


def suppress_windows_asyncio_warnings():
    """抑制 Windows 上的 asyncio 相關警告"""
    if platform.system().lower() == "windows":
        # 抑制 ResourceWarning 和 asyncio 相關警告
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", message=".*unclosed transport.*")
        warnings.filterwarnings("ignore", message=".*I/O operation on closed pipe.*")
        # 設置環境變數抑制 asyncio 警告
        os.environ.setdefault("PYTHONWARNINGS", "ignore::ResourceWarning")
        debug_log("已設置 Windows asyncio 警告抑制")


class ElectronManager:
    """Electron 進程管理器 - 跨平台支持"""

    def __init__(self):
        """初始化 Electron 管理器"""
        self.electron_process: asyncio.subprocess.Process | None = None
        self.desktop_dir = Path(__file__).parent
        self.web_server_port: int | None = None
        self.platform = platform.system().lower()
        self._cleanup_in_progress = False

        # 設置平台特定的警告抑制
        suppress_windows_asyncio_warnings()

        debug_log("ElectronManager 初始化完成")
        debug_log(f"桌面模組目錄: {self.desktop_dir}")
        debug_log(f"檢測到平台: {self.platform}")

    async def launch_desktop_app(self, summary: str, project_dir: str) -> bool:
        """
        啟動 Electron 桌面應用

        Args:
            summary: AI 工作摘要
            project_dir: 專案目錄

        Returns:
            bool: 啟動是否成功
        """
        debug_log("=== 桌面應用啟動 ===")
        debug_log(f"摘要: {summary}")
        debug_log(f"專案目錄: {project_dir}")

        try:
            # 確保依賴已安裝
            if not await self.ensure_dependencies():
                debug_log("依賴檢查失敗，無法啟動桌面應用")
                return False

            # 啟動 Electron 應用
            success = await self._start_electron_process()
            if success:
                debug_log("Electron 桌面應用啟動成功")
                return True
            debug_log("Electron 桌面應用啟動失敗")
            return False

        except Exception as e:
            error_id = ErrorHandler.log_error_with_context(
                e,
                context={"operation": "桌面應用啟動", "project_dir": project_dir},
                error_type=ErrorType.SYSTEM,
            )
            debug_log(f"桌面應用啟動異常 [錯誤ID: {error_id}]: {e}")
            return False

    def set_web_server_port(self, port: int):
        """設置 Web 服務器端口"""
        self.web_server_port = port
        debug_log(f"設置 Web 服務器端口: {port}")

    def is_electron_available(self) -> bool:
        """檢查 Electron 是否可用"""
        try:
            # 檢查 Node.js
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode != 0:
                debug_log("Node.js 不可用")
                return False

            debug_log(f"Node.js 版本: {result.stdout.strip()}")

            # 檢查 package.json 是否存在
            package_json = self.desktop_dir / "package.json"
            if not package_json.exists():
                debug_log("package.json 不存在，需要在階段 2 中創建")
                return False

            return True

        except Exception as e:
            debug_log(f"Electron 可用性檢查失敗: {e}")
            return False

    async def ensure_dependencies(self) -> bool:
        """確保依賴已安裝"""
        debug_log("檢查 Electron 依賴...")

        try:
            # 檢查 package.json 是否存在
            package_json = self.desktop_dir / "package.json"
            if not package_json.exists():
                debug_log("package.json 不存在，創建中...")
                await self._create_package_json()

            # 檢查 node_modules 是否存在
            node_modules = self.desktop_dir / "node_modules"
            if not node_modules.exists():
                debug_log("node_modules 不存在，安裝依賴中...")
                if not await self._install_dependencies():
                    return False

            # 檢查 main.js 是否存在
            main_js = self.desktop_dir / "main.js"
            if not main_js.exists():
                debug_log("main.js 不存在，將在後續步驟中創建")
                return False

            debug_log("所有依賴檢查通過")
            return True

        except Exception as e:
            error_id = ErrorHandler.log_error_with_context(
                e, context={"operation": "依賴檢查"}, error_type=ErrorType.DEPENDENCY
            )
            debug_log(f"依賴檢查失敗 [錯誤ID: {error_id}]: {e}")
            return False

    def cleanup(self):
        """同步清理資源（向後兼容）"""
        try:
            # 在事件循環中運行異步清理
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循環正在運行，創建任務
                asyncio.create_task(self.cleanup_async())
            else:
                # 如果沒有事件循環，運行異步清理
                asyncio.run(self.cleanup_async())
        except Exception as e:
            debug_log(f"同步清理失敗，嘗試基本清理: {e}")
            self._basic_cleanup()

    async def cleanup_async(self):
        """異步清理資源 - 跨平台支持"""
        if self._cleanup_in_progress or not self.electron_process:
            return

        self._cleanup_in_progress = True
        debug_log(f"開始清理 Electron 進程 (平台: {self.platform})")

        try:
            # 檢查進程是否還在運行
            if self.electron_process.returncode is None:
                await self._terminate_process_cross_platform()
            else:
                debug_log("Electron 進程已自然結束")

            # 等待進程完全結束並清理管道
            await self._wait_and_cleanup_pipes()

        except Exception as e:
            debug_log(f"清理 Electron 進程時出錯: {e}")
            # 嘗試強制清理
            await self._force_cleanup()
        finally:
            self.electron_process = None
            self._cleanup_in_progress = False
            debug_log("Electron 進程清理完成")

    async def _terminate_process_cross_platform(self):
        """跨平台進程終止"""
        if self.platform == "windows":
            await self._terminate_windows()
        else:
            await self._terminate_unix()

    async def _terminate_windows(self):
        """Windows 平台進程終止"""
        debug_log("使用 Windows 進程終止策略")
        if not self.electron_process:
            return

        try:
            # Windows: 使用 terminate() 然後等待
            self.electron_process.terminate()
            try:
                await asyncio.wait_for(self.electron_process.wait(), timeout=5.0)
                debug_log("Electron 進程已優雅終止")
            except TimeoutError:
                debug_log("優雅終止超時，強制終止")
                self.electron_process.kill()
                await asyncio.wait_for(self.electron_process.wait(), timeout=3.0)
                debug_log("Electron 進程已強制終止")
        except Exception as e:
            debug_log(f"Windows 進程終止失敗: {e}")
            raise

    async def _terminate_unix(self):
        """Unix 系統進程終止"""
        debug_log("使用 Unix 進程終止策略")
        if not self.electron_process:
            return

        try:
            # Unix: 發送 SIGTERM 然後等待
            self.electron_process.send_signal(signal.SIGTERM)
            try:
                await asyncio.wait_for(self.electron_process.wait(), timeout=5.0)
                debug_log("Electron 進程已優雅終止")
            except TimeoutError:
                debug_log("優雅終止超時，發送 SIGKILL")
                # 使用 getattr 來處理可能不存在的 SIGKILL
                sigkill = getattr(signal, "SIGKILL", signal.SIGTERM)
                self.electron_process.send_signal(sigkill)
                await asyncio.wait_for(self.electron_process.wait(), timeout=3.0)
                debug_log("Electron 進程已強制終止")
        except Exception as e:
            debug_log(f"Unix 進程終止失敗: {e}")
            raise

    async def _wait_and_cleanup_pipes(self):
        """等待進程結束並清理管道"""
        if not self.electron_process:
            return

        try:
            # 確保進程已經結束
            if self.electron_process.returncode is None:
                await self.electron_process.wait()

            # 平台特定的管道清理
            if self.platform == "windows":
                await self._cleanup_pipes_windows()
            else:
                await self._cleanup_pipes_unix()

        except Exception as e:
            debug_log(f"管道清理失敗: {e}")

    async def _cleanup_pipes_windows(self):
        """Windows 平台管道清理"""
        debug_log("清理 Windows 管道")
        if not self.electron_process:
            return

        try:
            # Windows: 需要特殊處理 asyncio 管道
            pipes = [
                ("stdout", self.electron_process.stdout),
                ("stderr", self.electron_process.stderr),
                ("stdin", self.electron_process.stdin),
            ]

            for pipe_name, pipe in pipes:
                if pipe and hasattr(pipe, "close"):
                    try:
                        # 檢查是否有 is_closing 方法（某些管道類型可能沒有）
                        if not hasattr(pipe, "is_closing") or not pipe.is_closing():
                            pipe.close()
                        # 等待管道關閉
                        if hasattr(pipe, "wait_closed"):
                            await pipe.wait_closed()
                        debug_log(f"已關閉 {pipe_name} 管道")
                    except Exception as e:
                        # Windows 上的管道關閉錯誤通常是無害的
                        debug_log(f"關閉 {pipe_name} 管道時出現預期錯誤: {e}")

        except Exception as e:
            debug_log(f"Windows 管道清理失敗: {e}")

    async def _cleanup_pipes_unix(self):
        """Unix 系統管道清理"""
        debug_log("清理 Unix 管道")
        if not self.electron_process:
            return

        try:
            # Unix: 直接關閉管道
            pipes = [
                ("stdout", self.electron_process.stdout),
                ("stderr", self.electron_process.stderr),
                ("stdin", self.electron_process.stdin),
            ]

            for pipe_name, pipe in pipes:
                if pipe and hasattr(pipe, "close"):
                    try:
                        pipe.close()
                        if hasattr(pipe, "wait_closed"):
                            await pipe.wait_closed()
                        debug_log(f"已關閉 {pipe_name} 管道")
                    except Exception as e:
                        debug_log(f"關閉 {pipe_name} 管道失敗: {e}")

        except Exception as e:
            debug_log(f"Unix 管道清理失敗: {e}")

    async def _force_cleanup(self):
        """強制清理（最後手段）"""
        debug_log("執行強制清理")
        try:
            if self.electron_process and self.electron_process.returncode is None:
                # 嘗試使用 psutil 強制終止
                try:
                    import psutil

                    process = psutil.Process(self.electron_process.pid)
                    process.kill()
                    debug_log("使用 psutil 強制終止進程")
                except ImportError:
                    debug_log("psutil 不可用，使用系統調用")
                    if self.electron_process:
                        if self.platform == "windows":
                            self.electron_process.kill()
                        else:
                            # 使用 getattr 來處理可能不存在的 SIGKILL
                            sigkill = getattr(signal, "SIGKILL", signal.SIGTERM)
                            self.electron_process.send_signal(sigkill)
                except Exception as e:
                    debug_log(f"強制終止失敗: {e}")

            # 基本清理
            self._basic_cleanup()

        except Exception as e:
            debug_log(f"強制清理失敗: {e}")

    def _basic_cleanup(self):
        """基本清理（同步）"""
        debug_log("執行基本清理")
        try:
            if self.electron_process:
                # 嘗試基本的管道關閉
                for pipe_name in ["stdout", "stderr", "stdin"]:
                    pipe = getattr(self.electron_process, pipe_name, None)
                    if pipe and hasattr(pipe, "close"):
                        try:
                            pipe.close()
                        except Exception:
                            pass  # 忽略錯誤
                self.electron_process = None
        except Exception as e:
            debug_log(f"基本清理失敗: {e}")

    async def _create_package_json(self):
        """創建 package.json 文件"""
        package_config = {
            "name": "mcp-feedback-enhanced-desktop",
            "version": "2.3.0",
            "description": "MCP Feedback Enhanced Desktop Application",
            "main": "main.js",
            "scripts": {"start": "electron .", "dev": "electron . --dev"},
            "dependencies": {"electron": "^28.0.0"},
            "devDependencies": {"electron-builder": "^24.0.0"},
        }

        package_json_path = self.desktop_dir / "package.json"
        with open(package_json_path, "w", encoding="utf-8") as f:
            import json

            json.dump(package_config, f, indent=2, ensure_ascii=False)

        debug_log(f"已創建 package.json: {package_json_path}")

    async def _install_dependencies(self) -> bool:
        """安裝 Node.js 依賴"""
        debug_log("開始安裝 Node.js 依賴...")

        try:
            # 使用 npm install
            install_cmd = ["npm", "install"]
            process = await asyncio.create_subprocess_exec(
                *install_cmd,
                cwd=self.desktop_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            _, stderr = await process.communicate()

            if process.returncode == 0:
                debug_log("Node.js 依賴安裝成功")
                return True
            debug_log(f"依賴安裝失敗: {stderr.decode()}")
            return False

        except Exception as e:
            debug_log(f"依賴安裝過程中出錯: {e}")
            return False

    async def _start_electron_process(self) -> bool:
        """啟動 Electron 進程"""
        debug_log("啟動 Electron 進程...")

        try:
            # 構建 Electron 命令 - 使用本地安裝的 electron
            import platform

            if platform.system() == "Windows":
                electron_path = (
                    self.desktop_dir / "node_modules" / ".bin" / "electron.cmd"
                )
            else:
                electron_path = self.desktop_dir / "node_modules" / ".bin" / "electron"

            if electron_path.exists():
                electron_cmd = [
                    str(electron_path),
                    ".",
                    "--port",
                    str(self.web_server_port or 8765),
                ]
            else:
                # 回退到 npx
                electron_cmd = [
                    "npx",
                    "electron",
                    ".",
                    "--port",
                    str(self.web_server_port or 8765),
                ]

            debug_log(f"使用 Electron 命令: {' '.join(electron_cmd)}")

            # 啟動 Electron 進程
            self.electron_process = await asyncio.create_subprocess_exec(
                *electron_cmd,
                cwd=self.desktop_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            debug_log(f"Electron 進程已啟動，PID: {self.electron_process.pid}")

            # 等待一小段時間確保進程正常啟動
            await asyncio.sleep(2)

            # 檢查進程是否仍在運行
            if self.electron_process.returncode is None:
                debug_log("Electron 進程運行正常")
                return True
            debug_log(
                f"Electron 進程異常退出，返回碼: {self.electron_process.returncode}"
            )
            # 讀取錯誤輸出
            try:
                _, stderr = await self.electron_process.communicate()
                if stderr:
                    debug_log(f"Electron 錯誤輸出: {stderr.decode()}")
            except Exception as e:
                debug_log(f"讀取 Electron 錯誤輸出失敗: {e}")
            return False

        except Exception as e:
            debug_log(f"啟動 Electron 進程失敗: {e}")
            return False

    def __del__(self):
        """析構函數"""
        self.cleanup()


# 便利函數
async def create_electron_manager() -> ElectronManager:
    """創建 Electron 管理器實例"""
    manager = ElectronManager()

    # 檢查可用性
    if not manager.is_electron_available():
        debug_log("Electron 環境不可用，建議使用 Web 模式")

    return manager
