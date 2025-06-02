#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令執行管理器
===============

負責處理命令執行、輸出讀取和進程管理。
"""

import os
import subprocess
import threading
import time
import queue
import select
import sys
from typing import Optional, Callable

from PySide6.QtCore import QObject, QTimer, Signal

from ...debug import gui_debug_log as debug_log


class CommandExecutor(QObject):
    """命令執行管理器"""
    output_received = Signal(str)  # 輸出接收信號
    
    def __init__(self, project_dir: str, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir
        self.command_process: Optional[subprocess.Popen] = None
        self.timer: Optional[QTimer] = None
        self._output_queue: Optional[queue.Queue] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._command_start_time: Optional[float] = None
    
    def run_command(self, command: str) -> None:
        """執行命令"""
        if not command.strip():
            return

        # 如果已經有命令在執行，先停止
        if self.timer and self.timer.isActive():
            self.terminate_command()

        self.output_received.emit(f"$ {command}\n")
        
        # 保存當前命令用於輸出過濾
        self._last_command = command
        
        try:
            # 準備環境變數以避免不必要的輸出
            env = os.environ.copy()
            env['NO_UPDATE_NOTIFIER'] = '1'
            env['NPM_CONFIG_UPDATE_NOTIFIER'] = 'false'
            env['NPM_CONFIG_FUND'] = 'false'
            env['NPM_CONFIG_AUDIT'] = 'false'
            env['PYTHONUNBUFFERED'] = '1'
            
            # 啟動進程
            self.command_process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                env=env,
                universal_newlines=True
            )
            
            # 設置計時器來定期讀取輸出
            if not self.timer:
                self.timer = QTimer()
                self.timer.timeout.connect(self._read_command_output)
            
            self.timer.start(100)  # 每100ms檢查一次
            self._command_start_time = time.time()
            
            debug_log(f"命令已啟動: {command}")
            
        except Exception as e:
            self.output_received.emit(f"錯誤: 無法執行命令 - {str(e)}\n")
            debug_log(f"命令執行錯誤: {e}")
    
    def terminate_command(self) -> None:
        """終止正在運行的命令"""
        if self.command_process and self.command_process.poll() is None:
            try:
                self.command_process.terminate()
                self.output_received.emit("命令已被用戶終止。\n")
                debug_log("用戶終止了正在運行的命令")
                
                # 停止計時器
                if self.timer:
                    self.timer.stop()
                    
            except Exception as e:
                debug_log(f"終止命令失敗: {e}")
                self.output_received.emit(f"終止命令失敗: {e}\n")
        else:
            self.output_received.emit("沒有正在運行的命令可以終止。\n")
    
    def _read_command_output(self) -> None:
        """讀取命令輸出（非阻塞方式）"""
        if not self.command_process:
            if self.timer:
                self.timer.stop()
            return
            
        # 檢查進程是否還在運行
        if self.command_process.poll() is None:
            try:
                if sys.platform == "win32":
                    # Windows 下使用隊列方式
                    try:
                        if not self._output_queue:
                            self._output_queue = queue.Queue()
                            self._reader_thread = threading.Thread(
                                target=self._read_process_output_thread,
                                daemon=True
                            )
                            self._reader_thread.start()
                        
                        # 從隊列中獲取輸出（非阻塞）
                        try:
                            while True:
                                output = self._output_queue.get_nowait()
                                if output is None:  # 進程結束信號
                                    break
                                self.output_received.emit(output)
                        except queue.Empty:
                            pass  # 沒有新輸出，繼續等待
                            
                    except ImportError:
                        output = self.command_process.stdout.readline()
                        if output:
                            filtered_output = self._filter_command_output(output)
                            if filtered_output:
                                self.output_received.emit(filtered_output)
                else:
                    # Unix/Linux/macOS 下使用 select
                    ready, _, _ = select.select([self.command_process.stdout], [], [], 0.1)
                    if ready:
                        output = self.command_process.stdout.readline()
                        if output:
                            filtered_output = self._filter_command_output(output)
                            if filtered_output:
                                self.output_received.emit(filtered_output)
                
                # 檢查命令執行超時（30秒）
                if self._command_start_time and time.time() - self._command_start_time > 30:
                    self.output_received.emit(f"\n⚠️ 命令執行超過30秒，自動終止...")
                    self.terminate_command()
                    
            except Exception as e:
                debug_log(f"讀取命令輸出錯誤: {e}")
        else:
            # 進程結束，停止計時器並讀取剩餘輸出
            if self.timer:
                self.timer.stop()
            
            # 清理資源
            self._cleanup_resources()
                
            try:
                # 讀取剩餘的輸出
                remaining_output, _ = self.command_process.communicate(timeout=2)
                if remaining_output and remaining_output.strip():
                    filtered_output = self._filter_command_output(remaining_output)
                    if filtered_output:
                        self.output_received.emit(filtered_output)
            except subprocess.TimeoutExpired:
                debug_log("讀取剩餘輸出超時")
            except Exception as e:
                debug_log(f"讀取剩餘輸出錯誤: {e}")
            
            return_code = self.command_process.returncode
            self.output_received.emit(f"\n進程結束，返回碼: {return_code}\n")
    
    def _read_process_output_thread(self) -> None:
        """在背景線程中讀取進程輸出"""
        try:
            while self.command_process and self.command_process.poll() is None:
                output = self.command_process.stdout.readline()
                if output:
                    self._output_queue.put(output)
                else:
                    break
            # 進程結束信號
            if self._output_queue:
                self._output_queue.put(None)
        except Exception as e:
            debug_log(f"背景讀取線程錯誤: {e}")
    
    def _filter_command_output(self, output: str) -> str:
        """過濾命令輸出，移除不必要的行"""
        if not output:
            return ""
        
        # 要過濾的字串（避免干擾的輸出）
        filter_patterns = [
            "npm notice",
            "npm WARN deprecated",
            "npm fund",
            "npm audit",
            "found 0 vulnerabilities",
            "Run `npm audit` for details",
            "[##",  # 進度條
            "⸩ ░░░░░░░░░░░░░░░░"  # 其他進度指示器
        ]
        
        # 檢查是否需要過濾
        for pattern in filter_patterns:
            if pattern in output:
                return ""
        
        return output
    
    def _cleanup_resources(self) -> None:
        """清理資源"""
        if hasattr(self, '_output_queue') and self._output_queue:
            self._output_queue = None
        if hasattr(self, '_reader_thread') and self._reader_thread:
            self._reader_thread = None
        if hasattr(self, '_command_start_time') and self._command_start_time:
            self._command_start_time = None
    
    def cleanup(self) -> None:
        """清理所有資源"""
        if self.command_process and self.command_process.poll() is None:
            try:
                self.command_process.terminate()
                debug_log("已終止正在運行的命令")
            except Exception as e:
                debug_log(f"終止命令失敗: {e}")
        
        if self.timer:
            self.timer.stop()
        
        self._cleanup_resources() 