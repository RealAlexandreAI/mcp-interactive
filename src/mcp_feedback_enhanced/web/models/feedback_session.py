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
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import WebSocket

from ...debug import web_debug_log as debug_log

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
        self.feedback_completed = threading.Event()
        self.process: Optional[subprocess.Popen] = None
        self.command_logs = []
        
        # 確保臨時目錄存在
        TEMP_DIR.mkdir(parents=True, exist_ok=True)

    async def wait_for_feedback(self, timeout: int = 600) -> dict:
        """
        等待用戶回饋，包含圖片
        
        Args:
            timeout: 超時時間（秒）
            
        Returns:
            dict: 回饋結果
        """
        loop = asyncio.get_event_loop()
        
        def wait_in_thread():
            return self.feedback_completed.wait(timeout)
        
        completed = await loop.run_in_executor(None, wait_in_thread)
        
        if completed:
            return {
                "logs": "\n".join(self.command_logs),
                "interactive_feedback": self.feedback_result or "",
                "images": self.images
            }
        else:
            raise TimeoutError("等待用戶回饋超時")

    async def submit_feedback(self, feedback: str, images: List[dict]):
        """
        提交回饋和圖片
        
        Args:
            feedback: 文字回饋
            images: 圖片列表
        """
        self.feedback_result = feedback
        self.images = self._process_images(images)
        self.feedback_completed.set()
        
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
    
    def _process_images(self, images: List[dict]) -> List[dict]:
        """
        處理圖片數據，轉換為統一格式
        
        Args:
            images: 原始圖片數據列表
            
        Returns:
            List[dict]: 處理後的圖片數據
        """
        processed_images = []
        
        for img in images:
            try:
                if not all(key in img for key in ["name", "data", "size"]):
                    continue
                
                # 檢查文件大小
                if img["size"] > MAX_IMAGE_SIZE:
                    debug_log(f"圖片 {img['name']} 超過大小限制，跳過")
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

    def cleanup(self):
        """清理會話資源"""
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