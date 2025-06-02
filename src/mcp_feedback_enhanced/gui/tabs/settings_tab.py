#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設置分頁組件
============

專門處理應用設置的分頁組件。
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QComboBox, QRadioButton, QButtonGroup, QMessageBox
)
from PySide6.QtCore import Signal

from ...i18n import t, get_i18n_manager


class SettingsTab(QWidget):
    """設置分頁組件"""
    language_changed = Signal()
    layout_mode_change_requested = Signal(bool)  # 佈局模式變更請求信號
    
    def __init__(self, combined_mode: bool, parent=None):
        super().__init__(parent)
        self.combined_mode = combined_mode
        self.i18n = get_i18n_manager()
        self._setup_ui()
    
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
        
        # 佈局模式選擇
        self.layout_button_group = QButtonGroup()
        
        # 分離模式
        self.separate_mode_radio = QRadioButton(t('settings.layout.separateMode'))
        self.separate_mode_radio.setChecked(not self.combined_mode)
        self.separate_mode_radio.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
        self.layout_button_group.addButton(self.separate_mode_radio, 0)
        layout_layout.addWidget(self.separate_mode_radio)
        
        self.separate_desc_label = QLabel(t('settings.layout.separateModeDescription'))
        self.separate_desc_label.setStyleSheet("color: #9e9e9e; font-size: 12px; margin-left: 20px; margin-bottom: 8px;")
        self.separate_desc_label.setWordWrap(True)
        layout_layout.addWidget(self.separate_desc_label)
        
        # 合併模式
        self.combined_mode_radio = QRadioButton(t('settings.layout.combinedMode'))
        self.combined_mode_radio.setChecked(self.combined_mode)
        self.combined_mode_radio.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
        self.layout_button_group.addButton(self.combined_mode_radio, 1)
        layout_layout.addWidget(self.combined_mode_radio)
        
        self.combined_desc_label = QLabel(t('settings.layout.combinedModeDescription'))
        self.combined_desc_label.setStyleSheet("color: #9e9e9e; font-size: 12px; margin-left: 20px; margin-bottom: 8px;")
        self.combined_desc_label.setWordWrap(True)
        layout_layout.addWidget(self.combined_desc_label)
        
        # 連接佈局模式變更信號
        self.layout_button_group.buttonToggled.connect(self._on_layout_mode_changed)
        
        layout.addWidget(self.layout_group)
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
    
    def _on_layout_mode_changed(self, button, checked: bool) -> None:
        """處理佈局模式變更"""
        if not checked:  # 只處理選中的按鈕
            return
            
        # 確定新的模式
        new_combined_mode = button == self.combined_mode_radio
        
        if new_combined_mode != self.combined_mode:
            # 提示用戶需要重新創建界面
            reply = QMessageBox.question(
                self, 
                t('app.layoutChangeTitle'), 
                t('app.layoutChangeMessage'),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # 用戶確認變更，發送佈局模式變更請求
                self.combined_mode = new_combined_mode
                self.layout_mode_change_requested.emit(self.combined_mode)
            else:
                # 用戶選擇不重新載入，恢復原來的選項
                if self.combined_mode:
                    self.combined_mode_radio.setChecked(True)
                else:
                    self.separate_mode_radio.setChecked(True)
    
    def update_texts(self) -> None:
        """更新界面文字（用於語言切換）"""
        # 更新GroupBox標題
        self.language_group.setTitle(t('settings.language.title'))
        self.layout_group.setTitle(t('settings.layout.title'))
        
        # 更新標籤文字
        self.language_label.setText(t('settings.language.selector'))
        self.language_description_label.setText(t('settings.language.description'))
        
        # 更新佈局設置文字
        self.separate_mode_radio.setText(t('settings.layout.separateMode'))
        self.combined_mode_radio.setText(t('settings.layout.combinedMode'))
        
        # 更新佈局描述文字
        self.separate_desc_label.setText(t('settings.layout.separateModeDescription'))
        self.combined_desc_label.setText(t('settings.layout.combinedModeDescription'))
        
        # 重新填充語言選擇器
        self._populate_language_selector()
    
    def set_layout_mode(self, combined_mode: bool) -> None:
        """設置佈局模式"""
        self.combined_mode = combined_mode
        if combined_mode:
            self.combined_mode_radio.setChecked(True)
        else:
            self.separate_mode_radio.setChecked(True) 