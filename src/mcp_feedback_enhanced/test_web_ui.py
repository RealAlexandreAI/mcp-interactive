#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Feedback Enhanced - Web UI 測試模組
========================================

用於測試 MCP Feedback Enhanced 的 Web UI 功能。
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
import json
from pathlib import Path
from typing import Dict, Any, Optional

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from .debug import debug_log
from .i18n import t, get_i18n_manager

# 嘗試導入 Web UI 模組
try:
    # 使用新的 web 模組
    from .web import WebUIManager, launch_web_feedback_ui, get_web_ui_manager
    from .web.utils.browser import smart_browser_open, is_wsl_environment
    WEB_UI_AVAILABLE = True
    debug_log(t('test.messages.webModuleLoaded'))
except ImportError as e:
    debug_log(t('test.messages.webModuleLoadFailed', error=str(e)))
    WEB_UI_AVAILABLE = False

def load_web_ui_language_setting():
    """載入 Web UI 的語言設定並同步到 GUI 國際化系統"""
    try:
        # 讀取 ui_settings.json 配置文件
        config_dir = Path.home() / ".config" / "mcp-feedback-enhanced"
        settings_file = config_dir / "ui_settings.json"

        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                language = settings.get('language')

                if language:
                    debug_log(t('test.messages.loadingLanguageFromSettings', language=language))

                    # 獲取 GUI 國際化管理器並設定語言
                    i18n_manager = get_i18n_manager()
                    current_language = i18n_manager.get_current_language()

                    if language != current_language:
                        debug_log(t('test.messages.syncingLanguage', **{'from': current_language, 'to': language}))
                        success = i18n_manager.set_language(language)
                        if success:
                            debug_log(t('test.messages.guiLanguageSynced', language=language))
                        else:
                            debug_log(t('test.messages.languageSetFailed', language=current_language))
                    else:
                        debug_log(t('test.messages.languageAlreadySynced', language=language))

                    return language
                else:
                    debug_log(t('test.messages.noLanguageInSettings'))
        else:
            debug_log(t('test.messages.settingsFileNotExists'))

    except Exception as e:
        debug_log(t('test.messages.loadLanguageSettingsFailed', error=str(e)))

    # 返回當前語言作為回退
    return get_i18n_manager().get_current_language()

def get_test_summary():
    """獲取測試摘要，使用國際化系統"""
    return t('test.webUiSummary')

def find_free_port():
    """Find a free port to use for testing"""
    try:
        # 嘗試使用增強的端口管理
        from .web.utils.port_manager import PortManager
        return PortManager.find_free_port_enhanced(preferred_port=8765, auto_cleanup=False)
    except ImportError:
        # 回退到原始方法
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

