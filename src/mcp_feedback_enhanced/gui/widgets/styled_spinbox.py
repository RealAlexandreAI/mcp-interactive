#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定義樣式的 QSpinBox
==================

提供美觀的深色主題 QSpinBox，帶有自定義箭頭按鈕。
"""

from PySide6.QtWidgets import QSpinBox, QStyleOptionSpinBox, QStyle
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor


class StyledSpinBox(QSpinBox):
    """自定義樣式的 QSpinBox"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """設置基本樣式"""
        self.setStyleSheet("""
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 4px 8px;
                color: #ffffff;
                font-size: 12px;
                min-width: 100px;
                min-height: 24px;
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
            }
            
            QSpinBox:focus {
                border-color: #007acc;
                background-color: #404040;
            }
            
            QSpinBox:hover {
                background-color: #404040;
                border-color: #666666;
            }
            
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #555555;
                border-bottom: 1px solid #555555;
                border-top-right-radius: 5px;
                background-color: #4a4a4a;
            }
            
            QSpinBox::up-button:hover {
                background-color: #5a5a5a;
            }
            
            QSpinBox::up-button:pressed {
                background-color: #007acc;
            }
            
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border-left: 1px solid #555555;
                border-top: 1px solid #555555;
                border-bottom-right-radius: 5px;
                background-color: #4a4a4a;
            }
            
            QSpinBox::down-button:hover {
                background-color: #5a5a5a;
            }
            
            QSpinBox::down-button:pressed {
                background-color: #007acc;
            }
            
            QSpinBox::up-arrow {
                width: 0px;
                height: 0px;
            }
            
            QSpinBox::down-arrow {
                width: 0px;
                height: 0px;
            }
        """)
    
    def paintEvent(self, event):
        """重寫繪製事件以添加自定義箭頭"""
        # 先調用父類的繪製方法
        super().paintEvent(event)
        
        # 創建畫筆
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 獲取按鈕區域
        opt = QStyleOptionSpinBox()
        self.initStyleOption(opt)
        
        # 計算按鈕位置
        button_width = 20
        widget_rect = self.rect()
        
        # 上箭頭按鈕區域
        up_rect = QRect(
            widget_rect.width() - button_width,
            1,
            button_width - 1,
            widget_rect.height() // 2 - 1
        )
        
        # 下箭頭按鈕區域
        down_rect = QRect(
            widget_rect.width() - button_width,
            widget_rect.height() // 2,
            button_width - 1,
            widget_rect.height() // 2 - 1
        )
        
        # 繪製上箭頭
        self._draw_arrow(painter, up_rect, True)
        
        # 繪製下箭頭
        self._draw_arrow(painter, down_rect, False)
    
    def _draw_arrow(self, painter: QPainter, rect: QRect, is_up: bool):
        """繪製箭頭"""
        # 設置畫筆
        pen = QPen(QColor("#cccccc"), 1)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor("#cccccc")))
        
        # 計算箭頭位置
        center_x = rect.center().x()
        center_y = rect.center().y()
        arrow_size = 4
        
        if is_up:
            # 上箭頭：▲
            points = [
                (center_x, center_y - arrow_size // 2),      # 頂點
                (center_x - arrow_size, center_y + arrow_size // 2),  # 左下
                (center_x + arrow_size, center_y + arrow_size // 2)   # 右下
            ]
        else:
            # 下箭頭：▼
            points = [
                (center_x, center_y + arrow_size // 2),      # 底點
                (center_x - arrow_size, center_y - arrow_size // 2),  # 左上
                (center_x + arrow_size, center_y - arrow_size // 2)   # 右上
            ]
        
        # 繪製三角形
        from PySide6.QtCore import QPoint
        triangle = [QPoint(x, y) for x, y in points]
        painter.drawPolygon(triangle)
