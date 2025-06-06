#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 測試框架
============

完整的 MCP 測試系統，模擬真實的 Cursor IDE 調用場景。

主要功能：
- MCP 客戶端模擬器
- 完整的回饋循環測試
- 多場景測試覆蓋
- 詳細的測試報告

作者: Augment Agent
創建時間: 2025-01-05
"""

from .mcp_client import MCPTestClient
from .scenarios import TestScenarios
from .validators import TestValidators
from .reporter import TestReporter
from .utils import TestUtils
from .config import TestConfig, DEFAULT_CONFIG

__all__ = [
    'MCPTestClient',
    'TestScenarios',
    'TestValidators',
    'TestReporter',
    'TestUtils',
    'TestConfig',
    'DEFAULT_CONFIG'
]

__version__ = "1.0.0"
__author__ = "Augment Agent"
