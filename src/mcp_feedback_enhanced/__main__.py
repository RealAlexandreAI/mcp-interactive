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
import asyncio
import warnings

# 抑制 Windows 上的 asyncio ResourceWarning
if sys.platform == 'win32':
    warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed transport.*")
    warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed.*")

    # 設置 asyncio 事件循環策略以減少警告
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except AttributeError:
        pass

def main():
    """主程式入口點"""
    parser = argparse.ArgumentParser(
        description="MCP Feedback Enhanced Enhanced - 互動式回饋收集 MCP 伺服器"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 伺服器命令（預設）
    server_parser = subparsers.add_parser('server', help='啟動 MCP 伺服器（預設）')
    
    # 測試命令
    test_parser = subparsers.add_parser('test', help='執行測試')
    test_parser.add_argument('--web', action='store_true', help='測試 Web UI (自動持續運行)')
    test_parser.add_argument('--desktop', action='store_true', help='測試桌面應用 (啟動 Electron 應用)')
    test_parser.add_argument('--full', action='store_true', help='完整整合測試 (Web + 桌面)')
    test_parser.add_argument('--electron-only', action='store_true', help='僅測試 Electron 環境')
    test_parser.add_argument('--timeout', type=int, default=60, help='測試超時時間 (秒)')
    
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

    # 在 Windows 上抑制 asyncio 警告
    if sys.platform == 'win32':
        os.environ["PYTHONWARNINGS"] = "ignore::ResourceWarning"

    if args.web:
        print("🧪 執行 Web UI 測試...")
        success = test_web_ui_simple()
        if not success:
            sys.exit(1)
    elif args.desktop:
        print("🧪 執行桌面應用測試...")
        success = test_desktop_app()
        if not success:
            sys.exit(1)
    elif args.full:
        print("🧪 執行完整整合測試...")
        success = test_full_integration()
        if not success:
            sys.exit(1)
    elif args.electron_only:
        print("🧪 執行 Electron 環境測試...")
        success = test_electron_environment()
        if not success:
            sys.exit(1)
    else:
        print("❌ 測試功能已簡化")
        print("💡 可用的測試選項：")
        print("  --web         測試 Web UI")
        print("  --desktop     測試桌面應用")
        print("  --full        完整整合測試")
        print("  --electron-only  僅測試 Electron 環境")
        print("💡 對於開發者：使用 'uv run pytest' 執行完整測試")
        sys.exit(1)


def test_web_ui_simple():
    """簡單的 Web UI 測試"""
    try:
        from .web.main import WebUIManager
        import tempfile
        import time
        import webbrowser

        print("🔧 創建 Web UI 管理器...")
        manager = WebUIManager(host="127.0.0.1", port=8765)  # 使用固定端口

        print("🔧 創建測試會話...")
        with tempfile.TemporaryDirectory() as temp_dir:
            session_id = manager.create_session(
                temp_dir,
                "Web UI 測試 - 驗證基本功能"
            )

            if session_id:
                print("✅ 會話創建成功")

                print("🚀 啟動 Web 服務器...")
                manager.start_server()
                time.sleep(5)  # 等待服務器完全啟動

                if manager.server_thread and manager.server_thread.is_alive():
                    print("✅ Web 服務器啟動成功")
                    url = f"http://{manager.host}:{manager.port}"
                    print(f"🌐 服務器運行在: {url}")

                    # 嘗試開啟瀏覽器
                    print("🌐 正在開啟瀏覽器...")
                    try:
                        webbrowser.open(url)
                        print("✅ 瀏覽器已開啟")
                    except Exception as e:
                        print(f"⚠️  無法自動開啟瀏覽器: {e}")
                        print(f"💡 請手動開啟瀏覽器並訪問: {url}")

                    print("📝 Web UI 測試完成，進入持續模式...")
                    print("💡 提示：服務器將持續運行，可在瀏覽器中測試互動功能")
                    print("💡 按 Ctrl+C 停止服務器")

                    try:
                        # 保持服務器運行
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n🛑 停止服務器...")
                        return True
                else:
                    print("❌ Web 服務器啟動失敗")
                    return False
            else:
                print("❌ 會話創建失敗")
                return False

    except Exception as e:
        print(f"❌ Web UI 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_desktop_app():
    """測試桌面應用"""
    try:
        print("🔧 檢查桌面環境...")

        # 檢查桌面環境可用性
        from .desktop import is_desktop_available
        if not is_desktop_available():
            print("❌ 桌面環境不可用")
            print("💡 請確保 Node.js 已安裝且不在遠程環境中")
            return False

        print("✅ 桌面環境檢查通過")

        # 設置桌面模式
        os.environ['MCP_FEEDBACK_MODE'] = 'desktop'

        print("🔧 創建 Electron 管理器...")
        from .desktop.electron_manager import ElectronManager
        import asyncio

        async def run_desktop_test():
            print("🚀 啟動完整桌面應用測試...")
            print("💡 這將啟動 Web 服務器和 Electron 應用視窗")
            print("💡 請在應用中測試基本功能，然後關閉視窗")

            # 使用完整的桌面應用啟動函數
            from .desktop import launch_desktop_app

            try:
                # 這會啟動 Web 服務器和 Electron 應用
                result = await launch_desktop_app(
                    os.getcwd(),
                    "桌面應用測試 - 驗證 Electron 整合功能",
                    300  # 5分鐘超時
                )

                print("✅ 桌面應用測試完成")
                print(f"收到回饋: {result.get('interactive_feedback', '無回饋')}")
                return True

            except Exception as e:
                print(f"❌ 桌面應用測試失敗: {e}")
                return False

        return asyncio.run(run_desktop_test())

    except Exception as e:
        print(f"❌ 桌面應用測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def wait_for_process(process):
    """等待進程結束"""
    try:
        # 等待進程自然結束
        await process.wait()

        # 確保管道正確關閉
        try:
            if hasattr(process, 'stdout') and process.stdout:
                process.stdout.close()
            if hasattr(process, 'stderr') and process.stderr:
                process.stderr.close()
            if hasattr(process, 'stdin') and process.stdin:
                process.stdin.close()
        except Exception as close_error:
            print(f"關閉進程管道時出錯: {close_error}")

    except Exception as e:
        print(f"等待進程時出錯: {e}")


def test_electron_environment():
    """測試 Electron 環境"""
    try:
        print("🔧 檢查 Electron 環境...")

        # 檢查 Node.js
        import subprocess
        try:
            result = subprocess.run(['node', '--version'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Node.js 版本: {result.stdout.strip()}")
            else:
                print("❌ Node.js 不可用")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Node.js 不可用")
            return False

        # 檢查桌面模組
        from .desktop import is_desktop_available
        if is_desktop_available():
            print("✅ 桌面環境可用")
        else:
            print("❌ 桌面環境不可用")
            return False

        # 檢查 Electron 管理器
        from .desktop.electron_manager import ElectronManager
        manager = ElectronManager()

        if manager.is_electron_available():
            print("✅ Electron 環境可用")
        else:
            print("❌ Electron 環境不可用")
            return False

        # 檢查文件結構
        desktop_dir = manager.desktop_dir
        required_files = ['main.js', 'preload.js', 'package.json']

        for file_name in required_files:
            file_path = desktop_dir / file_name
            if file_path.exists():
                print(f"✅ {file_name} 存在")
            else:
                print(f"❌ {file_name} 不存在")
                return False

        # 檢查 node_modules
        node_modules = desktop_dir / "node_modules"
        if node_modules.exists():
            print("✅ node_modules 存在")
        else:
            print("❌ node_modules 不存在")
            return False

        print("🎉 Electron 環境測試完成，所有檢查通過")
        return True

    except Exception as e:
        print(f"❌ Electron 環境測試失敗: {e}")
        return False


def test_full_integration():
    """完整整合測試"""
    try:
        print("🧪 執行完整整合測試...")

        # 1. 環境變數測試
        print("\n📋 1. 測試環境變數控制...")
        test_cases = [("auto", "auto"), ("web", "web"), ("desktop", "desktop")]

        for env_value, expected in test_cases:
            os.environ['MCP_FEEDBACK_MODE'] = env_value

            # 重新導入以獲取新的環境變數值
            import sys
            if 'mcp_feedback_enhanced.server' in sys.modules:
                del sys.modules['mcp_feedback_enhanced.server']

            from .server import get_feedback_mode
            actual = get_feedback_mode().value

            if actual == expected:
                print(f"  ✅ MCP_FEEDBACK_MODE='{env_value}' → {actual}")
            else:
                print(f"  ❌ MCP_FEEDBACK_MODE='{env_value}' → {actual} (期望: {expected})")
                return False

        # 2. Electron 環境測試
        print("\n📋 2. 測試 Electron 環境...")
        if not test_electron_environment():
            print("❌ Electron 環境測試失敗")
            return False

        # 3. Web UI 基本功能測試
        print("\n📋 3. 測試 Web UI 基本功能...")
        from .web.main import WebUIManager
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = WebUIManager(host="127.0.0.1", port=8766)  # 使用不同端口避免衝突
            session_id = manager.create_session(temp_dir, "整合測試會話")

            if session_id:
                print("  ✅ Web UI 會話創建成功")
            else:
                print("  ❌ Web UI 會話創建失敗")
                return False

        # 4. 桌面模式檢測測試
        print("\n📋 4. 測試桌面模式檢測...")
        os.environ['MCP_FEEDBACK_MODE'] = 'desktop'

        manager = WebUIManager()
        if manager.should_use_desktop_mode():
            print("  ✅ 桌面模式檢測正常")
        else:
            print("  ❌ 桌面模式檢測失敗")
            return False

        print("\n🎉 完整整合測試通過！")
        print("💡 所有核心功能正常運作")
        return True

    except Exception as e:
        print(f"❌ 完整整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_version():
    """顯示版本資訊"""
    from . import __version__, __author__
    print(f"MCP Feedback Enhanced Enhanced v{__version__}")
    print(f"作者: {__author__}")
    print("GitHub: https://github.com/Minidoracat/mcp-feedback-enhanced")

if __name__ == "__main__":
    main() 