def test_web_ui(keep_running=False):
    """Test the Web UI functionality"""

    debug_log(t('test.messages.testingWebUi'))
    debug_log("=" * 50)

    # 同步 Web UI 語言設定到 GUI 國際化系統
    debug_log(t('test.messages.syncingLanguageSettings'))
    current_language = load_web_ui_language_setting()
    debug_log(t('test.messages.currentLanguage', language=current_language))
    debug_log("-" * 30)
    
    # Test import
    try:
        # 使用新的 web 模組
        from .web import WebUIManager, launch_web_feedback_ui
        debug_log(t('test.messages.webUiModuleImportSuccess'))
    except ImportError as e:
        debug_log(t('test.messages.webUiModuleImportFailed', error=str(e)))
        return False, None
    
    # Check for environment variable port setting
    env_port = os.getenv("MCP_WEB_PORT")
    if env_port:
        try:
            custom_port = int(env_port)
            if 1024 <= custom_port <= 65535:
                debug_log(t('test.messages.foundAvailablePort', port=custom_port))
                debug_log(f"使用環境變數 MCP_WEB_PORT 指定的端口: {custom_port}")
                test_port = custom_port
            else:
                debug_log(f"MCP_WEB_PORT 值無效 ({custom_port})，必須在 1024-65535 範圍內")
                # Find free port as fallback
                test_port = find_free_port()
                debug_log(t('test.messages.foundAvailablePort', port=test_port))
        except ValueError:
            debug_log(f"MCP_WEB_PORT 格式錯誤 ({env_port})，必須為數字")
            # Find free port as fallback
            test_port = find_free_port()
            debug_log(t('test.messages.foundAvailablePort', port=test_port))
    else:
        # Find free port
        try:
            test_port = find_free_port()
            debug_log(t('test.messages.foundAvailablePort', port=test_port))
        except Exception as e:
            debug_log(t('test.messages.findPortFailed', error=str(e)))
            return False, None

    # Test manager creation (不傳遞 port 參數，讓 WebUIManager 自己處理環境變數)
    try:
        manager = WebUIManager()  # 讓 WebUIManager 自己處理端口邏輯
        debug_log(t('test.messages.webUiManagerCreateSuccess'))
    except Exception as e:
        debug_log(t('test.messages.webUiManagerCreateFailed', error=str(e)))
        return False, None
    
    # Test server start (with timeout)
    server_started = False
    try:
        debug_log(t('test.messages.startingWebServer'))

        def start_server():
            try:
                manager.start_server()
                return True
            except Exception as e:
                debug_log(t('test.messages.serverStartError', error=str(e)))
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
                debug_log(t('test.messages.webServerStartSuccess'))
                debug_log(t('test.messages.serverRunningAt', host=manager.host, port=manager.port))
            else:
                debug_log(t('test.messages.cannotConnectToPort', port=manager.port))

    except Exception as e:
        debug_log(t('test.messages.webServerStartFailed', error=str(e)))
        return False, None

    if not server_started:
        debug_log(t('test.messages.serverNotStarted'))
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
            'url': f"http://{manager.host}:{manager.port}"  # 使用根路徑
        }
        debug_log(t('test.messages.testSessionCreated', sessionId=session_id[:8]))
        debug_log(t('test.messages.testUrl', url=session_info['url']))

        # 測試瀏覽器啟動功能
        try:
            debug_log(t('test.messages.testingBrowserLaunch'))
            if is_wsl_environment():
                debug_log(t('test.messages.wslEnvironmentDetected'))
            else:
                debug_log(t('test.messages.nonWslEnvironment'))

            smart_browser_open(session_info['url'])
            debug_log(t('test.messages.browserLaunchSuccess', url=session_info['url']))
        except Exception as browser_error:
            debug_log(t('test.messages.browserLaunchFailed', error=str(browser_error)))
            debug_log(t('test.messages.browserLaunchNote'))

    except Exception as e:
        debug_log(t('test.messages.sessionCreationFailed', error=str(e)))
        return False, None
    
    debug_log("\n" + "=" * 50)
    debug_log(t('test.messages.allTestsPassed'))
    debug_log(t('test.messages.notes'))
    debug_log(t('test.messages.webUiAutoEnabled'))
    debug_log(t('test.messages.localEnvironmentGui'))
    debug_log(t('test.messages.realtimeCommandSupport'))
    debug_log(t('test.messages.modernDarkTheme'))
    debug_log(t('test.messages.smartCtrlVPaste'))
    
    return True, session_info

def test_environment_detection():
    """Test environment detection logic"""
    debug_log(t('test.messages.testingEnvironmentDetection'))
    debug_log("-" * 30)

    try:
        from .server import is_remote_environment, is_wsl_environment, can_use_gui

        wsl_detected = is_wsl_environment()
        remote_detected = is_remote_environment()
        gui_available = can_use_gui()

        debug_log(t('test.messages.wslDetection', result=t('test.messages.yes') if wsl_detected else t('test.messages.no')))
        debug_log(t('test.messages.remoteDetection', result=t('test.messages.yes') if remote_detected else t('test.messages.no')))
        debug_log(t('test.messages.guiAvailability', result=t('test.messages.yes') if gui_available else t('test.messages.no')))

        if wsl_detected:
            debug_log(t('test.messages.wslEnvironmentWebUi'))
        elif remote_detected:
            debug_log(t('test.messages.remoteEnvironmentWebUi'))
        else:
            debug_log(t('test.messages.localEnvironmentQtGui'))

        return True

    except Exception as e:
        debug_log(t('test.messages.environmentDetectionFailed', error=str(e)))
        return False

def test_mcp_integration():
    """Test MCP server integration"""
    debug_log(t('test.messages.testingMcpIntegration'))
    debug_log("-" * 30)

    try:
        from .server import interactive_feedback
        debug_log(t('test.messages.mcpToolFunctionAvailable'))

        # Test timeout parameter
        debug_log(t('test.messages.timeoutParameterSupported'))

        # Test environment-based Web UI selection
        debug_log(t('test.messages.environmentBasedWebUiSupported'))

        # Test would require actual MCP call, so just verify import
        debug_log(t('test.messages.readyForAiAssistantCalls'))
        return True

    except Exception as e:
        debug_log(t('test.messages.mcpIntegrationTestFailed', error=str(e)))
        return False

def test_new_parameters():
    """Test timeout parameter and environment variable support"""
    debug_log(t('test.messages.testingParameterFunctionality'))
    debug_log("-" * 30)

    try:
        from .server import interactive_feedback

        # 測試參數是否存在
        import inspect
        sig = inspect.signature(interactive_feedback)

        # 檢查 timeout 參數
        if 'timeout' in sig.parameters:
            timeout_param = sig.parameters['timeout']
            debug_log(t('test.messages.timeoutParameterExists', default=timeout_param.default))
        else:
            debug_log(t('test.messages.timeoutParameterMissing'))
            return False

        # 檢查環境變數支援
        import os
        current_force_web = os.getenv("FORCE_WEB")
        if current_force_web:
            debug_log(t('test.messages.forceWebDetected', value=current_force_web))
        else:
            debug_log(t('test.messages.forceWebNotSet'))

        debug_log(t('test.messages.parameterFunctionalityNormal'))
        return True

    except Exception as e:
        debug_log(t('test.messages.parameterTestFailed', error=str(e)))
        return False

