#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摘要分頁組件
============

專門顯示AI工作摘要的分頁組件。
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

from ...i18n import t


class SummaryTab(QWidget):
    """摘要分頁組件"""
    
    def __init__(self, summary: str, parent=None):
        super().__init__(parent)
        self.summary = summary
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """設置用戶介面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 說明文字
        if self._is_test_summary():
            self.summary_description_label = QLabel(t('summary.testDescription'))
        else:
            self.summary_description_label = QLabel(t('summary.description'))
        
        self.summary_description_label.setStyleSheet("color: #9e9e9e; font-size: 12px; margin-bottom: 10px;")
        self.summary_description_label.setWordWrap(True)
        layout.addWidget(self.summary_description_label)
        
        # 摘要顯示區域
        self.summary_display = QTextEdit()
        # 檢查是否為測試摘要，如果是則使用翻譯的內容
        if self._is_test_summary():
            self.summary_display.setPlainText(t('test.qtGuiSummary'))
        else:
            self.summary_display.setPlainText(self.summary)
        
        self.summary_display.setReadOnly(True)
        self.summary_display.setStyleSheet("""
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
        layout.addWidget(self.summary_display, 1)
    
    def _is_test_summary(self) -> bool:
        """檢查是否為測試摘要"""
        test_indicators = [
            # 繁體中文
            "圖片預覽和視窗調整測試",
            "圖片預覽和窗口調整測試",
            "這是一個測試會話",
            "功能測試項目",
            
            # 簡體中文
            "图片预览和窗口调整测试",
            "这是一个测试会话", 
            "功能测试项目",
            
            # 英文
            "Image Preview and Window Adjustment Test",
            "This is a test session",
            "Test Items",
            
            # 通用
            "測試", "测试", "test", "Test",
            "🎯", "✅", "📋"  # 測試摘要特有的 emoji
        ]
        return any(indicator in self.summary for indicator in test_indicators)
    
    def update_texts(self) -> None:
        """更新界面文字（用於語言切換）"""
        if self._is_test_summary():
            self.summary_description_label.setText(t('summary.testDescription'))
            # 更新測試摘要的內容
            self.summary_display.setPlainText(t('test.qtGuiSummary'))
        else:
            self.summary_description_label.setText(t('summary.description')) 