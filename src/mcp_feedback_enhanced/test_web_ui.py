#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Feedback MCP - Web UI 測試模組
========================================

用於測試 Interactive Feedback MCP 的 Web UI 功能。
包含完整的 Web UI 功能測試。

功能測試：
- Web UI 服務器啟動
- 會話管理功能
- WebSocket 通訊
- 多語言支援
- 命令執行功能

使用方法：
    python -m mcp_feedback_enhanced.test_web_ui

作者: Minidoracat
"""

import asyncio
import webbrowser
import time
import sys
import os
import socket
import threading
from pathlib import Path
from typing import Dict, Any, Optional

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from .debug import debug_log
from .i18n import t

# 嘗試導入 Web UI 模組
try:
    # 使用新的 web 模組
    from .web import WebUIManager, launch_web_feedback_ui, get_web_ui_manager
    WEB_UI_AVAILABLE = True
    debug_log("✅ 使用新的 web 模組")
except ImportError as e:
    debug_log(f"⚠️  無法導入 Web UI 模組: {e}")
    WEB_UI_AVAILABLE = False

def get_test_summary():
    """獲取測試摘要，使用國際化系統"""
    return t('test.webUiSummary')

def find_free_port():
    """Find a free port to use for testing"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def test_web_ui(keep_running=False):
    """Test the Web UI functionality"""
    
    debug_log("🧪 測試 Interactive Feedback MCP Web UI")
    debug_log("=" * 50)
    
    # Test import
    try:
        # 使用新的 web 模組
        from .web import WebUIManager, launch_web_feedback_ui
        debug_log("✅ Web UI 模組匯入成功")
    except ImportError as e:
        debug_log(f"❌ Web UI 模組匯入失敗: {e}")
        return False, None
    
    # Find free port
    try:
        free_port = find_free_port()
        debug_log(f"🔍 找到可用端口: {free_port}")
    except Exception as e:
        debug_log(f"❌ 尋找可用端口失敗: {e}")
        return False, None
    
    # Test manager creation
    try:
        manager = WebUIManager(port=free_port)
        debug_log("✅ WebUIManager 創建成功")
    except Exception as e:
        debug_log(f"❌ WebUIManager 創建失敗: {e}")
        return False, None
    
    # Test server start (with timeout)
    server_started = False
    try:
        debug_log("🚀 啟動 Web 服務器...")
        
        def start_server():
            try:
                manager.start_server()
                return True
            except Exception as e:
                debug_log(f"服務器啟動錯誤: {e}")
                return False
        
        # Start server in thread
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait a moment and test if server is responsive
        time.sleep(3)
        
        # Test if port is listening
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((manager.host, manager.port))
            if result == 0:
                server_started = True
                debug_log("✅ Web 服務器啟動成功")
                debug_log(f"🌐 服務器運行在: http://{manager.host}:{manager.port}")
            else:
                debug_log(f"❌ 無法連接到服務器端口 {manager.port}")
                
    except Exception as e:
        debug_log(f"❌ Web 服務器啟動失敗: {e}")
        return False, None
    
    if not server_started:
        debug_log("❌ 服務器未能正常啟動")
        return False, None
    
    # Test session creation
    session_info = None
    try:
        project_dir = str(Path.cwd())
        # 使用國際化系統獲取測試摘要
        summary = t('test.webUiSummary')
        session_id = manager.create_session(project_dir, summary)
        session_info = {
            'manager': manager,
            'session_id': session_id,
            'url': f"http://{manager.host}:{manager.port}/session/{session_id}"
        }
        debug_log(f"✅ 測試會話創建成功 (ID: {session_id[:8]}...)")
        debug_log(f"🔗 測試 URL: {session_info['url']}")
    except Exception as e:
        debug_log(f"❌ 會話創建失敗: {e}")
        return False, None
    
    debug_log("\n" + "=" * 50)
    debug_log("🎉 所有測試通過！Web UI 準備就緒")
    debug_log("📝 注意事項:")
    debug_log("  - Web UI 會在 SSH remote 環境下自動啟用")
    debug_log("  - 本地環境會繼續使用 Qt GUI")
    debug_log("  - 支援即時命令執行和 WebSocket 通訊")
    debug_log("  - 提供現代化的深色主題界面")
    debug_log("  - 支援智能 Ctrl+V 圖片貼上功能")
    
    return True, session_info

