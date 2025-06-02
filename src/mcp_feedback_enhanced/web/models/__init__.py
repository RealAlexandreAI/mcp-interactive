#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web UI 資料模型模組
==================

定義 Web UI 相關的資料結構和型別。
"""

from .feedback_session import WebFeedbackSession
from .feedback_result import FeedbackResult

__all__ = [
    'WebFeedbackSession',
    'FeedbackResult'
] 