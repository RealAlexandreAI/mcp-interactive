#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設置分頁組件
============

專門處理應用設置的分頁組件。
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QComboBox, QRadioButton, QButtonGroup, QMessageBox,
    QCheckBox
)
from PySide6.QtCore import Signal

from ...i18n import t, get_i18n_manager


class SettingsTab(QWidget):
    """設置分頁組件"""
    language_changed = Signal()
    layout_change_requested = Signal(bool, str)  # 佈局變更請求信號 (combined_mode, orientation)
    
    def __init__(self, combined_mode: bool, config_manager, parent=None):
        super().__init__(parent)
        self.combined_mode = combined_mode
        self.config_manager = config_manager
        self.layout_orientation = self.config_manager.get_layout_orientation()
        self.i18n = get_i18n_manager()
        self._setup_ui()
        
        # 在UI設置完成後，確保正確設置初始狀態
        self._set_initial_layout_state()
    
    def _setup_ui(self) -> None:
        """設置用戶介面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # === 語言設置區域 ===
        self.language_group = QGroupBox(t('settings.language.title'))
        self.language_group.setObjectName('language_group')
        language_layout = QVBoxLayout(self.language_group)
        language_layout.setSpacing(12)
        language_layout.setContentsMargins(16, 16, 16, 16)
        
        # 語言選擇器
        language_row = QHBoxLayout()
        
        self.language_label = QLabel(t('settings.language.selector'))
        self.language_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 14px;")
        language_row.addWidget(self.language_label)
        
        self.language_selector = QComboBox()
        self.language_selector.setMinimumWidth(180)
        self.language_selector.setMinimumHeight(35)
        self.language_selector.setStyleSheet("""
            QComboBox {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #e0e0e0;
                margin-right: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #404040;
                border: 1px solid #606060;
                selection-background-color: #0078d4;
                color: #e0e0e0;
                font-size: 14px;
            }
        """)
        
        # 填充語言選項和連接信號
        self._populate_language_selector()
        self.language_selector.currentIndexChanged.connect(self._on_language_changed)
        
        language_row.addWidget(self.language_selector)
        language_row.addStretch()
        language_layout.addLayout(language_row)
        
        # 語言說明
        self.language_description_label = QLabel(t('settings.language.description'))
        self.language_description_label.setStyleSheet("color: #9e9e9e; font-size: 12px; margin-top: 8px;")
        self.language_description_label.setWordWrap(True)
        language_layout.addWidget(self.language_description_label)
        
        layout.addWidget(self.language_group)
        
        # === 界面佈局設置區域 ===
        self.layout_group = QGroupBox(t('settings.layout.title'))
        self.layout_group.setObjectName('layout_group')
        layout_layout = QVBoxLayout(self.layout_group)
        layout_layout.setSpacing(12)
        layout_layout.setContentsMargins(16, 16, 16, 16)
        
        # 佈局模式選擇 - 使用三個獨立的單選按鈕
        self.layout_button_group = QButtonGroup()
        
        # 分離模式
        self.separate_mode_radio = QRadioButton(t('settings.layout.separateMode'))
        self.separate_mode_radio.setChecked(not self.combined_mode)
        self.separate_mode_radio.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
        self.layout_button_group.addButton(self.separate_mode_radio, 0)
        layout_layout.addWidget(self.separate_mode_radio)
        
        self.separate_desc_label = QLabel(t('settings.layout.separateModeDescription'))
        self.separate_desc_label.setStyleSheet("color: #9e9e9e; font-size: 12px; margin-left: 20px; margin-bottom: 12px;")
        self.separate_desc_label.setWordWrap(True)
        layout_layout.addWidget(self.separate_desc_label)
        
        # 合併模式（垂直布局）
        self.combined_vertical_radio = QRadioButton(t('settings.layout.combinedVertical'))
        self.combined_vertical_radio.setChecked(self.combined_mode and self.layout_orientation == 'vertical')
        self.combined_vertical_radio.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
        self.layout_button_group.addButton(self.combined_vertical_radio, 1)
        layout_layout.addWidget(self.combined_vertical_radio)
        
        self.combined_vertical_desc_label = QLabel(t('settings.layout.combinedVerticalDescription'))
        self.combined_vertical_desc_label.setStyleSheet("color: #9e9e9e; font-size: 12px; margin-left: 20px; margin-bottom: 12px;")
        self.combined_vertical_desc_label.setWordWrap(True)
        layout_layout.addWidget(self.combined_vertical_desc_label)
        
        # 合併模式（水平布局）
        self.combined_horizontal_radio = QRadioButton(t('settings.layout.combinedHorizontal'))
        self.combined_horizontal_radio.setChecked(self.combined_mode and self.layout_orientation == 'horizontal')
        self.combined_horizontal_radio.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
        self.layout_button_group.addButton(self.combined_horizontal_radio, 2)
        layout_layout.addWidget(self.combined_horizontal_radio)
        
        self.combined_horizontal_desc_label = QLabel(t('settings.layout.combinedHorizontalDescription'))
        self.combined_horizontal_desc_label.setStyleSheet("color: #9e9e9e; font-size: 12px; margin-left: 20px; margin-bottom: 12px;")
        self.combined_horizontal_desc_label.setWordWrap(True)
        layout_layout.addWidget(self.combined_horizontal_desc_label)
        
        # 連接佈局變更信號
        self.layout_button_group.buttonToggled.connect(self._on_layout_changed)
        
        layout.addWidget(self.layout_group)
        
        # === 視窗定位設置區域 ===
        self.window_group = QGroupBox(t('settings.window.title'))
        self.window_group.setObjectName('window_group')
        window_layout = QVBoxLayout(self.window_group)
        window_layout.setSpacing(12)
        window_layout.setContentsMargins(16, 16, 16, 16)
        
        # 總是在主螢幕中心顯示視窗選項
        self.always_center_checkbox = QCheckBox(t('settings.window.alwaysCenter'))
        self.always_center_checkbox.setChecked(self.config_manager.get_always_center_window())
        self.always_center_checkbox.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
        self.always_center_checkbox.stateChanged.connect(self._on_always_center_changed)
        window_layout.addWidget(self.always_center_checkbox)
        
        self.center_desc_label = QLabel(t('settings.window.alwaysCenterDescription'))
        self.center_desc_label.setStyleSheet("color: #9e9e9e; font-size: 12px; margin-left: 20px; margin-bottom: 8px;")
        self.center_desc_label.setWordWrap(True)
        window_layout.addWidget(self.center_desc_label)
        
        layout.addWidget(self.window_group)
        layout.addStretch()
    
    def _populate_language_selector(self) -> None:
        """填充語言選擇器"""
        # 保存當前選擇
        current_lang = self.i18n.get_current_language()
        
        # 暫時斷開信號連接，避免觸發語言變更事件
        try:
            self.language_selector.currentIndexChanged.disconnect()
        except RuntimeError:
            pass  # 如果沒有連接則忽略
        
        # 清空並重新填充
        self.language_selector.clear()
        for lang_code in self.i18n.get_supported_languages():
            display_name = self.i18n.get_language_display_name(lang_code)
            self.language_selector.addItem(display_name, lang_code)
        
        # 設置當前選中的語言
        for i in range(self.language_selector.count()):
            if self.language_selector.itemData(i) == current_lang:
                self.language_selector.setCurrentIndex(i)
                break
        
        # 重新連接信號
        self.language_selector.currentIndexChanged.connect(self._on_language_changed)
    
    def _on_language_changed(self, index: int) -> None:
        """處理語言變更"""
        lang_code = self.language_selector.itemData(index)
        if lang_code and self.i18n.set_language(lang_code):
            # 發送語言變更信號
            self.language_changed.emit()
    
    def _on_layout_changed(self, button, checked: bool) -> None:
        """處理佈局變更"""
        if not checked:  # 只處理選中的按鈕
            return
            
        # 確定新的模式和方向
        new_combined_mode = button == self.combined_vertical_radio or button == self.combined_horizontal_radio
        new_orientation = 'vertical' if button == self.combined_vertical_radio else 'horizontal'
        
        if new_combined_mode != self.combined_mode or new_orientation != self.layout_orientation:
            # 提示用戶需要重新創建界面
            reply = QMessageBox.question(
                self, 
                t('app.layoutChangeTitle'), 
                t('app.layoutChangeMessage'),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # 用戶確認變更，發送佈局變更請求
                self.combined_mode = new_combined_mode
                self.layout_orientation = new_orientation
                self.layout_change_requested.emit(self.combined_mode, self.layout_orientation)
            else:
                # 用戶選擇不重新載入，恢復原來的選項
                if self.combined_mode:
                    if self.layout_orientation == 'vertical':
                        self.combined_vertical_radio.setChecked(True)
                    else:
                        self.combined_horizontal_radio.setChecked(True)
                else:
                    self.separate_mode_radio.setChecked(True)
    
    def _on_always_center_changed(self, state: int) -> None:
        """處理視窗定位設置變更"""
        always_center = state == 2  # Qt.Checked = 2
        self.config_manager.set_always_center_window(always_center)
    
    def update_texts(self) -> None:
        """更新界面文字（用於語言切換）"""
        # 更新GroupBox標題
        self.language_group.setTitle(t('settings.language.title'))
        self.layout_group.setTitle(t('settings.layout.title'))
        self.window_group.setTitle(t('settings.window.title'))
        
        # 更新標籤文字
        self.language_label.setText(t('settings.language.selector'))
        self.language_description_label.setText(t('settings.language.description'))
        
        # 更新佈局設置文字
        self.separate_mode_radio.setText(t('settings.layout.separateMode'))
        self.combined_vertical_radio.setText(t('settings.layout.combinedVertical'))
        self.combined_horizontal_radio.setText(t('settings.layout.combinedHorizontal'))
        
        # 更新佈局描述文字
        self.separate_desc_label.setText(t('settings.layout.separateModeDescription'))
        self.combined_vertical_desc_label.setText(t('settings.layout.combinedVerticalDescription'))
        self.combined_horizontal_desc_label.setText(t('settings.layout.combinedHorizontalDescription'))
        
        # 更新視窗設置文字
        self.always_center_checkbox.setText(t('settings.window.alwaysCenter'))
        self.center_desc_label.setText(t('settings.window.alwaysCenterDescription'))
        
        # 重新填充語言選擇器
        self._populate_language_selector()
        
        # 重新設置勾選狀態，確保設置被正確保持
        self.always_center_checkbox.setChecked(self.config_manager.get_always_center_window())
    
    def set_layout_mode(self, combined_mode: bool) -> None:
        """設置佈局模式"""
        self.combined_mode = combined_mode
        # 暫時斷開信號連接，避免觸發變更事件
        try:
            self.layout_button_group.buttonToggled.disconnect()
        except RuntimeError:
            pass
        
        # 根據當前模式和方向設置正確的選項
        if combined_mode:
            if self.layout_orientation == 'vertical':
                self.combined_vertical_radio.setChecked(True)
            else:  # horizontal
                self.combined_horizontal_radio.setChecked(True)
        else:
            self.separate_mode_radio.setChecked(True)
        
        # 重新連接信號
        self.layout_button_group.buttonToggled.connect(self._on_layout_changed)
    
    def set_layout_orientation(self, orientation: str) -> None:
        """設置佈局方向"""
        self.layout_orientation = orientation
        
        # 暫時斷開信號連接，避免觸發變更事件
        try:
            self.layout_button_group.buttonToggled.disconnect()
        except RuntimeError:
            pass
        
        # 如果是合併模式，根據方向設置正確的選項
        if self.combined_mode:
            if orientation == 'vertical':
                self.combined_vertical_radio.setChecked(True)
            else:  # horizontal
                self.combined_horizontal_radio.setChecked(True)
        
        # 重新連接信號
        self.layout_button_group.buttonToggled.connect(self._on_layout_changed)
    
    def _set_initial_layout_state(self) -> None:
        """設置初始佈局狀態"""
        # 暫時斷開信號連接，避免觸發變更事件
        try:
            self.layout_button_group.buttonToggled.disconnect()
        except RuntimeError:
            pass
        
        # 根據當前配置設置正確的選項
        if self.combined_mode:
            if self.layout_orientation == 'vertical':
                self.combined_vertical_radio.setChecked(True)
            else:  # horizontal
                self.combined_horizontal_radio.setChecked(True)
        else:
            self.separate_mode_radio.setChecked(True)
        
        # 重新連接信號
        self.layout_button_group.buttonToggled.connect(self._on_layout_changed) 