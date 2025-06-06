#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試結果驗證器
==============

驗證 MCP 測試結果是否符合規範和預期。
"""

import json
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path

from .config import TestConfig, DEFAULT_CONFIG
from .utils import TestUtils
from ..debug import debug_log


@dataclass
class ValidationResult:
    """驗證結果"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]
    
    def add_error(self, message: str):
        """添加錯誤"""
        self.errors.append(message)
        self.valid = False
    
    def add_warning(self, message: str):
        """添加警告"""
        self.warnings.append(message)
    
    def add_detail(self, key: str, value: Any):
        """添加詳細信息"""
        self.details[key] = value


class MCPMessageValidator:
    """MCP 消息驗證器"""
    
    @staticmethod
    def validate_json_rpc(message: Dict[str, Any]) -> ValidationResult:
        """驗證 JSON-RPC 2.0 格式"""
        result = ValidationResult(True, [], [], {})
        
        # 檢查必需字段
        if "jsonrpc" not in message:
            result.add_error("缺少 'jsonrpc' 字段")
        elif message["jsonrpc"] != "2.0":
            result.add_error(f"無效的 jsonrpc 版本: {message['jsonrpc']}")
        
        # 檢查消息類型
        is_request = "method" in message
        is_response = "result" in message or "error" in message
        is_notification = is_request and "id" not in message
        
        if not (is_request or is_response):
            result.add_error("消息既不是請求也不是響應")
        
        if is_request and is_response:
            result.add_error("消息不能同時是請求和響應")
        
        # 驗證請求格式
        if is_request:
            if not isinstance(message.get("method"), str):
                result.add_error("method 字段必須是字符串")
            
            if not is_notification and "id" not in message:
                result.add_error("非通知請求必須包含 id 字段")
        
        # 驗證響應格式
        if is_response:
            if "id" not in message:
                result.add_error("響應必須包含 id 字段")
            
            if "result" in message and "error" in message:
                result.add_error("響應不能同時包含 result 和 error")
            
            if "result" not in message and "error" not in message:
                result.add_error("響應必須包含 result 或 error")
        
        # 驗證錯誤格式
        if "error" in message:
            error = message["error"]
            if not isinstance(error, dict):
                result.add_error("error 字段必須是對象")
            else:
                if "code" not in error:
                    result.add_error("error 對象必須包含 code 字段")
                elif not isinstance(error["code"], int):
                    result.add_error("error.code 必須是整數")
                
                if "message" not in error:
                    result.add_error("error 對象必須包含 message 字段")
                elif not isinstance(error["message"], str):
                    result.add_error("error.message 必須是字符串")
        
        result.add_detail("message_type", "request" if is_request else "response")
        result.add_detail("is_notification", is_notification)
        
        return result
    
    @staticmethod
    def validate_mcp_initialize(message: Dict[str, Any]) -> ValidationResult:
        """驗證 MCP 初始化消息"""
        result = ValidationResult(True, [], [], {})
        
        # 先驗證 JSON-RPC 格式
        json_rpc_result = MCPMessageValidator.validate_json_rpc(message)
        result.errors.extend(json_rpc_result.errors)
        result.warnings.extend(json_rpc_result.warnings)
        
        if not json_rpc_result.valid:
            result.valid = False
            return result
        
        # 驗證初始化特定字段
        if message.get("method") == "initialize":
            params = message.get("params", {})
            
            if "protocolVersion" not in params:
                result.add_error("初始化請求必須包含 protocolVersion")
            
            if "clientInfo" not in params:
                result.add_error("初始化請求必須包含 clientInfo")
            else:
                client_info = params["clientInfo"]
                if not isinstance(client_info, dict):
                    result.add_error("clientInfo 必須是對象")
                else:
                    if "name" not in client_info:
                        result.add_error("clientInfo 必須包含 name")
                    if "version" not in client_info:
                        result.add_error("clientInfo 必須包含 version")
        
        elif "result" in message:
            # 驗證初始化響應
            result_data = message.get("result", {})
            
            if "serverInfo" not in result_data:
                result.add_warning("初始化響應建議包含 serverInfo")
            
            if "capabilities" not in result_data:
                result.add_warning("初始化響應建議包含 capabilities")
        
        return result
    
    @staticmethod
    def validate_tools_list(message: Dict[str, Any]) -> ValidationResult:
        """驗證工具列表消息"""
        result = ValidationResult(True, [], [], {})
        
        # 先驗證 JSON-RPC 格式
        json_rpc_result = MCPMessageValidator.validate_json_rpc(message)
        result.errors.extend(json_rpc_result.errors)
        result.warnings.extend(json_rpc_result.warnings)
        
        if not json_rpc_result.valid:
            result.valid = False
            return result
        
        # 驗證工具列表響應
        if "result" in message:
            result_data = message.get("result", {})
            
            if "tools" not in result_data:
                result.add_error("工具列表響應必須包含 tools 字段")
            else:
                tools = result_data["tools"]
                if not isinstance(tools, list):
                    result.add_error("tools 字段必須是數組")
                else:
                    for i, tool in enumerate(tools):
                        if not isinstance(tool, dict):
                            result.add_error(f"工具 {i} 必須是對象")
                            continue
                        
                        if "name" not in tool:
                            result.add_error(f"工具 {i} 必須包含 name 字段")
                        
                        if "description" not in tool:
                            result.add_warning(f"工具 {i} 建議包含 description 字段")
                        
                        if "inputSchema" not in tool:
                            result.add_warning(f"工具 {i} 建議包含 inputSchema 字段")
                
                result.add_detail("tools_count", len(tools))
        
        return result