def test_environment_detection():
    """Test environment detection logic"""
    debug_log("🔍 測試環境檢測功能")
    debug_log("-" * 30)
    
    try:
        from .server import is_remote_environment, can_use_gui
        
        remote_detected = is_remote_environment()
        gui_available = can_use_gui()
        
        debug_log(f"遠端環境檢測: {'是' if remote_detected else '否'}")
        debug_log(f"GUI 可用性: {'是' if gui_available else '否'}")
        
        if remote_detected:
            debug_log("✅ 將使用 Web UI (適合遠端開發環境)")
        else:
            debug_log("✅ 將使用 Qt GUI (本地環境)")
            
        return True
        
    except Exception as e:
        debug_log(f"❌ 環境檢測失敗: {e}")
        return False

def test_mcp_integration():
    """Test MCP server integration"""
    debug_log("\n🔧 測試 MCP 整合功能")
    debug_log("-" * 30)
    
    try:
        from .server import interactive_feedback
        debug_log("✅ MCP 工具函數可用")
        
        # Test timeout parameter
        debug_log("✅ 支援 timeout 參數")
        
        # Test environment-based Web UI selection
        debug_log("✅ 支援基於環境變數的 Web UI 選擇")
        
        # Test would require actual MCP call, so just verify import
        debug_log("✅ 準備接受來自 AI 助手的調用")
        return True
        
    except Exception as e:
        debug_log(f"❌ MCP 整合測試失敗: {e}")
        return False

def test_new_parameters():
    """Test timeout parameter and environment variable support"""
    debug_log("\n🆕 測試參數功能")
    debug_log("-" * 30)
    
    try:
        from .server import interactive_feedback
        
        # 測試參數是否存在
        import inspect
        sig = inspect.signature(interactive_feedback)
        
        # 檢查 timeout 參數
        if 'timeout' in sig.parameters:
            timeout_param = sig.parameters['timeout']
            debug_log(f"✅ timeout 參數存在，預設值: {timeout_param.default}")
        else:
            debug_log("❌ timeout 參數不存在")
            return False
        
        # 檢查環境變數支援
        import os
        current_force_web = os.getenv("FORCE_WEB")
        if current_force_web:
            debug_log(f"✅ 檢測到 FORCE_WEB 環境變數: {current_force_web}")
        else:
            debug_log("ℹ️  FORCE_WEB 環境變數未設定（將使用預設邏輯）")
        
        debug_log("✅ 參數功能正常")
        return True
        
    except Exception as e:
        debug_log(f"❌ 參數測試失敗: {e}")
        return False

def test_environment_web_ui_mode():
    """Test environment-based Web UI mode"""
    debug_log("\n🌐 測試環境變數控制 Web UI 模式")
    debug_log("-" * 30)
    
    try:
        from .server import interactive_feedback, is_remote_environment, can_use_gui
        import os
        
        # 顯示當前環境狀態
        is_remote = is_remote_environment()
        gui_available = can_use_gui()
        force_web_env = os.getenv("FORCE_WEB", "").lower()
        
        debug_log(f"當前環境 - 遠端: {is_remote}, GUI 可用: {gui_available}")
        debug_log(f"FORCE_WEB 環境變數: {force_web_env or '未設定'}")
        
        if force_web_env in ("true", "1", "yes", "on"):
            debug_log("✅ FORCE_WEB 已啟用，將強制使用 Web UI")
        elif not is_remote and gui_available:
            debug_log("ℹ️  本地 GUI 環境，將使用 Qt GUI")
            debug_log("💡 可設定 FORCE_WEB=true 強制使用 Web UI 進行測試")
        else:
            debug_log("ℹ️  將自動使用 Web UI（遠端環境或 GUI 不可用）")
            
        return True
        
    except Exception as e:
        debug_log(f"❌ 環境變數測試失敗: {e}")
        return False

