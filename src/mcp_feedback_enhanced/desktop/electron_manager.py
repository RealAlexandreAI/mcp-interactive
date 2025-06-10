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
import subprocess
from pathlib import Path

from ..debug import web_debug_log as debug_log
from ..utils.error_handler import ErrorHandler, ErrorType


class ElectronManager:
    """Electron 進程管理器"""

    def __init__(self):
        """初始化 Electron 管理器"""
        self.electron_process: subprocess.Popen | None = None
        self.desktop_dir = Path(__file__).parent
        self.web_server_port: int | None = None

        debug_log("ElectronManager 初始化完成")
        debug_log(f"桌面模組目錄: {self.desktop_dir}")

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
        """清理資源"""
        if self.electron_process:
            try:
                # 檢查進程是否還在運行
                if self.electron_process.returncode is None:
                    self.electron_process.terminate()
                    debug_log("Electron 進程已終止")
                else:
                    debug_log("Electron 進程已自然結束")
            except Exception as e:
                debug_log(f"終止 Electron 進程時出錯: {e}")
                try:
                    if self.electron_process.returncode is None:
                        self.electron_process.kill()
                        debug_log("強制終止 Electron 進程")
                except Exception as kill_error:
                    debug_log(f"強制終止 Electron 進程失敗: {kill_error}")
            finally:
                # 關閉管道以避免 ResourceWarning
                try:
                    # 對於 asyncio 子進程，需要特殊處理
                    if (
                        hasattr(self.electron_process, "stdout")
                        and self.electron_process.stdout
                    ):
                        if hasattr(self.electron_process.stdout, "close"):
                            self.electron_process.stdout.close()
                    if (
                        hasattr(self.electron_process, "stderr")
                        and self.electron_process.stderr
                    ):
                        if hasattr(self.electron_process.stderr, "close"):
                            self.electron_process.stderr.close()
                    if (
                        hasattr(self.electron_process, "stdin")
                        and self.electron_process.stdin
                    ):
                        if hasattr(self.electron_process.stdin, "close"):
                            self.electron_process.stdin.close()
                except Exception:
                    # 忽略管道關閉錯誤，這些通常是無害的
                    pass

                self.electron_process = None

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
