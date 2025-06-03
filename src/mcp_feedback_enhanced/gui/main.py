#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 主要入口點
==============

提供 GUI 回饋介面的主要入口點函數。
"""

import threading
import time
from typing import Optional
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer
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
    
    # 設定全域微軟正黑體字體
    font = QFont("Microsoft JhengHei", 11)  # 微軟正黑體，11pt
    app.setFont(font)
    
    # 設定字體回退順序，確保中文字體正確顯示
    app.setStyleSheet("""
        * {
            font-family: "Microsoft JhengHei", "微軟正黑體", "Microsoft YaHei", "微软雅黑", "SimHei", "黑体", sans-serif;
        }
    """)
    
    # 創建主窗口
    window = FeedbackWindow(project_directory, summary)
    window.show()
    
    # 運行事件循環直到窗口關閉
    app.exec()
    
    # 返回結果
    return window.result 


def feedback_ui_with_timeout(project_directory: str, summary: str, timeout: int) -> Optional[FeedbackResult]:
    """
    啟動帶超時的回饋收集 GUI 介面
    
    Args:
        project_directory: 專案目錄路徑
        summary: AI 工作摘要
        timeout: 超時時間（秒）
        
    Returns:
        Optional[FeedbackResult]: 回饋結果，如果用戶取消或超時則返回 None
        
    Raises:
        TimeoutError: 當超時時拋出
    """
    # 檢查是否已有 QApplication 實例
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 設定全域微軟正黑體字體
    font = QFont("Microsoft JhengHei", 11)  # 微軟正黑體，11pt
    app.setFont(font)
    
    # 設定字體回退順序，確保中文字體正確顯示
    app.setStyleSheet("""
        * {
            font-family: "Microsoft JhengHei", "微軟正黑體", "Microsoft YaHei", "微软雅黑", "SimHei", "黑体", sans-serif;
        }
    """)
    
    # 創建主窗口
    window = FeedbackWindow(project_directory, summary)
    window.show()
    
    # 創建超時計時器
    timeout_timer = QTimer()
    timeout_timer.setSingleShot(True)
    timeout_timer.timeout.connect(lambda: _handle_timeout(window, app))
    timeout_timer.start(timeout * 1000)  # 轉換為毫秒
    
    # 運行事件循環直到窗口關閉
    app.exec()
    
    # 停止計時器（如果還在運行）
    timeout_timer.stop()
    
    # 檢查是否超時
    if hasattr(window, '_timeout_occurred'):
        raise TimeoutError(f"回饋收集超時（{timeout}秒），GUI 介面已自動關閉")
    
    # 返回結果
    return window.result


def _handle_timeout(window: FeedbackWindow, app: QApplication) -> None:
    """處理超時事件"""
    # 標記超時發生
    window._timeout_occurred = True
    # 強制關閉視窗
    window.force_close()
    # 退出應用程式
    app.quit() 