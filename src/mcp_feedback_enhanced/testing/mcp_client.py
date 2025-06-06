#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 客戶端模擬器
================

模擬 Cursor IDE 作為 MCP 客戶端的完整調用流程，實現標準的 JSON-RPC 2.0 通信協議。

主要功能：
- MCP 協議握手和初始化
- 工具發現和能力協商
- 工具調用和結果處理
- 錯誤處理和重連機制
"""

import asyncio
import json
import uuid
import time
import subprocess
import signal
import os
from typing import Dict, Any, Optional, List, Callable, Awaitable
from pathlib import Path
from dataclasses import dataclass, field

from .config import TestConfig, DEFAULT_CONFIG
from .utils import TestUtils, PerformanceMonitor, AsyncEventWaiter
from ..debug import debug_log


@dataclass
class MCPMessage:
    """MCP 消息類"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        data = {"jsonrpc": self.jsonrpc}
        
        if self.id is not None:
            data["id"] = self.id
        if self.method is not None:
            data["method"] = self.method
        if self.params is not None:
            data["params"] = self.params
        if self.result is not None:
            data["result"] = self.result
        if self.error is not None:
            data["error"] = self.error
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """從字典創建"""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method"),
            params=data.get("params"),
            result=data.get("result"),
            error=data.get("error")
        )
    
    def is_request(self) -> bool:
        """是否為請求消息"""
        return self.method is not None
    
    def is_response(self) -> bool:
        """是否為響應消息"""
        return self.result is not None or self.error is not None
    
    def is_notification(self) -> bool:
        """是否為通知消息"""
        return self.method is not None and self.id is None


@dataclass
class MCPClientState:
    """MCP 客戶端狀態"""
    connected: bool = False
    initialized: bool = False
    tools_discovered: bool = False
    available_tools: List[Dict[str, Any]] = field(default_factory=list)
    server_capabilities: Dict[str, Any] = field(default_factory=dict)
    client_info: Dict[str, Any] = field(default_factory=dict)
    server_info: Dict[str, Any] = field(default_factory=dict)


