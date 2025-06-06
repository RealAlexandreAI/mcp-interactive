#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試配置管理
============

管理 MCP 測試框架的配置參數和設定。
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class TestConfig:
    """測試配置類"""
    
    # 服務器配置
    server_host: str = "127.0.0.1"
    server_port: int = 8765
    server_timeout: int = 30
    
    # MCP 客戶端配置
    mcp_timeout: int = 60
    mcp_retry_count: int = 3
    mcp_retry_delay: float = 1.0
    
    # WebSocket 配置
    websocket_timeout: int = 10
    websocket_ping_interval: int = 5
    websocket_ping_timeout: int = 3
    
    # 測試配置
    test_timeout: int = 120
    test_parallel: bool = False
    test_verbose: bool = True
    test_debug: bool = False
    
    # 報告配置
    report_format: str = "html"  # html, json, markdown
    report_output_dir: str = "test_reports"
    report_include_logs: bool = True
    report_include_performance: bool = True
    
    # 測試數據配置
    test_project_dir: Optional[str] = None
    test_summary: str = "MCP 測試框架 - 模擬 Cursor IDE 調用"
    test_feedback_text: str = "這是一個測試回饋，用於驗證 MCP 系統功能。"
    
    @classmethod
    def from_env(cls) -> 'TestConfig':
        """從環境變數創建配置"""
        config = cls()
        
        # 從環境變數讀取配置
        config.server_host = os.getenv('MCP_TEST_HOST', config.server_host)
        config.server_port = int(os.getenv('MCP_TEST_PORT', str(config.server_port)))
        config.server_timeout = int(os.getenv('MCP_TEST_SERVER_TIMEOUT', str(config.server_timeout)))
        
        config.mcp_timeout = int(os.getenv('MCP_TEST_TIMEOUT', str(config.mcp_timeout)))
        config.mcp_retry_count = int(os.getenv('MCP_TEST_RETRY_COUNT', str(config.mcp_retry_count)))
        
        config.test_timeout = int(os.getenv('MCP_TEST_CASE_TIMEOUT', str(config.test_timeout)))
        config.test_parallel = os.getenv('MCP_TEST_PARALLEL', '').lower() in ('true', '1', 'yes')
        config.test_verbose = os.getenv('MCP_TEST_VERBOSE', '').lower() not in ('false', '0', 'no')
        config.test_debug = os.getenv('MCP_DEBUG', '').lower() in ('true', '1', 'yes')
        
        config.report_format = os.getenv('MCP_TEST_REPORT_FORMAT', config.report_format)
        config.report_output_dir = os.getenv('MCP_TEST_REPORT_DIR', config.report_output_dir)
        
        config.test_project_dir = os.getenv('MCP_TEST_PROJECT_DIR', config.test_project_dir)
        
        return config
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestConfig':
        """從字典創建配置"""
        config = cls()
        
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'server_host': self.server_host,
            'server_port': self.server_port,
            'server_timeout': self.server_timeout,
            'mcp_timeout': self.mcp_timeout,
            'mcp_retry_count': self.mcp_retry_count,
            'mcp_retry_delay': self.mcp_retry_delay,
            'websocket_timeout': self.websocket_timeout,
            'websocket_ping_interval': self.websocket_ping_interval,
            'websocket_ping_timeout': self.websocket_ping_timeout,
            'test_timeout': self.test_timeout,
            'test_parallel': self.test_parallel,
            'test_verbose': self.test_verbose,
            'test_debug': self.test_debug,
            'report_format': self.report_format,
            'report_output_dir': self.report_output_dir,
            'report_include_logs': self.report_include_logs,
            'report_include_performance': self.report_include_performance,
            'test_project_dir': self.test_project_dir,
            'test_summary': self.test_summary,
            'test_feedback_text': self.test_feedback_text
        }
    
    def get_server_url(self) -> str:
        """獲取服務器 URL"""
        return f"http://{self.server_host}:{self.server_port}"
    
    def get_websocket_url(self) -> str:
        """獲取 WebSocket URL"""
        return f"ws://{self.server_host}:{self.server_port}/ws"
    
    def get_report_output_path(self) -> Path:
        """獲取報告輸出路徑"""
        return Path(self.report_output_dir)
    
    def ensure_report_dir(self) -> Path:
        """確保報告目錄存在"""
        report_dir = self.get_report_output_path()
        report_dir.mkdir(parents=True, exist_ok=True)
        return report_dir


# 默認配置實例
DEFAULT_CONFIG = TestConfig.from_env()