class TestResultValidator:
    """測試結果驗證器"""
    
    def __init__(self, config: Optional[TestConfig] = None):
        self.config = config or DEFAULT_CONFIG
    
    def validate_test_result(self, test_result: Dict[str, Any]) -> ValidationResult:
        """驗證測試結果"""
        result = ValidationResult(True, [], [], {})
        
        # 檢查必需字段
        required_fields = ["success", "steps", "performance", "errors"]
        for field in required_fields:
            if field not in test_result:
                result.add_error(f"測試結果缺少必需字段: {field}")
        
        # 驗證成功標誌
        if "success" in test_result:
            if not isinstance(test_result["success"], bool):
                result.add_error("success 字段必須是布爾值")
        
        # 驗證步驟信息
        if "steps" in test_result:
            steps = test_result["steps"]
            if not isinstance(steps, dict):
                result.add_error("steps 字段必須是對象")
            else:
                result.add_detail("completed_steps", list(steps.keys()))
                result.add_detail("steps_count", len(steps))
        
        # 驗證錯誤信息
        if "errors" in test_result:
            errors = test_result["errors"]
            if not isinstance(errors, list):
                result.add_error("errors 字段必須是數組")
            else:
                result.add_detail("error_count", len(errors))
                if len(errors) > 0 and test_result.get("success", False):
                    result.add_warning("測試標記為成功但包含錯誤信息")
        
        # 驗證性能數據
        if "performance" in test_result:
            performance = test_result["performance"]
            if not isinstance(performance, dict):
                result.add_error("performance 字段必須是對象")
            else:
                self._validate_performance_data(performance, result)
        
        return result
    
    def _validate_performance_data(self, performance: Dict[str, Any], result: ValidationResult):
        """驗證性能數據"""
        # 檢查時間相關字段
        time_fields = ["total_duration", "total_time"]
        for field in time_fields:
            if field in performance:
                value = performance[field]
                if not isinstance(value, (int, float)):
                    result.add_error(f"性能字段 {field} 必須是數字")
                elif value < 0:
                    result.add_error(f"性能字段 {field} 不能為負數")
                elif value > self.config.test_timeout:
                    result.add_warning(f"性能字段 {field} 超過測試超時時間")
        
        # 檢查內存相關字段
        memory_fields = ["memory_start", "memory_end", "memory_diff"]
        for field in memory_fields:
            if field in performance:
                value = performance[field]
                if not isinstance(value, dict):
                    result.add_warning(f"性能字段 {field} 應該是對象")
        
        # 檢查檢查點數據
        if "checkpoints" in performance:
            checkpoints = performance["checkpoints"]
            if not isinstance(checkpoints, list):
                result.add_error("checkpoints 字段必須是數組")
            else:
                result.add_detail("checkpoints_count", len(checkpoints))
    
    def validate_interactive_feedback_result(self, feedback_result: Dict[str, Any]) -> ValidationResult:
        """驗證互動回饋結果"""
        result = ValidationResult(True, [], [], {})
        
        # 檢查是否有錯誤
        if "error" in feedback_result:
            result.add_detail("has_error", True)
            result.add_detail("error_message", feedback_result["error"])
            return result
        
        # 檢查預期字段
        expected_fields = ["command_logs", "interactive_feedback", "images"]
        for field in expected_fields:
            if field not in feedback_result:
                result.add_warning(f"互動回饋結果建議包含 {field} 字段")
        
        # 驗證命令日誌
        if "command_logs" in feedback_result:
            logs = feedback_result["command_logs"]
            if not isinstance(logs, str):
                result.add_error("command_logs 字段必須是字符串")
        
        # 驗證互動回饋
        if "interactive_feedback" in feedback_result:
            feedback = feedback_result["interactive_feedback"]
            if not isinstance(feedback, str):
                result.add_error("interactive_feedback 字段必須是字符串")
            elif len(feedback.strip()) == 0:
                result.add_warning("interactive_feedback 為空")
        
        # 驗證圖片數據
        if "images" in feedback_result:
            images = feedback_result["images"]
            if not isinstance(images, list):
                result.add_error("images 字段必須是數組")
            else:
                result.add_detail("images_count", len(images))
                for i, image in enumerate(images):
                    if not isinstance(image, dict):
                        result.add_error(f"圖片 {i} 必須是對象")
                        continue
                    
                    if "data" not in image:
                        result.add_error(f"圖片 {i} 必須包含 data 字段")
                    
                    if "media_type" not in image:
                        result.add_error(f"圖片 {i} 必須包含 media_type 字段")
        
        return result


