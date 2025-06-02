#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令分頁組件
============

專門處理命令執行的分頁組件。
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QLineEdit, QPushButton
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

from ..utils import apply_widget_styles
from ..window.command_executor import CommandExecutor
from ...i18n import t


class CommandTab(QWidget):
    """命令分頁組件"""
    
    def __init__(self, project_dir: str, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir
        self.command_executor = CommandExecutor(project_dir, self)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """設置用戶介面"""
        command_layout = QVBoxLayout(self)
        command_layout.setSpacing(0)  # 緊湊佈局
        command_layout.setContentsMargins(0, 0, 0, 0)
        
        # 命令說明區域（頂部，只保留說明文字）
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(6)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        self.command_description_label = QLabel(t('command.description'))
        self.command_description_label.setStyleSheet("color: #9e9e9e; font-size: 11px; margin-bottom: 6px;")
        self.command_description_label.setWordWrap(True)
        header_layout.addWidget(self.command_description_label)
        
        command_layout.addWidget(header_widget)
        
        # 命令輸出區域（中間，佔大部分空間）
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.setSpacing(6)
        output_layout.setContentsMargins(12, 4, 12, 8)
        
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        self.command_output.setFont(QFont("Consolas", 11))
        self.command_output.setPlaceholderText(t('command.outputPlaceholder'))
        # 終端機風格樣式
        self.command_output.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                color: #00ff00;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
        """)
        output_layout.addWidget(self.command_output, 1)  # 佔據剩餘空間
        
        command_layout.addWidget(output_widget, 1)  # 輸出區域佔大部分空間
        
        # 命令輸入區域（底部，固定高度）
        input_widget = QWidget()
        input_widget.setFixedHeight(70)  # 固定高度
        input_layout = QVBoxLayout(input_widget)
        input_layout.setSpacing(6)
        input_layout.setContentsMargins(12, 8, 12, 12)
        
        # 命令輸入和執行按鈕（水平布局）
        input_row_layout = QHBoxLayout()
        input_row_layout.setSpacing(8)
        
        # 提示符號標籤
        prompt_label = QLabel("$")
        prompt_label.setStyleSheet("color: #00ff00; font-family: 'Consolas', 'Monaco', monospace; font-size: 14px; font-weight: bold;")
        prompt_label.setFixedWidth(20)
        input_row_layout.addWidget(prompt_label)
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText(t('command.placeholder'))
        self.command_input.setMinimumHeight(36)
        # 終端機風格輸入框
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 4px;
                padding: 8px 12px;
                color: #00ff00;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #007acc;
                background-color: #1e1e1e;
            }
        """)
        self.command_input.returnPressed.connect(self._run_command)
        input_row_layout.addWidget(self.command_input, 1)  # 佔據大部分空間
        
        self.command_run_button = QPushButton(t('command.run'))
        self.command_run_button.clicked.connect(self._run_command)
        self.command_run_button.setFixedSize(80, 36)
        apply_widget_styles(self.command_run_button, "primary_button")
        input_row_layout.addWidget(self.command_run_button)
        
        self.command_terminate_button = QPushButton(t('command.terminate'))
        self.command_terminate_button.clicked.connect(self._terminate_command)
        self.command_terminate_button.setFixedSize(80, 36)
        apply_widget_styles(self.command_terminate_button, "danger_button")
        input_row_layout.addWidget(self.command_terminate_button)
        
        input_layout.addLayout(input_row_layout)
        
        command_layout.addWidget(input_widget)  # 輸入區域在底部
    
    def _connect_signals(self) -> None:
        """連接信號"""
        self.command_executor.output_received.connect(self._append_command_output)
    
    def _run_command(self) -> None:
        """執行命令"""
        command = self.command_input.text().strip()
        if command:
            self.command_executor.run_command(command)
            self.command_input.clear()
    
    def _terminate_command(self) -> None:
        """終止命令"""
        self.command_executor.terminate_command()
    
    def _append_command_output(self, text: str) -> None:
        """添加命令輸出並自動滾動到底部"""
        # 移動光標到最後
        cursor = self.command_output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.command_output.setTextCursor(cursor)
        
        # 插入文本
        self.command_output.insertPlainText(text)
        
        # 確保滾動到最底部
        scrollbar = self.command_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # 刷新界面
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
    
    def get_command_logs(self) -> str:
        """獲取命令日誌"""
        return self.command_output.toPlainText().strip()
    
    def update_texts(self) -> None:
        """更新界面文字（用於語言切換）"""
        self.command_description_label.setText(t('command.description'))
        self.command_input.setPlaceholderText(t('command.placeholder'))
        self.command_output.setPlaceholderText(t('command.outputPlaceholder'))
        self.command_run_button.setText(t('command.run'))
        self.command_terminate_button.setText(t('command.terminate'))
    
    def cleanup(self) -> None:
        """清理資源"""
        if self.command_executor:
            self.command_executor.cleanup() 