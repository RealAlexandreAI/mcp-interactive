#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回饋結果資料模型
===============

定義回饋收集的資料結構。
"""

from typing import TypedDict, List


class FeedbackResult(TypedDict):
    """回饋結果的型別定義"""
    command_logs: str
    interactive_feedback: str
    images: List[dict] 