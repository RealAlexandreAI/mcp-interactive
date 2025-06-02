#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快捷鍵設置工具
==============

管理 GUI 快捷鍵設置的工具函數。
"""

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt


def setup_shortcuts(window):
    """
    設置窗口的快捷鍵
    
    Args:
        window: 主窗口實例
    """
    # Ctrl+Enter 提交回饋
    submit_shortcut = QShortcut(QKeySequence("Ctrl+Return"), window)
    submit_shortcut.activated.connect(window._submit_feedback)
    
    # Escape 取消回饋
    cancel_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), window)
    cancel_shortcut.activated.connect(window._cancel_feedback)
    
    # Ctrl+R 執行命令
    run_shortcut = QShortcut(QKeySequence("Ctrl+R"), window)
    run_shortcut.activated.connect(window._run_command)
    
    # Ctrl+Shift+C 終止命令
    terminate_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), window)
    terminate_shortcut.activated.connect(window._terminate_command) 