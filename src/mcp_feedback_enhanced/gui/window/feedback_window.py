#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回饋收集主窗口（重構版）
========================

簡化的主窗口，專注於主要職責：窗口管理和協調各組件。
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QPushButton, QMessageBox, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeySequence, QShortcut

from .config_manager import ConfigManager
from .tab_manager import TabManager
from ..utils import apply_widget_styles
from ...i18n import t, get_i18n_manager
from ...debug import gui_debug_log as debug_log


class FeedbackWindow(QMainWindow):
    """回饋收集主窗口（重構版）"""
    language_changed = Signal()
    
    def __init__(self, project_dir: str, summary: str):
        super().__init__()
        self.project_dir = project_dir
        self.summary = summary
        self.result = None
        self.i18n = get_i18n_manager()
        
        # 初始化組件
        self.config_manager = ConfigManager()
        self.combined_mode = self.config_manager.get_layout_mode()
        
        # 設置UI
        self._setup_ui()
        self._setup_shortcuts()
        self._connect_signals()
        
        debug_log("主窗口初始化完成")
    
    def _setup_ui(self) -> None:
        """設置用戶介面"""
        self.setWindowTitle(t('app.title'))
        self.setMinimumSize(1000, 800)
        self.resize(1200, 900)
        
        # 中央元件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(16, 8, 16, 12)
        
        # 頂部專案目錄信息
        self._create_project_header(main_layout)
        
        # 分頁區域
        self._create_tab_area(main_layout)
        
        # 操作按鈕
        self._create_action_buttons(main_layout)
        
        # 應用深色主題
        self._apply_dark_style()
    
    def _create_project_header(self, layout: QVBoxLayout) -> None:
        """創建專案目錄頭部信息"""
        self.project_label = QLabel(f"{t('app.projectDirectory')}: {self.project_dir}")
        self.project_label.setStyleSheet("color: #9e9e9e; font-size: 12px; padding: 4px 0;")
        layout.addWidget(self.project_label)
    
    def _create_tab_area(self, layout: QVBoxLayout) -> None:
        """創建分頁區域"""
        # 創建滾動區域來包裝整個分頁組件
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMinimumHeight(500)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #464647;
                border-radius: 4px;
                background-color: #2b2b2b;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #2b2b2b;
            }
            QScrollArea QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollArea QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 4px;
                min-height: 20px;
                margin: 1px;
            }
            QScrollArea QScrollBar::handle:vertical:hover {
                background-color: #777;
            }
            QScrollArea QScrollBar::add-line:vertical,
            QScrollArea QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollArea QScrollBar:horizontal {
                background-color: #2a2a2a;
                height: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollArea QScrollBar::handle:horizontal {
                background-color: #555;
                border-radius: 4px;
                min-width: 20px;
                margin: 1px;
            }
            QScrollArea QScrollBar::handle:horizontal:hover {
                background-color: #777;
            }
            QScrollArea QScrollBar::add-line:horizontal,
            QScrollArea QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
        """)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(500)
        # 設置分頁組件的大小策略，確保能觸發滾動
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 初始化分頁管理器
        self.tab_manager = TabManager(
            self.tab_widget, 
            self.project_dir, 
            self.summary, 
            self.combined_mode
        )
        
        # 創建分頁
        self.tab_manager.create_tabs()
        
        # 將分頁組件放入滾動區域
        scroll_area.setWidget(self.tab_widget)
        
        layout.addWidget(scroll_area, 1)
    
    def _create_action_buttons(self, layout: QVBoxLayout) -> None:
        """創建操作按鈕"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按鈕
        self.cancel_button = QPushButton(t('buttons.cancel'))
        self.cancel_button.clicked.connect(self._cancel_feedback)
        self.cancel_button.setFixedSize(130, 40)
        apply_widget_styles(self.cancel_button, "secondary_button")
        button_layout.addWidget(self.cancel_button)
        
        # 提交按鈕
        self.submit_button = QPushButton(t('buttons.submit'))
        self.submit_button.clicked.connect(self._submit_feedback)
        self.submit_button.setFixedSize(160, 40)
        self.submit_button.setDefault(True)
        apply_widget_styles(self.submit_button, "success_button")
        button_layout.addWidget(self.submit_button)
        
        layout.addLayout(button_layout)
    
    def _setup_shortcuts(self) -> None:
        """設置快捷鍵"""
        # Ctrl+Enter 或 Cmd+Enter 提交回饋
        submit_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        submit_shortcut.activated.connect(self._submit_feedback)
        
        # macOS 支援
        submit_shortcut_mac = QShortcut(QKeySequence("Meta+Return"), self)
        submit_shortcut_mac.activated.connect(self._submit_feedback)
        
        # Escape 取消回饋
        cancel_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        cancel_shortcut.activated.connect(self._cancel_feedback)
    
    def _connect_signals(self) -> None:
        """連接信號"""
        # 連接語言變更信號
        self.language_changed.connect(self._refresh_ui_texts)
        
        # 連接分頁管理器的信號
        self.tab_manager.connect_signals(self)
    
    def _apply_dark_style(self) -> None:
        """應用深色主題"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #464647;
                border-radius: 8px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTextEdit {
                background-color: #2d2d30;
                border: 1px solid #464647;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2d2d30;
                border: 1px solid #464647;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #464647;
                border-radius: 4px;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #464647;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QSplitter {
                background-color: #2b2b2b;
            }
            QSplitter::handle {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                margin: 0px;
            }
            QSplitter::handle:horizontal {
                width: 6px;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                margin: 0px;
            }
            QSplitter::handle:vertical {
                height: 6px;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                margin: 0px;
            }
            QSplitter::handle:hover {
                background-color: #606060;
                border-color: #808080;
            }
            QSplitter::handle:pressed {
                background-color: #007acc;
                border-color: #005a9e;
            }
        """)
    
    def _on_layout_mode_change_requested(self, combined_mode: bool) -> None:
        """處理佈局模式變更請求"""
        try:
            # 保存當前內容
            current_data = self.tab_manager.get_feedback_data()
            
            # 保存新設置
            self.combined_mode = combined_mode
            self.config_manager.set_layout_mode(combined_mode)
            
            # 重新創建分頁
            self.tab_manager.set_layout_mode(combined_mode)
            self.tab_manager.create_tabs()
            
            # 恢復內容
            self.tab_manager.restore_content(
                current_data["interactive_feedback"],
                current_data["command_logs"],
                current_data["images"]
            )
            
            # 重新連接信號
            self.tab_manager.connect_signals(self)
            
            # 刷新UI文字
            self._refresh_ui_texts()
            
            debug_log(f"佈局模式已切換到: {'合併模式' if combined_mode else '分離模式'}")
            
        except Exception as e:
            debug_log(f"佈局模式切換失敗: {e}")
            QMessageBox.warning(self, t('errors.title'), t('errors.interfaceReloadError', error=str(e)))
    
    def _handle_image_paste_from_textarea(self) -> None:
        """處理從文字框智能貼上圖片的功能"""
        if self.tab_manager.feedback_tab:
            self.tab_manager.feedback_tab.handle_image_paste_from_textarea()
    
    def _submit_feedback(self) -> None:
        """提交回饋"""
        # 獲取所有回饋數據
        data = self.tab_manager.get_feedback_data()
        
        self.result = data
        debug_log(f"回饋提交: 文字長度={len(data['interactive_feedback'])}, "
                  f"命令日誌長度={len(data['command_logs'])}, "
                  f"圖片數量={len(data['images'])}")
        
        # 關閉窗口
        self.close()
    
    def _cancel_feedback(self) -> None:
        """取消回饋"""
        reply = QMessageBox.question(
            self, t('app.confirmCancel'), 
            t('app.confirmCancelMessage'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.result = None
            self.close()
    
    def _refresh_ui_texts(self) -> None:
        """刷新界面文字"""
        self.setWindowTitle(t('app.title'))
        self.project_label.setText(f"{t('app.projectDirectory')}: {self.project_dir}")
        
        # 更新按鈕文字
        self.submit_button.setText(t('buttons.submit'))
        self.cancel_button.setText(t('buttons.cancel'))
        
        # 更新分頁文字
        self.tab_manager.update_tab_texts()
    
    def closeEvent(self, event) -> None:
        """窗口關閉事件"""
        # 清理分頁管理器
        self.tab_manager.cleanup()
        event.accept()
        debug_log("主窗口已關閉") 