class TestValidators:
    """測試驗證器集合"""
    
    def __init__(self, config: Optional[TestConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.message_validator = MCPMessageValidator()
        self.result_validator = TestResultValidator(config)
    
    def validate_all(self, test_data: Dict[str, Any]) -> Dict[str, ValidationResult]:
        """驗證所有測試數據"""
        results = {}
        
        # 驗證測試結果
        if "test_result" in test_data:
            results["test_result"] = self.result_validator.validate_test_result(
                test_data["test_result"]
            )
        
        # 驗證 MCP 消息
        if "mcp_messages" in test_data:
            message_results = []
            for i, message in enumerate(test_data["mcp_messages"]):
                msg_result = self.message_validator.validate_json_rpc(message)
                msg_result.add_detail("message_index", i)
                message_results.append(msg_result)
            results["mcp_messages"] = message_results
        
        # 驗證互動回饋結果
        if "feedback_result" in test_data:
            results["feedback_result"] = self.result_validator.validate_interactive_feedback_result(
                test_data["feedback_result"]
            )
        
        return results
    
    def get_validation_summary(self, validation_results: Dict[str, ValidationResult]) -> Dict[str, Any]:
        """獲取驗證摘要"""
        total_errors = 0
        total_warnings = 0
        valid_count = 0
        total_count = 0
        
        for key, result in validation_results.items():
            if isinstance(result, list):
                # 處理消息列表
                for msg_result in result:
                    total_errors += len(msg_result.errors)
                    total_warnings += len(msg_result.warnings)
                    if msg_result.valid:
                        valid_count += 1
                    total_count += 1
            else:
                # 處理單個結果
                total_errors += len(result.errors)
                total_warnings += len(result.warnings)
                if result.valid:
                    valid_count += 1
                total_count += 1
        
        return {
            "total_validations": total_count,
            "valid_count": valid_count,
            "invalid_count": total_count - valid_count,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "success_rate": valid_count / total_count if total_count > 0 else 0
        }
