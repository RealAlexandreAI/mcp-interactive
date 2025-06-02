#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回饋分頁組件
============

專門處理用戶回饋輸入的分頁組件。
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSplitter
from PySide6.QtCore import Qt, Signal

from ..widgets import SmartTextEdit, ImageUploadWidget
from ...i18n import t


class FeedbackTab(QWidget):
    """回饋分頁組件"""
    image_paste_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """設置用戶介面"""
        # 主布局
        tab_layout = QVBoxLayout(self)
        tab_layout.setSpacing(12)
        tab_layout.setContentsMargins(16, 16, 16, 16)
        
        # 說明文字
        self.feedback_description = QLabel(t('feedback.description'))
        self.feedback_description.setStyleSheet("color: #9e9e9e; font-size: 12px; margin-bottom: 10px;")
        self.feedback_description.setWordWrap(True)
        tab_layout.addWidget(self.feedback_description)
        
        # 使用分割器來管理回饋輸入和圖片區域
        feedback_splitter = QSplitter(Qt.Vertical)
        feedback_splitter.setChildrenCollapsible(False)
        
        # 回饋輸入區域
        self.feedback_input = SmartTextEdit()
        placeholder_text = t('feedback.placeholder').replace("Ctrl+Enter", "Ctrl+Enter/Cmd+Enter").replace("Ctrl+V", "Ctrl+V/Cmd+V")
        self.feedback_input.setPlaceholderText(placeholder_text)
        self.feedback_input.setMinimumHeight(120)
        self.feedback_input.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d30;
                border: 1px solid #464647;
                border-radius: 4px;
                padding: 10px;
                color: #ffffff;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        self.feedback_input.image_paste_requested.connect(self.image_paste_requested)
        
        # 圖片上傳區域
        image_upload_widget = QWidget()
        image_upload_widget.setMinimumHeight(140)
        image_upload_widget.setMaximumHeight(250)
        image_upload_layout = QVBoxLayout(image_upload_widget)
        image_upload_layout.setSpacing(8)
        image_upload_layout.setContentsMargins(0, 8, 0, 0)
        
        self.image_upload = ImageUploadWidget()
        image_upload_layout.addWidget(self.image_upload, 1)
        
        # 添加到分割器
        feedback_splitter.addWidget(self.feedback_input)
        feedback_splitter.addWidget(image_upload_widget)
        
        # 設置分割器比例 (70% : 30%)
        feedback_splitter.setStretchFactor(0, 3)  # 回饋輸入區域較大
        feedback_splitter.setStretchFactor(1, 1)  # 圖片上傳區域較小
        feedback_splitter.setSizes([300, 140])    # 設置初始大小
        
        # 設置分割器的最小尺寸，防止子元件被過度壓縮
        feedback_splitter.setMinimumHeight(340)   # 設置分割器最小高度
        
        tab_layout.addWidget(feedback_splitter, 1)
    
    def get_feedback_text(self) -> str:
        """獲取回饋文字"""
        return self.feedback_input.toPlainText().strip()
    
    def get_images_data(self) -> list:
        """獲取圖片數據"""
        return self.image_upload.get_images_data()
    
    def update_texts(self) -> None:
        """更新界面文字（用於語言切換）"""
        self.feedback_description.setText(t('feedback.description'))
        placeholder_text = t('feedback.placeholder').replace("Ctrl+Enter", "Ctrl+Enter/Cmd+Enter").replace("Ctrl+V", "Ctrl+V/Cmd+V")
        self.feedback_input.setPlaceholderText(placeholder_text)
        
        if hasattr(self, 'image_upload'):
            self.image_upload.update_texts()
    
    def handle_image_paste_from_textarea(self) -> None:
        """處理從文字框智能貼上圖片的功能"""
        self.image_upload.paste_from_clipboard() 