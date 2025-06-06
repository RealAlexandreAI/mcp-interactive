#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web 回饋會話模型
===============

管理 Web 回饋會話的資料和邏輯。
"""

import asyncio
import base64
import subprocess
import threading
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import WebSocket

from ...debug import web_debug_log as debug_log


class SessionStatus(Enum):
    """會話狀態枚舉"""
    WAITING = "waiting"          # 等待中
    ACTIVE = "active"            # 活躍中
    FEEDBACK_SUBMITTED = "feedback_submitted"  # 已提交反饋
    COMPLETED = "completed"      # 已完成
    TIMEOUT = "timeout"          # 超時
    ERROR = "error"              # 錯誤

# 常數定義
MAX_IMAGE_SIZE = 1 * 1024 * 1024  # 1MB 圖片大小限制
SUPPORTED_IMAGE_TYPES = {'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'}
TEMP_DIR = Path.home() / ".cache" / "interactive-feedback-mcp-web"


class WebFeedbackSession:
    """Web 回饋會話管理"""
    
    def __init__(self, session_id: str, project_directory: str, summary: str):
        self.session_id = session_id
        self.project_directory = project_directory
        self.summary = summary
        self.websocket: Optional[WebSocket] = None
        self.feedback_result: Optional[str] = None
        self.images: List[dict] = []
        self.settings: dict = {}  # 圖片設定
        self.feedback_completed = threading.Event()
        self.process: Optional[subprocess.Popen] = None
        self.command_logs = []
        self._cleanup_done = False  # 防止重複清理

        # 新增：會話狀態管理
        self.status = SessionStatus.WAITING
        self.status_message = "等待用戶回饋"
        self.created_at = asyncio.get_event_loop().time()
        self.last_activity = self.created_at

        # 確保臨時目錄存在
        TEMP_DIR.mkdir(parents=True, exist_ok=True)

    def update_status(self, status: SessionStatus, message: str = None):
        """更新會話狀態"""
        self.status = status
        if message:
            self.status_message = message
        self.last_activity = asyncio.get_event_loop().time()
        debug_log(f"會話 {self.session_id} 狀態更新: {status.value} - {self.status_message}")

    def get_status_info(self) -> dict:
        """獲取會話狀態信息"""
        return {
            "status": self.status.value,
            "message": self.status_message,
            "feedback_completed": self.feedback_completed.is_set(),
            "has_websocket": self.websocket is not None,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "project_directory": self.project_directory,
            "summary": self.summary,
            "session_id": self.session_id
        }

    def is_active(self) -> bool:
        """檢查會話是否活躍"""
        return self.status in [SessionStatus.WAITING, SessionStatus.ACTIVE, SessionStatus.FEEDBACK_SUBMITTED]

    async def wait_for_feedback(self, timeout: int = 600) -> dict:
        """
        等待用戶回饋，包含圖片，支援超時自動清理
        
        Args:
            timeout: 超時時間（秒）
            
        Returns:
            dict: 回饋結果
        """
        try:
            # 使用比 MCP 超時稍短的時間（提前處理，避免邊界競爭）
            # 對於短超時（<30秒），提前1秒；對於長超時，提前5秒
            if timeout <= 30:
                actual_timeout = max(timeout - 1, 5)  # 短超時提前1秒，最少5秒
            else:
                actual_timeout = timeout - 5  # 長超時提前5秒
            debug_log(f"會話 {self.session_id} 開始等待回饋，超時時間: {actual_timeout} 秒（原始: {timeout} 秒）")
            
            loop = asyncio.get_event_loop()
            
            def wait_in_thread():
                return self.feedback_completed.wait(actual_timeout)
            
            completed = await loop.run_in_executor(None, wait_in_thread)
            
            if completed:
                debug_log(f"會話 {self.session_id} 收到用戶回饋")
                return {
                    "logs": "\n".join(self.command_logs),
                    "interactive_feedback": self.feedback_result or "",
                    "images": self.images,
                    "settings": self.settings
                }
            else:
                # 超時了，立即清理資源
                debug_log(f"會話 {self.session_id} 在 {actual_timeout} 秒後超時，開始清理資源...")
                await self._cleanup_resources_on_timeout()
                raise TimeoutError(f"等待用戶回饋超時（{actual_timeout}秒），介面已自動關閉")
                
        except Exception as e:
            # 任何異常都要確保清理資源
            debug_log(f"會話 {self.session_id} 發生異常: {e}")
            await self._cleanup_resources_on_timeout()
            raise

    async def submit_feedback(self, feedback: str, images: List[dict], settings: dict = None):
        """
        提交回饋和圖片

        Args:
            feedback: 文字回饋
            images: 圖片列表
            settings: 圖片設定（可選）
        """
        self.feedback_result = feedback
        # 先設置設定，再處理圖片（因為處理圖片時需要用到設定）
        self.settings = settings or {}
        self.images = self._process_images(images)

        # 更新狀態為已提交反饋
        self.update_status(SessionStatus.FEEDBACK_SUBMITTED, "已送出反饋，等待下次 MCP 調用")

        self.feedback_completed.set()

        # 發送反饋已收到的消息給前端
        if self.websocket:
            try:
                await self.websocket.send_json({
                    "type": "feedback_received",
                    "message": "反饋已成功提交",
                    "status": self.status.value
                })
            except Exception as e:
                debug_log(f"發送反饋確認失敗: {e}")

        # 重構：不再自動關閉 WebSocket，保持連接以支援頁面持久性
    
    def _process_images(self, images: List[dict]) -> List[dict]:
        """
        處理圖片數據，轉換為統一格式

        Args:
            images: 原始圖片數據列表

        Returns:
            List[dict]: 處理後的圖片數據
        """
        processed_images = []

        # 從設定中獲取圖片大小限制，如果沒有設定則使用預設值
        size_limit = self.settings.get('image_size_limit', MAX_IMAGE_SIZE)

        for img in images:
            try:
                if not all(key in img for key in ["name", "data", "size"]):
                    continue

                # 檢查文件大小（只有當限制大於0時才檢查）
                if size_limit > 0 and img["size"] > size_limit:
                    debug_log(f"圖片 {img['name']} 超過大小限制 ({size_limit} bytes)，跳過")
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
            debug_log(f"執行命令: {command}")
            
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
            async def read_output():
                loop = asyncio.get_event_loop()
                try:
                    # 使用線程池執行器來處理阻塞的讀取操作
                    def read_line():
                        if self.process and self.process.stdout:
                            return self.process.stdout.readline()
                        return ''
                    
                    while True:
                        line = await loop.run_in_executor(None, read_line)
                        if not line:
                            break
                            
                        self.add_log(line.rstrip())
                        if self.websocket:
                            try:
                                await self.websocket.send_json({
                                    "type": "command_output",
                                    "output": line
                                })
                            except Exception as e:
                                debug_log(f"WebSocket 發送失敗: {e}")
                                break
                                
                except Exception as e:
                    debug_log(f"讀取命令輸出錯誤: {e}")
                finally:
                    # 等待進程完成
                    if self.process:
                        exit_code = self.process.wait()
                        
                        # 發送命令完成信號
                        if self.websocket:
                            try:
                                await self.websocket.send_json({
                                    "type": "command_complete",
                                    "exit_code": exit_code
                                })
                            except Exception as e:
                                debug_log(f"發送完成信號失敗: {e}")

            # 啟動異步任務讀取輸出
            asyncio.create_task(read_output())

        except Exception as e:
            debug_log(f"執行命令錯誤: {e}")
            if self.websocket:
                try:
                    await self.websocket.send_json({
                        "type": "command_error",
                        "error": str(e)
                    })
                except:
                    pass

    async def _cleanup_resources_on_timeout(self):
        """超時時清理所有資源"""
        if self._cleanup_done:
            return  # 避免重複清理
        
        self._cleanup_done = True
        debug_log(f"開始清理會話 {self.session_id} 的資源...")
        
        try:
            # 1. 關閉 WebSocket 連接
            if self.websocket:
                try:
                    # 先通知前端超時
                    await self.websocket.send_json({
                        "type": "session_timeout",
                        "message": "會話已超時，介面將自動關閉"
                    })
                    await asyncio.sleep(0.1)  # 給前端一點時間處理消息
                    await self.websocket.close()
                    debug_log(f"會話 {self.session_id} WebSocket 已關閉")
                except Exception as e:
                    debug_log(f"關閉 WebSocket 時發生錯誤: {e}")
                finally:
                    self.websocket = None
            
            # 2. 終止正在運行的命令進程
            if self.process:
                try:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=3)
                        debug_log(f"會話 {self.session_id} 命令進程已正常終止")
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        debug_log(f"會話 {self.session_id} 命令進程已強制終止")
                except Exception as e:
                    debug_log(f"終止命令進程時發生錯誤: {e}")
                finally:
                    self.process = None
            
            # 3. 設置完成事件（防止其他地方還在等待）
            self.feedback_completed.set()
            
            # 4. 清理臨時數據
            self.command_logs.clear()
            self.images.clear()
            
            debug_log(f"會話 {self.session_id} 資源清理完成")
            
        except Exception as e:
            debug_log(f"清理會話 {self.session_id} 資源時發生錯誤: {e}")

    def _cleanup_sync(self):
        """同步清理會話資源（但保留 WebSocket 連接）"""
        if self._cleanup_done:
            return

        debug_log(f"同步清理會話 {self.session_id} 資源（保留 WebSocket）...")

        # 只清理進程，不清理 WebSocket 連接
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None

        # 清理臨時數據
        self.command_logs.clear()
        # 注意：不設置 _cleanup_done = True，因為還需要清理 WebSocket

    def cleanup(self):
        """同步清理會話資源（保持向後兼容）"""
        if self._cleanup_done:
            return

        self._cleanup_done = True
        debug_log(f"同步清理會話 {self.session_id} 資源...")

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None

        # 設置完成事件
        self.feedback_completed.set()