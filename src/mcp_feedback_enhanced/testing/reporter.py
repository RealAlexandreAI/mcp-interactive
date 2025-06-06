#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試報告生成器
==============

生成詳細的 MCP 測試報告，支持多種格式輸出。
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from .config import TestConfig, DEFAULT_CONFIG
from .utils import TestUtils
from .validators import TestValidators, ValidationResult
from ..debug import debug_log


@dataclass
class TestReport:
    """測試報告數據結構"""
    timestamp: str
    duration: float
    total_scenarios: int
    passed_scenarios: int
    failed_scenarios: int
    success_rate: float
    scenarios: List[Dict[str, Any]]
    validation_summary: Dict[str, Any]
    performance_summary: Dict[str, Any]
    system_info: Dict[str, Any]
    config: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class TestReporter:
    """測試報告生成器"""
    
    def __init__(self, config: Optional[TestConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.validators = TestValidators(config)
    
    def generate_report(self, test_results: Dict[str, Any]) -> TestReport:
        """生成測試報告"""
        start_time = time.time()
        
        # 提取基本信息
        scenarios = test_results.get("results", [])
        total_scenarios = test_results.get("total_scenarios", len(scenarios))
        passed_scenarios = test_results.get("passed_scenarios", 0)
        failed_scenarios = test_results.get("failed_scenarios", 0)
        
        # 計算成功率
        success_rate = passed_scenarios / total_scenarios if total_scenarios > 0 else 0
        
        # 驗證測試結果
        validation_results = {}
        for i, scenario in enumerate(scenarios):
            validation_results[f"scenario_{i}"] = self.validators.result_validator.validate_test_result(scenario)
        
        validation_summary = self.validators.get_validation_summary(validation_results)
        
        # 生成性能摘要
        performance_summary = self._generate_performance_summary(scenarios)
        
        # 收集錯誤和警告
        all_errors = []
        all_warnings = []
        
        for scenario in scenarios:
            all_errors.extend(scenario.get("errors", []))
        
        # 計算總持續時間
        total_duration = 0
        for scenario in scenarios:
            perf = scenario.get("performance", {})
            duration = perf.get("total_duration", 0) or perf.get("total_time", 0)
            total_duration += duration
        
        # 創建報告
        report = TestReport(
            timestamp=datetime.now().isoformat(),
            duration=total_duration,
            total_scenarios=total_scenarios,
            passed_scenarios=passed_scenarios,
            failed_scenarios=failed_scenarios,
            success_rate=success_rate,
            scenarios=scenarios,
            validation_summary=validation_summary,
            performance_summary=performance_summary,
            system_info=TestUtils.get_system_info(),
            config=self.config.to_dict(),
            errors=all_errors,
            warnings=all_warnings
        )
        
        debug_log(f"📊 測試報告生成完成 (耗時: {time.time() - start_time:.2f}s)")
        return report
    
    def _generate_performance_summary(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成性能摘要"""
        total_duration = 0
        min_duration = float('inf')
        max_duration = 0
        durations = []
        
        memory_usage = []
        
        for scenario in scenarios:
            perf = scenario.get("performance", {})
            
            # 處理持續時間
            duration = perf.get("total_duration", 0) or perf.get("total_time", 0)
            if duration > 0:
                total_duration += duration
                min_duration = min(min_duration, duration)
                max_duration = max(max_duration, duration)
                durations.append(duration)
            
            # 處理內存使用
            memory_diff = perf.get("memory_diff", {})
            if memory_diff:
                memory_usage.append(memory_diff)
        
        # 計算平均值
        avg_duration = total_duration / len(durations) if durations else 0
        
        # 計算中位數
        if durations:
            sorted_durations = sorted(durations)
            n = len(sorted_durations)
            median_duration = (
                sorted_durations[n // 2] if n % 2 == 1
                else (sorted_durations[n // 2 - 1] + sorted_durations[n // 2]) / 2
            )
        else:
            median_duration = 0
        
        return {
            "total_duration": total_duration,
            "total_duration_formatted": TestUtils.format_duration(total_duration),
            "avg_duration": avg_duration,
            "avg_duration_formatted": TestUtils.format_duration(avg_duration),
            "median_duration": median_duration,
            "median_duration_formatted": TestUtils.format_duration(median_duration),
            "min_duration": min_duration if min_duration != float('inf') else 0,
            "min_duration_formatted": TestUtils.format_duration(min_duration if min_duration != float('inf') else 0),
            "max_duration": max_duration,
            "max_duration_formatted": TestUtils.format_duration(max_duration),
            "scenarios_with_performance": len(durations),
            "memory_usage_samples": len(memory_usage)
        }
    
    def save_report(self, report: TestReport, output_path: Optional[Path] = None) -> Path:
        """保存測試報告"""
        if output_path is None:
            output_dir = self.config.ensure_report_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mcp_test_report_{timestamp}.{self.config.report_format}"
            output_path = output_dir / filename
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.config.report_format.lower() == "json":
            self._save_json_report(report, output_path)
        elif self.config.report_format.lower() == "html":
            self._save_html_report(report, output_path)
        elif self.config.report_format.lower() == "markdown":
            self._save_markdown_report(report, output_path)
        else:
            raise ValueError(f"不支持的報告格式: {self.config.report_format}")
        
        debug_log(f"📄 測試報告已保存: {output_path}")
        return output_path
    
    def _save_json_report(self, report: TestReport, output_path: Path):
        """保存 JSON 格式報告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False, default=str)
    
    def _save_html_report(self, report: TestReport, output_path: Path):
        """保存 HTML 格式報告"""
        html_content = self._generate_html_report(report)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _save_markdown_report(self, report: TestReport, output_path: Path):
        """保存 Markdown 格式報告"""
        markdown_content = self._generate_markdown_report(report)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    
    def _generate_html_report(self, report: TestReport) -> str:
        """生成 HTML 報告"""
        # 狀態圖標
        status_icon = "✅" if report.success_rate == 1.0 else "❌" if report.success_rate == 0 else "⚠️"
        
        # 性能圖表數據（簡化版）
        scenario_names = [s.get("scenario_name", f"Scenario {i}") for i, s in enumerate(report.scenarios)]
        scenario_durations = []
        for s in report.scenarios:
            perf = s.get("performance", {})
            duration = perf.get("total_duration", 0) or perf.get("total_time", 0)
            scenario_durations.append(duration)
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP 測試報告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .status {{ font-size: 24px; margin: 10px 0; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .error {{ color: #dc3545; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #007bff; }}
        .card h3 {{ margin: 0 0 10px 0; color: #333; }}
        .card .value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .scenarios {{ margin: 20px 0; }}
        .scenario {{ background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 6px; border-left: 4px solid #28a745; }}
        .scenario.failed {{ border-left-color: #dc3545; }}
        .scenario h4 {{ margin: 0 0 10px 0; }}
        .scenario-details {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px; }}
        .errors {{ background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px; margin: 10px 0; }}
        .performance {{ margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 MCP 測試報告</h1>
            <div class="status {'success' if report.success_rate == 1.0 else 'warning' if report.success_rate > 0 else 'error'}">
                {status_icon} 測試完成
            </div>
            <p>生成時間: {report.timestamp}</p>
        </div>
        
        <div class="summary">
            <div class="card">
                <h3>總測試數</h3>
                <div class="value">{report.total_scenarios}</div>
            </div>
            <div class="card">
                <h3>通過測試</h3>
                <div class="value" style="color: #28a745;">{report.passed_scenarios}</div>
            </div>
            <div class="card">
                <h3>失敗測試</h3>
                <div class="value" style="color: #dc3545;">{report.failed_scenarios}</div>
            </div>
            <div class="card">
                <h3>成功率</h3>
                <div class="value">{report.success_rate:.1%}</div>
            </div>
            <div class="card">
                <h3>總耗時</h3>
                <div class="value">{report.performance_summary.get('total_duration_formatted', 'N/A')}</div>
            </div>
            <div class="card">
                <h3>平均耗時</h3>
                <div class="value">{report.performance_summary.get('avg_duration_formatted', 'N/A')}</div>
            </div>
        </div>
        
        <div class="scenarios">
            <h2>📋 測試場景詳情</h2>
"""
        
        for i, scenario in enumerate(report.scenarios):
            success = scenario.get("success", False)
            scenario_name = scenario.get("scenario_name", f"Scenario {i+1}")
            scenario_desc = scenario.get("scenario_description", "無描述")
            
            perf = scenario.get("performance", {})
            duration = perf.get("total_duration", 0) or perf.get("total_time", 0)
            duration_str = TestUtils.format_duration(duration) if duration > 0 else "N/A"
            
            steps = scenario.get("steps", {})
            completed_steps = sum(1 for v in steps.values() if v)
            total_steps = len(steps)
            
            errors = scenario.get("errors", [])
            
            html += f"""
            <div class="scenario {'failed' if not success else ''}">
                <h4>{'✅' if success else '❌'} {scenario_name}</h4>
                <p>{scenario_desc}</p>
                <div class="scenario-details">
                    <div><strong>狀態:</strong> {'通過' if success else '失敗'}</div>
                    <div><strong>耗時:</strong> {duration_str}</div>
                    <div><strong>完成步驟:</strong> {completed_steps}/{total_steps}</div>
                    <div><strong>錯誤數:</strong> {len(errors)}</div>
                </div>
"""
            
            if errors:
                html += '<div class="errors"><strong>錯誤信息:</strong><ul>'
                for error in errors:
                    html += f'<li>{error}</li>'
                html += '</ul></div>'
            
            html += '</div>'
        
        html += f"""
        </div>
        
        <div class="performance">
            <h2>📊 性能統計</h2>
            <div class="summary">
                <div class="card">
                    <h3>最快測試</h3>
                    <div class="value">{report.performance_summary.get('min_duration_formatted', 'N/A')}</div>
                </div>
                <div class="card">
                    <h3>最慢測試</h3>
                    <div class="value">{report.performance_summary.get('max_duration_formatted', 'N/A')}</div>
                </div>
                <div class="card">
                    <h3>中位數</h3>
                    <div class="value">{report.performance_summary.get('median_duration_formatted', 'N/A')}</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>MCP Feedback Enhanced 測試框架 | 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_markdown_report(self, report: TestReport) -> str:
        """生成 Markdown 報告"""
        status_icon = "✅" if report.success_rate == 1.0 else "❌" if report.success_rate == 0 else "⚠️"
        
        md = f"""# 🧪 MCP 測試報告

{status_icon} **測試狀態**: {'全部通過' if report.success_rate == 1.0 else '部分失敗' if report.success_rate > 0 else '全部失敗'}

**生成時間**: {report.timestamp}

## 📊 測試摘要

| 指標 | 數值 |
|------|------|
| 總測試數 | {report.total_scenarios} |
| 通過測試 | {report.passed_scenarios} |
| 失敗測試 | {report.failed_scenarios} |
| 成功率 | {report.success_rate:.1%} |
| 總耗時 | {report.performance_summary.get('total_duration_formatted', 'N/A')} |
| 平均耗時 | {report.performance_summary.get('avg_duration_formatted', 'N/A')} |

## 📋 測試場景詳情

"""
        
        for i, scenario in enumerate(report.scenarios):
            success = scenario.get("success", False)
            scenario_name = scenario.get("scenario_name", f"Scenario {i+1}")
            scenario_desc = scenario.get("scenario_description", "無描述")
            
            perf = scenario.get("performance", {})
            duration = perf.get("total_duration", 0) or perf.get("total_time", 0)
            duration_str = TestUtils.format_duration(duration) if duration > 0 else "N/A"
            
            steps = scenario.get("steps", {})
            completed_steps = sum(1 for v in steps.values() if v)
            total_steps = len(steps)
            
            errors = scenario.get("errors", [])
            
            md += f"""### {'✅' if success else '❌'} {scenario_name}

**描述**: {scenario_desc}

- **狀態**: {'通過' if success else '失敗'}
- **耗時**: {duration_str}
- **完成步驟**: {completed_steps}/{total_steps}
- **錯誤數**: {len(errors)}

"""
            
            if errors:
                md += "**錯誤信息**:\n"
                for error in errors:
                    md += f"- {error}\n"
                md += "\n"
        
        md += f"""## 📊 性能統計

| 指標 | 數值 |
|------|------|
| 最快測試 | {report.performance_summary.get('min_duration_formatted', 'N/A')} |
| 最慢測試 | {report.performance_summary.get('max_duration_formatted', 'N/A')} |
| 中位數 | {report.performance_summary.get('median_duration_formatted', 'N/A')} |

## 🔧 系統信息

| 項目 | 值 |
|------|---|
| CPU 核心數 | {report.system_info.get('cpu_count', 'N/A')} |
| 總內存 | {report.system_info.get('memory_total', 'N/A')} |
| 可用內存 | {report.system_info.get('memory_available', 'N/A')} |

---

*報告由 MCP Feedback Enhanced 測試框架生成 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return md
    
    def print_summary(self, report: TestReport):
        """打印測試摘要到控制台"""
        status_icon = "✅" if report.success_rate == 1.0 else "❌" if report.success_rate == 0 else "⚠️"
        
        print("\n" + "="*60)
        print(f"🧪 MCP 測試報告摘要 {status_icon}")
        print("="*60)
        print(f"📊 總測試數: {report.total_scenarios}")
        print(f"✅ 通過測試: {report.passed_scenarios}")
        print(f"❌ 失敗測試: {report.failed_scenarios}")
        print(f"📈 成功率: {report.success_rate:.1%}")
        print(f"⏱️  總耗時: {report.performance_summary.get('total_duration_formatted', 'N/A')}")
        print(f"⚡ 平均耗時: {report.performance_summary.get('avg_duration_formatted', 'N/A')}")
        
        if report.errors:
            print(f"\n❌ 發現 {len(report.errors)} 個錯誤:")
            for error in report.errors[:5]:  # 只顯示前5個錯誤
                print(f"   • {error}")
            if len(report.errors) > 5:
                print(f"   ... 還有 {len(report.errors) - 5} 個錯誤")
        
        print("="*60)
