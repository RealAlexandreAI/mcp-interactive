# Interactive Feedback MCP
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
import os
import sys
import json
import tempfile
import subprocess

from typing import Annotated, Dict

from fastmcp import FastMCP
from pydantic import Field

# The log_level is necessary for Cline to work: https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")

def is_ssh_session() -> bool:
    """Check if we're running in an SSH session or remote environment"""
    # Check for SSH environment variables
    ssh_indicators = [
        'SSH_CONNECTION',
        'SSH_CLIENT', 
        'SSH_TTY'
    ]
    
    for indicator in ssh_indicators:
        if os.getenv(indicator):
            return True
    
    # Check if DISPLAY is not set (common in SSH without X11 forwarding)
    if sys.platform.startswith('linux') and not os.getenv('DISPLAY'):
        return True
    
    # Check for other remote indicators
    if os.getenv('TERM_PROGRAM') == 'vscode' and os.getenv('VSCODE_INJECTION') == '1':
        # VSCode remote development
        return True
    
    return False

def can_use_gui() -> bool:
    """Check if GUI can be used in current environment"""
    if is_ssh_session():
        return False
    
    try:
        # Try to import Qt and check if display is available
        if sys.platform == 'win32':
            return True  # Windows should generally support GUI
        elif sys.platform == 'darwin':
            return True  # macOS should generally support GUI
        else:
            # Linux - check for DISPLAY
            return bool(os.getenv('DISPLAY'))
    except ImportError:
        return False

def launch_feedback_ui(project_directory: str, summary: str) -> dict[str, str]:
    """Launch appropriate UI based on environment"""
    
    if can_use_gui():
        # Use Qt GUI (original implementation)
        return launch_qt_feedback_ui(project_directory, summary)
    else:
        # Use Web UI
        return launch_web_feedback_ui(project_directory, summary)

def launch_qt_feedback_ui(project_directory: str, summary: str) -> dict[str, str]:
    """Original Qt GUI implementation"""
    # Create a temporary file for the feedback result
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name

    try:
        # Get the path to feedback_ui.py relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        feedback_ui_path = os.path.join(script_dir, "feedback_ui.py")

        # Run feedback_ui.py as a separate process
        # NOTE: There appears to be a bug in uv, so we need
        # to pass a bunch of special flags to make this work
        args = [
            sys.executable,
            "-u",
            feedback_ui_path,
            "--project-directory", project_directory,
            "--prompt", summary,
            "--output-file", output_file
        ]
        result = subprocess.run(
            args,
            check=False,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True
        )
        if result.returncode != 0:
            raise Exception(f"Failed to launch feedback UI: {result.returncode}")

        # Read the result from the temporary file
        with open(output_file, 'r') as f:
            result = json.load(f)
        os.unlink(output_file)
        return result
    except Exception as e:
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise e

def launch_web_feedback_ui(project_directory: str, summary: str) -> dict[str, str]:
    """Launch Web UI implementation"""
    try:
        from web_ui import launch_web_feedback_ui as launch_web
        return launch_web(project_directory, summary)
    except ImportError as e:
        # Fallback to command line if web UI fails
        print(f"Web UI not available: {e}")
        return launch_cli_feedback_ui(project_directory, summary)

def launch_cli_feedback_ui(project_directory: str, summary: str) -> dict[str, str]:
    """Simple command line fallback"""
    print(f"\n{'='*60}")
    print("Interactive Feedback MCP")
    print(f"{'='*60}")
    print(f"專案目錄: {project_directory}")
    print(f"任務描述: {summary}")
    print(f"{'='*60}")
    
    # Ask for command to run
    command = input("要執行的命令 (留空跳過): ").strip()
    command_logs = ""
    
    if command:
        print(f"執行命令: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=project_directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            command_logs = f"$ {command}\n{result.stdout}{result.stderr}"
            print(command_logs)
        except Exception as e:
            command_logs = f"$ {command}\nError: {str(e)}\n"
            print(command_logs)
    
    # Ask for feedback
    print(f"\n{'='*60}")
    print("請提供您的回饋意見:")
    feedback = input().strip()
    
    return {
        "command_logs": command_logs,
        "interactive_feedback": feedback
    }

def first_line(text: str) -> str:
    return text.split("\n")[0].strip()

@mcp.tool()
def interactive_feedback(
    project_directory: Annotated[str, Field(description="Full path to the project directory")],
    summary: Annotated[str, Field(description="Short, one-line summary of the changes")],
) -> Dict[str, str]:
    """Request interactive feedback for a given project directory and summary"""
    return launch_feedback_ui(first_line(project_directory), first_line(summary))

if __name__ == "__main__":
    mcp.run(transport="stdio")
