#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圖片上傳元件
============

支援文件選擇、剪貼板貼上、拖拽上傳等多種方式的圖片上傳元件。
"""

import os
import uuid
import time
from typing import Dict, List
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QGridLayout, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QSizePolicy

# 導入多語系支援
from ...i18n import t
from ...debug import gui_debug_log as debug_log
from .image_preview import ImagePreviewWidget


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
        layout.setContentsMargins(0, 8, 0, 8)  # 調整邊距使其與其他區域一致
        
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
        self.preview_widget.setMinimumHeight(140)  # 設置預覽部件的最小高度
        # 設置尺寸策略，允許垂直擴展
        self.preview_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.preview_layout = QVBoxLayout(self.preview_widget)
        self.preview_layout.setSpacing(6)
        self.preview_layout.setContentsMargins(8, 8, 8, 8)
        
        # 創建操作按鈕區域
        self._create_buttons_in_area()
        
        # 創建拖拽提示標籤（初始顯示）
        self.drop_hint_label = QLabel(t('images.dragHint'))
        self.drop_hint_label.setAlignment(Qt.AlignCenter)
        self.drop_hint_label.setMinimumHeight(80)  # 增加最小高度
        self.drop_hint_label.setMaximumHeight(120) # 設置最大高度
        self.drop_hint_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #464647;
                border-radius: 6px;
                background-color: #2d2d30;
                color: #9e9e9e;
                font-size: 11px;
                margin: 4px 0;
                padding: 16px 8px;
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
        self.preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 改回按需顯示滾動條
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.preview_scroll.setMinimumHeight(160)  # 增加最小高度，確保有足夠空間
        self.preview_scroll.setMaximumHeight(300)  # 增加最大高度
        self.preview_scroll.setWidgetResizable(True)
        
        # 增強的滾動區域樣式，改善 macOS 兼容性
        self.preview_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #464647;
                border-radius: 4px;
                background-color: #1e1e1e;
            }
            QScrollArea QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 14px;
                border-radius: 7px;
                margin: 0;
            }
            QScrollArea QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 7px;
                min-height: 30px;
                margin: 2px;
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
                height: 14px;
                border-radius: 7px;
                margin: 0;
            }
            QScrollArea QScrollBar::handle:horizontal {
                background-color: #555;
                border-radius: 7px;
                min-width: 30px;
                margin: 2px;
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
        mimeData = clipboard.mimeData()
        
        if mimeData.hasImage():
            image = clipboard.image()
            if not image.isNull():
                # 創建一個唯一的臨時文件名
                temp_dir = Path.home() / ".cache" / "mcp-feedback-enhanced"
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = int(time.time() * 1000)
                temp_file = temp_dir / f"clipboard_{timestamp}_{uuid.uuid4().hex[:8]}.png"
                
                # 保存剪貼板圖片
                if image.save(str(temp_file), "PNG"):
                    if os.path.getsize(temp_file) > 0:
                        self._add_images([str(temp_file)])
                        debug_log(f"從剪貼板成功粘貼圖片: {temp_file}")
                    else:
                        QMessageBox.warning(self, t('errors.warning'), t('errors.imageSaveEmpty', path=str(temp_file)))
                else:
                    QMessageBox.warning(self, t('errors.warning'), t('errors.imageSaveFailed'))
            else:
                QMessageBox.warning(self, t('errors.warning'), t('errors.clipboardSaveFailed'))
        elif mimeData.hasText():
            # 檢查是否為圖片數據
            text = mimeData.text()
            if text.startswith('data:image/') or any(ext in text.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                QMessageBox.information(self, t('errors.info'), t('errors.noValidImage'))
        else:
            QMessageBox.information(self, t('errors.info'), t('errors.noImageContent'))
            
    def clear_all_images(self) -> None:
        """清除所有圖片"""
        if self.images:
            reply = QMessageBox.question(
                self, t('errors.confirmClearTitle'), 
                t('errors.confirmClearAll', count=len(self.images)),
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
                        self, t('errors.warning'), 
                        t('errors.fileSizeExceeded', filename=os.path.basename(file_path), size=f"{file_size/1024/1024:.1f}")
                    )
                    continue
                
                if file_size == 0:
                    QMessageBox.warning(self, t('errors.warning'), t('errors.emptyFile', filename=os.path.basename(file_path)))
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
                            self, t('errors.warning'), 
                            t('errors.dataSizeExceeded', filename=os.path.basename(file_path))
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
                QMessageBox.warning(self, t('errors.title'), t('errors.loadImageFailed', filename=os.path.basename(file_path), error=str(e)))
                
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
        
        # 強制更新佈局和滾動區域
        self.preview_widget.updateGeometry()
        self.preview_scroll.updateGeometry()
        
        # 確保滾動區域能正確計算內容大小
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
    
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
        """獲取所有圖片的數據列表"""
        images_data = []
        for image_info in self.images.values():
            images_data.append(image_info)
        return images_data
    
    def add_image_data(self, image_data: dict) -> None:
        """添加圖片數據（用於恢復界面時的圖片）"""
        try:
            # 檢查必要的字段
            if not all(key in image_data for key in ['filename', 'data', 'size']):
                debug_log("圖片數據格式不正確，缺少必要字段")
                return
            
            # 生成新的圖片ID
            image_id = str(uuid.uuid4())
            
            # 復制圖片數據
            self.images[image_id] = image_data.copy()
            
            # 刷新預覽
            self._refresh_preview()
            self._update_status()
            self.images_changed.emit()
            
            debug_log(f"成功恢復圖片: {image_data['filename']}")
            
        except Exception as e:
            debug_log(f"添加圖片數據失敗: {e}")
    
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
            QMessageBox.warning(self, t('errors.warning'), t('errors.dragInvalidFiles'))
    
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