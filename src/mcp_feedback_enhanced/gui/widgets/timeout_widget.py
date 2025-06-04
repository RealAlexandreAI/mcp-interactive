#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超時控制組件
============

提供超時設置和倒數計時器顯示功能。
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QSpinBox, QPushButton, QFrame
)
from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtGui import QFont

from .switch import SwitchWidget
from ...i18n import t
from ...debug import gui_debug_log as debug_log


class TimeoutWidget(QWidget):
    """超時控制組件"""
    
    # 信號
    timeout_occurred = Signal()  # 超時發生
    settings_changed = Signal(bool, int)  # 設置變更 (enabled, timeout_seconds)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timeout_enabled = False
        self.timeout_seconds = 600  # 預設 10 分鐘
        self.remaining_seconds = 0
        
        # 計時器
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self._update_countdown)
        
        self._setup_ui()
        self._connect_signals()
        
        debug_log("超時控制組件初始化完成")
    
    def _setup_ui(self):
        """設置用戶介面"""
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(12)
        
        # 超時開關區域
        switch_layout = QHBoxLayout()
        switch_layout.setSpacing(8)
        
        self.timeout_label = QLabel(t('timeout.enable'))
        self.timeout_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        switch_layout.addWidget(self.timeout_label)
        
        self.timeout_switch = SwitchWidget()
        self.timeout_switch.setToolTip(t('timeout.enableTooltip'))
        switch_layout.addWidget(self.timeout_switch)
        
        main_layout.addLayout(switch_layout)
        
        # 分隔線
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #464647;")
        main_layout.addWidget(separator)
        
        # 超時時間設置區域
        time_layout = QHBoxLayout()
        time_layout.setSpacing(8)
        
        self.time_label = QLabel(t('timeout.duration.label'))
        self.time_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        time_layout.addWidget(self.time_label)
        
        self.time_spinbox = QSpinBox()
        self.time_spinbox.setRange(30, 7200)  # 30秒到2小時
        self.time_spinbox.setValue(600)  # 預設10分鐘
        self.time_spinbox.setSuffix(" " + t('timeout.seconds'))
        # 應用自定義樣式
        style = self._get_spinbox_style(False)
        self.time_spinbox.setStyleSheet(style)
        debug_log("QSpinBox 樣式已應用")
        time_layout.addWidget(self.time_spinbox)

        main_layout.addLayout(time_layout)
        
        # 分隔線
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("color: #464647;")
        main_layout.addWidget(separator2)
        
        # 倒數計時器顯示區域
        countdown_layout = QHBoxLayout()
        countdown_layout.setSpacing(8)
        
        self.countdown_label = QLabel(t('timeout.remaining'))
        self.countdown_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        countdown_layout.addWidget(self.countdown_label)
        
        self.countdown_display = QLabel("--:--")
        self.countdown_display.setStyleSheet("""
            color: #ffa500; 
            font-size: 14px; 
            font-weight: bold; 
            font-family: 'Consolas', 'Monaco', monospace;
            min-width: 50px;
        """)
        countdown_layout.addWidget(self.countdown_display)
        
        main_layout.addLayout(countdown_layout)
        
        # 彈性空間
        main_layout.addStretch()
        
        # 初始狀態：隱藏倒數計時器
        self._update_visibility()
    
    def _connect_signals(self):
        """連接信號"""
        self.timeout_switch.toggled.connect(self._on_timeout_enabled_changed)
        self.time_spinbox.valueChanged.connect(self._on_timeout_duration_changed)
    
    def _on_timeout_enabled_changed(self, enabled: bool):
        """超時啟用狀態變更"""
        self.timeout_enabled = enabled
        self._update_visibility()
        
        if enabled:
            self.start_countdown()
        else:
            self.stop_countdown()
        
        self.settings_changed.emit(enabled, self.timeout_seconds)
        debug_log(f"超時功能已{'啟用' if enabled else '停用'}")
    
    def _on_timeout_duration_changed(self, seconds: int):
        """超時時間變更"""
        self.timeout_seconds = seconds
        
        # 如果正在倒數，重新開始
        if self.timeout_enabled and self.countdown_timer.isActive():
            self.start_countdown()
        
        self.settings_changed.emit(self.timeout_enabled, seconds)
        debug_log(f"超時時間設置為 {seconds} 秒")
    
    def _update_visibility(self):
        """更新組件可見性"""
        # 倒數計時器只在啟用超時時顯示
        self.countdown_label.setVisible(self.timeout_enabled)
        self.countdown_display.setVisible(self.timeout_enabled)
        
        # 時間設置在啟用時更明顯
        style = self._get_spinbox_style(self.timeout_enabled)
        self.time_spinbox.setStyleSheet(style)
        debug_log(f"QSpinBox 樣式已更新 (啟用: {self.timeout_enabled})")
    
    def start_countdown(self):
        """開始倒數計時"""
        if not self.timeout_enabled:
            return
        
        self.remaining_seconds = self.timeout_seconds
        self.countdown_timer.start(1000)  # 每秒更新
        self._update_countdown_display()
        debug_log(f"開始倒數計時：{self.timeout_seconds} 秒")
    
    def stop_countdown(self):
        """停止倒數計時"""
        self.countdown_timer.stop()
        self.countdown_display.setText("--:--")
        debug_log("倒數計時已停止")
    
    def _update_countdown(self):
        """更新倒數計時"""
        self.remaining_seconds -= 1
        self._update_countdown_display()
        
        if self.remaining_seconds <= 0:
            self.countdown_timer.stop()
            self.timeout_occurred.emit()
            debug_log("倒數計時結束，觸發超時事件")
    
    def _update_countdown_display(self):
        """更新倒數顯示"""
        if self.remaining_seconds <= 0:
            self.countdown_display.setText("00:00")
            self.countdown_display.setStyleSheet("""
                color: #ff4444; 
                font-size: 14px; 
                font-weight: bold; 
                font-family: 'Consolas', 'Monaco', monospace;
                min-width: 50px;
            """)
        else:
            minutes = self.remaining_seconds // 60
            seconds = self.remaining_seconds % 60
            time_text = f"{minutes:02d}:{seconds:02d}"
            self.countdown_display.setText(time_text)
            
            # 根據剩餘時間調整顏色
            if self.remaining_seconds <= 60:  # 最後1分鐘
                color = "#ff4444"  # 紅色
            elif self.remaining_seconds <= 300:  # 最後5分鐘
                color = "#ffaa00"  # 橙色
            else:
                color = "#ffa500"  # 黃色
            
            self.countdown_display.setStyleSheet(f"""
                color: {color}; 
                font-size: 14px; 
                font-weight: bold; 
                font-family: 'Consolas', 'Monaco', monospace;
                min-width: 50px;
            """)
    
    def set_timeout_settings(self, enabled: bool, seconds: int):
        """設置超時參數"""
        self.timeout_switch.setChecked(enabled)
        self.time_spinbox.setValue(seconds)
        self.timeout_enabled = enabled
        self.timeout_seconds = seconds
        self._update_visibility()
    
    def get_timeout_settings(self) -> tuple[bool, int]:
        """獲取超時設置"""
        return self.timeout_enabled, self.timeout_seconds
    
    def update_texts(self):
        """更新界面文字（用於語言切換）"""
        self.timeout_label.setText(t('timeout.enable'))
        self.time_label.setText(t('timeout.duration.label'))
        self.countdown_label.setText(t('timeout.remaining'))
        self.timeout_switch.setToolTip(t('timeout.enableTooltip'))
        self.time_spinbox.setSuffix(" " + t('timeout.seconds'))

    def _get_spinbox_style(self, enabled: bool) -> str:
        """獲取 QSpinBox 的樣式字符串"""
        border_color = "#007acc" if enabled else "#555555"
        focus_color = "#0099ff" if enabled else "#007acc"

        return f"""
            QSpinBox {{
                background-color: #3c3c3c;
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 4px 8px;
                color: #ffffff;
                font-size: 12px;
                min-width: 90px;
                min-height: 24px;
            }}

            QSpinBox:focus {{
                border-color: {focus_color};
                background-color: #404040;
            }}

            QSpinBox:hover {{
                background-color: #404040;
                border-color: #666666;
            }}

            QSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 18px;
                border-left: 1px solid #555555;
                border-bottom: 1px solid #555555;
                border-top-right-radius: 5px;
                background-color: #4a4a4a;
            }}

            QSpinBox::up-button:hover {{
                background-color: #5a5a5a;
            }}

            QSpinBox::up-button:pressed {{
                background-color: #007acc;
            }}

            QSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 18px;
                border-left: 1px solid #555555;
                border-top: 1px solid #555555;
                border-bottom-right-radius: 5px;
                background-color: #4a4a4a;
            }}

            QSpinBox::down-button:hover {{
                background-color: #5a5a5a;
            }}

            QSpinBox::down-button:pressed {{
                background-color: #007acc;
            }}

            QSpinBox::up-arrow {{
                width: 0px;
                height: 0px;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 6px solid #cccccc;
            }}

            QSpinBox::down-arrow {{
                width: 0px;
                height: 0px;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #cccccc;
            }}
        """