class MCPTestClient:
    """MCP 測試客戶端"""
    
    def __init__(self, config: Optional[TestConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.state = MCPClientState()
        self.process: Optional[subprocess.Popen] = None
        self.event_waiter = AsyncEventWaiter()
        self.performance_monitor = PerformanceMonitor()
        self.message_id_counter = 0
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.message_handlers: Dict[str, Callable] = {}
        
        # 設置默認消息處理器
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """設置默認消息處理器"""
        self.message_handlers.update({
            'initialize': self._handle_initialize_response,
            'tools/list': self._handle_tools_list_response,
            'tools/call': self._handle_tools_call_response,
        })
    
    def _generate_message_id(self) -> str:
        """生成消息 ID"""
        self.message_id_counter += 1
        return f"msg_{self.message_id_counter}_{uuid.uuid4().hex[:8]}"
    
    async def start_server(self) -> bool:
        """啟動 MCP 服務器"""
        try:
            debug_log("🚀 啟動 MCP 服務器...")
            self.performance_monitor.start()
            
            # 構建啟動命令
            cmd = [
                "python", "-m", "src.mcp_feedback_enhanced", "server"
            ]
            
            # 設置環境變數
            env = os.environ.copy()
            env.update({
                "MCP_DEBUG": "true" if self.config.test_debug else "false",
                "PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)
            })
            
            # 啟動進程
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                bufsize=0
            )
            
            debug_log(f"✅ MCP 服務器進程已啟動 (PID: {self.process.pid})")
            
            # 等待服務器初始化
            await asyncio.sleep(2)
            
            # 檢查進程是否仍在運行
            if self.process.poll() is not None:
                stderr_output = self.process.stderr.read() if self.process.stderr else ""
                raise RuntimeError(f"MCP 服務器啟動失敗: {stderr_output}")
            
            self.state.connected = True
            self.performance_monitor.checkpoint("server_started")
            return True
            
        except Exception as e:
            debug_log(f"❌ 啟動 MCP 服務器失敗: {e}")
            await self.cleanup()
            return False
    
    async def stop_server(self):
        """停止 MCP 服務器"""
        if self.process:
            try:
                debug_log("🛑 停止 MCP 服務器...")
                
                # 嘗試優雅關閉
                self.process.terminate()
                
                try:
                    await asyncio.wait_for(
                        asyncio.create_task(self._wait_for_process()),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    debug_log("⚠️ 優雅關閉超時，強制終止進程")
                    self.process.kill()
                    await self._wait_for_process()
                
                debug_log("✅ MCP 服務器已停止")
                
            except Exception as e:
                debug_log(f"⚠️ 停止 MCP 服務器時發生錯誤: {e}")
            finally:
                self.process = None
                self.state.connected = False
    
    async def _wait_for_process(self):
        """等待進程結束"""
        if self.process:
            while self.process.poll() is None:
                await asyncio.sleep(0.1)
    
    async def send_message(self, message: MCPMessage) -> Optional[MCPMessage]:
        """發送 MCP 消息"""
        if not self.process or not self.state.connected:
            raise RuntimeError("MCP 服務器未連接")
        
        try:
            # 序列化消息
            message_data = json.dumps(message.to_dict()) + "\n"
            
            debug_log(f"📤 發送 MCP 消息: {message.method or 'response'}")
            if self.config.test_debug:
                debug_log(f"   內容: {message_data.strip()}")
            
            # 發送消息
            self.process.stdin.write(message_data)
            self.process.stdin.flush()
            
            # 如果是請求，等待響應
            if message.is_request() and message.id:
                future = asyncio.Future()
                self.pending_requests[message.id] = future
                
                try:
                    response = await asyncio.wait_for(
                        future, 
                        timeout=self.config.mcp_timeout
                    )
                    return response
                except asyncio.TimeoutError:
                    self.pending_requests.pop(message.id, None)
                    raise TimeoutError(f"MCP 請求超時: {message.method}")
            
            return None
            
        except Exception as e:
            debug_log(f"❌ 發送 MCP 消息失敗: {e}")
            raise
    
    async def read_messages(self):
        """讀取 MCP 消息"""
        if not self.process:
            return
        
        try:
            while self.process and self.process.poll() is None:
                # 讀取一行
                line = await asyncio.create_task(self._read_line())
                if not line:
                    continue
                
                try:
                    # 解析 JSON
                    data = json.loads(line.strip())
                    message = MCPMessage.from_dict(data)
                    
                    debug_log(f"📨 收到 MCP 消息: {message.method or 'response'}")
                    if self.config.test_debug:
                        debug_log(f"   內容: {line.strip()}")
                    
                    # 處理消息
                    await self._handle_message(message)
                    
                except json.JSONDecodeError as e:
                    debug_log(f"⚠️ JSON 解析失敗: {e}, 原始數據: {line}")
                except Exception as e:
                    debug_log(f"❌ 處理消息失敗: {e}")
        
        except Exception as e:
            debug_log(f"❌ 讀取 MCP 消息失敗: {e}")
    
    async def _read_line(self) -> str:
        """異步讀取一行"""
        if not self.process or not self.process.stdout:
            return ""
        
        # 使用線程池執行阻塞的讀取操作
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process.stdout.readline)
    
    async def _handle_message(self, message: MCPMessage):
        """處理收到的消息"""
        if message.is_response() and message.id:
            # 處理響應
            future = self.pending_requests.pop(message.id, None)
            if future and not future.done():
                future.set_result(message)
        
        elif message.is_request():
            # 處理請求（通常是服務器發起的）
            debug_log(f"收到服務器請求: {message.method}")
        
        # 調用特定的消息處理器
        if message.method in self.message_handlers:
            await self.message_handlers[message.method](message)
    
    async def _handle_initialize_response(self, message: MCPMessage):
        """處理初始化響應"""
        if message.result:
            self.state.server_info = message.result.get('serverInfo', {})
            self.state.server_capabilities = message.result.get('capabilities', {})
            self.state.initialized = True
            debug_log("✅ MCP 初始化完成")
    
    async def _handle_tools_list_response(self, message: MCPMessage):
        """處理工具列表響應"""
        if message.result and 'tools' in message.result:
            self.state.available_tools = message.result['tools']
            self.state.tools_discovered = True
            debug_log(f"✅ 發現 {len(self.state.available_tools)} 個工具")
    
    async def _handle_tools_call_response(self, message: MCPMessage):
        """處理工具調用響應"""
        if message.result:
            debug_log("✅ 工具調用完成")
        elif message.error:
            debug_log(f"❌ 工具調用失敗: {message.error}")
    
    async def initialize(self) -> bool:
        """初始化 MCP 連接"""
        try:
            debug_log("🔄 初始化 MCP 連接...")

            message = MCPMessage(
                id=self._generate_message_id(),
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {
                        "name": "mcp-test-client",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "roots": {
                            "listChanged": True
                        },
                        "sampling": {}
                    }
                }
            )

            response = await self.send_message(message)

            if response and response.result:
                self.performance_monitor.checkpoint("initialized")
                return True
            else:
                debug_log(f"❌ 初始化失敗: {response.error if response else '無響應'}")
                return False

        except Exception as e:
            debug_log(f"❌ 初始化異常: {e}")
            return False

    async def list_tools(self) -> List[Dict[str, Any]]:
        """獲取可用工具列表"""
        try:
            debug_log("🔍 獲取工具列表...")

            message = MCPMessage(
                id=self._generate_message_id(),
                method="tools/list",
                params={}
            )

            response = await self.send_message(message)

            if response and response.result and 'tools' in response.result:
                tools = response.result['tools']
                debug_log(f"✅ 獲取到 {len(tools)} 個工具")
                self.performance_monitor.checkpoint("tools_listed", {"tools_count": len(tools)})
                return tools
            else:
                debug_log(f"❌ 獲取工具列表失敗: {response.error if response else '無響應'}")
                return []

        except Exception as e:
            debug_log(f"❌ 獲取工具列表異常: {e}")
            return []

    async def call_interactive_feedback(self, project_directory: str, summary: str,
                                      timeout: int = 60) -> Dict[str, Any]:
        """調用互動回饋工具"""
        try:
            debug_log("🎯 調用互動回饋工具...")

            message = MCPMessage(
                id=self._generate_message_id(),
                method="tools/call",
                params={
                    "name": "interactive_feedback",
                    "arguments": {
                        "project_directory": project_directory,
                        "summary": summary,
                        "timeout": timeout
                    }
                }
            )

            # 設置較長的超時時間，因為需要等待用戶互動
            old_timeout = self.config.mcp_timeout
            self.config.mcp_timeout = timeout + 30  # 額外 30 秒緩衝

            try:
                response = await self.send_message(message)

                if response and response.result:
                    result = response.result
                    debug_log("✅ 互動回饋工具調用成功")
                    self.performance_monitor.checkpoint("interactive_feedback_completed")
                    return result
                else:
                    error_msg = response.error if response else "無響應"
                    debug_log(f"❌ 互動回饋工具調用失敗: {error_msg}")
                    return {"error": str(error_msg)}

            finally:
                self.config.mcp_timeout = old_timeout

        except Exception as e:
            debug_log(f"❌ 互動回饋工具調用異常: {e}")
            return {"error": str(e)}

    async def full_workflow_test(self, project_directory: Optional[str] = None,
                               summary: Optional[str] = None) -> Dict[str, Any]:
        """執行完整的工作流程測試"""
        try:
            debug_log("🚀 開始完整工作流程測試...")
            self.performance_monitor.start()

            # 使用配置中的默認值
            project_dir = project_directory or self.config.test_project_dir or str(Path.cwd())
            test_summary = summary or self.config.test_summary

            results = {
                "success": False,
                "steps": {},
                "performance": {},
                "errors": []
            }

            # 步驟 1: 啟動服務器
            if not await self.start_server():
                results["errors"].append("服務器啟動失敗")
                return results
            results["steps"]["server_started"] = True

            # 啟動消息讀取任務
            read_task = asyncio.create_task(self.read_messages())

            try:
                # 步驟 2: 初始化連接
                if not await self.initialize():
                    results["errors"].append("MCP 初始化失敗")
                    return results
                results["steps"]["initialized"] = True

                # 步驟 3: 獲取工具列表
                tools = await self.list_tools()
                if not tools:
                    results["errors"].append("獲取工具列表失敗")
                    return results
                results["steps"]["tools_discovered"] = True
                results["tools_count"] = len(tools)

                # 檢查是否有 interactive_feedback 工具
                has_interactive_tool = any(
                    tool.get("name") == "interactive_feedback"
                    for tool in tools
                )
                if not has_interactive_tool:
                    results["errors"].append("未找到 interactive_feedback 工具")
                    return results

                # 步驟 4: 調用互動回饋工具
                feedback_result = await self.call_interactive_feedback(
                    project_dir, test_summary, self.config.test_timeout
                )

                if "error" in feedback_result:
                    results["errors"].append(f"互動回饋調用失敗: {feedback_result['error']}")
                    return results

                results["steps"]["interactive_feedback_called"] = True
                results["feedback_result"] = feedback_result
                results["success"] = True

                debug_log("🎉 完整工作流程測試成功完成")

            finally:
                read_task.cancel()
                try:
                    await read_task
                except asyncio.CancelledError:
                    pass

            return results

        except Exception as e:
            debug_log(f"❌ 完整工作流程測試異常: {e}")
            results["errors"].append(f"測試異常: {str(e)}")
            return results

        finally:
            # 獲取性能數據
            self.performance_monitor.stop()
            results["performance"] = self.performance_monitor.get_summary()

            # 清理資源
            await self.cleanup()

    async def cleanup(self):
        """清理資源"""
        await self.stop_server()

        # 取消所有待處理的請求
        for future in self.pending_requests.values():
            if not future.done():
                future.cancel()
        self.pending_requests.clear()

        self.performance_monitor.stop()
        debug_log("🧹 MCP 客戶端資源已清理")
