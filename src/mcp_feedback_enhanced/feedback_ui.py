#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
互動式回饋收集 GUI 介面
=======================

基於 PySide6 的圖形用戶介面，提供直觀的回饋收集功能。
支援文字輸入、圖片上傳、命令執行等功能。

作者: Fábio Ferreira  
靈感來源: dotcursorrules.com
增強功能: 圖片支援和現代化界面設計
"""

import os
import sys
import subprocess
import base64
import uuid
import time
from typing import Optional, TypedDict, List, Dict
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QGridLayout, QFileDialog, QMessageBox,
    QTabWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QDragEnterEvent, QDropEvent, QKeySequence, QShortcut

# ===== 調試日誌函數 =====
def debug_log(message: str) -> None:
    """輸出調試訊息到標準錯誤，避免污染標準輸出"""
    # 只在啟用調試模式時才輸出，避免干擾 MCP 通信
    if not os.getenv("MCP_DEBUG", "").lower() in ("true", "1", "yes", "on"):
        return
        
    try:
        # 確保消息是字符串類型
        if not isinstance(message, str):
            message = str(message)
        
        # 安全地輸出到 stderr，處理編碼問題
        try:
            print(f"[GUI_DEBUG] {message}", file=sys.stderr, flush=True)
        except UnicodeEncodeError:
            # 如果遇到編碼問題，使用 ASCII 安全模式
            safe_message = message.encode('ascii', errors='replace').decode('ascii')
            print(f"[GUI_DEBUG] {safe_message}", file=sys.stderr, flush=True)
    except Exception:
        # 最後的備用方案：靜默失敗，不影響主程序
        pass

# ===== 型別定義 =====
class FeedbackResult(TypedDict):
    """回饋結果的型別定義"""
    command_logs: str
    interactive_feedback: str
    images: List[dict]


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
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        self.delete_button.clicked.connect(self._on_delete_clicked)
        self.delete_button.setToolTip("刪除圖片")
        
    def _on_delete_clicked(self) -> None:
        """處理刪除按鈕點擊事件"""
        reply = QMessageBox.question(
            self, '確認刪除', 
            f'確定要移除圖片 "{os.path.basename(self.image_path)}" 嗎？',
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
        title = QLabel("🖼️ 圖片附件（可選）")
        title.setFont(QFont("", 10, QFont.Bold))
        title.setStyleSheet("color: #007acc; margin: 1px 0;")
        layout.addWidget(title)
        
        # 操作按鈕
        self._create_buttons(layout)
        
        # 拖拽區域
        self._create_drop_zone(layout)
        
        # 狀態標籤 - 移到預覽區域前面
        self.status_label = QLabel("已選擇 0 張圖片")
        self.status_label.setStyleSheet("color: #9e9e9e; font-size: 10px; margin: 5px 0;")
        layout.addWidget(self.status_label)
        
        # 圖片預覽區域
        self._create_preview_area(layout)
    
    def _create_buttons(self, layout: QVBoxLayout) -> None:
        """創建操作按鈕"""
        button_layout = QHBoxLayout()
        
        # 選擇文件按鈕
        self.file_button = QPushButton("📁 選擇文件")
        self.file_button.clicked.connect(self.select_files)
        
        # 剪貼板按鈕
        self.paste_button = QPushButton("📋 剪貼板")
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        
        # 清除按鈕
        self.clear_button = QPushButton("❌ 清除")
        self.clear_button.clicked.connect(self.clear_all_images)
        
        # 設置按鈕樣式
        button_style = """
            QPushButton {
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
        """
        
        self.file_button.setStyleSheet(button_style + "QPushButton { background-color: #0e639c; }")
        self.paste_button.setStyleSheet(button_style + "QPushButton { background-color: #4caf50; }")
        self.clear_button.setStyleSheet(button_style + "QPushButton { background-color: #f44336; }")
        
        button_layout.addWidget(self.file_button)
        button_layout.addWidget(self.paste_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def _create_drop_zone(self, layout: QVBoxLayout) -> None:
        """創建拖拽區域"""
        self.drop_zone = QLabel("🎯 拖拽圖片到這裡 (PNG、JPG、JPEG、GIF、BMP、WebP)")
        self.drop_zone.setFixedHeight(50)
        self.drop_zone.setAlignment(Qt.AlignCenter)
        self.drop_zone.setStyleSheet("""
            QLabel {
                border: 2px dashed #464647;
                border-radius: 6px;
                background-color: #2d2d30;
                color: #9e9e9e;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.drop_zone)
        
    def _create_preview_area(self, layout: QVBoxLayout) -> None:
        """創建圖片預覽區域"""
        self.preview_scroll = QScrollArea()
        self.preview_widget = QWidget()
        self.preview_layout = QGridLayout(self.preview_widget)
        self.preview_layout.setSpacing(4)
        self.preview_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.preview_scroll.setWidget(self.preview_widget)
        self.preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.preview_scroll.setMinimumHeight(100)  # 增加最小高度
        self.preview_scroll.setMaximumHeight(250)  # 增加最大高度
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #464647;
                border-radius: 4px;
                background-color: #1e1e1e;
            }
        """)
        
        layout.addWidget(self.preview_scroll)
        
    def select_files(self) -> None:
        """選擇文件對話框"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "選擇圖片文件",
            "",
            "圖片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;所有文件 (*)"
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
                debug_log(f"圖片添加成功: {os.path.basename(file_path)}, 數據大小: {len(raw_data)} bytes")
                
            except Exception as e:
                debug_log(f"添加圖片失敗: {e}")
                QMessageBox.warning(self, "錯誤", f"無法載入圖片 {os.path.basename(file_path)}:\n{str(e)}")
                
        debug_log(f"共添加 {added_count} 張圖片")
        debug_log(f"當前總共有 {len(self.images)} 張圖片")
        if added_count > 0:
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
        while self.preview_layout.count():
            child = self.preview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # 重新添加圖片預覽
        for i, (image_id, image_info) in enumerate(self.images.items()):
            preview = ImagePreviewWidget(image_info["path"], image_id, self)
            preview.remove_clicked.connect(self._remove_image)
            
            row = i // 5
            col = i % 5
            self.preview_layout.addWidget(preview, row, col)
            
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
            self.status_label.setText("已選擇 0 張圖片")
        else:
            total_size = sum(img["size"] for img in self.images.values())
            
            # 智能單位顯示
            if total_size < 1024:
                size_str = f"{total_size} B"
            elif total_size < 1024 * 1024:
                size_kb = total_size / 1024
                size_str = f"{size_kb:.1f} KB"
            else:
                size_mb = total_size / (1024 * 1024)
                size_str = f"{size_mb:.1f} MB"
            
            self.status_label.setText(f"已選擇 {count} 張圖片 (總計 {size_str})")
            
            # 詳細調試信息
            debug_log(f"=== 圖片狀態更新 ===")
            debug_log(f"圖片數量: {count}")
            debug_log(f"總大小: {total_size} bytes ({size_str})")
            for i, (image_id, img) in enumerate(self.images.items(), 1):
                data_size = len(img["data"]) if isinstance(img["data"], bytes) else 0
                # 智能顯示每張圖片的大小
                if data_size < 1024:
                    data_str = f"{data_size} B"
                elif data_size < 1024 * 1024:
                    data_str = f"{data_size/1024:.1f} KB"
                else:
                    data_str = f"{data_size/(1024*1024):.1f} MB"
                debug_log(f"圖片 {i}: {img['name']} - 數據大小: {data_str}")
            debug_log(f"==================")
            
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
                    self.drop_zone.setStyleSheet("""
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
        self.drop_zone.setStyleSheet("""
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


# ===== 主要回饋介面 =====
class FeedbackWindow(QMainWindow):
    """主要的回饋收集視窗"""
    
    def __init__(self, project_dir: str, summary: str):
        super().__init__()
        self.project_dir = project_dir
        self.summary = summary
        self.result: Optional[FeedbackResult] = None
        self.process: Optional[subprocess.Popen] = None
        self.accepted = False
        
        self._setup_ui()
        self._apply_dark_style()
    
    def _setup_ui(self) -> None:
        """設置用戶介面"""
        self.setWindowTitle("互動式回饋收集")
        self.setMinimumSize(800, 600)
        
        # 主要元件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主要佈局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # AI 工作摘要（適度參與拉伸）
        self._create_summary_section(main_layout)
        
        # 分頁標籤（主要工作區域）
        self._create_tabs(main_layout)
        
        # 操作按鈕（固定大小）
        self._create_action_buttons(main_layout)
        
        # 設置比例拉伸：摘要區域佔1份，分頁區域佔3份，按鈕不拉伸
        summary_widget = main_layout.itemAt(0).widget()  # 摘要區域
        main_layout.setStretchFactor(summary_widget, 1)   # 適度拉伸
        main_layout.setStretchFactor(self.tabs, 3)        # 主要拉伸區域
    
    def _create_summary_section(self, layout: QVBoxLayout) -> None:
        """創建 AI 工作摘要區域"""
        summary_group = QGroupBox("📋 AI 工作摘要")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setPlainText(self.summary)
        # 設置合理的高度範圍，允許適度拉伸
        self.summary_text.setMinimumHeight(80)
        self.summary_text.setMaximumHeight(250)  # 增加最大高度，允許更多拉伸
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("background-color: #2d2d30; border: 1px solid #464647;")
        
        # 設置大小策略：允許適度垂直擴展
        self.summary_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 設置群組框的大小策略：允許適度擴展
        summary_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        summary_layout.addWidget(self.summary_text)
        layout.addWidget(summary_group)
    
    def _create_tabs(self, layout: QVBoxLayout) -> None:
        """創建分頁標籤"""
        self.tabs = QTabWidget()
        
        # 設置分頁標籤的大小策略，確保能夠獲得主要空間
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 回饋分頁
        self._create_feedback_tab()
        
        # 命令分頁
        self._create_command_tab()
        
        layout.addWidget(self.tabs)
    
    def _create_feedback_tab(self) -> None:
        """創建回饋分頁"""
        feedback_widget = QWidget()
        feedback_layout = QVBoxLayout(feedback_widget)
        
        # 文字回饋區域
        feedback_group = QGroupBox("💬 您的回饋")
        feedback_group_layout = QVBoxLayout(feedback_group)
        
        self.feedback_text = QTextEdit()
        self.feedback_text.setPlaceholderText("請在這裡輸入您的回饋、建議或問題...\n\n💡 小提示：按 Ctrl+Enter 可快速提交回饋")
        self.feedback_text.setMinimumHeight(150)
        # 確保文字輸入區域能夠擴展
        self.feedback_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 添加快捷鍵支援
        submit_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self.feedback_text)
        submit_shortcut.activated.connect(self._submit_feedback)
        
        feedback_group_layout.addWidget(self.feedback_text)
        feedback_layout.addWidget(feedback_group)
        
        # 圖片上傳區域（允許適度拉伸）
        self.image_upload = ImageUploadWidget()
        self.image_upload.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_upload.setMinimumHeight(200)   # 設置最小高度
        self.image_upload.setMaximumHeight(400)   # 增加最大高度限制
        feedback_layout.addWidget(self.image_upload)
        
        # 設置比例拉伸：文字區域佔2份，圖片區域佔1份
        feedback_layout.setStretchFactor(feedback_group, 2)
        feedback_layout.setStretchFactor(self.image_upload, 1)
        
        self.tabs.addTab(feedback_widget, "💬 回饋")
    
    def _create_command_tab(self) -> None:
        """創建命令分頁"""
        command_widget = QWidget()
        command_layout = QVBoxLayout(command_widget)
        
        # 命令輸入區域
        command_group = QGroupBox("⚡ 命令執行")
        command_group_layout = QVBoxLayout(command_group)
        
        # 命令輸入
        cmd_input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("輸入要執行的命令...")
        self.command_input.returnPressed.connect(self._run_command)
        
        self.run_button = QPushButton("▶️ 執行")
        self.run_button.clicked.connect(self._run_command)
        
        cmd_input_layout.addWidget(self.command_input)
        cmd_input_layout.addWidget(self.run_button)
        command_group_layout.addLayout(cmd_input_layout)
        
        # 命令輸出
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        self.command_output.setMinimumHeight(200)
        self.command_output.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-family: 'Consolas', 'Monaco', 'Courier New', monospace;")
        # 確保命令輸出區域能夠擴展
        self.command_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        command_group_layout.addWidget(self.command_output)
        
        # 設置群組框的大小策略
        command_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        command_layout.addWidget(command_group)
        
        self.tabs.addTab(command_widget, "⚡ 命令")
    
    def _create_action_buttons(self, layout: QVBoxLayout) -> None:
        """創建操作按鈕"""
        button_layout = QHBoxLayout()
        
        self.submit_button = QPushButton("✅ 提交回饋")
        self.submit_button.clicked.connect(self._submit_feedback)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        self.cancel_button = QPushButton("❌ 取消")
        self.cancel_button.clicked.connect(self._cancel_feedback)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
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

    def _run_command(self) -> None:
        """執行命令"""
        command = self.command_input.text().strip()
        if not command:
            return

        self.command_output.append(f"$ {command}")
        
        try:
            # 在專案目錄中執行命令
            self.process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 使用計時器讀取輸出
            self.timer = QTimer()
            self.timer.timeout.connect(self._read_command_output)
            self.timer.start(100)
            
        except Exception as e:
            self.command_output.append(f"錯誤: {str(e)}")
    
    def _read_command_output(self) -> None:
        """讀取命令輸出"""
        if self.process and self.process.poll() is None:
            try:
                output = self.process.stdout.readline()
                if output:
                    self.command_output.insertPlainText(output)
                    # 自動滾動到底部
                    cursor = self.command_output.textCursor()
                    cursor.movePosition(cursor.End)
                    self.command_output.setTextCursor(cursor)
            except:
                pass
        else:
            # 進程結束
            if hasattr(self, 'timer'):
                self.timer.stop()
            if self.process:
                return_code = self.process.returncode
                self.command_output.append(f"\n進程結束，返回碼: {return_code}\n")
    
    def _submit_feedback(self) -> None:
        """提交回饋"""
        self.result = {
            "interactive_feedback": self.feedback_text.toPlainText(),
            "command_logs": self.command_output.toPlainText(),
            "images": self.image_upload.get_images_data()
        }
        self.accepted = True
        self.close()
    
    def _cancel_feedback(self) -> None:
        """取消回饋"""
        self.accepted = False
        self.close()

    def closeEvent(self, event) -> None:
        """處理視窗關閉事件"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        if self.process:
            try:
                self.process.terminate()
            except:
                pass
        
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
    if window.accepted:
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