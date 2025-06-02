#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web UI 模組
===========

提供基於 FastAPI 的 Web 用戶介面，專為 SSH 遠端開發環境設計。
支援文字輸入、圖片上傳、命令執行等功能，並參考 GUI 的設計模式。
"""

from .main import WebUIManager, launch_web_feedback_ui, get_web_ui_manager, stop_web_ui

__all__ = [
    'WebUIManager',
    'launch_web_feedback_ui', 
    'get_web_ui_manager',
    'stop_web_ui'
] 