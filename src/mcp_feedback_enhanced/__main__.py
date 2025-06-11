#!/usr/bin/env python3
"""
MCP Interactive Feedback Enhanced - 主程式入口
==============================================

此檔案允許套件透過 `python -m mcp_feedback_enhanced` 執行。

使用方法:
  python -m mcp_feedback_enhanced        # 啟動 MCP 伺服器
  python -m mcp_feedback_enhanced test   # 執行測試
"""

import argparse
import asyncio
import os
import sys
import warnings


# 抑制 Windows 上的 asyncio ResourceWarning
if sys.platform == "win32":
    warnings.filterwarnings(
        "ignore", category=ResourceWarning, message=".*unclosed transport.*"
    )
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

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 伺服器命令（預設）
    subparsers.add_parser("server", help="啟動 MCP 伺服器（預設）")

    # 測試命令
    test_parser = subparsers.add_parser("test", help="執行測試")
    test_parser.add_argument(
        "--web", action="store_true", help="測試 Web UI (自動持續運行)"
    )
    test_parser.add_argument(
        "--timeout", type=int, default=60, help="測試超時時間 (秒)"
    )

    # 版本命令
    subparsers.add_parser("version", help="顯示版本資訊")

    args = parser.parse_args()

    if args.command == "test":
        run_tests(args)
    elif args.command == "version":
        show_version()
    elif args.command == "server" or args.command is None:
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
    if sys.platform == "win32":
        import warnings

        # 設置更全面的警告抑制
        os.environ["PYTHONWARNINGS"] = (
            "ignore::ResourceWarning,ignore::DeprecationWarning"
        )
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", message=".*unclosed transport.*")
        warnings.filterwarnings("ignore", message=".*I/O operation on closed pipe.*")
        warnings.filterwarnings("ignore", message=".*unclosed.*")
        # 抑制 asyncio 相關的所有警告
        warnings.filterwarnings("ignore", module="asyncio.*")

    if args.web:
        print("🧪 執行 Web UI 測試...")
        success = test_web_ui_simple()
        if not success:
            sys.exit(1)
    else:
        print("❌ 測試功能已簡化")
        print("💡 可用的測試選項：")
        print("  --web         測試 Web UI")
        print("💡 對於開發者：使用 'uv run pytest' 執行完整測試")
        sys.exit(1)


def test_web_ui_simple():
    """簡單的 Web UI 測試"""
    try:
        import tempfile
        import time
        import webbrowser

        from .web.main import WebUIManager

        # 設置測試模式，禁用自動清理避免權限問題
        os.environ["MCP_TEST_MODE"] = "true"
        # 設置更高的端口範圍避免系統保留端口
        os.environ["MCP_WEB_PORT"] = "9765"

        print("🔧 創建 Web UI 管理器...")
        manager = WebUIManager(host="127.0.0.1")  # 使用動態端口分配

        print("🔧 創建測試會話...")
        with tempfile.TemporaryDirectory() as temp_dir:
            created_session_id = manager.create_session(
                temp_dir, "Web UI 測試 - 驗證基本功能"
            )

            if created_session_id:
                print("✅ 會話創建成功")

                print("🚀 啟動 Web 服務器...")
                manager.start_server()
                time.sleep(5)  # 等待服務器完全啟動

                if (
                    manager.server_thread is not None
                    and manager.server_thread.is_alive()
                ):
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
    finally:
        # 清理測試環境變數
        os.environ.pop("MCP_TEST_MODE", None)
        os.environ.pop("MCP_WEB_PORT", None)


async def wait_for_process(process):
    """等待進程結束"""
    try:
        # 等待進程自然結束
        await process.wait()

        # 確保管道正確關閉
        try:
            if hasattr(process, "stdout") and process.stdout:
                process.stdout.close()
            if hasattr(process, "stderr") and process.stderr:
                process.stderr.close()
            if hasattr(process, "stdin") and process.stdin:
                process.stdin.close()
        except Exception as close_error:
            print(f"關閉進程管道時出錯: {close_error}")

    except Exception as e:
        print(f"等待進程時出錯: {e}")


def show_version():
    """顯示版本資訊"""
    from . import __author__, __version__

    print(f"MCP Feedback Enhanced Enhanced v{__version__}")
    print(f"作者: {__author__}")
    print("GitHub: https://github.com/Minidoracat/mcp-feedback-enhanced")


if __name__ == "__main__":
    main()
