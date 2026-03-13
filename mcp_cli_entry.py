#!/usr/bin/env python3
"""
MCP CLI adapter entrypoint.

Allows `mcp run mcp_cli_entry.py:mcp --transport stdio` to work with src layout.
"""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from mcp_feedback_enhanced.server import mcp


if __name__ == "__main__":
    mcp.run()