def test_environment_web_ui_mode():
    """Test environment-based Web UI mode"""
    debug_log(t('test.messages.testingEnvironmentWebUiMode'))
    debug_log("-" * 30)

    try:
        from .server import interactive_feedback, is_remote_environment, is_wsl_environment, can_use_gui
        import os

        # 顯示當前環境狀態
        is_wsl = is_wsl_environment()
        is_remote = is_remote_environment()
        gui_available = can_use_gui()
        force_web_env = os.getenv("FORCE_WEB", "").lower()

        debug_log(t('test.messages.currentEnvironment', wsl=is_wsl, remote=is_remote, gui=gui_available))
        debug_log(t('test.messages.forceWebVariable', value=force_web_env or t('test.messages.notSet')))

        if force_web_env in ("true", "1", "yes", "on"):
            debug_log(t('test.messages.forceWebEnabled'))
        elif is_wsl:
            debug_log(t('test.messages.wslEnvironmentWebUiBrowser'))
        elif not is_remote and gui_available:
            debug_log(t('test.messages.localGuiEnvironmentQtGui'))
            debug_log(t('test.messages.forceWebTestHint'))
        else:
            debug_log(t('test.messages.autoWebUiRemoteOrNoGui'))

        return True

    except Exception as e:
        debug_log(t('test.messages.environmentVariableTestFailed', error=str(e)))
        return False

def interactive_demo(session_info):
    """Run interactive demo with the Web UI"""
    debug_log(t('test.messages.webUiInteractiveTestMode'))
    debug_log("=" * 50)
    debug_log(t('test.messages.serverAddress', url=session_info['url']))  # 簡化輸出，只顯示服務器地址
    debug_log(t('test.messages.operationGuide'))
    debug_log(t('test.messages.openServerInBrowser'))
    debug_log(t('test.messages.tryFollowingFeatures'))
    debug_log(t('test.messages.clickShowCommandBlock'))
    debug_log(t('test.messages.inputCommandAndExecute'))
    debug_log(t('test.messages.inputTextInFeedbackArea'))
    debug_log(t('test.messages.useCtrlEnterSubmit'))
    debug_log(t('test.messages.testWebSocketRealtime'))
    debug_log(t('test.messages.testPagePersistence'))
    debug_log(t('test.messages.controlOptions'))
    debug_log(t('test.messages.pressEnterContinue'))
    debug_log(t('test.messages.inputQuitToStop'))
    
    while True:
        try:
            user_input = input("\n>>> ").strip().lower()
            if user_input in ['q', 'quit', 'exit']:
                debug_log(t('test.messages.stoppingServer'))
                break
            elif user_input == '':
                debug_log(t('test.messages.serverContinuesRunning', url=session_info['url']))
                debug_log(t('test.messages.browserShouldStillAccess'))
            else:
                debug_log(t('test.messages.unknownCommand'))
        except KeyboardInterrupt:
            debug_log(t('test.messages.interruptSignalReceived'))
            break

    debug_log(t('test.messages.webUiTestComplete'))

if __name__ == "__main__":
    debug_log(t('test.messages.webUiTest'))
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
        debug_log(t('test.messages.allTestsComplete'))
        debug_log(t('test.messages.usageInstructions'))
        debug_log(t('test.messages.configureMcpServer'))
        debug_log(t('test.messages.aiAssistantAutoCall'))
        debug_log(t('test.messages.autoSelectGuiOrWebUi'))
        debug_log(t('test.messages.provideFeedbackContinue'))

        debug_log(t('test.messages.webUiNewFeatures'))
        debug_log(t('test.messages.sshRemoteSupport'))
        debug_log(t('test.messages.modernDarkThemeInterface'))
        debug_log(t('test.messages.webSocketRealtime'))
        debug_log(t('test.messages.autoBrowserLaunch'))
        debug_log(t('test.messages.commandExecutionRealtime'))

        debug_log(t('test.messages.testCompleteSystemReady'))
        if session_info:
            debug_log(t('test.messages.canTestInBrowserNow', url=session_info['url']))
            debug_log(t('test.messages.serverWillContinueRunning'))
            time.sleep(10)  # Keep running for a short time for immediate testing
    else:
        debug_log(t('test.messages.someTestsFailed'))
        sys.exit(1)