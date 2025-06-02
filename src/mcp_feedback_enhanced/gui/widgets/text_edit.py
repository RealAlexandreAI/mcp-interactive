#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文字編輯器
==============

支援智能 Ctrl+V 的文字輸入框，能自動處理圖片貼上。
"""

from PySide6.QtWidgets import QTextEdit, QApplication
from PySide6.QtCore import Qt, Signal


class SmartTextEdit(QTextEdit):
    """支援智能 Ctrl+V 的文字輸入框"""
    image_paste_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def keyPressEvent(self, event):
        """處理按鍵事件，實現智能 Ctrl+V"""
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            # 檢查剪貼簿是否有圖片
            clipboard = QApplication.clipboard()
            
            if clipboard.mimeData().hasImage():
                # 如果有圖片，發送信號通知主窗口處理圖片貼上
                self.image_paste_requested.emit()
                # 不執行預設的文字貼上行為
                return
            else:
                # 如果沒有圖片，執行正常的文字貼上
                super().keyPressEvent(event)
        else:
            # 其他按鍵正常處理
            super().keyPressEvent(event) 