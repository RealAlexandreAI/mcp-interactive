#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
關於分頁組件
============

顯示應用程式資訊和聯繫方式的分頁組件。
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QPushButton, QTextEdit, QScrollArea
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices

from ...i18n import t
from ... import __version__


class AboutTab(QWidget):
    """關於分頁組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """設置用戶介面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 創建滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #464647;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #555555;
            }
        """)
        
        # 創建內容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(16, 16, 16, 16)
        
        # === 主要資訊區域（合併應用程式資訊、專案連結、聯繫與支援） ===
        self.main_info_group = QGroupBox(t('about.appInfo'))
        self.main_info_group.setObjectName('main_info_group')
        main_info_layout = QVBoxLayout(self.main_info_group)
        main_info_layout.setSpacing(16)
        main_info_layout.setContentsMargins(20, 20, 20, 20)
        
        # 應用程式標題和版本
        title_layout = QHBoxLayout()
        self.app_title_label = QLabel("MCP Feedback Enhanced")
        self.app_title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e0e0e0;")
        title_layout.addWidget(self.app_title_label)
        
        title_layout.addStretch()
        
        self.version_label = QLabel(f"v{__version__}")
        self.version_label.setStyleSheet("font-size: 16px; color: #007acc; font-weight: bold;")
        title_layout.addWidget(self.version_label)
        
        main_info_layout.addLayout(title_layout)
        
        # 應用程式描述
        self.app_description = QLabel(t('about.description'))
        self.app_description.setStyleSheet("color: #9e9e9e; font-size: 13px; line-height: 1.4; margin-bottom: 16px;")
        self.app_description.setWordWrap(True)
        main_info_layout.addWidget(self.app_description)
        
        # 分隔線
        separator1 = QLabel()
        separator1.setFixedHeight(1)
        separator1.setStyleSheet("background-color: #464647; margin: 8px 0;")
        main_info_layout.addWidget(separator1)
        
        # GitHub 專案區域
        github_layout = QHBoxLayout()
        self.github_label = QLabel("📂 " + t('about.githubProject'))
        self.github_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 14px;")
        github_layout.addWidget(self.github_label)
        
        github_layout.addStretch()
        
        self.github_button = QPushButton(t('about.visitGithub'))
        self.github_button.setFixedSize(120, 32)
        self.github_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        self.github_button.clicked.connect(self._open_github)
        github_layout.addWidget(self.github_button)
        
        main_info_layout.addLayout(github_layout)
        
        # GitHub URL
        self.github_url_label = QLabel("https://github.com/Minidoracat/mcp-feedback-enhanced")
        self.github_url_label.setStyleSheet("color: #9e9e9e; font-size: 11px; margin-left: 24px; margin-bottom: 12px;")
        main_info_layout.addWidget(self.github_url_label)
        
        # 分隔線
        separator2 = QLabel()
        separator2.setFixedHeight(1)
        separator2.setStyleSheet("background-color: #464647; margin: 8px 0;")
        main_info_layout.addWidget(separator2)
        
        # Discord 支援區域
        discord_layout = QHBoxLayout()
        self.discord_label = QLabel("💬 " + t('about.discordSupport'))
        self.discord_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 14px;")
        discord_layout.addWidget(self.discord_label)
        
        discord_layout.addStretch()
        
        self.discord_button = QPushButton(t('about.joinDiscord'))
        self.discord_button.setFixedSize(120, 32)
        self.discord_button.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QPushButton:pressed {
                background-color: #3C45A5;
            }
        """)
        self.discord_button.clicked.connect(self._open_discord)
        discord_layout.addWidget(self.discord_button)
        
        main_info_layout.addLayout(discord_layout)
        
        # Discord URL 和說明
        self.discord_url_label = QLabel("https://discord.gg/ACjf9Q58")
        self.discord_url_label.setStyleSheet("color: #9e9e9e; font-size: 11px; margin-left: 24px;")
        main_info_layout.addWidget(self.discord_url_label)
        
        self.contact_description = QLabel(t('about.contactDescription'))
        self.contact_description.setStyleSheet("color: #9e9e9e; font-size: 12px; margin-left: 24px; margin-top: 8px;")
        self.contact_description.setWordWrap(True)
        main_info_layout.addWidget(self.contact_description)
        
        content_layout.addWidget(self.main_info_group)
        
        # === 致謝區域 ===
        self.thanks_group = QGroupBox(t('about.thanks'))
        self.thanks_group.setObjectName('thanks_group')
        thanks_layout = QVBoxLayout(self.thanks_group)
        thanks_layout.setSpacing(12)
        thanks_layout.setContentsMargins(20, 20, 20, 20)
        
        # 致謝文字
        self.thanks_text = QTextEdit()
        self.thanks_text.setReadOnly(True)
        self.thanks_text.setMinimumHeight(160)
        self.thanks_text.setMaximumHeight(220)
        self.thanks_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d30;
                border: 1px solid #464647;
                border-radius: 4px;
                padding: 12px;
                color: #e0e0e0;
                font-size: 12px;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #464647;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #555555;
            }
        """)
        self.thanks_text.setPlainText(t('about.thanksText'))
        thanks_layout.addWidget(self.thanks_text)
        
        content_layout.addWidget(self.thanks_group)
        
        # 添加彈性空間
        content_layout.addStretch()
        
        # 設置滾動區域的內容
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def _open_github(self) -> None:
        """開啟 GitHub 專案連結"""
        QDesktopServices.openUrl(QUrl("https://github.com/Minidoracat/mcp-feedback-enhanced"))
    
    def _open_discord(self) -> None:
        """開啟 Discord 邀請連結"""
        QDesktopServices.openUrl(QUrl("https://discord.gg/ACjf9Q58"))
    
    def update_texts(self) -> None:
        """更新界面文字（用於語言切換）"""
        # 更新GroupBox標題
        self.main_info_group.setTitle(t('about.appInfo'))
        self.thanks_group.setTitle(t('about.thanks'))
        
        # 更新版本資訊
        self.version_label.setText(f"v{__version__}")
        
        # 更新描述文字
        self.app_description.setText(t('about.description'))
        self.contact_description.setText(t('about.contactDescription'))
        
        # 更新標籤文字
        self.github_label.setText("📂 " + t('about.githubProject'))
        self.discord_label.setText("💬 " + t('about.discordSupport'))
        
        # 更新按鈕文字
        self.github_button.setText(t('about.visitGithub'))
        self.discord_button.setText(t('about.joinDiscord'))
        
        # 更新致謝文字
        self.thanks_text.setPlainText(t('about.thanksText')) 