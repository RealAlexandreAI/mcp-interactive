#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試工具函數
============

提供 MCP 測試框架使用的通用工具函數。
"""

import asyncio
import time
import json
import uuid
import socket
import psutil
import threading
from typing import Dict, Any, Optional, List, Callable, Awaitable
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from ..debug import debug_log


class TestUtils:
    """測試工具類"""
    
    @staticmethod
    def generate_test_id() -> str:
        """生成測試 ID"""
        return f"test_{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def generate_session_id() -> str:
        """生成會話 ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def get_timestamp() -> str:
        """獲取當前時間戳"""
        return datetime.now().isoformat()
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化持續時間"""
        if seconds < 1:
            return f"{seconds*1000:.1f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
    
    @staticmethod
    def find_free_port(start_port: int = 8765, max_attempts: int = 100) -> int:
        """尋找可用端口 - 使用增強的端口管理"""
        try:
            # 嘗試使用增強的端口管理
            from ..web.utils.port_manager import PortManager
            return PortManager.find_free_port_enhanced(
                preferred_port=start_port,
                auto_cleanup=False,  # 測試時不自動清理
                host='127.0.0.1',
                max_attempts=max_attempts
            )
        except ImportError:
            # 回退到原始方法
            for port in range(start_port, start_port + max_attempts):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('127.0.0.1', port))
                        return port
                except OSError:
                    continue
            raise RuntimeError(f"無法找到可用端口 (嘗試範圍: {start_port}-{start_port + max_attempts})")
    
    @staticmethod
    def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
        """檢查端口是否開放"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    @staticmethod
    async def wait_for_port(host: str, port: int, timeout: float = 30.0, interval: float = 0.5) -> bool:
        """等待端口開放"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if TestUtils.is_port_open(host, port):
                return True
            await asyncio.sleep(interval)
        return False
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """獲取系統信息"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else None,
                'platform': psutil.WINDOWS if hasattr(psutil, 'WINDOWS') else 'unknown'
            }
        except Exception as e:
            debug_log(f"獲取系統信息失敗: {e}")
            return {}
    
    @staticmethod
    def measure_memory_usage() -> Dict[str, float]:
        """測量內存使用情況"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss': memory_info.rss / 1024 / 1024,  # MB
                'vms': memory_info.vms / 1024 / 1024,  # MB
                'percent': process.memory_percent()
            }
        except Exception as e:
            debug_log(f"測量內存使用失敗: {e}")
            return {}
    
    @staticmethod
    async def timeout_wrapper(coro: Awaitable, timeout: float, error_message: str = "操作超時"):
        """為協程添加超時包裝"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"{error_message} (超時: {timeout}s)")
    
    @staticmethod
    def safe_json_loads(data: str) -> Optional[Dict[str, Any]]:
        """安全的 JSON 解析"""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError) as e:
            debug_log(f"JSON 解析失敗: {e}")
            return None
    
    @staticmethod
    def safe_json_dumps(data: Any, indent: int = 2) -> str:
        """安全的 JSON 序列化"""
        try:
            return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
        except (TypeError, ValueError) as e:
            debug_log(f"JSON 序列化失敗: {e}")
            return str(data)
    
    @staticmethod
    def create_test_directory(base_dir: str = "test_temp") -> Path:
        """創建測試目錄"""
        test_dir = Path(base_dir) / f"test_{uuid.uuid4().hex[:8]}"
        test_dir.mkdir(parents=True, exist_ok=True)
        return test_dir
    
    @staticmethod
    def cleanup_test_directory(test_dir: Path):
        """清理測試目錄"""
        try:
            if test_dir.exists() and test_dir.is_dir():
                import shutil
                shutil.rmtree(test_dir)
        except Exception as e:
            debug_log(f"清理測試目錄失敗: {e}")


class PerformanceMonitor:
    """性能監控器"""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.memory_start: Optional[Dict[str, float]] = None
        self.memory_end: Optional[Dict[str, float]] = None
        self.checkpoints: List[Dict[str, Any]] = []
    
    def start(self):
        """開始監控"""
        self.start_time = time.time()
        self.memory_start = TestUtils.measure_memory_usage()
        self.checkpoints = []
    
    def checkpoint(self, name: str, data: Optional[Dict[str, Any]] = None):
        """添加檢查點"""
        if self.start_time is None:
            return
        
        checkpoint = {
            'name': name,
            'timestamp': time.time(),
            'elapsed': time.time() - self.start_time,
            'memory': TestUtils.measure_memory_usage(),
            'data': data or {}
        }
        self.checkpoints.append(checkpoint)
    
    def stop(self):
        """停止監控"""
        self.end_time = time.time()
        self.memory_end = TestUtils.measure_memory_usage()
    
    def get_summary(self) -> Dict[str, Any]:
        """獲取監控摘要"""
        if self.start_time is None or self.end_time is None:
            return {}
        
        total_duration = self.end_time - self.start_time
        memory_diff = {}
        
        if self.memory_start and self.memory_end:
            for key in self.memory_start:
                if key in self.memory_end:
                    memory_diff[f"memory_{key}_diff"] = self.memory_end[key] - self.memory_start[key]
        
        return {
            'total_duration': total_duration,
            'total_duration_formatted': TestUtils.format_duration(total_duration),
            'memory_start': self.memory_start,
            'memory_end': self.memory_end,
            'memory_diff': memory_diff,
            'checkpoints_count': len(self.checkpoints),
            'checkpoints': self.checkpoints
        }


@asynccontextmanager
async def performance_context(name: str = "test"):
    """性能監控上下文管理器"""
    monitor = PerformanceMonitor()
    monitor.start()
    try:
        yield monitor
    finally:
        monitor.stop()
        summary = monitor.get_summary()
        debug_log(f"性能監控 [{name}]: {TestUtils.format_duration(summary.get('total_duration', 0))}")


class AsyncEventWaiter:
    """異步事件等待器"""
    
    def __init__(self):
        self.events: Dict[str, asyncio.Event] = {}
        self.results: Dict[str, Any] = {}
    
    def create_event(self, event_name: str):
        """創建事件"""
        self.events[event_name] = asyncio.Event()
    
    def set_event(self, event_name: str, result: Any = None):
        """設置事件"""
        if event_name in self.events:
            self.results[event_name] = result
            self.events[event_name].set()
    
    async def wait_for_event(self, event_name: str, timeout: float = 30.0) -> Any:
        """等待事件"""
        if event_name not in self.events:
            self.create_event(event_name)
        
        try:
            await asyncio.wait_for(self.events[event_name].wait(), timeout=timeout)
            return self.results.get(event_name)
        except asyncio.TimeoutError:
            raise TimeoutError(f"等待事件 '{event_name}' 超時 ({timeout}s)")
    
    def clear_event(self, event_name: str):
        """清除事件"""
        if event_name in self.events:
            self.events[event_name].clear()
            self.results.pop(event_name, None)
