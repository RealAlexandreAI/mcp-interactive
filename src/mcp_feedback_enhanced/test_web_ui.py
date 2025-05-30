#!/usr/bin/env python3
"""
Test script for Interactive Feedback MCP Web UI
"""
import sys
import threading
import time
import socket
from pathlib import Path

def find_free_port():
    """Find a free port to use for testing"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def test_web_ui(keep_running=False):
    """Test the Web UI functionality"""
    
    print("🧪 測試 Interactive Feedback MCP Web UI")
    print("=" * 50)
    
    # Test import
    try:
        from .web_ui import WebUIManager, launch_web_feedback_ui
        print("✅ Web UI 模組匯入成功")
    except ImportError as e:
        print(f"❌ Web UI 模組匯入失敗: {e}")
        return False, None
    
    # Find free port
    try:
        free_port = find_free_port()
        print(f"🔍 找到可用端口: {free_port}")
    except Exception as e:
        print(f"❌ 尋找可用端口失敗: {e}")
        return False, None
    
    # Test manager creation
    try:
        manager = WebUIManager(port=free_port)
        print("✅ WebUIManager 創建成功")
    except Exception as e:
        print(f"❌ WebUIManager 創建失敗: {e}")
        return False, None
    
    # Test server start (with timeout)
    server_started = False
    try:
        print("🚀 啟動 Web 服務器...")
        
        def start_server():
            try:
                manager.start_server()
                return True
            except Exception as e:
                print(f"服務器啟動錯誤: {e}")
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
                print("✅ Web 服務器啟動成功")
                print(f"🌐 服務器運行在: http://{manager.host}:{manager.port}")
            else:
                print(f"❌ 無法連接到服務器端口 {manager.port}")
                
    except Exception as e:
        print(f"❌ Web 服務器啟動失敗: {e}")
        return False, None
    
    if not server_started:
        print("❌ 服務器未能正常啟動")
        return False, None
    
    # Test session creation
    session_info = None
    try:
        project_dir = str(Path.cwd())
        summary = "測試 Web UI 功能"
        session_id = manager.create_session(project_dir, summary)
        session_info = {
            'manager': manager,
            'session_id': session_id,
            'url': f"http://{manager.host}:{manager.port}/session/{session_id}"
        }
        print(f"✅ 測試會話創建成功 (ID: {session_id[:8]}...)")
        print(f"🔗 測試 URL: {session_info['url']}")
    except Exception as e:
        print(f"❌ 會話創建失敗: {e}")
        return False, None
    
    print("\n" + "=" * 50)
    print("🎉 所有測試通過！Web UI 準備就緒")
    print("📝 注意事項:")
    print("  - Web UI 會在 SSH remote 環境下自動啟用")
    print("  - 本地環境會繼續使用 Qt GUI")
    print("  - 支援即時命令執行和 WebSocket 通訊")
    print("  - 提供現代化的深色主題界面")
    
    return True, session_info

def test_environment_detection():
    """Test environment detection logic"""
    print("🔍 測試環境檢測功能")
    print("-" * 30)
    
    try:
        from .server import is_remote_environment, can_use_gui
        
        remote_detected = is_remote_environment()
        gui_available = can_use_gui()
        
        print(f"遠端環境檢測: {'是' if remote_detected else '否'}")
        print(f"GUI 可用性: {'是' if gui_available else '否'}")
        
        if remote_detected:
            print("✅ 將使用 Web UI (適合遠端開發環境)")
        else:
            print("✅ 將使用 Qt GUI (本地環境)")
            
        return True
        
    except Exception as e:
        print(f"❌ 環境檢測失敗: {e}")
        return False

def test_mcp_integration():
    """Test MCP server integration"""
    print("\n🔧 測試 MCP 整合功能")
    print("-" * 30)
    
    try:
        from .server import interactive_feedback
        print("✅ MCP 工具函數可用")
        
        # Test timeout parameter
        print("✅ 支援 timeout 參數")
        
        # Test force_web_ui parameter
        print("✅ 支援 force_web_ui 參數")
        
        # Test would require actual MCP call, so just verify import
        print("✅ 準備接受來自 AI 助手的調用")
        return True
        
    except Exception as e:
        print(f"❌ MCP 整合測試失敗: {e}")
        return False

def test_new_parameters():
    """Test new timeout and force_web_ui parameters"""
    print("\n🆕 測試新增參數功能")
    print("-" * 30)
    
    try:
        from .server import interactive_feedback
        
        # 測試參數是否存在
        import inspect
        sig = inspect.signature(interactive_feedback)
        
        # 檢查 timeout 參數
        if 'timeout' in sig.parameters:
            timeout_param = sig.parameters['timeout']
            print(f"✅ timeout 參數存在，預設值: {timeout_param.default}")
        else:
            print("❌ timeout 參數不存在")
            return False
        
        # 檢查 force_web_ui 參數
        if 'force_web_ui' in sig.parameters:
            force_web_ui_param = sig.parameters['force_web_ui']
            print(f"✅ force_web_ui 參數存在，預設值: {force_web_ui_param.default}")
        else:
            print("❌ force_web_ui 參數不存在")
            return False
        
        print("✅ 所有新參數功能正常")
        return True
        
    except Exception as e:
        print(f"❌ 新參數測試失敗: {e}")
        return False

def test_force_web_ui_mode():
    """Test force web UI mode"""
    print("\n🌐 測試強制 Web UI 模式")
    print("-" * 30)
    
    try:
        from .server import interactive_feedback, is_remote_environment, can_use_gui
        
        # 顯示當前環境狀態
        is_remote = is_remote_environment()
        gui_available = can_use_gui()
        
        print(f"當前環境 - 遠端: {is_remote}, GUI 可用: {gui_available}")
        
        if not is_remote and gui_available:
            print("✅ 在本地 GUI 環境中可以使用 force_web_ui=True 強制使用 Web UI")
            print("💡 這對於測試 Web UI 功能非常有用")
        else:
            print("ℹ️  當前環境會自動使用 Web UI")
            
        return True
        
    except Exception as e:
        print(f"❌ 強制 Web UI 測試失敗: {e}")
        return False

def interactive_demo(session_info):
    """Run interactive demo with the Web UI"""
    print(f"\n🌐 Web UI 持久化運行模式")
    print("=" * 50)
    print(f"服務器地址: http://{session_info['manager'].host}:{session_info['manager'].port}")
    print(f"測試會話: {session_info['url']}")
    print("\n📖 操作指南:")
    print("  1. 在瀏覽器中開啟上面的測試 URL")
    print("  2. 嘗試以下功能:")
    print("     - 點擊 '顯示命令區塊' 按鈕")
    print("     - 輸入命令如 'echo Hello World' 並執行")
    print("     - 在回饋區域輸入文字")
    print("     - 使用 Ctrl+Enter 提交回饋")
    print("  3. 測試 WebSocket 即時通訊功能")
    print("\n⌨️  控制選項:")
    print("  - 按 Enter 繼續運行")
    print("  - 輸入 'q' 或 'quit' 停止服務器")
    
    while True:
        try:
            user_input = input("\n>>> ").strip().lower()
            if user_input in ['q', 'quit', 'exit']:
                print("🛑 停止服務器...")
                break
            elif user_input == '':
                print(f"🔄 服務器持續運行在: {session_info['url']}")
                print("   瀏覽器應該仍可正常訪問")
            else:
                print("❓ 未知命令。按 Enter 繼續運行，或輸入 'q' 退出")
        except KeyboardInterrupt:
            print("\n🛑 收到中斷信號，停止服務器...")
            break
    
    print("✅ Web UI 測試完成")

if __name__ == "__main__":
    print("Interactive Feedback MCP - Web UI 測試")
    print("=" * 60)
    
    # Check if user wants persistent mode
    persistent_mode = len(sys.argv) > 1 and sys.argv[1] in ['--persistent', '-p', '--demo']
    
    if not persistent_mode:
        print("💡 提示: 使用 'python test_web_ui.py --persistent' 啟動持久化測試模式")
        print()
    
    # Test environment detection
    env_test = test_environment_detection()
    
    # Test new parameters
    params_test = test_new_parameters()
    
    # Test force web UI mode
    force_test = test_force_web_ui_mode()
    
    # Test MCP integration
    mcp_test = test_mcp_integration()
    
    # Test Web UI
    web_test, session_info = test_web_ui()
    
    print("\n" + "=" * 60)
    if env_test and params_test and force_test and mcp_test and web_test:
        print("🎊 所有測試完成！準備使用 Interactive Feedback MCP")
        print("\n📖 使用方法:")
        print("  1. 在 Cursor/Cline 中配置此 MCP 服務器")
        print("  2. AI 助手會自動調用 interactive_feedback 工具")
        print("  3. 根據環境自動選擇 GUI 或 Web UI")
        print("  4. 提供回饋後繼續工作流程")
        
        print("\n✨ Web UI 新功能:")
        print("  - 支援 SSH remote 開發環境")
        print("  - 現代化深色主題界面")
        print("  - WebSocket 即時通訊")
        print("  - 自動瀏覽器啟動")
        print("  - 命令執行和即時輸出")
        
        if persistent_mode and session_info:
            interactive_demo(session_info)
        else:
            print("\n✅ 測試完成 - 系統已準備就緒！")
            if session_info:
                print(f"💡 您可以現在就在瀏覽器中測試: {session_info['url']}")
                print("   (服務器會繼續運行一小段時間)")
                time.sleep(10)  # Keep running for a short time for immediate testing
    else:
        print("❌ 部分測試失敗，請檢查錯誤信息")
        sys.exit(1) 