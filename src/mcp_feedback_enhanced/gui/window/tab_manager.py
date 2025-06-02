#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分頁管理器
==========

負責管理和創建各種分頁組件。
"""

from typing import Dict, Any
from PySide6.QtWidgets import QTabWidget, QSplitter, QWidget, QVBoxLayout
from PySide6.QtCore import Signal, Qt

from ..tabs import FeedbackTab, SummaryTab, CommandTab, SettingsTab
from ..widgets import SmartTextEdit, ImageUploadWidget
from ...i18n import t
from ...debug import gui_debug_log as debug_log


class TabManager:
    """分頁管理器"""
    
    def __init__(self, tab_widget: QTabWidget, project_dir: str, summary: str, combined_mode: bool):
        self.tab_widget = tab_widget
        self.project_dir = project_dir
        self.summary = summary
        self.combined_mode = combined_mode
        
        # 分頁組件實例
        self.feedback_tab = None
        self.summary_tab = None
        self.command_tab = None
        self.settings_tab = None
        self.combined_feedback_tab = None
    
    def create_tabs(self) -> None:
        """創建所有分頁"""
        # 清除現有分頁
        self.tab_widget.clear()
        
        if self.combined_mode:
            # 合併模式：回饋頁包含AI摘要
            self._create_combined_feedback_tab()
            self.tab_widget.addTab(self.combined_feedback_tab, t('tabs.feedback'))
        else:
            # 分離模式：分別的回饋和摘要頁
            self.feedback_tab = FeedbackTab()
            self.tab_widget.addTab(self.feedback_tab, t('tabs.feedback'))
            
            self.summary_tab = SummaryTab(self.summary)
            self.tab_widget.addTab(self.summary_tab, t('tabs.summary'))
        
        # 命令分頁
        self.command_tab = CommandTab(self.project_dir)
        self.tab_widget.addTab(self.command_tab, t('tabs.command'))
        
        # 設置分頁
        self.settings_tab = SettingsTab(self.combined_mode)
        self.tab_widget.addTab(self.settings_tab, t('tabs.language'))
        
        debug_log(f"分頁創建完成，模式: {'合併' if self.combined_mode else '分離'}")
    
    def _create_combined_feedback_tab(self) -> None:
        """創建合併模式的回饋分頁（包含AI摘要）"""
        self.combined_feedback_tab = QWidget()
        
        # 主布局
        tab_layout = QVBoxLayout(self.combined_feedback_tab)
        tab_layout.setSpacing(12)
        tab_layout.setContentsMargins(16, 16, 16, 16)
        
        # 使用垂直分割器管理 AI摘要、回饋輸入和圖片區域
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setChildrenCollapsible(False)
        
        # 創建AI摘要組件
        self.summary_tab = SummaryTab(self.summary)
        self.summary_tab.setMinimumHeight(150)
        self.summary_tab.setMaximumHeight(300)
        
        # 創建回饋輸入組件
        self.feedback_tab = FeedbackTab()
        
        # 添加到主分割器
        main_splitter.addWidget(self.summary_tab)
        main_splitter.addWidget(self.feedback_tab)
        
        # 設置分割器比例 (摘要:回饋 = 2:3)
        main_splitter.setStretchFactor(0, 2)  # AI摘要區域
        main_splitter.setStretchFactor(1, 3)  # 回饋輸入區域（包含圖片）
        main_splitter.setSizes([200, 400])  # 設置初始大小
        
        tab_layout.addWidget(main_splitter, 1)
    
    def update_tab_texts(self) -> None:
        """更新分頁標籤文字"""
        if self.combined_mode:
            # 合併模式：只有回饋、命令、設置
            self.tab_widget.setTabText(0, t('tabs.feedback'))
            self.tab_widget.setTabText(1, t('tabs.command'))
            self.tab_widget.setTabText(2, t('tabs.language'))
        else:
            # 分離模式：回饋、摘要、命令、設置
            self.tab_widget.setTabText(0, t('tabs.feedback'))
            self.tab_widget.setTabText(1, t('tabs.summary'))
            self.tab_widget.setTabText(2, t('tabs.command'))
            self.tab_widget.setTabText(3, t('tabs.language'))
        
        # 更新各分頁的內部文字
        if self.feedback_tab:
            self.feedback_tab.update_texts()
        if self.summary_tab:
            self.summary_tab.update_texts()
        if self.command_tab:
            self.command_tab.update_texts()
        if self.settings_tab:
            self.settings_tab.update_texts()
    
    def get_feedback_data(self) -> Dict[str, Any]:
        """獲取回饋數據"""
        result = {
            "interactive_feedback": "",
            "command_logs": "",
            "images": []
        }
        
        # 獲取回饋文字和圖片
        if self.feedback_tab:
            result["interactive_feedback"] = self.feedback_tab.get_feedback_text()
            result["images"] = self.feedback_tab.get_images_data()
        
        # 獲取命令日誌
        if self.command_tab:
            result["command_logs"] = self.command_tab.get_command_logs()
        
        return result
    
    def restore_content(self, feedback_text: str, command_logs: str, images_data: list) -> None:
        """恢復內容（用於界面重新創建時）"""
        try:
            if self.feedback_tab and feedback_text:
                if hasattr(self.feedback_tab, 'feedback_input'):
                    self.feedback_tab.feedback_input.setPlainText(feedback_text)
            
            if self.command_tab and command_logs:
                if hasattr(self.command_tab, 'command_output'):
                    self.command_tab.command_output.setPlainText(command_logs)
            
            if self.feedback_tab and images_data:
                if hasattr(self.feedback_tab, 'image_upload'):
                    for img_data in images_data:
                        try:
                            self.feedback_tab.image_upload.add_image_data(img_data)
                        except:
                            pass  # 如果無法恢復圖片，忽略錯誤
                            
            debug_log("內容恢復完成")
        except Exception as e:
            debug_log(f"恢復內容失敗: {e}")
    
    def connect_signals(self, parent) -> None:
        """連接信號"""
        # 連接設置分頁的信號
        if self.settings_tab:
            if hasattr(parent, 'language_changed'):
                self.settings_tab.language_changed.connect(parent.language_changed)
            if hasattr(parent, '_on_layout_mode_change_requested'):
                self.settings_tab.layout_mode_change_requested.connect(parent._on_layout_mode_change_requested)
        
        # 連接回饋分頁的圖片貼上信號
        if self.feedback_tab:
            if hasattr(parent, '_handle_image_paste_from_textarea'):
                self.feedback_tab.image_paste_requested.connect(parent._handle_image_paste_from_textarea)
    
    def cleanup(self) -> None:
        """清理資源"""
        if self.command_tab:
            self.command_tab.cleanup()
        
        debug_log("分頁管理器清理完成")
    
    def set_layout_mode(self, combined_mode: bool) -> None:
        """設置佈局模式"""
        self.combined_mode = combined_mode
        if self.settings_tab:
            self.settings_tab.set_layout_mode(combined_mode) 