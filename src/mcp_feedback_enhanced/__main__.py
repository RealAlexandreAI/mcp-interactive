#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Interactive Feedback Enhanced - 主程式入口
==============================================

此檔案允許套件透過 `python -m mcp_feedback_enhanced` 執行。

使用方法:
  python -m mcp_feedback_enhanced        # 啟動 MCP 伺服器
  python -m mcp_feedback_enhanced test   # 執行測試
"""

import sys
import argparse
import os

def main():
    """主程式入口點"""
    parser = argparse.ArgumentParser(
        description="Interactive Feedback MCP Enhanced - 互動式回饋收集 MCP 伺服器"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 伺服器命令（預設）
    server_parser = subparsers.add_parser('server', help='啟動 MCP 伺服器（預設）')
    
    # 測試命令
    test_parser = subparsers.add_parser('test', help='執行測試')
    test_parser.add_argument('--web', action='store_true', help='測試 Web UI (自動持續運行)')
    test_parser.add_argument('--gui', action='store_true', help='測試 Qt GUI (快速測試)')
    
    # 版本命令
    version_parser = subparsers.add_parser('version', help='顯示版本資訊')
    
    args = parser.parse_args()
    
    if args.command == 'test':
        run_tests(args)
    elif args.command == 'version':
        show_version()
    elif args.command == 'server':
        run_server()
    elif args.command is None:
        run_server()
    else:
        # 不應該到達這裡
        parser.print_help()
        sys.exit(1)

def run_server():
    """啟動 MCP 伺服器"""
    from .server import main as server_main
    return server_main()

def run_tests(args):
    """執行測試"""
    # 啟用調試模式以顯示測試過程
    os.environ["MCP_DEBUG"] = "true"
    
    if args.web:
        print("🧪 執行 Web UI 測試...")
        from .test_web_ui import test_web_ui, interactive_demo
        success, session_info = test_web_ui()
        if not success:
            sys.exit(1)
        # Web UI 測試自動啟用持續模式
        if session_info:
            print("📝 Web UI 測試完成，進入持續模式...")
            print("💡 提示：服務器將持續運行，可在瀏覽器中測試互動功能")
            print("💡 按 Ctrl+C 停止服務器")
            interactive_demo(session_info)
    elif args.gui:
        print("🧪 執行 Qt GUI 測試...")
        from .test_qt_gui import test_qt_gui
        if not test_qt_gui():
            sys.exit(1)
    else:
        # 執行所有測試
        print("🧪 執行完整測試套件...")
        success = True
        session_info = None
        
        try:
            from .test_web_ui import (
                test_environment_detection,
                test_new_parameters,
                test_mcp_integration,
                test_web_ui,
                interactive_demo
            )
            
            if not test_environment_detection():
                success = False
            if not test_new_parameters():
                success = False
            if not test_mcp_integration():
                success = False
            
            web_success, session_info = test_web_ui()
            if not web_success:
                success = False
            
        except Exception as e:
            print(f"❌ 測試執行失敗: {e}")
            success = False
        
        if not success:
            sys.exit(1)
        
        print("🎉 所有測試通過！")

def show_version():
    """顯示版本資訊"""
    from . import __version__, __author__
    print(f"Interactive Feedback MCP Enhanced v{__version__}")
    print(f"作者: {__author__}")
    print("GitHub: https://github.com/Minidoracat/mcp-feedback-enhanced")

if __name__ == "__main__":
    main() 