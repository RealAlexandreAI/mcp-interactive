#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qt GUI 測試模組
===============

用於測試 Interactive Feedback MCP 的 Qt GUI 功能。
包含完整的 GUI 功能測試。

功能測試：
- Qt GUI 界面啟動
- 多語言支援
- 圖片上傳功能
- 回饋提交功能
- 快捷鍵功能

使用方法：
    python -m mcp_feedback_enhanced.test_qt_gui

作者: Minidoracat
"""

import sys
import os
from typing import Optional, Dict, Any

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from .debug import debug_log
from .i18n import t

# 嘗試導入 Qt GUI 模組
try:
    from .gui import feedback_ui
    QT_GUI_AVAILABLE = True
except ImportError as e:
    debug_log(f"⚠️  無法導入 Qt GUI 模組: {e}")
    QT_GUI_AVAILABLE = False

def test_qt_gui():
    """測試 Qt GUI 功能"""
    try:
        # 測試參數
        project_directory = os.getcwd()
        # 使用國際化系統獲取測試摘要
        prompt = t('test.qtGuiSummary')
        
        debug_log("🚀 啟動 Qt GUI 測試...")
        debug_log("📝 測試項目:")
        debug_log("   - 圖片預覽功能")
        debug_log("   - X刪除按鈕")
        debug_log("   - 視窗大小調整")
        debug_log("   - 分割器調整")
        debug_log("   - 智能 Ctrl+V 功能")
        debug_log("")
        
        # 啟動 GUI
        result = feedback_ui(project_directory, prompt)
        
        if result:
            debug_log("\n✅ 測試完成！")
            debug_log(f"📄 收到回饋: {result.get('interactive_feedback', '無')}")
            if result.get('images'):
                debug_log(f"🖼️  收到圖片: {len(result['images'])} 張")
            if result.get('logs'):
                debug_log(f"📋 命令日誌: {len(result['logs'])} 行")
        else:
            debug_log("\n❌ 測試取消或無回饋")
            
    except ImportError as e:
        debug_log(f"❌ 導入錯誤: {e}")
        debug_log("請確保已安裝 PySide6: pip install PySide6")
        return False
    except Exception as e:
        debug_log(f"❌ 測試錯誤: {e}")
        return False
    
    return True

if __name__ == "__main__":
    debug_log("🧪 Interactive Feedback MCP - Qt GUI 測試")
    debug_log("=" * 50)
    
    # 檢查環境
    try:
        from PySide6.QtWidgets import QApplication
        debug_log("✅ PySide6 已安裝")
    except ImportError:
        debug_log("❌ PySide6 未安裝，請執行: pip install PySide6")
        sys.exit(1)
    
    # 運行測試
    success = test_qt_gui()
    
    if success:
        debug_log("\n🎉 測試程序運行完成")
    else:
        debug_log("\n💥 測試程序運行失敗")
        sys.exit(1) 