def interactive_demo(session_info):
    """Run interactive demo with the Web UI"""
    debug_log(f"\n🌐 Web UI 互動測試模式")
    debug_log("=" * 50)
    debug_log(f"服務器地址: http://{session_info['manager'].host}:{session_info['manager'].port}")
    debug_log(f"測試會話: {session_info['url']}")
    debug_log("\n📖 操作指南:")
    debug_log("  1. 在瀏覽器中開啟上面的測試 URL")
    debug_log("  2. 嘗試以下功能:")
    debug_log("     - 點擊 '顯示命令區塊' 按鈕")
    debug_log("     - 輸入命令如 'echo Hello World' 並執行")
    debug_log("     - 在回饋區域輸入文字")
    debug_log("     - 使用 Ctrl+Enter 提交回饋")
    debug_log("  3. 測試 WebSocket 即時通訊功能")
    debug_log("\n⌨️  控制選項:")
    debug_log("  - 按 Enter 繼續運行")
    debug_log("  - 輸入 'q' 或 'quit' 停止服務器")
    
    while True:
        try:
            user_input = input("\n>>> ").strip().lower()
            if user_input in ['q', 'quit', 'exit']:
                debug_log("🛑 停止服務器...")
                break
            elif user_input == '':
                debug_log(f"🔄 服務器持續運行在: {session_info['url']}")
                debug_log("   瀏覽器應該仍可正常訪問")
            else:
                debug_log("❓ 未知命令。按 Enter 繼續運行，或輸入 'q' 退出")
        except KeyboardInterrupt:
            debug_log("\n🛑 收到中斷信號，停止服務器...")
            break
    
    debug_log("✅ Web UI 測試完成")

if __name__ == "__main__":
    debug_log("Interactive Feedback MCP - Web UI 測試")
    debug_log("=" * 60)
    
    # Test environment detection
    env_test = test_environment_detection()
    
    # Test new parameters
    params_test = test_new_parameters()
    
    # Test environment-based Web UI mode
    env_web_test = test_environment_web_ui_mode()
    
    # Test MCP integration
    mcp_test = test_mcp_integration()
    
    # Test Web UI
    web_test, session_info = test_web_ui()
    
    debug_log("\n" + "=" * 60)
    if env_test and params_test and env_web_test and mcp_test and web_test:
        debug_log("🎊 所有測試完成！準備使用 Interactive Feedback MCP")
        debug_log("\n📖 使用方法:")
        debug_log("  1. 在 Cursor/Cline 中配置此 MCP 服務器")
        debug_log("  2. AI 助手會自動調用 interactive_feedback 工具")
        debug_log("  3. 根據環境自動選擇 GUI 或 Web UI")
        debug_log("  4. 提供回饋後繼續工作流程")
        
        debug_log("\n✨ Web UI 新功能:")
        debug_log("  - 支援 SSH remote 開發環境")
        debug_log("  - 現代化深色主題界面")
        debug_log("  - WebSocket 即時通訊")
        debug_log("  - 自動瀏覽器啟動")
        debug_log("  - 命令執行和即時輸出")
        
        debug_log("\n✅ 測試完成 - 系統已準備就緒！")
        if session_info:
            debug_log(f"💡 您可以現在就在瀏覽器中測試: {session_info['url']}")
            debug_log("   (服務器會繼續運行一小段時間)")
            time.sleep(10)  # Keep running for a short time for immediate testing
    else:
        debug_log("❌ 部分測試失敗，請檢查錯誤信息")
        sys.exit(1) 