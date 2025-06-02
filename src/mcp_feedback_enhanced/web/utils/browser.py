#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瀏覽器工具函數
==============

提供瀏覽器相關的工具函數。
"""

import webbrowser
from typing import Callable


def get_browser_opener() -> Callable[[str], None]:
    """
    獲取瀏覽器開啟函數
    
    Returns:
        Callable: 瀏覽器開啟函數
    """
    return webbrowser.open 