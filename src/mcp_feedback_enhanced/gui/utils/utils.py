#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用工具函數
============

提供 GUI 相關的通用工具函數。
"""

from ..styles import *


def apply_widget_styles(widget, style_type="default"):
    """
    應用樣式到元件
    
    Args:
        widget: 要應用樣式的元件
        style_type: 樣式類型
    """
    if style_type == "primary_button":
        widget.setStyleSheet(PRIMARY_BUTTON_STYLE)
    elif style_type == "success_button":
        widget.setStyleSheet(SUCCESS_BUTTON_STYLE)
    elif style_type == "danger_button":
        widget.setStyleSheet(DANGER_BUTTON_STYLE)
    elif style_type == "secondary_button":
        widget.setStyleSheet(SECONDARY_BUTTON_STYLE)
    elif style_type == "dark_theme":
        widget.setStyleSheet(DARK_STYLE)


def format_file_size(size_bytes):
    """
    格式化文件大小顯示
    
    Args:
        size_bytes: 文件大小（字節）
        
    Returns:
        str: 格式化後的文件大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        size_kb = size_bytes / 1024
        return f"{size_kb:.1f} KB"
    else:
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.1f} MB" 