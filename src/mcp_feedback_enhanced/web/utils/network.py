#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
網絡工具函數
============

提供網絡相關的工具函數，如端口檢測等。
"""

import socket
from typing import Optional


def find_free_port(start_port: int = 8765, max_attempts: int = 100) -> int:
    """
    尋找可用的端口
    
    Args:
        start_port: 起始端口號
        max_attempts: 最大嘗試次數
        
    Returns:
        int: 可用的端口號
        
    Raises:
        RuntimeError: 如果找不到可用端口
    """
    for i in range(max_attempts):
        port = start_port + i
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"無法在 {start_port}-{start_port + max_attempts - 1} 範圍內找到可用端口")


def is_port_available(host: str, port: int) -> bool:
    """
    檢查端口是否可用
    
    Args:
        host: 主機地址
        port: 端口號
        
    Returns:
        bool: 端口是否可用
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
            return True
    except OSError:
        return False 