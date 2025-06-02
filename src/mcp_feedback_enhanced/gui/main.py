#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 主要入口點
==============

提供 GUI 回饋介面的主要入口點函數。
"""

from typing import Optional
from PySide6.QtWidgets import QApplication, QMainWindow
import sys

from .models import FeedbackResult
from .window import FeedbackWindow


def feedback_ui(project_directory: str, summary: str) -> Optional[FeedbackResult]:
    """
    啟動回饋收集 GUI 介面
    
    Args:
        project_directory: 專案目錄路徑
        summary: AI 工作摘要
        
    Returns:
        Optional[FeedbackResult]: 回饋結果，如果用戶取消則返回 None
    """
    # 檢查是否已有 QApplication 實例
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 創建主窗口
    window = FeedbackWindow(project_directory, summary)
    window.show()
    
    # 運行事件循環直到窗口關閉
    app.exec()
    
    # 返回結果
    return window.result 