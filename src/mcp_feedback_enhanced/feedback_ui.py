#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
互動式回饋收集 GUI 介面
=======================

基於 PySide6 的圖形用戶介面，提供直觀的回饋收集功能。
支援文字輸入、圖片上傳、命令執行等功能。
新增多語系支援（繁體中文、英文、簡體中文）。

作者: Fábio Ferreira  
靈感來源: dotcursorrules.com
增強功能: 圖片支援和現代化界面設計
多語系支援: Minidoracat
"""

import os
import sys
import subprocess
import base64
import uuid
import time
import platform
from typing import Optional, TypedDict, List, Dict
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QGridLayout, QFileDialog, QMessageBox,
    QTabWidget, QSizePolicy, QComboBox, QMenuBar, QMenu, QSplitter
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QDragEnterEvent, QDropEvent, QKeySequence, QShortcut, QAction

# 導入多語系支援
from .i18n import t, get_i18n_manager

from .debug import gui_debug_log as debug_log

# ===== 型別定義 =====
class FeedbackResult(TypedDict):
    """回饋結果的型別定義"""
    command_logs: str
    interactive_feedback: str
    images: List[dict]


# ===== 自定義文字輸入框 =====
class SmartTextEdit(QTextEdit):
    """支援智能 Ctrl+V 的文字輸入框"""
    image_paste_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def keyPressEvent(self, event):
        """處理按鍵事件，實現智能 Ctrl+V"""
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            # 檢查剪貼簿是否有圖片
            clipboard = QApplication.clipboard()
            
            if clipboard.mimeData().hasImage():
                # 如果有圖片，發送信號通知主窗口處理圖片貼上
                self.image_paste_requested.emit()
                # 不執行預設的文字貼上行為
                return
            else:
                # 如果沒有圖片，執行正常的文字貼上
                super().keyPressEvent(event)
        else:
            # 其他按鍵正常處理
            super().keyPressEvent(event)


# ===== 圖片預覽元件 =====
class ImagePreviewWidget(QLabel):
    """圖片預覽元件"""
    remove_clicked = Signal(str)
    
    def __init__(self, image_path: str, image_id: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.image_id = image_id
        self._setup_widget()
        self._load_image()
        self._create_delete_button()
    
    def _setup_widget(self) -> None:
        """設置元件基本屬性"""
        self.setFixedSize(100, 100)
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #464647;
                border-radius: 8px;
                background-color: #2d2d30;
                padding: 2px;
            }
            QLabel:hover {
                border-color: #007acc;
                background-color: #383838;
            }
        """)
        self.setToolTip(f"圖片: {os.path.basename(self.image_path)}")
    
    def _load_image(self) -> None:
        """載入並顯示圖片"""
        try:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.setPixmap(scaled_pixmap)
                self.setAlignment(Qt.AlignCenter)
            else:
                self.setText("無法載入圖片")
                self.setAlignment(Qt.AlignCenter)
        except Exception:
            self.setText("載入錯誤")
            self.setAlignment(Qt.AlignCenter)
    
    def _create_delete_button(self) -> None:
        """創建刪除按鈕"""
        self.delete_button = QPushButton("×", self)
        self.delete_button.setFixedSize(20, 20)
        self.delete_button.move(78, 2)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { 
                background-color: #d32f2f; 
                color: #ffffff;
            }
        """)
        self.delete_button.clicked.connect(self._on_delete_clicked)
        self.delete_button.setToolTip(t('images.clear'))
        
    def _on_delete_clicked(self) -> None:
        """處理刪除按鈕點擊事件"""
        reply = QMessageBox.question(
            self, t('images.deleteTitle'), 
            t('images.deleteConfirm', filename=os.path.basename(self.image_path)),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.remove_clicked.emit(self.image_id)
        

# ===== 圖片上傳元件 =====
class ImageUploadWidget(QWidget):
    """圖片上傳元件"""
    images_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.images: Dict[str, Dict[str, str]] = {}
        self._setup_ui()
        self.setAcceptDrops(True)
        # 啟動時清理舊的臨時文件
        self._cleanup_old_temp_files()
        
    def _setup_ui(self) -> None:
        """設置用戶介面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # 標題
        self.title = QLabel(t('images.title'))
        self.title.setFont(QFont("", 10, QFont.Bold))
        self.title.setStyleSheet("color: #007acc; margin: 1px 0;")
        layout.addWidget(self.title)
        
        # 狀態標籤
        self.status_label = QLabel(t('images.status', count=0))
        self.status_label.setStyleSheet("color: #9e9e9e; font-size: 10px; margin: 5px 0;")
        layout.addWidget(self.status_label)
        
        # 統一的圖片區域（整合按鈕、拖拽、預覽）
        self._create_unified_image_area(layout)
    
    def _create_unified_image_area(self, layout: QVBoxLayout) -> None:
        """創建統一的圖片區域"""
        # 創建滾動區域
        self.preview_scroll = QScrollArea()
        self.preview_widget = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_widget)
        self.preview_layout.setSpacing(6)
        self.preview_layout.setContentsMargins(8, 8, 8, 8)
        
        # 創建操作按鈕區域
        self._create_buttons_in_area()
        
        # 創建拖拽提示標籤（初始顯示）
        self.drop_hint_label = QLabel(t('images.dragHint'))
        self.drop_hint_label.setAlignment(Qt.AlignCenter)
        self.drop_hint_label.setMinimumHeight(60)
        self.drop_hint_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #464647;
                border-radius: 6px;
                background-color: #2d2d30;
                color: #9e9e9e;
                font-size: 11px;
                margin: 4px 0;
            }
        """)
        
        # 創建圖片網格容器
        self.images_grid_widget = QWidget()
        self.images_grid_layout = QGridLayout(self.images_grid_widget)
        self.images_grid_layout.setSpacing(4)
        self.images_grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # 將部分添加到主布局
        self.preview_layout.addWidget(self.button_widget)  # 按鈕始終顯示
        self.preview_layout.addWidget(self.drop_hint_label)
        self.preview_layout.addWidget(self.images_grid_widget)
        
        # 初始時隱藏圖片網格
        self.images_grid_widget.hide()
        
        # 設置滾動區域
        self.preview_scroll.setWidget(self.preview_widget)
        self.preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.preview_scroll.setMinimumHeight(120)  # 增加最小高度以容納按鈕
        self.preview_scroll.setMaximumHeight(200)  # 調整最大高度
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #464647;
                border-radius: 4px;
                background-color: #1e1e1e;
            }
        """)
        
        layout.addWidget(self.preview_scroll)
    
    def _create_buttons_in_area(self) -> None:
        """在統一區域內創建操作按鈕"""
        self.button_widget = QWidget()
        button_layout = QHBoxLayout(self.button_widget)
        button_layout.setContentsMargins(0, 0, 0, 4)
        button_layout.setSpacing(6)
        
        # 選擇文件按鈕
        self.file_button = QPushButton(t('buttons.selectFiles'))
        self.file_button.clicked.connect(self.select_files)
        
        # 剪貼板按鈕
        self.paste_button = QPushButton(t('buttons.pasteClipboard'))
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        
        # 清除按鈕
        self.clear_button = QPushButton(t('buttons.clearAll'))
        self.clear_button.clicked.connect(self.clear_all_images)
        
        # 設置按鈕樣式（更緊湊）
        button_style = """
            QPushButton {
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
                min-height: 24px;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """
        
        self.file_button.setStyleSheet(button_style + """
            QPushButton { 
                background-color: #0e639c; 
            }
            QPushButton:hover { 
                background-color: #005a9e; 
            }
        """)
        
        self.paste_button.setStyleSheet(button_style + """
            QPushButton { 
                background-color: #4caf50; 
            }
            QPushButton:hover { 
                background-color: #45a049; 
            }
        """)
        
        self.clear_button.setStyleSheet(button_style + """
            QPushButton { 
                background-color: #f44336; 
                color: #ffffff;
            }
            QPushButton:hover { 
                background-color: #d32f2f; 
                color: #ffffff;
            }
        """)
        
        button_layout.addWidget(self.file_button)
        button_layout.addWidget(self.paste_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()  # 左對齊按鈕
    
    def select_files(self) -> None:
        """選擇文件對話框"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            t('images.select'),
            "",
            "Image files (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;All files (*)"
        )
        if files:
            self._add_images(files)
            
    def paste_from_clipboard(self) -> None:
        """從剪貼板粘貼圖片"""
        clipboard = QApplication.clipboard()
        
        if clipboard.mimeData().hasImage():
            image = clipboard.image()
            if not image.isNull():
                # 保存臨時文件
                temp_dir = Path.home() / ".cache" / "interactive-feedback-mcp"
                temp_dir.mkdir(parents=True, exist_ok=True)
                temp_file = temp_dir / f"clipboard_{uuid.uuid4().hex}.png"
                
                # 檢查圖片尺寸，如果太大則壓縮
                max_dimension = 1024  # 最大尺寸
                if image.width() > max_dimension or image.height() > max_dimension:
                    # 計算縮放比例
                    scale = min(max_dimension / image.width(), max_dimension / image.height())
                    new_width = int(image.width() * scale)
                    new_height = int(image.height() * scale)
                    
                    # 縮放圖片
                    image = image.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    debug_log(f"圖片已縮放至: {new_width}x{new_height}")
                
                # 使用較低的質量保存以減小文件大小
                quality = 70  # 降低質量以減小文件大小
                if image.save(str(temp_file), "PNG", quality):
                    # 檢查保存後的文件大小
                    if temp_file.exists():
                        file_size = temp_file.stat().st_size
                        debug_log(f"剪貼板圖片保存成功: {temp_file}, 大小: {file_size} bytes")
                        
                        # 檢查文件大小是否超過限制
                        if file_size > 1 * 1024 * 1024:  # 1MB 限制
                            temp_file.unlink()  # 刪除過大的文件
                            QMessageBox.warning(
                                self, "圖片過大", 
                                f"剪貼板圖片壓縮後仍然超過 1MB 限制 ({file_size/1024/1024:.1f}MB)！\n"
                                f"請使用圖片編輯軟體進一步壓縮。"
                            )
                            return
                        
                        if file_size > 0:
                            self._add_images([str(temp_file)])
                        else:
                            QMessageBox.warning(self, "錯誤", f"保存的圖片文件為空！位置: {temp_file}")
                    else:
                        QMessageBox.warning(self, "錯誤", "圖片保存失敗！")
                else:
                    QMessageBox.warning(self, "錯誤", "無法保存剪貼板圖片！")
            else:
                QMessageBox.information(self, "提示", "剪貼板中沒有有效的圖片！")
        else:
            QMessageBox.information(self, "提示", "剪貼板中沒有圖片內容！")
            
    def clear_all_images(self) -> None:
        """清除所有圖片"""
        if self.images:
            reply = QMessageBox.question(
                self, '確認清除', 
                f'確定要清除所有 {len(self.images)} 張圖片嗎？',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # 清理臨時文件
                temp_files_cleaned = 0
                for image_info in self.images.values():
                    file_path = image_info["path"]
                    if "clipboard_" in os.path.basename(file_path) and ".cache" in file_path:
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                temp_files_cleaned += 1
                                debug_log(f"已刪除臨時文件: {file_path}")
                        except Exception as e:
                            debug_log(f"刪除臨時文件失敗: {e}")
                
                # 清除內存中的圖片數據
                self.images.clear()
                self._refresh_preview()
                self._update_status()
                self.images_changed.emit()
                debug_log(f"已清除所有圖片，包括 {temp_files_cleaned} 個臨時文件")
    
    def _add_images(self, file_paths: List[str]) -> None:
        """添加圖片"""
        added_count = 0
        for file_path in file_paths:
            try:
                debug_log(f"嘗試添加圖片: {file_path}")
                
                if not os.path.exists(file_path):
                    debug_log(f"文件不存在: {file_path}")
                    continue
                    
                if not self._is_image_file(file_path):
                    debug_log(f"不是圖片文件: {file_path}")
                    continue
                
                file_size = os.path.getsize(file_path)
                debug_log(f"文件大小: {file_size} bytes")
                
                # 更嚴格的大小限制（1MB）
                if file_size > 1 * 1024 * 1024:
                    QMessageBox.warning(
                        self, "文件過大", 
                        f"圖片 {os.path.basename(file_path)} 大小為 {file_size/1024/1024:.1f}MB，"
                        f"超過 1MB 限制！\n建議使用圖片編輯軟體壓縮後再上傳。"
                    )
                    continue
                
                if file_size == 0:
                    QMessageBox.warning(self, "文件為空", f"圖片 {os.path.basename(file_path)} 是空文件！")
                    continue
                
                # 讀取圖片原始二進制數據
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    debug_log(f"讀取原始數據大小: {len(raw_data)} bytes")
                    
                    if len(raw_data) == 0:
                        debug_log(f"讀取的數據為空！")
                        continue
                    
                    # 再次檢查內存中的數據大小
                    if len(raw_data) > 1 * 1024 * 1024:
                        QMessageBox.warning(
                            self, "數據過大", 
                            f"圖片 {os.path.basename(file_path)} 數據大小超過 1MB 限制！"
                        )
                        continue
                
                image_id = str(uuid.uuid4())
                self.images[image_id] = {
                    "path": file_path,
                    "data": raw_data,  # 直接保存原始二進制數據
                    "name": os.path.basename(file_path),
                    "size": file_size
                }
                added_count += 1
                debug_log(f"圖片添加成功: {os.path.basename(file_path)}")
                
            except Exception as e:
                debug_log(f"添加圖片失敗: {e}")
                QMessageBox.warning(self, "錯誤", f"無法載入圖片 {os.path.basename(file_path)}:\n{str(e)}")
                
        if added_count > 0:
            debug_log(f"共添加 {added_count} 張圖片，當前總數: {len(self.images)}")
            self._refresh_preview()
            self._update_status()
            self.images_changed.emit()
            
    def _is_image_file(self, file_path: str) -> bool:
        """檢查是否為支援的圖片格式"""
        extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        return Path(file_path).suffix.lower() in extensions
    
    def _refresh_preview(self) -> None:
        """刷新預覽布局"""
        # 清除現有預覽
        while self.images_grid_layout.count():
            child = self.images_grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 根據圖片數量決定顯示內容
        if len(self.images) == 0:
            # 沒有圖片時，顯示拖拽提示
            self.drop_hint_label.show()
            self.images_grid_widget.hide()
        else:
            # 有圖片時，隱藏拖拽提示，顯示圖片網格
            self.drop_hint_label.hide()
            self.images_grid_widget.show()
            
            # 重新添加圖片預覽
            for i, (image_id, image_info) in enumerate(self.images.items()):
                preview = ImagePreviewWidget(image_info["path"], image_id, self)
                preview.remove_clicked.connect(self._remove_image)
                
                row = i // 5
                col = i % 5
                self.images_grid_layout.addWidget(preview, row, col)
    
    def _remove_image(self, image_id: str) -> None:
        """移除圖片"""
        if image_id in self.images:
            image_info = self.images[image_id]
            
            # 如果是臨時文件（剪貼板圖片），則物理刪除文件
            file_path = image_info["path"]
            if "clipboard_" in os.path.basename(file_path) and ".cache" in file_path:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        debug_log(f"已刪除臨時文件: {file_path}")
                except Exception as e:
                    debug_log(f"刪除臨時文件失敗: {e}")
            
            # 從內存中移除圖片數據
            del self.images[image_id]
            self._refresh_preview()
            self._update_status()
            self.images_changed.emit()
            debug_log(f"已移除圖片: {image_info['name']}")
    
    def _update_status(self) -> None:
        """更新狀態標籤"""
        count = len(self.images)
        if count == 0:
            self.status_label.setText(t('images.status', count=0))
        else:
            total_size = sum(img["size"] for img in self.images.values())
            
            # 格式化文件大小
            if total_size > 1024 * 1024:  # MB
                size_mb = total_size / (1024 * 1024)
                size_str = f"{size_mb:.1f} MB"
            else:  # KB
                size_kb = total_size / 1024
                size_str = f"{size_kb:.1f} KB"
            
            self.status_label.setText(t('images.statusWithSize', count=count, size=size_str))
            
            # 基本調試信息
            debug_log(f"圖片狀態: {count} 張圖片，總大小: {size_str}")
            
    def get_images_data(self) -> List[dict]:
        """獲取圖片數據"""
        return [
            {
                "name": img["name"],
                "data": img["data"],  # 原始二進制數據
                "size": len(img["data"]) if isinstance(img["data"], bytes) else img["size"]  # 使用實際數據大小
            }
            for img in self.images.values()
        ]

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """拖拽進入事件"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and self._is_image_file(url.toLocalFile()):
                    event.acceptProposedAction()
                    self.drop_hint_label.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #007acc;
                            border-radius: 6px;
                            background-color: #383838;
                            color: #007acc;
                            font-size: 11px;
                        }
                    """)
        return
        event.ignore()
    
    def dragLeaveEvent(self, event) -> None:
        """拖拽離開事件"""
        self.drop_hint_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #464647;
                border-radius: 6px;
                background-color: #2d2d30;
                color: #9e9e9e;
                font-size: 11px;
            }
        """)
    
    def dropEvent(self, event: QDropEvent) -> None:
        """拖拽放下事件"""
        self.dragLeaveEvent(event)
        
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if self._is_image_file(file_path):
                    files.append(file_path)
        
        if files:
            self._add_images(files)
            event.acceptProposedAction()
        else:
            QMessageBox.warning(self, "格式錯誤", "請拖拽有效的圖片文件！")
    
    def _cleanup_old_temp_files(self) -> None:
        """清理舊的臨時文件"""
        try:
            temp_dir = Path.home() / ".cache" / "interactive-feedback-mcp"
            if temp_dir.exists():
                cleaned_count = 0
                for temp_file in temp_dir.glob("clipboard_*.png"):
                    try:
                        # 清理超過1小時的臨時文件
                        if temp_file.exists():
                            file_age = time.time() - temp_file.stat().st_mtime
                            if file_age > 3600:  # 1小時 = 3600秒
                                temp_file.unlink()
                                cleaned_count += 1
                    except Exception as e:
                        debug_log(f"清理舊臨時文件失敗: {e}")
                if cleaned_count > 0:
                    debug_log(f"清理了 {cleaned_count} 個舊的臨時文件")
        except Exception as e:
            debug_log(f"臨時文件清理過程出錯: {e}")
    
    def update_texts(self) -> None:
        """更新界面文字（用於語言切換）"""
        # 更新標題
        if hasattr(self, 'title'):
            self.title.setText(t('images.title'))
        
        # 更新按鈕文字
        if hasattr(self, 'file_button'):
            self.file_button.setText(t('buttons.selectFiles'))
        if hasattr(self, 'paste_button'):
            self.paste_button.setText(t('buttons.pasteClipboard'))
        if hasattr(self, 'clear_button'):
            self.clear_button.setText(t('buttons.clearAll'))
        
        # 更新拖拽區域文字
        if hasattr(self, 'drop_hint_label'):
            self.drop_hint_label.setText(t('images.dragHint'))
        
        # 更新狀態文字
        self._update_status()


