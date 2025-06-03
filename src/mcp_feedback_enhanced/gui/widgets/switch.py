#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
現代化切換開關組件
==================

提供類似 web 的現代化 switch 切換開關。
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QToolTip
from PySide6.QtCore import Signal, QPropertyAnimation, QRect, QEasingCurve, Property, Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPainterPath, QFont


class SwitchWidget(QWidget):
    """現代化切換開關組件"""
    
    toggled = Signal(bool)  # 狀態變更信號
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 狀態變數
        self._checked = False
        self._enabled = True
        self._animating = False
        
        # 尺寸設定
        self._width = 50
        self._height = 24
        self._thumb_radius = 10
        self._track_radius = 12
        
        # 顏色設定
        self._track_color_off = QColor(102, 102, 102)  # #666666
        self._track_color_on = QColor(0, 120, 212)     # #0078d4
        self._thumb_color = QColor(255, 255, 255)      # white
        self._track_color_disabled = QColor(68, 68, 68)  # #444444
        
        # 動畫屬性
        self._thumb_position = 2.0
        
        # 設定基本屬性
        self.setFixedSize(self._width, self._height)
        self.setCursor(Qt.PointingHandCursor)
        
        # 創建動畫
        self._animation = QPropertyAnimation(self, b"thumbPosition")
        self._animation.setDuration(200)  # 200ms 動畫時間
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 設置工具提示延遲
        self._tooltip_timer = QTimer()
        self._tooltip_timer.setSingleShot(True)
        self._tooltip_timer.timeout.connect(self._show_delayed_tooltip)
    
    @Property(float)
    def thumbPosition(self):
        return self._thumb_position
    
    @thumbPosition.setter
    def thumbPosition(self, position):
        self._thumb_position = position
        self.update()
    
    def isChecked(self) -> bool:
        """獲取選中狀態"""
        return self._checked
    
    def setChecked(self, checked: bool) -> None:
        """設置選中狀態"""
        if self._checked != checked:
            self._checked = checked
            self._animate_to_position()
            self.toggled.emit(checked)
    
    def setEnabled(self, enabled: bool) -> None:
        """設置啟用狀態"""
        super().setEnabled(enabled)
        self._enabled = enabled
        self.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
        self.update()
    
    def _animate_to_position(self) -> None:
        """動畫到目標位置"""
        if self._animating:
            return
            
        self._animating = True
        target_position = self._width - self._thumb_radius * 2 - 2 if self._checked else 2
        
        self._animation.setStartValue(self._thumb_position)
        self._animation.setEndValue(target_position)
        self._animation.finished.connect(self._on_animation_finished)
        self._animation.start()
    
    def _on_animation_finished(self) -> None:
        """動畫完成處理"""
        self._animating = False
        self._animation.finished.disconnect()
    
    def mousePressEvent(self, event):
        """滑鼠按下事件"""
        if event.button() == Qt.LeftButton and self._enabled:
            self.setChecked(not self._checked)
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """滑鼠進入事件"""
        if self._enabled:
            # 延遲顯示工具提示
            self._tooltip_timer.start(500)  # 500ms 延遲
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """滑鼠離開事件"""
        self._tooltip_timer.stop()
        super().leaveEvent(event)
    
    def _show_delayed_tooltip(self):
        """顯示延遲的工具提示"""
        if self.toolTip():
            QToolTip.showText(self.mapToGlobal(self.rect().center()), self.toolTip(), self)
    
    def paintEvent(self, event):
        """繪製事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 計算軌道矩形
        track_rect = QRect(0, (self._height - self._track_radius * 2) // 2, 
                          self._width, self._track_radius * 2)
        
        # 繪製軌道
        track_path = QPainterPath()
        track_path.addRoundedRect(track_rect, self._track_radius, self._track_radius)
        
        if not self._enabled:
            track_color = self._track_color_disabled
        elif self._checked:
            track_color = self._track_color_on
        else:
            track_color = self._track_color_off
            
        painter.fillPath(track_path, track_color)
        
        # 繪製滑塊
        thumb_x = self._thumb_position
        thumb_y = (self._height - self._thumb_radius * 2) // 2
        thumb_rect = QRect(int(thumb_x), thumb_y, self._thumb_radius * 2, self._thumb_radius * 2)
        
        thumb_path = QPainterPath()
        thumb_path.addEllipse(thumb_rect)
        
        # 滑塊顏色（可以根據狀態調整透明度）
        thumb_color = self._thumb_color
        if not self._enabled:
            thumb_color.setAlpha(180)  # 半透明效果
        
        painter.fillPath(thumb_path, thumb_color)
        
        # 添加微妙的陰影效果
        if self._enabled:
            shadow_color = QColor(0, 0, 0, 30)
            shadow_rect = thumb_rect.translated(0, 1)
            shadow_path = QPainterPath()
            shadow_path.addEllipse(shadow_rect)
            painter.fillPath(shadow_path, shadow_color)


class SwitchWithLabel(QWidget):
    """帶標籤的切換開關組件"""
    
    toggled = Signal(bool)
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        
        # 創建布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 創建標籤
        self.label = QLabel(text)
        self.label.setStyleSheet("""
            QLabel {
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
                font-size: 13px;
                color: #ffffff;
            }
        """)
        
        # 創建切換開關
        self.switch = SwitchWidget()
        self.switch.toggled.connect(self.toggled.emit)
        
        # 添加到布局
        layout.addWidget(self.label)
        layout.addStretch()  # 彈性空間，將開關推到右側
        layout.addWidget(self.switch)
        
        # 設置點擊標籤也能切換開關
        self.label.mousePressEvent = self._on_label_clicked
    
    def _on_label_clicked(self, event):
        """標籤點擊事件"""
        if event.button() == Qt.LeftButton:
            self.switch.setChecked(not self.switch.isChecked())
    
    def setText(self, text: str) -> None:
        """設置標籤文字"""
        self.label.setText(text)
    
    def text(self) -> str:
        """獲取標籤文字"""
        return self.label.text()
    
    def isChecked(self) -> bool:
        """獲取選中狀態"""
        return self.switch.isChecked()
    
    def setChecked(self, checked: bool) -> None:
        """設置選中狀態"""
        self.switch.setChecked(checked)
    
    def setEnabled(self, enabled: bool) -> None:
        """設置啟用狀態"""
        super().setEnabled(enabled)
        self.switch.setEnabled(enabled)
        self.label.setStyleSheet(f"""
            QLabel {{
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
                font-size: 13px;
                color: {"#ffffff" if enabled else "#888888"};
            }}
        """) 