"""
互動式回饋收集 GUI 模組
=======================

基於 PySide6 的圖形用戶介面模組，提供直觀的回饋收集功能。
支援文字輸入、圖片上傳、命令執行等功能。

模組結構：
- main.py: 主要介面入口點
- window/: 窗口類別
- widgets/: 自定義元件
- styles/: 樣式定義
- utils/: 工具函數
- models/: 資料模型

作者: Fábio Ferreira  
靈感來源: dotcursorrules.com
增強功能: 圖片支援和現代化界面設計
多語系支援: Minidoracat
重構: 模塊化設計
"""

from .main import feedback_ui

__all__ = ['feedback_ui'] 