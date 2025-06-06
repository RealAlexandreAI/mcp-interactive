#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 增強測試系統
================

完整的 MCP 測試框架，模擬真實的 Cursor IDE 調用場景。

主要功能：
- 真實 MCP 調用模擬
- 完整的回饋循環測試
- 多場景測試覆蓋
- 詳細的測試報告

使用方法：
    python -m mcp_feedback_enhanced.test_mcp_enhanced
    python -m mcp_feedback_enhanced.test_mcp_enhanced --scenario basic_workflow
    python -m mcp_feedback_enhanced.test_mcp_enhanced --tags quick
"""

import asyncio
import argparse
import sys
import os
from typing import List, Optional
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from .testing import TestScenarios, TestReporter, TestConfig, DEFAULT_CONFIG
from .debug import debug_log


class MCPTestRunner:
    """MCP 測試運行器"""
    
    def __init__(self, config: Optional[TestConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.scenarios = TestScenarios(self.config)
        self.reporter = TestReporter(self.config)
    
    async def run_single_scenario(self, scenario_name: str) -> bool:
        """運行單個測試場景"""
        debug_log(f"🎯 運行單個測試場景: {scenario_name}")
        
        result = await self.scenarios.run_scenario(scenario_name)
        
        # 生成報告
        test_results = {
            "success": result.get("success", False),
            "total_scenarios": 1,
            "passed_scenarios": 1 if result.get("success", False) else 0,
            "failed_scenarios": 0 if result.get("success", False) else 1,
            "results": [result]
        }
        
        report = self.reporter.generate_report(test_results)
        self.reporter.print_summary(report)
        
        # 保存報告
        if self.config.report_output_dir:
            report_path = self.reporter.save_report(report)
            debug_log(f"📄 詳細報告已保存: {report_path}")
        
        return result.get("success", False)
    
    async def run_scenarios_by_tags(self, tags: List[str]) -> bool:
        """根據標籤運行測試場景"""
        debug_log(f"🏷️  運行標籤測試: {', '.join(tags)}")
        
        results = await self.scenarios.run_all_scenarios(tags)
        
        # 生成報告
        report = self.reporter.generate_report(results)
        self.reporter.print_summary(report)
        
        # 保存報告
        if self.config.report_output_dir:
            report_path = self.reporter.save_report(report)
            debug_log(f"📄 詳細報告已保存: {report_path}")
        
        return results.get("success", False)
    
    async def run_all_scenarios(self) -> bool:
        """運行所有測試場景"""
        debug_log("🚀 運行所有測試場景")
        
        results = await self.scenarios.run_all_scenarios()
        
        # 生成報告
        report = self.reporter.generate_report(results)
        self.reporter.print_summary(report)
        
        # 保存報告
        if self.config.report_output_dir:
            report_path = self.reporter.save_report(report)
            debug_log(f"📄 詳細報告已保存: {report_path}")
        
        return results.get("success", False)
    
    def list_scenarios(self, tags: Optional[List[str]] = None):
        """列出可用的測試場景"""
        scenarios = self.scenarios.list_scenarios(tags)
        
        print("\n📋 可用的測試場景:")
        print("=" * 50)
        
        for scenario in scenarios:
            tags_str = f" [{', '.join(scenario.tags)}]" if scenario.tags else ""
            print(f"🧪 {scenario.name}{tags_str}")
            print(f"   {scenario.description}")
            print(f"   超時: {scenario.timeout}s")
            print()
        
        print(f"總計: {len(scenarios)} 個測試場景")


def create_config_from_args(args) -> TestConfig:
    """從命令行參數創建配置"""
    config = TestConfig.from_env()
    
    # 覆蓋命令行參數
    if args.timeout:
        config.test_timeout = args.timeout
    
    if args.verbose is not None:
        config.test_verbose = args.verbose
    
    if args.debug:
        config.test_debug = True
        os.environ["MCP_DEBUG"] = "true"
    
    if args.report_format:
        config.report_format = args.report_format
    
    if args.report_dir:
        config.report_output_dir = args.report_dir
    
    if args.project_dir:
        config.test_project_dir = args.project_dir
    
    return config


async def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="MCP 增強測試系統",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s                                    # 運行所有測試
  %(prog)s --scenario basic_workflow          # 運行特定場景
  %(prog)s --tags quick                       # 運行快速測試
  %(prog)s --tags basic,integration           # 運行多個標籤
  %(prog)s --list                             # 列出所有場景
  %(prog)s --debug --verbose                  # 調試模式
        """
    )
    
    # 測試選項
    parser.add_argument(
        '--scenario', 
        help='運行特定的測試場景'
    )
    parser.add_argument(
        '--tags', 
        help='根據標籤運行測試場景 (逗號分隔)'
    )
    parser.add_argument(
        '--list', 
        action='store_true',
        help='列出所有可用的測試場景'
    )
    
    # 配置選項
    parser.add_argument(
        '--timeout', 
        type=int,
        help='測試超時時間 (秒)'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='詳細輸出'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='調試模式'
    )
    parser.add_argument(
        '--project-dir',
        help='測試項目目錄'
    )
    
    # 報告選項
    parser.add_argument(
        '--report-format',
        choices=['html', 'json', 'markdown'],
        help='報告格式'
    )
    parser.add_argument(
        '--report-dir',
        help='報告輸出目錄'
    )
    
    args = parser.parse_args()
    
    # 創建配置
    config = create_config_from_args(args)
    
    # 創建測試運行器
    runner = MCPTestRunner(config)
    
    try:
        if args.list:
            # 列出測試場景
            tags = args.tags.split(',') if args.tags else None
            runner.list_scenarios(tags)
            return
        
        success = False
        
        if args.scenario:
            # 運行特定場景
            success = await runner.run_single_scenario(args.scenario)
        elif args.tags:
            # 根據標籤運行
            tags = [tag.strip() for tag in args.tags.split(',')]
            success = await runner.run_scenarios_by_tags(tags)
        else:
            # 運行所有場景
            success = await runner.run_all_scenarios()
        
        if success:
            debug_log("🎉 所有測試通過！")
            sys.exit(0)
        else:
            debug_log("❌ 部分測試失敗")
            sys.exit(1)
    
    except KeyboardInterrupt:
        debug_log("\n⚠️ 測試被用戶中斷")
        sys.exit(130)
    except Exception as e:
        debug_log(f"❌ 測試執行失敗: {e}")
        if config.test_debug:
            import traceback
            debug_log(f"詳細錯誤: {traceback.format_exc()}")
        sys.exit(1)


def run_quick_test():
    """快速測試入口"""
    os.environ["MCP_DEBUG"] = "true"
    
    # 設置快速測試配置
    config = TestConfig.from_env()
    config.test_timeout = 60
    config.report_format = "markdown"
    
    async def quick_test():
        runner = MCPTestRunner(config)
        return await runner.run_scenarios_by_tags(["quick"])
    
    return asyncio.run(quick_test())


def run_basic_workflow_test():
    """基礎工作流程測試入口"""
    os.environ["MCP_DEBUG"] = "true"
    
    config = TestConfig.from_env()
    config.test_timeout = 180
    
    async def workflow_test():
        runner = MCPTestRunner(config)
        return await runner.run_single_scenario("basic_workflow")
    
    return asyncio.run(workflow_test())


if __name__ == "__main__":
    asyncio.run(main())
