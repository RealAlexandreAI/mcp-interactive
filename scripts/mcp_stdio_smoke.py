#!/usr/bin/env python3
"""
MCP stdio smoke test.

Validates a minimal JSON-RPC flow against the local MCP server:
initialize -> tools/list -> tools/call(interactive_feedback)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


async def _read_jsonrpc_response(
    stdout: Any, timeout_seconds: float
) -> dict[str, Any] | list[Any] | None:
    """Read next JSON-RPC response and skip notifications/log lines."""
    deadline = time.monotonic() + timeout_seconds

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Timed out waiting for JSON-RPC response")

        raw_line = await asyncio.wait_for(
            asyncio.to_thread(stdout.readline), timeout=remaining
        )
        if not raw_line:
            return None

        line = raw_line.strip()
        if not line:
            continue

        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            # Some runtimes print plain log lines to stdout; ignore and continue.
            continue

        if isinstance(payload, dict) and "id" not in payload and "method" in payload:
            # Notification, not a response to our request.
            continue

        if isinstance(payload, dict):
            return dict(payload)
        if isinstance(payload, list):
            return payload
        return None


def _require_result(response: dict[str, Any] | list[Any] | None, step: str) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise RuntimeError(f"{step} returned non-dict response: {response!r}")
    if "error" in response:
        raise RuntimeError(f"{step} returned error: {response['error']!r}")
    if "result" not in response:
        raise RuntimeError(f"{step} missing result field: {response!r}")
    return response


async def run_smoke_test(project_directory: Path, call_timeout: int) -> int:
    cmd = [
        "uv",
        "run",
        "mcp",
        "run",
        "mcp_cli_entry.py:mcp",
        "--transport",
        "stdio",
    ]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=project_directory,
        bufsize=0,
    )

    try:
        if process.stdin is None or process.stdout is None:
            raise RuntimeError("Failed to open subprocess stdio")

        initialize = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": True}, "sampling": {}},
                "clientInfo": {"name": "mcp-stdio-smoke", "version": "1.0.0"},
            },
        }
        process.stdin.write(json.dumps(initialize) + "\n")
        process.stdin.flush()
        init_response = _require_result(
            await _read_jsonrpc_response(process.stdout, timeout_seconds=20),
            "initialize",
        )
        print("PASS initialize")

        tools_list = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
        process.stdin.write(json.dumps(tools_list) + "\n")
        process.stdin.flush()
        tools_response = _require_result(
            await _read_jsonrpc_response(process.stdout, timeout_seconds=20),
            "tools/list",
        )
        tools = tools_response["result"].get("tools", [])
        has_interactive_feedback = any(
            isinstance(tool, dict) and tool.get("name") == "interactive_feedback"
            for tool in tools
        )
        if not has_interactive_feedback:
            raise RuntimeError("tools/list missing interactive_feedback")
        print("PASS tools/list")

        call_interactive_feedback = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "interactive_feedback",
                "arguments": {
                    "project_directory": str(project_directory),
                    "summary": "stdio smoke test",
                    "timeout": call_timeout,
                },
            },
        }
        process.stdin.write(json.dumps(call_interactive_feedback) + "\n")
        process.stdin.flush()
        _require_result(
            await _read_jsonrpc_response(
                process.stdout, timeout_seconds=max(30, call_timeout + 15)
            ),
            "tools/call interactive_feedback",
        )
        print("PASS tools/call interactive_feedback")

        server_info = init_response.get("result", {}).get("serverInfo", {})
        if server_info:
            print(f"Server: {server_info.get('name', 'unknown')} {server_info.get('version', '')}".strip())
        print("Smoke test passed.")
        return 0

    except Exception as exc:
        stderr_tail = ""
        if process.stderr is not None:
            try:
                stderr_tail = process.stderr.read(1000).strip()
            except Exception:
                stderr_tail = ""
        print(f"Smoke test failed: {exc}", file=sys.stderr)
        if stderr_tail:
            print(f"stderr: {stderr_tail}", file=sys.stderr)
        return 1
    finally:
        try:
            process.terminate()
            await asyncio.wait_for(asyncio.to_thread(process.wait), timeout=5)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MCP stdio smoke test")
    parser.add_argument(
        "--project-directory",
        default=str(Path(__file__).resolve().parents[1]),
        help="Project root to run mcp server from",
    )
    parser.add_argument(
        "--call-timeout",
        type=int,
        default=5,
        help="Timeout argument passed to interactive_feedback",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_directory = Path(args.project_directory).resolve()
    if not project_directory.exists():
        print(f"Project directory does not exist: {project_directory}", file=sys.stderr)
        return 2

    return asyncio.run(run_smoke_test(project_directory, call_timeout=args.call_timeout))


if __name__ == "__main__":
    raise SystemExit(main())
