#!/usr/bin/env python3
# Test script for Qt GUI functionality
import os
import sys
from pathlib import Path

# 添加項目路徑到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

def test_qt_gui():
    """測試 Qt GUI 功能"""
    try:
        from .feedback_ui import feedback_ui
        
        # 測試參數
        project_directory = os.getcwd()
        prompt = """🎯 圖片預覽和視窗調整測試

這是一個測試會話，用於驗證以下功能：

✅ 功能測試項目：
1. 圖片上傳和預覽功能
2. 圖片右上角X刪除按鈕
3. 視窗自由調整大小
4. 分割器的靈活調整
5. 各區域的動態佈局

📋 測試步驟：
1. 嘗試上傳一些圖片（拖拽、文件選擇、剪貼板）
2. 檢查圖片預覽是否正常顯示
3. 點擊圖片右上角的X按鈕刪除圖片
4. 嘗試調整視窗大小，檢查是否可以自由調整
5. 拖動分割器調整各區域大小
6. 提供任何回饋或發現的問題

請測試這些功能並提供回饋！"""
        
        print("🚀 啟動 Qt GUI 測試...")
        print("📝 測試項目:")
        print("   - 圖片預覽功能")
        print("   - X刪除按鈕")
        print("   - 視窗大小調整")
        print("   - 分割器調整")
        print()
        
        # 啟動 GUI
        result = feedback_ui(project_directory, prompt)
        
        if result:
            print("\n✅ 測試完成！")
            print(f"📄 收到回饋: {result.get('interactive_feedback', '無')}")
            if result.get('images'):
                print(f"🖼️  收到圖片: {len(result['images'])} 張")
            if result.get('logs'):
                print(f"📋 命令日誌: {len(result['logs'])} 行")
        else:
            print("\n❌ 測試取消或無回饋")
            
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        print("請確保已安裝 PySide6: pip install PySide6")
        return False
    except Exception as e:
        print(f"❌ 測試錯誤: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Interactive Feedback MCP - Qt GUI 測試")
    print("=" * 50)
    
    # 檢查環境
    try:
        from PySide6.QtWidgets import QApplication
        print("✅ PySide6 已安裝")
    except ImportError:
        print("❌ PySide6 未安裝，請執行: pip install PySide6")
        sys.exit(1)
    
    # 運行測試
    success = test_qt_gui()
    
    if success:
        print("\n🎉 測試程序運行完成")
    else:
        print("\n💥 測試程序運行失敗")
        sys.exit(1) 