# ===== 主要回饋介面 =====
class FeedbackWindow(QMainWindow):
    """回饋收集主窗口"""
    language_changed = Signal()
    
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
    
    def __init__(self, project_dir: str, summary: str):
        super().__init__()
        self.project_dir = project_dir
        self.summary = summary
        self.result = None
        self.command_process = None
        self.i18n = get_i18n_manager()
        
        self._setup_ui()
        self._apply_dark_style()
        
        # 連接語言變更信號
        self.language_changed.connect(self._refresh_ui_texts)
        
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
        
        # 分頁區域（包含AI摘要、語言設置、回饋、命令）
        self._create_tabs(main_layout)
        
        # 操作按鈕
        self._create_action_buttons(main_layout)
        
        # 設置快捷鍵
        self._setup_shortcuts()
    
    def _create_project_header(self, layout: QVBoxLayout) -> None:
        """創建專案目錄頭部信息"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 8)
        
        # 專案目錄信息 - 修改為單行顯示
        self.project_label = QLabel(f"{t('app.projectDirectory')}: {self.project_dir}")
        self.project_label.setStyleSheet("color: #9e9e9e; font-size: 12px; padding: 4px 0;")
        # 移除 setWordWrap(True) 以實現單行顯示
        header_layout.addWidget(self.project_label)
        
        header_layout.addStretch()
        
        layout.addWidget(header_widget)
    
    def _refresh_ui_texts(self) -> None:
        """刷新界面文字"""
        # 更新窗口標題
        self.setWindowTitle(t('app.title'))
        
        # 更新工具欄文字
        self._update_toolbar_texts()
        
        # 更新標籤和按鈕文字
        self._update_widget_texts()
        
        # 更新圖片上傳元件的文字
        self._update_image_upload_texts()
    
    def _update_toolbar_texts(self) -> None:
        """更新工具欄文字"""
        # 更新語言選擇器標籤
        if hasattr(self, 'language_label'):
            self.language_label.setText(t('language.selector'))
        
        # 更新語言選擇器選項
        if hasattr(self, 'language_selector'):
            # 暫時斷開信號連接以避免觸發語言變更
            self.language_selector.currentIndexChanged.disconnect()
            
            # 重新填充語言選項
            self._populate_language_selector()
            
            # 重新連接信號
            self.language_selector.currentIndexChanged.connect(self._on_language_changed)
    
    def _update_widget_texts(self) -> None:
        """更新元件文字"""
        # 更新分頁標籤
        if hasattr(self, 'tab_widget'):
            # 回饋分頁 - 現在是第一個
            self.tab_widget.setTabText(0, t('tabs.feedback'))
            # AI 摘要分頁 - 現在是第二個
            self.tab_widget.setTabText(1, t('tabs.summary'))
            # 命令分頁 - 現在是第三個
            self.tab_widget.setTabText(2, t('tabs.command'))
            # 語言設置分頁 - 現在是第四個
            self.tab_widget.setTabText(3, t('tabs.language'))
        
        # 更新專案目錄標籤
        if hasattr(self, 'project_label'):
            self.project_label.setText(f"{t('app.projectDirectory')}: {self.project_dir}")
        
        # 更新 AI 摘要相關文字
        if hasattr(self, 'summary_title'):
            self.summary_title.setText(t('aiSummary'))
        
        # 更新AI摘要內容（如果是測試摘要）
        if hasattr(self, 'summary_text'):
            # 檢查是否為測試摘要，需要動態翻譯
            if self._is_test_summary():
                # 判斷是哪種測試類型並重新獲取翻譯
                if any(keyword in self.summary for keyword in ['圖片預覽', 'Image Preview', '图片预览', '視窗調整', 'Window Adjustment', '窗口调整']):
                    # Qt GUI 測試
                    translated_summary = t('test.qtGuiSummary')
                elif any(keyword in self.summary for keyword in ['Web UI', 'WebSocket', 'web ui']):
                    # Web UI 測試
                    translated_summary = t('test.webUiSummary')
                else:
                    translated_summary = self.summary
                
                self.summary_text.setPlainText(translated_summary)
                # 更新儲存的摘要以保持一致
                self.summary = translated_summary
        
        # 更新語言設置分頁的文字
        if hasattr(self, 'language_title_label'):
            self.language_title_label.setText(t('language.settings'))
        if hasattr(self, 'language_label'):
            self.language_label.setText(t('language.selector'))
        if hasattr(self, 'language_description_label'):
            self.language_description_label.setText(t('language.description'))
        
        # 重新填充語言選擇器（確保顯示名稱正確）
        if hasattr(self, 'language_selector'):
            # 暫時斷開信號連接
            self.language_selector.currentIndexChanged.disconnect()
            self._populate_language_selector()
            # 重新連接信號
            self.language_selector.currentIndexChanged.connect(self._on_language_changed)
        
        # 更新回饋相關文字
        if hasattr(self, 'feedback_title'):
            self.feedback_title.setText(t('feedback.title'))
        if hasattr(self, 'feedback_description'):
            self.feedback_description.setText(t('feedback.description'))
        if hasattr(self, 'feedback_input'):
            # 同時支持 Windows 和 macOS 的快捷鍵提示
            placeholder_text = t('feedback.placeholder').replace("Ctrl+Enter", "Ctrl+Enter/Cmd+Enter").replace("Ctrl+V", "Ctrl+V/Cmd+V")
            self.feedback_input.setPlaceholderText(placeholder_text)
        
        # 更新命令相關文字
        if hasattr(self, 'command_title'):
            self.command_title.setText(t('command.title'))
        if hasattr(self, 'command_description'):
            self.command_description.setText(t('command.description'))
        if hasattr(self, 'command_input'):
            self.command_input.setPlaceholderText(t('command.placeholder'))
        if hasattr(self, 'command_output_label'):
            self.command_output_label.setText(t('command.output'))
        
        # 更新按鈕文字
        if hasattr(self, 'submit_button'):
            self.submit_button.setText(t('buttons.submitFeedback'))
            # 同時顯示 Windows 和 macOS 快捷鍵提示
            self.submit_button.setToolTip(f"{t('buttons.submitFeedback')} (Ctrl+Enter/Cmd+Enter)")
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setText(t('buttons.cancel'))
            self.cancel_button.setToolTip(f"{t('buttons.cancel')} (Esc)")
        if hasattr(self, 'run_command_button'):
            self.run_command_button.setText(t('buttons.runCommand'))
        
    def _is_test_summary(self) -> bool:
        """檢查是否為測試摘要，使用更嚴格的檢測邏輯"""
        # 更嚴格的測試摘要特徵組合檢測
        test_patterns = [
            # Qt GUI 測試特徵
            ('測試 Qt GUI 功能', '🎯 **功能測試項目'),
            ('Test Qt GUI Functionality', '🎯 **Test Items'),
            ('测试 Qt GUI 功能', '🎯 **功能测试项目'),
            
            # Web UI 測試特徵  
            ('測試 Web UI 功能', '🎯 **功能測試項目'),
            ('Test Web UI Functionality', '🎯 **Test Items'),
            ('测试 Web UI 功能', '🎯 **功能测试项目'),
            
            # 具體的測試項目描述
            ('圖片上傳和預覽', '智能 Ctrl+V 圖片貼上'),
            ('Image upload and preview', 'Smart Ctrl+V image paste'),
            ('图片上传和预览', '智能 Ctrl+V 图片粘贴'),
            
            # WebSocket 和服務器啟動描述
            ('WebSocket 即時通訊', 'Web UI 服務器啟動'),
            ('WebSocket real-time communication', 'Web UI server startup'),
            ('WebSocket 即时通讯', 'Web UI 服务器启动')
        ]
        
        # 必須同時包含模式中的兩個特徵才認為是測試摘要
        for pattern1, pattern2 in test_patterns:
            if pattern1 in self.summary and pattern2 in self.summary:
                return True
        
        return False
    
    def _update_image_upload_texts(self) -> None:
        """更新圖片上傳元件的文字"""
        if hasattr(self, 'image_upload'):
            self.image_upload.update_texts()

    def _create_summary_tab(self) -> None:
        """創建AI工作摘要分頁"""
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        summary_layout.setSpacing(12)  # 增加間距
        summary_layout.setContentsMargins(18, 18, 18, 18)  # 增加邊距
        
        # AI 工作摘要標題
        self.summary_title = QLabel(t('aiSummary'))
        self.summary_title.setFont(QFont("", 16, QFont.Bold))  # 增大字體
        self.summary_title.setStyleSheet("color: #007acc; margin-bottom: 10px; padding: 6px 0;")
        summary_layout.addWidget(self.summary_title)
        
        # 摘要內容
        self.summary_text = QTextEdit()
        self.summary_text.setPlainText(self.summary)
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 16px;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        
        summary_layout.addWidget(self.summary_text, 1)
        
        self.tab_widget.addTab(summary_widget, t('tabs.summary'))
    
    def _create_language_tab(self) -> None:
        """創建語言設置分頁"""
        language_widget = QWidget()
        language_layout = QVBoxLayout(language_widget)
        language_layout.setSpacing(12)
        language_layout.setContentsMargins(16, 16, 16, 16)
        
        # 語言設置標題
        self.language_title_label = QLabel(t('language.settings'))
        self.language_title_label.setFont(QFont("", 16, QFont.Bold))  # 增大字體
        self.language_title_label.setStyleSheet("color: #007acc; margin-bottom: 8px; padding: 4px 0;")
        language_layout.addWidget(self.language_title_label)
        
        # 語言選擇區域
        selector_group = QGroupBox()
        selector_layout = QVBoxLayout(selector_group)
        selector_layout.setSpacing(12)  # 增加間距
        selector_layout.setContentsMargins(16, 16, 16, 16)  # 增加邊距
        
        # 語言選擇器標籤和下拉框
        selector_row = QHBoxLayout()
        
        self.language_label = QLabel(t('language.selector'))
        self.language_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 14px;")  # 增大字體
        selector_row.addWidget(self.language_label)
        
        self.language_selector = QComboBox()
        self.language_selector.setMinimumWidth(180)  # 增加寬度
        self.language_selector.setMinimumHeight(35)  # 增加高度
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
        
        # 填充語言選項
        self._populate_language_selector()
        
        # 連接語言切換信號
        self.language_selector.currentIndexChanged.connect(self._on_language_changed)
        
        selector_row.addWidget(self.language_selector)
        selector_row.addStretch()
        
        selector_layout.addLayout(selector_row)
        
        # 語言說明
        self.language_description_label = QLabel(t('language.description'))
        self.language_description_label.setStyleSheet("color: #9e9e9e; font-size: 12px; margin-top: 12px;")  # 增大字體
        self.language_description_label.setWordWrap(True)
        selector_layout.addWidget(self.language_description_label)
        
        language_layout.addWidget(selector_group)
        language_layout.addStretch()
        
        self.tab_widget.addTab(language_widget, t('tabs.language'))
    
    def _populate_language_selector(self) -> None:
        """填充語言選擇器"""
        # 保存當前選擇
        current_lang = self.i18n.get_current_language()
        
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
    
    def _on_language_changed(self, index: int) -> None:
        """處理語言變更"""
        lang_code = self.language_selector.itemData(index)
        if lang_code and self.i18n.set_language(lang_code):
            # 發送語言變更信號
            self.language_changed.emit()

    def _create_tabs(self, layout: QVBoxLayout) -> None:
        """創建分頁標籤（重新組織結構）"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(500)  # 增加分頁區域高度
        
        # 回饋分頁 - 移到第一個位置
        self._create_feedback_tab()
        
        # AI 工作摘要分頁 - 移到第二個位置
        self._create_summary_tab()
        
        # 命令分頁  
        self._create_command_tab()
        
        # 語言設置分頁
        self._create_language_tab()
        
        layout.addWidget(self.tab_widget, 1)  # 讓分頁區域能夠擴展
    
    def _create_feedback_tab(self) -> None:
        """創建回饋分頁（修復布局比例）"""
        feedback_widget = QWidget()
        
        # 使用分割器來管理回饋輸入和圖片區域
        feedback_splitter = QSplitter(Qt.Vertical)
        feedback_splitter.setChildrenCollapsible(False)
        
        # 回饋輸入區域
        feedback_input_widget = QWidget()
        feedback_input_widget.setMinimumHeight(200)  # 設置最小高度，確保輸入框可見
        feedback_input_layout = QVBoxLayout(feedback_input_widget)
        feedback_input_layout.setSpacing(8)
        feedback_input_layout.setContentsMargins(12, 12, 12, 8)
        
        feedback_group = QGroupBox()
        feedback_layout = QVBoxLayout(feedback_group)
        feedback_layout.setSpacing(8)
        feedback_layout.setContentsMargins(12, 8, 12, 12)
        
        # 回饋標題和說明
        self.feedback_title = QLabel(t('feedback.title'))
        self.feedback_title.setFont(QFont("", 13, QFont.Bold))  # 增大字體
        self.feedback_title.setStyleSheet("color: #007acc; margin-bottom: 6px;")
        feedback_layout.addWidget(self.feedback_title)
        
        # 說明文字
        self.feedback_description = QLabel(t('feedback.description'))
        self.feedback_description.setStyleSheet("color: #9e9e9e; font-size: 11px; margin-bottom: 10px;")  # 增大字體
        self.feedback_description.setWordWrap(True)
        feedback_layout.addWidget(self.feedback_description)
        
        # 文字輸入框（調整最小高度並設置合理的最大高度）
        self.feedback_input = SmartTextEdit()
        # 同時支持 Windows 和 macOS 的快捷鍵提示
        placeholder_text = t('feedback.placeholder').replace("Ctrl+Enter", "Ctrl+Enter/Cmd+Enter").replace("Ctrl+V", "Ctrl+V/Cmd+V")
        self.feedback_input.setPlaceholderText(placeholder_text)
        
        self.feedback_input.setMinimumHeight(120)  # 增加最小高度
        self.feedback_input.setMaximumHeight(450)  # 增加最大高度
        # 設置輸入框字體
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
        # 連接智能貼上信號
        self.feedback_input.image_paste_requested.connect(self._handle_image_paste_from_textarea)
        feedback_layout.addWidget(self.feedback_input, 1)  # 讓輸入框能夠擴展
        
        feedback_input_layout.addWidget(feedback_group, 1)
        
        # 圖片上傳區域
        image_upload_widget = QWidget()
        image_upload_widget.setMinimumHeight(140)  # 設置最小高度
        image_upload_widget.setMaximumHeight(250)  # 設置最大高度，防止過度擴展
        image_upload_layout = QVBoxLayout(image_upload_widget)
        image_upload_layout.setSpacing(8)
        image_upload_layout.setContentsMargins(12, 8, 12, 12)
        
        self.image_upload = ImageUploadWidget()
        image_upload_layout.addWidget(self.image_upload, 1)  # 讓圖片上傳區域能夠擴展
        
        # 添加到分割器
        feedback_splitter.addWidget(feedback_input_widget)
        feedback_splitter.addWidget(image_upload_widget)
        
        # 調整分割器的初始比例和最小尺寸
        feedback_splitter.setStretchFactor(0, 3)  # 回饋輸入區域較大
        feedback_splitter.setStretchFactor(1, 1)  # 圖片上傳區域較小
        feedback_splitter.setSizes([300, 140])    # 設置初始大小
        
        # 設置分割器的最小尺寸，防止子元件被過度壓縮
        feedback_splitter.setMinimumHeight(340)   # 設置分割器最小高度
        
        # 設置主布局
        main_layout = QVBoxLayout(feedback_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(feedback_splitter)
        
        self.tab_widget.addTab(feedback_widget, t('tabs.feedback'))
        
    def _create_command_tab(self) -> None:
        """創建命令分頁（終端機風格布局）"""
        command_widget = QWidget()
        command_layout = QVBoxLayout(command_widget)
        command_layout.setSpacing(0)  # 緊湊佈局
        command_layout.setContentsMargins(0, 0, 0, 0)
        
        # 命令標題區域（頂部）
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(6)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        self.command_title = QLabel(t('command.title'))
        self.command_title.setFont(QFont("", 13, QFont.Bold))
        self.command_title.setStyleSheet("color: #007acc; margin-bottom: 4px;")
        header_layout.addWidget(self.command_title)
        
        self.command_description = QLabel(t('command.description'))
        self.command_description.setStyleSheet("color: #9e9e9e; font-size: 11px; margin-bottom: 6px;")
        self.command_description.setWordWrap(True)
        header_layout.addWidget(self.command_description)
        
        command_layout.addWidget(header_widget)
        
        # 命令輸出區域（中間，佔大部分空間）
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.setSpacing(6)
        output_layout.setContentsMargins(12, 4, 12, 8)
        
        self.command_output_label = QLabel(t('command.output'))
        self.command_output_label.setFont(QFont("", 12, QFont.Bold))
        self.command_output_label.setStyleSheet("color: #007acc; margin-bottom: 4px;")
        output_layout.addWidget(self.command_output_label)
        
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        self.command_output.setFont(QFont("Consolas", 11))
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
        
        self.run_command_button = QPushButton(t('buttons.runCommand'))
        self.run_command_button.clicked.connect(self._run_command)
        self.run_command_button.setFixedSize(80, 36)
        self.run_command_button.setStyleSheet(self.PRIMARY_BUTTON_STYLE)
        input_row_layout.addWidget(self.run_command_button)
        
        input_layout.addLayout(input_row_layout)
        
        command_layout.addWidget(input_widget)  # 輸入區域在底部
        
        self.tab_widget.addTab(command_widget, t('tabs.command'))
    
    def _create_action_buttons(self, layout: QVBoxLayout) -> None:
        """創建操作按鈕"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按鈕
        self.cancel_button = QPushButton(t('buttons.cancel'))
        self.cancel_button.clicked.connect(self._cancel_feedback)
        self.cancel_button.setFixedSize(130, 40)  # 增大按鈕尺寸
        self.cancel_button.setStyleSheet(self.SECONDARY_BUTTON_STYLE)
        button_layout.addWidget(self.cancel_button)
        
        # 提交按鈕
        self.submit_button = QPushButton(t('buttons.submitFeedback'))
        self.submit_button.clicked.connect(self._submit_feedback)
        self.submit_button.setFixedSize(160, 40)  # 增大按鈕尺寸
        self.submit_button.setDefault(True)
        self.submit_button.setStyleSheet(self.PRIMARY_BUTTON_STYLE)
        button_layout.addWidget(self.submit_button)
        
        layout.addLayout(button_layout)
    
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
            """)

    def _handle_image_paste_from_textarea(self) -> None:
        """處理從文字框智能貼上圖片的功能"""
        try:
            # 調用圖片上傳組件的剪貼簿貼上功能
            self.image_upload.paste_from_clipboard()
            
            # 顯示智能貼上提示
            # 可以在這裡添加狀態提示，比如狀態欄或臨時通知
            debug_log("智能貼上：已將圖片從文字框貼到圖片區域")
            
        except Exception as e:
            debug_log(f"智能貼上失敗: {e}")

    def _append_command_output(self, text: str) -> None:
        """添加命令輸出並自動滾動到底部"""
        if hasattr(self, 'command_output'):
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
            QApplication.processEvents()

    def _read_command_output(self) -> None:
        """讀取命令輸出（非阻塞方式）"""
        if not hasattr(self, 'command_process') or not self.command_process:
            if hasattr(self, 'timer'):
                self.timer.stop()
            return
            
        # 檢查進程是否還在運行
        if self.command_process.poll() is None:
            try:
                # 檢查是否有可讀取的輸出（非阻塞）
                import select
                import sys
                
                if sys.platform == "win32":
                    # Windows 下使用不同的方法
                    try:
                        # 嘗試讀取一行，但設置較短的超時
                        import threading
                        import queue
                        
                        if not hasattr(self, '_output_queue'):
                            self._output_queue = queue.Queue()
                            self._reader_thread = threading.Thread(
                                target=self._read_process_output_thread,
                                daemon=True
                            )
                            self._reader_thread.start()
                        
                        # 從隊列中獲取輸出（非阻塞）
                        try:
                            while True:
                                output = self._output_queue.get_nowait()
                                if output is None:  # 進程結束信號
                                    break
                                self._append_command_output(output)
                        except queue.Empty:
                            pass  # 沒有新輸出，繼續等待
                            
                    except ImportError:
                        # 如果threading不可用，使用原來的方法但加上非阻塞檢查
                        output = self.command_process.stdout.readline()
                        if output:
                            filtered_output = self._filter_command_output(output)
                            if filtered_output:
                                self._append_command_output(filtered_output)
                else:
                    # Unix/Linux/macOS 下使用 select
                    ready, _, _ = select.select([self.command_process.stdout], [], [], 0.1)
                    if ready:
                        output = self.command_process.stdout.readline()
                        if output:
                            # 過濾不必要的輸出行
                            filtered_output = self._filter_command_output(output)
                            if filtered_output:
                                self._append_command_output(filtered_output)
                
                # 檢查命令執行超時（30秒）
                if not hasattr(self, '_command_start_time'):
                    self._command_start_time = time.time()
                elif time.time() - self._command_start_time > 30:
                    self._append_command_output(f"\n⚠️ 命令執行超過30秒，自動終止...")
                    self._terminate_command()
                    
            except Exception as e:
                debug_log(f"讀取命令輸出錯誤: {e}")
        else:
            # 進程結束，停止計時器並讀取剩餘輸出
            if hasattr(self, 'timer'):
                self.timer.stop()
            
            # 清理資源
            if hasattr(self, '_output_queue'):
                delattr(self, '_output_queue')
            if hasattr(self, '_reader_thread'):
                delattr(self, '_reader_thread')
            if hasattr(self, '_command_start_time'):
                delattr(self, '_command_start_time')
                
            try:
                # 讀取剩餘的輸出
                remaining_output, _ = self.command_process.communicate(timeout=2)
                if remaining_output and remaining_output.strip():
                    filtered_output = self._filter_command_output(remaining_output)
                    if filtered_output:
                        self._append_command_output(filtered_output)
            except subprocess.TimeoutExpired:
                debug_log("讀取剩餘輸出超時")
            except Exception as e:
                debug_log(f"讀取剩餘輸出錯誤: {e}")
            
            return_code = self.command_process.returncode
            self._append_command_output(f"\n進程結束，返回碼: {return_code}\n")

    def _run_command(self) -> None:
        """執行命令"""
        command = self.command_input.text().strip()
        if not command:
            return

        # 如果已經有命令在執行，先停止
        if hasattr(self, 'timer') and self.timer.isActive():
            self._terminate_command()

        self._append_command_output(f"$ {command}\n")
        
        # 清空輸入欄位
        self.command_input.clear()
        
        # 保存當前命令用於輸出過濾
        self._last_command = command
        
        try:
            # 準備環境變數以避免不必要的輸出
            env = os.environ.copy()
            # 禁用npm的進度顯示和其他多餘輸出
            env['NO_UPDATE_NOTIFIER'] = '1'
            env['NPM_CONFIG_UPDATE_NOTIFIER'] = 'false'
            env['NPM_CONFIG_FUND'] = 'false'
            env['NPM_CONFIG_AUDIT'] = 'false'
            env['NPM_CONFIG_PROGRESS'] = 'false'
            env['CI'] = 'true'  # 這會讓很多工具使用非互動模式
            
            # 在專案目錄中執行命令
            self.command_process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env  # 使用修改過的環境變數
            )
            
            # 初始化命令開始時間
            self._command_start_time = time.time()
            
            # 清理之前的資源
            if hasattr(self, '_output_queue'):
                delattr(self, '_output_queue')
            if hasattr(self, '_reader_thread'):
                delattr(self, '_reader_thread')
            
            # 使用計時器讀取輸出
            self.timer = QTimer()
            self.timer.timeout.connect(self._read_command_output)
            self.timer.start(100)
            
        except Exception as e:
            self._append_command_output(f"錯誤: {str(e)}\n")
            # 發生錯誤時也要確保輸入欄位已清空
            self.command_input.clear()
    
    def _read_process_output_thread(self) -> None:
        """在後台線程中讀取進程輸出（Windows專用）"""
        try:
            while self.command_process and self.command_process.poll() is None:
                try:
                    output = self.command_process.stdout.readline()
                    if output:
                        # 過濾不必要的輸出行
                        filtered_output = self._filter_command_output(output)
                        if filtered_output:
                            self._output_queue.put(filtered_output)
                    else:
                        # 沒有輸出時稍微休眠，避免CPU過度使用
                        time.sleep(0.05)
                except Exception as e:
                    debug_log(f"後台線程讀取輸出錯誤: {e}")
                    break
            
            # 進程結束，發送結束信號
            if hasattr(self, '_output_queue'):
                self._output_queue.put(None)
                
        except Exception as e:
            debug_log(f"後台線程錯誤: {e}")

    def _filter_command_output(self, output: str) -> str:
        """過濾命令輸出，移除不必要的信息"""
        if not output or not output.strip():
            return ""
        
        # 需要過濾的模式
        filter_patterns = [
            # npm 相關的無關輸出
            "npm WARN config global",
            "npm WARN config user",
            "npm notice",
            "npm fund",
            "npm audit",
            "added",
            "found 0 vulnerabilities",
            "up to date",
            "packages are looking for funding",
            "run `npm fund` for details",
            # Python 相關的無關輸出
            "WARNING:",
            "Traceback",
            # 其他工具的無關輸出
            "deprecated",
            "WARN",
        ]
        
        # 檢查是否包含過濾模式
        for pattern in filter_patterns:
            if pattern.lower() in output.lower():
                return ""
        
        # 對於npm --version，只保留版本號行
        if hasattr(self, '_last_command') and 'npm' in self._last_command and '--version' in self._last_command:
            # 如果輸出看起來像版本號（數字.數字.數字格式）
            import re
            version_pattern = r'^\d+\.\d+\.\d+'
            if re.match(version_pattern, output.strip()):
                return output
            # 過濾掉其他非版本號的輸出
            elif not any(char.isdigit() for char in output):
                return ""
        
        return output

    def _terminate_command(self) -> None:
        """終止當前執行的命令"""
        if hasattr(self, 'timer'):
            self.timer.stop()
            
        if hasattr(self, 'command_process') and self.command_process:
            try:
                # 嘗試優雅地終止進程
                self.command_process.terminate()
                
                # 等待一段時間，如果進程沒有結束，強制殺死
                try:
                    self.command_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.command_process.kill()
                    self._append_command_output("強制終止進程")
                    
            except Exception as e:
                debug_log(f"終止命令進程錯誤: {e}")
        
        # 清理資源
        if hasattr(self, '_output_queue'):
            delattr(self, '_output_queue')
        if hasattr(self, '_reader_thread'):
            delattr(self, '_reader_thread')
        if hasattr(self, '_command_start_time'):
            delattr(self, '_command_start_time')

    def _submit_feedback(self) -> None:
        """提交回饋"""
        feedback_text = self.feedback_input.toPlainText().strip()
        
        # 檢查回饋內容是否為空
        if not feedback_text:
            QMessageBox.information(
                self, 
                t('feedback.emptyTitle'), 
                t('feedback.emptyMessage')
            )
            # 將焦點設置到回饋輸入框
            self.feedback_input.setFocus()
            return
        
        self.result = {
            "interactive_feedback": feedback_text,
            "command_logs": self.command_output.toPlainText(),
            "images": self.image_upload.get_images_data()
        }
        self.close()
    
    def _cancel_feedback(self) -> None:
        """取消回饋"""
        self.close()

    def closeEvent(self, event) -> None:
        """處理視窗關閉事件"""
        # 清理命令執行相關資源
        if hasattr(self, 'timer') or hasattr(self, 'command_process'):
            self._terminate_command()
        
        # 清理圖片上傳組件中的臨時文件
        if hasattr(self, 'image_upload') and self.image_upload:
            temp_files_cleaned = 0
            for image_info in self.image_upload.images.values():
                file_path = image_info["path"]
                if "clipboard_" in os.path.basename(file_path) and ".cache" in file_path:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            temp_files_cleaned += 1
                            debug_log(f"關閉時清理臨時文件: {file_path}")
                    except Exception as e:
                        debug_log(f"關閉時清理臨時文件失敗: {e}")
            if temp_files_cleaned > 0:
                debug_log(f"視窗關閉時清理了 {temp_files_cleaned} 個臨時文件")
        
        event.accept()

    def _setup_shortcuts(self) -> None:
        """設置快捷鍵"""
        # 同時支持 Windows (Ctrl) 和 macOS (Cmd) 快捷鍵
        
        # Windows/Linux: Ctrl+Enter 提交回饋
        ctrl_submit_shortcut1 = QShortcut(QKeySequence("Ctrl+Return"), self)
        ctrl_submit_shortcut2 = QShortcut(QKeySequence("Ctrl+Enter"), self)
        ctrl_submit_shortcut1.activated.connect(self._submit_feedback)
        ctrl_submit_shortcut2.activated.connect(self._submit_feedback)
        
        # macOS: Cmd+Enter 提交回饋
        cmd_submit_shortcut1 = QShortcut(QKeySequence("Cmd+Return"), self)
        cmd_submit_shortcut2 = QShortcut(QKeySequence("Cmd+Enter"), self)
        cmd_submit_shortcut1.activated.connect(self._submit_feedback)
        cmd_submit_shortcut2.activated.connect(self._submit_feedback)
        
        # Escape 取消（通用）
        cancel_shortcut = QShortcut(QKeySequence("Esc"), self)
        cancel_shortcut.activated.connect(self._cancel_feedback)


# ===== 主要入口函數 =====
def feedback_ui(project_directory: str, summary: str) -> Optional[FeedbackResult]:
    """
    啟動回饋收集 GUI 介面
    
    Args:
        project_directory: 專案目錄路徑
        summary: AI 工作摘要
        
    Returns:
        Optional[FeedbackResult]: 用戶回饋結果，如果取消則返回 None
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 設置應用程式屬性
    app.setApplicationName("互動式回饋收集")
    app.setApplicationVersion("1.0")
    
    # 創建並顯示視窗
    window = FeedbackWindow(project_directory, summary)
    window.show()
    
    # 使用事件循環等待視窗關閉
    app.exec()
    
    # 返回結果
    if window.result:
        return window.result
    else:
        return None


if __name__ == "__main__":
    # 測試用的主程式
    result = feedback_ui(".", "測試摘要")
    if result:
        debug_log(f"收到回饋: {result}")
    else:
        debug_log("用戶取消了回饋") 