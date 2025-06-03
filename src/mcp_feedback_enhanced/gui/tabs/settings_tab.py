#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設置分頁組件
============

專門處理應用設置的分頁組件。
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QRadioButton, QButtonGroup, QMessageBox,
    QCheckBox, QPushButton, QFrame
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from ...i18n import t, get_i18n_manager
from ...debug import gui_debug_log as debug_log


class SettingsTab(QWidget):
    """設置分頁組件"""
    language_changed = Signal()
    layout_change_requested = Signal(bool, str)  # 佈局變更請求信號 (combined_mode, orientation)
    reset_requested = Signal()  # 重置設定請求信號
    
    def __init__(self, combined_mode: bool, config_manager, parent=None):
        super().__init__(parent)
        self.combined_mode = combined_mode
        self.config_manager = config_manager
        self.layout_orientation = self.config_manager.get_layout_orientation()
        self.i18n = get_i18n_manager()
        
        # 保存需要更新的UI元素引用
        self.ui_elements = {}
        
        # 設置全域字體為微軟正黑體
        self._setup_font()
        self._setup_ui()
        
        # 在UI設置完成後，確保正確設置初始狀態
        self._set_initial_layout_state()
    
    def _setup_font(self) -> None:
        """設置全域字體"""
        font = QFont("Microsoft JhengHei", 9)  # 微軟正黑體，調整為 9pt
        self.setFont(font)
        
        # 設置整個控件的樣式表，確保中文字體正確
        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
            }
        """)
    
    def _setup_ui(self) -> None:
        """設置用戶介面"""
        # 主容器
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左側內容區域
        content_widget = QWidget()
        content_widget.setMaximumWidth(600)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)
        
        # === 語言設置 ===
        self._create_language_section(content_layout)
        
        # 添加分隔線
        self._add_separator(content_layout)
        
        # === 界面佈局 ===
        self._create_layout_section(content_layout)
        
        # 添加分隔線
        self._add_separator(content_layout)
        
        # === 視窗設置 ===
        self._create_window_section(content_layout)
        
        # 添加分隔線
        self._add_separator(content_layout)
        
        # === 重置設定 ===
        self._create_reset_section(content_layout)
        
        # 添加彈性空間
        content_layout.addStretch()
        
        # 添加到主布局
        main_layout.addWidget(content_widget)
        main_layout.addStretch()  # 右側彈性空間
        
        # 設定初始狀態
        self._set_initial_layout_state()
    
    def _add_separator(self, layout: QVBoxLayout) -> None:
        """添加分隔線"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            QFrame {
                color: #444444;
                background-color: #444444;
                border: none;
                height: 1px;
                margin: 6px 0px;
            }
        """)
        layout.addWidget(separator)
    
    def _create_section_header(self, title: str, emoji: str = "") -> QLabel:
        """創建區塊標題"""
        text = f"{emoji}  {title}" if emoji else title
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 6px;
                margin-top: 2px;
            }
        """)
        return label
    
    def _create_description(self, text: str) -> QLabel:
        """創建說明文字"""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
                color: #aaaaaa;
                font-size: 12px;
                margin-bottom: 12px;
                line-height: 1.3;
            }
        """)
        label.setWordWrap(True)
        return label
    
    def _create_language_section(self, layout: QVBoxLayout) -> None:
        """創建語言設置區域"""
        header = self._create_section_header(t('settings.language.title'), "🌐")
        layout.addWidget(header)
        # 保存引用以便更新
        self.ui_elements['language_header'] = header
        
        desc = self._create_description(t('settings.language.description'))
        layout.addWidget(desc)
        # 保存引用以便更新
        self.ui_elements['language_desc'] = desc
        
        # 語言選擇器容器
        lang_container = QHBoxLayout()
        lang_container.setContentsMargins(0, 0, 0, 0)
        
        self.language_selector = QComboBox()
        self.language_selector.setMinimumHeight(28)
        self.language_selector.setMaximumWidth(140)
        self.language_selector.setStyleSheet("""
            QComboBox {
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTMgNEw2IDdMOSA0IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPg==);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
                color: #ffffff;
                font-size: 12px;
            }
        """)
        
        # 填充語言選項
        self._populate_language_selector()
        self.language_selector.currentIndexChanged.connect(self._on_language_changed)
        
        lang_container.addWidget(self.language_selector)
        lang_container.addStretch()
        layout.addLayout(lang_container)
    
    def _create_layout_section(self, layout: QVBoxLayout) -> None:
        """創建界面佈局區域"""
        header = self._create_section_header(t('settings.layout.title'), "📐")
        layout.addWidget(header)
        # 保存引用以便更新
        self.ui_elements['layout_header'] = header
        
        desc = self._create_description(t('settings.layout.description'))
        layout.addWidget(desc)
        # 保存引用以便更新
        self.ui_elements['layout_desc'] = desc
        
        # 選項容器
        options_layout = QVBoxLayout()
        options_layout.setSpacing(2)
        
        # 創建按鈕組
        self.layout_button_group = QButtonGroup()
        
        # 分離模式
        self.separate_mode_radio = QRadioButton(t('settings.layout.separateMode'))
        self.separate_mode_radio.setStyleSheet("""
            QRadioButton {
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
                font-size: 13px;
                color: #ffffff;
                spacing: 8px;
                padding: 2px 0px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #666666;
                border-radius: 9px;
                background-color: transparent;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #0078d4;
                border-radius: 9px;
                background-color: #0078d4;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOCIgaGVpZ2h0PSI4IiB2aWV3Qm94PSIwIDAgOCA4IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8Y2lyY2xlIGN4PSI0IiBjeT0iNCIgcj0iMiIgZmlsbD0id2hpdGUiLz4KPC9zdmc+);
            }
            QRadioButton::indicator:hover {
                border-color: #0078d4;
            }
        """)
        self.layout_button_group.addButton(self.separate_mode_radio, 0)
        options_layout.addWidget(self.separate_mode_radio)
        
        separate_hint = QLabel(f"    {t('settings.layout.separateModeDescription')}")
        separate_hint.setStyleSheet("""
            QLabel {
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
                color: #888888;
                font-size: 11px;
                margin-left: 20px;
                margin-bottom: 4px;
            }
        """)
        options_layout.addWidget(separate_hint)
        # 保存引用以便更新
        self.ui_elements['separate_hint'] = separate_hint
        
        # 合併模式（垂直）
        self.combined_vertical_radio = QRadioButton(t('settings.layout.combinedVertical'))
        self.combined_vertical_radio.setStyleSheet(self.separate_mode_radio.styleSheet())
        self.layout_button_group.addButton(self.combined_vertical_radio, 1)
        options_layout.addWidget(self.combined_vertical_radio)
        
        vertical_hint = QLabel(f"    {t('settings.layout.combinedVerticalDescription')}")
        vertical_hint.setStyleSheet(separate_hint.styleSheet())
        options_layout.addWidget(vertical_hint)
        # 保存引用以便更新
        self.ui_elements['vertical_hint'] = vertical_hint
        
        # 合併模式（水平）
        self.combined_horizontal_radio = QRadioButton(t('settings.layout.combinedHorizontal'))
        self.combined_horizontal_radio.setStyleSheet(self.separate_mode_radio.styleSheet())
        self.layout_button_group.addButton(self.combined_horizontal_radio, 2)
        options_layout.addWidget(self.combined_horizontal_radio)
        
        horizontal_hint = QLabel(f"    {t('settings.layout.combinedHorizontalDescription')}")
        horizontal_hint.setStyleSheet(separate_hint.styleSheet())
        options_layout.addWidget(horizontal_hint)
        # 保存引用以便更新
        self.ui_elements['horizontal_hint'] = horizontal_hint
        
        layout.addLayout(options_layout)
        
        # 連接佈局變更信號
        self.layout_button_group.buttonToggled.connect(self._on_layout_changed)
    
    def _create_window_section(self, layout: QVBoxLayout) -> None:
        """創建視窗設置區域"""
        header = self._create_section_header(t('settings.window.title'), "🖥️")
        layout.addWidget(header)
        # 保存引用以便更新
        self.ui_elements['window_header'] = header
        
        desc = self._create_description(t('settings.window.alwaysCenterDescription'))
        layout.addWidget(desc)
        # 保存引用以便更新
        self.ui_elements['window_desc'] = desc
        
        # 選項容器
        options_layout = QVBoxLayout()
        options_layout.setSpacing(2)
        
        self.always_center_checkbox = QCheckBox(t('settings.window.alwaysCenter'))
        self.always_center_checkbox.setChecked(self.config_manager.get_always_center_window())
        self.always_center_checkbox.setStyleSheet("""
            QCheckBox {
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
                font-size: 13px;
                color: #ffffff;
                spacing: 8px;
                padding: 2px 0px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #666666;
                border-radius: 3px;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #0078d4;
                border-radius: 3px;
                background-color: #0078d4;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
            QCheckBox::indicator:hover {
                border-color: #0078d4;
            }
        """)
        self.always_center_checkbox.stateChanged.connect(self._on_always_center_changed)
        options_layout.addWidget(self.always_center_checkbox)
        
        center_hint = QLabel(f"    {t('settings.window.alwaysCenterDescription')}")
        center_hint.setStyleSheet("""
            QLabel {
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
                color: #888888;
                font-size: 11px;
                margin-left: 20px;
                margin-bottom: 4px;
            }
        """)
        options_layout.addWidget(center_hint)
        # 保存引用以便更新
        self.ui_elements['center_hint'] = center_hint
        
        layout.addLayout(options_layout)
    
    def _create_reset_section(self, layout: QVBoxLayout) -> None:
        """創建重置設定區域"""
        header = self._create_section_header(t('settings.reset.title'), "🔄")
        layout.addWidget(header)
        # 保存引用以便更新
        self.ui_elements['reset_header'] = header
        
        desc = self._create_description(t('settings.reset.description'))
        layout.addWidget(desc)
        # 保存引用以便更新
        self.ui_elements['reset_desc'] = desc
        
        reset_container = QHBoxLayout()
        reset_container.setContentsMargins(0, 0, 0, 0)
        
        self.reset_button = QPushButton(t('settings.reset.button'))
        self.reset_button.setMinimumHeight(32)
        self.reset_button.setMaximumWidth(110)
        self.reset_button.setStyleSheet("""
            QPushButton {
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #e55565;
            }
            QPushButton:pressed {
                background-color: #c82333;
            }
        """)
        self.reset_button.clicked.connect(self._on_reset_settings)
        
        reset_container.addWidget(self.reset_button)
        reset_container.addStretch()
        layout.addLayout(reset_container)

    def _populate_language_selector(self) -> None:
        """填充語言選擇器"""
        languages = [
            ('zh-TW', '繁體中文'),
            ('zh-CN', '简体中文'),
            ('en', 'English')
        ]
        
        current_language = self.i18n.get_current_language()
        
        # 暫時斷開信號連接以避免觸發變更事件
        self.language_selector.blockSignals(True)
        
        # 先清空現有選項
        self.language_selector.clear()
        
        for i, (code, name) in enumerate(languages):
            self.language_selector.addItem(name, code)
            if code == current_language:
                self.language_selector.setCurrentIndex(i)
        
        # 重新連接信號
        self.language_selector.blockSignals(False)
    
    def _on_language_changed(self, index: int) -> None:
        """語言變更事件處理"""
        if index < 0:
            return
            
        language_code = self.language_selector.itemData(index)
        if language_code and language_code != self.i18n.get_current_language():
            # 先保存語言設定
            self.config_manager.set_language(language_code)
            # 再設定語言
            self.i18n.set_language(language_code)
            # 發出信號
            self.language_changed.emit()
    
    def _on_layout_changed(self, button, checked: bool) -> None:
        """佈局變更事件處理"""
        if not checked:
            return
        
        button_id = self.layout_button_group.id(button)
        
        if button_id == 0:  # 分離模式
            new_combined_mode = False
            new_orientation = 'vertical'
        elif button_id == 1:  # 合併模式（垂直）
            new_combined_mode = True
            new_orientation = 'vertical'
        elif button_id == 2:  # 合併模式（水平）
            new_combined_mode = True
            new_orientation = 'horizontal'
        else:
            return
        
        # 檢查是否真的有變更
        if new_combined_mode != self.combined_mode or new_orientation != self.layout_orientation:
            # 先保存配置
            self.config_manager.set_layout_mode(new_combined_mode)
            self.config_manager.set_layout_orientation(new_orientation)
            
            # 更新內部狀態
            self.combined_mode = new_combined_mode
            self.layout_orientation = new_orientation
            
            # 發出佈局變更請求信號
            self.layout_change_requested.emit(new_combined_mode, new_orientation)
    
    def _on_always_center_changed(self, state: int) -> None:
        """視窗定位選項變更事件處理"""
        always_center = state == Qt.CheckState.Checked.value
        # 立即保存設定
        self.config_manager.set_always_center_window(always_center)
        debug_log(f"視窗定位設置已保存: {always_center}")  # 調試輸出
    
    def _on_reset_settings(self) -> None:
        """重置設定事件處理"""
        reply = QMessageBox.question(
            self,
            t('settings.reset.confirmTitle'),
            t('settings.reset.confirmMessage'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.reset_requested.emit()
    
    def update_texts(self) -> None:
        """更新界面文字（不重新創建界面）"""
        # 更新區塊標題
        if 'language_header' in self.ui_elements:
            self.ui_elements['language_header'].setText(f"🌐  {t('settings.language.title')}")
        if 'layout_header' in self.ui_elements:
            self.ui_elements['layout_header'].setText(f"📐  {t('settings.layout.title')}")
        if 'window_header' in self.ui_elements:
            self.ui_elements['window_header'].setText(f"🖥️  {t('settings.window.title')}")
        if 'reset_header' in self.ui_elements:
            self.ui_elements['reset_header'].setText(f"🔄  {t('settings.reset.title')}")
        
        # 更新描述文字
        if 'language_desc' in self.ui_elements:
            self.ui_elements['language_desc'].setText(t('settings.language.description'))
        if 'layout_desc' in self.ui_elements:
            self.ui_elements['layout_desc'].setText(t('settings.layout.description'))
        if 'window_desc' in self.ui_elements:
            self.ui_elements['window_desc'].setText(t('settings.window.alwaysCenterDescription'))
        if 'reset_desc' in self.ui_elements:
            self.ui_elements['reset_desc'].setText(t('settings.reset.description'))
        
        # 更新提示文字
        if 'separate_hint' in self.ui_elements:
            self.ui_elements['separate_hint'].setText(f"    {t('settings.layout.separateModeDescription')}")
        if 'vertical_hint' in self.ui_elements:
            self.ui_elements['vertical_hint'].setText(f"    {t('settings.layout.combinedVerticalDescription')}")
        if 'horizontal_hint' in self.ui_elements:
            self.ui_elements['horizontal_hint'].setText(f"    {t('settings.layout.combinedHorizontalDescription')}")
        if 'center_hint' in self.ui_elements:
            self.ui_elements['center_hint'].setText(f"    {t('settings.window.alwaysCenterDescription')}")
        
        # 更新按鈕文字
        if hasattr(self, 'reset_button'):
            self.reset_button.setText(t('settings.reset.button'))
        
        # 更新複選框文字
        if hasattr(self, 'always_center_checkbox'):
            self.always_center_checkbox.setText(t('settings.window.alwaysCenter'))
        
        # 更新單選按鈕文字
        if hasattr(self, 'separate_mode_radio'):
            self.separate_mode_radio.setText(t('settings.layout.separateMode'))
        if hasattr(self, 'combined_vertical_radio'):
            self.combined_vertical_radio.setText(t('settings.layout.combinedVertical'))
        if hasattr(self, 'combined_horizontal_radio'):
            self.combined_horizontal_radio.setText(t('settings.layout.combinedHorizontal'))
        
        # 注意：不要重新填充語言選擇器，避免重複選項問題
    
    def reload_settings_from_config(self) -> None:
        """從配置重新載入設定狀態"""
        # 重新載入語言設定
        if hasattr(self, 'language_selector'):
            self._populate_language_selector()
        
        # 重新載入佈局設定
        self.combined_mode = self.config_manager.get_layout_mode()
        self.layout_orientation = self.config_manager.get_layout_orientation()
        self._set_initial_layout_state()
        
        # 重新載入視窗設定
        if hasattr(self, 'always_center_checkbox'):
            always_center = self.config_manager.get_always_center_window()
            self.always_center_checkbox.setChecked(always_center)
            debug_log(f"重新載入視窗定位設置: {always_center}")  # 調試輸出
    
    def set_layout_mode(self, combined_mode: bool) -> None:
        """設置佈局模式"""
        self.combined_mode = combined_mode
        self._set_initial_layout_state()
    
    def set_layout_orientation(self, orientation: str) -> None:
        """設置佈局方向"""
        self.layout_orientation = orientation
        self._set_initial_layout_state()
    
    def _set_initial_layout_state(self) -> None:
        """設置初始佈局狀態"""
        if hasattr(self, 'separate_mode_radio'):
            # 暫時斷開信號連接以避免觸發變更事件
            self.layout_button_group.blockSignals(True)
            
            if not self.combined_mode:
                self.separate_mode_radio.setChecked(True)
            elif self.layout_orientation == 'vertical':
                self.combined_vertical_radio.setChecked(True)
            else:
                self.combined_horizontal_radio.setChecked(True)
            
            # 重新連接信號
            self.layout_button_group.blockSignals(False) 