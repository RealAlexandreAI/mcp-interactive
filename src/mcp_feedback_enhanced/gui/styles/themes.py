#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 主題樣式定義
===============

集中定義所有 GUI 元件的樣式。
"""

# 統一按鈕樣式常量
BUTTON_BASE_STYLE = """
    QPushButton {
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
    }
    QPushButton:hover {
        opacity: 0.8;
    }
"""

PRIMARY_BUTTON_STYLE = BUTTON_BASE_STYLE + """
    QPushButton { 
        background-color: #0e639c; 
    }
    QPushButton:hover { 
        background-color: #005a9e; 
    }
"""

SUCCESS_BUTTON_STYLE = BUTTON_BASE_STYLE + """
    QPushButton { 
        background-color: #4caf50; 
    }
    QPushButton:hover { 
        background-color: #45a049; 
    }
"""

DANGER_BUTTON_STYLE = BUTTON_BASE_STYLE + """
    QPushButton { 
        background-color: #f44336; 
        color: #ffffff;
    }
    QPushButton:hover { 
        background-color: #d32f2f; 
        color: #ffffff;
    }
"""

SECONDARY_BUTTON_STYLE = BUTTON_BASE_STYLE + """
    QPushButton { 
        background-color: #666666; 
    }
    QPushButton:hover { 
        background-color: #555555; 
    }
"""

# Dark 主題樣式
DARK_STYLE = """
    QMainWindow {
        background-color: #1e1e1e;
        color: #d4d4d4;
    }
    
    QWidget {
        background-color: #1e1e1e;
        color: #d4d4d4;
    }
    
    QLabel {
        color: #d4d4d4;
    }
    
    QLineEdit {
        background-color: #333333;
        border: 1px solid #464647;
        padding: 8px;
        border-radius: 6px;
        color: #d4d4d4;
        font-size: 14px;
    }
    
    QLineEdit:focus {
        border-color: #007acc;
        background-color: #383838;
    }
    
    QTextEdit {
        background-color: #333333;
        border: 1px solid #464647;
        padding: 8px;
        border-radius: 6px;
        color: #d4d4d4;
        font-size: 14px;
        line-height: 1.5;
    }
    
    QTextEdit:focus {
        border-color: #007acc;
        background-color: #383838;
    }
    
    QGroupBox {
        font-weight: bold;
        border: 2px solid #464647;
        border-radius: 6px;
        margin-top: 6px;
        padding-top: 10px;
        background-color: #2d2d30;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 8px;
        background-color: #2d2d30;
        color: #007acc;
    }
    
    QTabWidget::pane {
        border: 1px solid #464647;
        background-color: #2d2d30;
        border-radius: 6px;
    }
    
    QTabBar::tab {
        background-color: #3c3c3c;
        color: #d4d4d4;
        padding: 8px 12px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    
    QTabBar::tab:selected {
        background-color: #007acc;
        color: white;
    }
    
    QTabBar::tab:hover {
        background-color: #4a4a4a;
    }
    
    QComboBox {
        background-color: #333333;
        border: 1px solid #464647;
        padding: 6px 8px;
        border-radius: 6px;
        color: #d4d4d4;
        font-size: 14px;
        min-width: 120px;
    }
    
    QComboBox:focus {
        border-color: #007acc;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #d4d4d4;
        margin-top: 2px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #333333;
        border: 1px solid #464647;
        color: #d4d4d4;
        selection-background-color: #007acc;
    }
    
    QScrollBar:vertical {
        background-color: #333333;
        width: 12px;
        border: none;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #555555;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #777777;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    
    QScrollBar:horizontal {
        background-color: #333333;
        height: 12px;
        border: none;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #555555;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #777777;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        border: none;
        background: none;
    }
    
    QMenuBar {
        background-color: #2d2d30;
        color: #d4d4d4;
        border-bottom: 1px solid #464647;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 4px 8px;
    }
    
    QMenuBar::item:selected {
        background-color: #007acc;
    }
    
    QMenu {
        background-color: #2d2d30;
        color: #d4d4d4;
        border: 1px solid #464647;
    }
    
    QMenu::item {
        padding: 6px 12px;
    }
    
    QMenu::item:selected {
        background-color: #007acc;
    }
    
    QSplitter::handle {
        background-color: #464647;
    }
    
    QSplitter::handle:horizontal {
        width: 3px;
    }
    
    QSplitter::handle:vertical {
        height: 3px;
    }
    
    /* 訊息框樣式 */
    QMessageBox {
        background-color: #2d2d30;
        color: #d4d4d4;
    }
    
    QMessageBox QPushButton {
        min-width: 60px;
        padding: 6px 12px;
    }
""" 