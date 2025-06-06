#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試場景定義
============

定義各種 MCP 測試場景，包括正常流程、錯誤處理、性能測試等。
"""

import asyncio
import time
import random
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from pathlib import Path

from .mcp_client import MCPTestClient
from .config import TestConfig, DEFAULT_CONFIG
from .utils import TestUtils, PerformanceMonitor, performance_context
from ..debug import debug_log


@dataclass
class TestScenario:
    """測試場景類"""
    name: str
    description: str
    timeout: int = 120
    retry_count: int = 1
    parallel: bool = False
    tags: List[str] = field(default_factory=list)
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    
    async def run(self, client: MCPTestClient) -> Dict[str, Any]:
        """運行測試場景"""
        raise NotImplementedError


class BasicWorkflowScenario(TestScenario):
    """基礎工作流程測試場景"""
    
    def __init__(self):
        super().__init__(
            name="basic_workflow",
            description="測試基本的 MCP 工作流程：初始化 -> 工具發現 -> 工具調用",
            timeout=180,
            tags=["basic", "workflow", "integration"]
        )
    
    async def run(self, client: MCPTestClient) -> Dict[str, Any]:
        """運行基礎工作流程測試"""
        async with performance_context("basic_workflow") as monitor:
            result = await client.full_workflow_test()
            
            # 添加額外的驗證
            if result["success"]:
                # 檢查必要的步驟是否完成
                required_steps = ["server_started", "initialized", "tools_discovered", "interactive_feedback_called"]
                missing_steps = [step for step in required_steps if not result["steps"].get(step, False)]
                
                if missing_steps:
                    result["success"] = False
                    result["errors"].append(f"缺少必要步驟: {missing_steps}")
            
            return result


class QuickConnectionScenario(TestScenario):
    """快速連接測試場景"""
    
    def __init__(self):
        super().__init__(
            name="quick_connection",
            description="測試 MCP 服務器的快速啟動和連接",
            timeout=30,
            tags=["quick", "connection", "startup"]
        )
    
    async def run(self, client: MCPTestClient) -> Dict[str, Any]:
        """運行快速連接測試"""
        result = {
            "success": False,
            "steps": {},
            "performance": {},
            "errors": []
        }
        
        try:
            start_time = time.time()
            
            # 啟動服務器
            if not await client.start_server():
                result["errors"].append("服務器啟動失敗")
                return result
            result["steps"]["server_started"] = True
            
            # 啟動消息讀取
            read_task = asyncio.create_task(client.read_messages())
            
            try:
                # 初始化連接
                if not await client.initialize():
                    result["errors"].append("初始化失敗")
                    return result
                result["steps"]["initialized"] = True
                
                # 獲取工具列表
                tools = await client.list_tools()
                if not tools:
                    result["errors"].append("工具列表為空")
                    return result
                result["steps"]["tools_discovered"] = True
                
                end_time = time.time()
                result["performance"]["total_time"] = end_time - start_time
                result["performance"]["tools_count"] = len(tools)
                result["success"] = True
                
            finally:
                read_task.cancel()
                try:
                    await read_task
                except asyncio.CancelledError:
                    pass
            
        except Exception as e:
            result["errors"].append(f"測試異常: {str(e)}")
        
        finally:
            await client.cleanup()
        
        return result


class TimeoutHandlingScenario(TestScenario):
    """超時處理測試場景"""
    
    def __init__(self):
        super().__init__(
            name="timeout_handling",
            description="測試超時情況下的處理機制",
            timeout=60,
            tags=["timeout", "error_handling", "resilience"]
        )
    
    async def run(self, client: MCPTestClient) -> Dict[str, Any]:
        """運行超時處理測試"""
        result = {
            "success": False,
            "steps": {},
            "performance": {},
            "errors": []
        }
        
        try:
            # 設置很短的超時時間來觸發超時
            original_timeout = client.config.mcp_timeout
            client.config.mcp_timeout = 5  # 5 秒超時
            
            # 啟動服務器
            if not await client.start_server():
                result["errors"].append("服務器啟動失敗")
                return result
            result["steps"]["server_started"] = True
            
            # 啟動消息讀取
            read_task = asyncio.create_task(client.read_messages())
            
            try:
                # 初始化連接
                if not await client.initialize():
                    result["errors"].append("初始化失敗")
                    return result
                result["steps"]["initialized"] = True
                
                # 嘗試調用互動回饋工具（應該超時）
                feedback_result = await client.call_interactive_feedback(
                    str(Path.cwd()),
                    "超時測試 - 這個調用應該會超時",
                    timeout=10  # 10 秒超時，但 MCP 客戶端設置為 5 秒
                )
                
                # 檢查是否正確處理了超時
                if "error" in feedback_result:
                    result["steps"]["timeout_handled"] = True
                    result["success"] = True
                    debug_log("✅ 超時處理測試成功")
                else:
                    result["errors"].append("未正確處理超時情況")
                
            finally:
                read_task.cancel()
                try:
                    await read_task
                except asyncio.CancelledError:
                    pass
                
                # 恢復原始超時設置
                client.config.mcp_timeout = original_timeout
            
        except Exception as e:
            result["errors"].append(f"測試異常: {str(e)}")
        
        finally:
            await client.cleanup()
        
        return result


class ConcurrentCallsScenario(TestScenario):
    """並發調用測試場景"""
    
    def __init__(self):
        super().__init__(
            name="concurrent_calls",
            description="測試並發 MCP 調用的處理能力",
            timeout=300,
            parallel=True,
            tags=["concurrent", "performance", "stress"]
        )
    
    async def run(self, client: MCPTestClient) -> Dict[str, Any]:
        """運行並發調用測試"""
        result = {
            "success": False,
            "steps": {},
            "performance": {},
            "errors": []
        }
        
        try:
            # 啟動服務器
            if not await client.start_server():
                result["errors"].append("服務器啟動失敗")
                return result
            result["steps"]["server_started"] = True
            
            # 啟動消息讀取
            read_task = asyncio.create_task(client.read_messages())
            
            try:
                # 初始化連接
                if not await client.initialize():
                    result["errors"].append("初始化失敗")
                    return result
                result["steps"]["initialized"] = True
                
                # 並發獲取工具列表
                concurrent_count = 5
                tasks = []
                
                for i in range(concurrent_count):
                    task = asyncio.create_task(client.list_tools())
                    tasks.append(task)
                
                start_time = time.time()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.time()
                
                # 分析結果
                successful_calls = 0
                failed_calls = 0
                
                for i, res in enumerate(results):
                    if isinstance(res, Exception):
                        failed_calls += 1
                        debug_log(f"並發調用 {i+1} 失敗: {res}")
                    elif isinstance(res, list) and len(res) > 0:
                        successful_calls += 1
                    else:
                        failed_calls += 1
                
                result["performance"]["concurrent_count"] = concurrent_count
                result["performance"]["successful_calls"] = successful_calls
                result["performance"]["failed_calls"] = failed_calls
                result["performance"]["total_time"] = end_time - start_time
                result["performance"]["avg_time_per_call"] = (end_time - start_time) / concurrent_count
                
                # 判斷成功條件：至少 80% 的調用成功
                success_rate = successful_calls / concurrent_count
                if success_rate >= 0.8:
                    result["success"] = True
                    result["steps"]["concurrent_calls_handled"] = True
                    debug_log(f"✅ 並發調用測試成功 (成功率: {success_rate:.1%})")
                else:
                    result["errors"].append(f"並發調用成功率過低: {success_rate:.1%}")
                
            finally:
                read_task.cancel()
                try:
                    await read_task
                except asyncio.CancelledError:
                    pass
            
        except Exception as e:
            result["errors"].append(f"測試異常: {str(e)}")
        
        finally:
            await client.cleanup()
        
        return result


class MockTestScenario(TestScenario):
    """模擬測試場景（用於演示）"""

    def __init__(self):
        super().__init__(
            name="mock_test",
            description="模擬測試場景，用於演示測試框架功能",
            timeout=10,
            tags=["mock", "demo", "quick"]
        )

    async def run(self, client: MCPTestClient) -> Dict[str, Any]:
        """運行模擬測試"""
        result = {
            "success": True,
            "steps": {
                "mock_step_1": True,
                "mock_step_2": True,
                "mock_step_3": True
            },
            "performance": {
                "total_duration": 0.5,
                "total_time": 0.5
            },
            "errors": []
        }

        # 模擬一些處理時間
        await asyncio.sleep(0.5)

        debug_log("✅ 模擬測試完成")
        return result


class TestScenarios:
    """測試場景管理器"""

    def __init__(self, config: Optional[TestConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.scenarios: Dict[str, TestScenario] = {}
        self._register_default_scenarios()

    def _register_default_scenarios(self):
        """註冊默認測試場景"""
        scenarios = [
            MockTestScenario(),  # 添加模擬測試場景
            BasicWorkflowScenario(),
            QuickConnectionScenario(),
            TimeoutHandlingScenario(),
            ConcurrentCallsScenario(),
        ]

        for scenario in scenarios:
            self.scenarios[scenario.name] = scenario
    
    def register_scenario(self, scenario: TestScenario):
        """註冊自定義測試場景"""
        self.scenarios[scenario.name] = scenario
    
    def get_scenario(self, name: str) -> Optional[TestScenario]:
        """獲取測試場景"""
        return self.scenarios.get(name)
    
    def list_scenarios(self, tags: Optional[List[str]] = None) -> List[TestScenario]:
        """列出測試場景"""
        scenarios = list(self.scenarios.values())
        
        if tags:
            scenarios = [
                scenario for scenario in scenarios
                if any(tag in scenario.tags for tag in tags)
            ]
        
        return scenarios
    
    async def run_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """運行單個測試場景"""
        scenario = self.get_scenario(scenario_name)
        if not scenario:
            return {
                "success": False,
                "errors": [f"未找到測試場景: {scenario_name}"]
            }
        
        debug_log(f"🧪 運行測試場景: {scenario.name}")
        debug_log(f"   描述: {scenario.description}")
        
        client = MCPTestClient(self.config)
        
        try:
            # 執行設置
            if scenario.setup:
                await scenario.setup()
            
            # 運行測試
            result = await TestUtils.timeout_wrapper(
                scenario.run(client),
                scenario.timeout,
                f"測試場景 '{scenario.name}' 超時"
            )
            
            result["scenario_name"] = scenario.name
            result["scenario_description"] = scenario.description
            
            return result
            
        except Exception as e:
            debug_log(f"❌ 測試場景 '{scenario.name}' 執行失敗: {e}")
            return {
                "success": False,
                "scenario_name": scenario.name,
                "scenario_description": scenario.description,
                "errors": [f"執行異常: {str(e)}"]
            }
        
        finally:
            # 執行清理
            if scenario.teardown:
                try:
                    await scenario.teardown()
                except Exception as e:
                    debug_log(f"⚠️ 測試場景 '{scenario.name}' 清理失敗: {e}")
    
    async def run_all_scenarios(self, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """運行所有測試場景"""
        scenarios = self.list_scenarios(tags)
        
        if not scenarios:
            return {
                "success": False,
                "total_scenarios": 0,
                "passed_scenarios": 0,
                "failed_scenarios": 0,
                "results": [],
                "errors": ["沒有找到匹配的測試場景"]
            }
        
        debug_log(f"🚀 開始運行 {len(scenarios)} 個測試場景...")
        
        results = []
        passed_count = 0
        failed_count = 0
        
        for scenario in scenarios:
            result = await self.run_scenario(scenario.name)
            results.append(result)
            
            if result.get("success", False):
                passed_count += 1
                debug_log(f"✅ {scenario.name}: 通過")
            else:
                failed_count += 1
                debug_log(f"❌ {scenario.name}: 失敗")
        
        overall_success = failed_count == 0
        
        debug_log(f"📊 測試完成: {passed_count}/{len(scenarios)} 通過")
        
        return {
            "success": overall_success,
            "total_scenarios": len(scenarios),
            "passed_scenarios": passed_count,
            "failed_scenarios": failed_count,
            "results": results
        }
