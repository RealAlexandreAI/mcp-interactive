# Interactive Feedback MCP Web UI
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Web UI version for SSH remote development
import os
import sys
import json
import uuid
import asyncio
import webbrowser
import threading
import subprocess
import psutil
import time
from typing import Dict, Optional, List
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

class WebFeedbackSession:
    def __init__(self, session_id: str, project_directory: str, summary: str):
        self.session_id = session_id
        self.project_directory = project_directory
        self.summary = summary
        self.websocket: Optional[WebSocket] = None
        self.feedback_result: Optional[str] = None
        self.command_logs: List[str] = []
        self.process: Optional[subprocess.Popen] = None
        self.completed = False
        self.config = {
            "run_command": "",
            "execute_automatically": False
        }

class WebUIManager:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.app = FastAPI(title="Interactive Feedback MCP")
        self.sessions: Dict[str, WebFeedbackSession] = {}
        self.server_process = None
        self.setup_routes()
        
        # Setup static files and templates
        script_dir = Path(__file__).parent
        static_dir = script_dir / "static"
        templates_dir = script_dir / "templates"
        static_dir.mkdir(exist_ok=True)
        templates_dir.mkdir(exist_ok=True)
        
        self.app.mount("/static", StaticFiles(directory=static_dir), name="static")
        self.templates = Jinja2Templates(directory=templates_dir)

    def setup_routes(self):
        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            return self.templates.TemplateResponse("index.html", {"request": request})

        @self.app.get("/session/{session_id}", response_class=HTMLResponse) 
        async def session_page(request: Request, session_id: str):
            session = self.sessions.get(session_id)
            if not session:
                return HTMLResponse("Session not found", status_code=404)
            
            return self.templates.TemplateResponse("feedback.html", {
                "request": request,
                "session_id": session_id,
                "project_directory": session.project_directory,
                "summary": session.summary
            })

        @self.app.websocket("/ws/{session_id}")
        async def websocket_endpoint(websocket: WebSocket, session_id: str):
            await websocket.accept()
            
            session = self.sessions.get(session_id)
            if not session:
                await websocket.close(code=4000, reason="Session not found")
                return
                
            session.websocket = websocket
            
            # Send initial data
            await websocket.send_json({
                "type": "init",
                "project_directory": session.project_directory,
                "summary": session.summary,
                "config": session.config,
                "logs": session.command_logs
            })
            
            try:
                while True:
                    data = await websocket.receive_json()
                    await self.handle_websocket_message(session, data)
                    
            except WebSocketDisconnect:
                session.websocket = None

        @self.app.post("/api/complete/{session_id}")
        async def complete_session(session_id: str, feedback_data: dict):
            session = self.sessions.get(session_id)
            if not session:
                return {"error": "Session not found"}
                
            session.feedback_result = feedback_data.get("feedback", "")
            session.completed = True
            
            return {"success": True}

    async def handle_websocket_message(self, session: WebFeedbackSession, data: dict):
        message_type = data.get("type")
        
        if message_type == "run_command":
            command = data.get("command", "")
            await self.run_command(session, command)
            
        elif message_type == "stop_command":
            await self.stop_command(session)
            
        elif message_type == "submit_feedback":
            feedback = data.get("feedback", "")
            session.feedback_result = feedback
            session.completed = True
            
            await session.websocket.send_json({
                "type": "feedback_submitted",
                "message": "Feedback submitted successfully"
            })
            
        elif message_type == "update_config":
            session.config.update(data.get("config", {}))
            
        elif message_type == "clear_logs":
            session.command_logs.clear()
            await session.websocket.send_json({
                "type": "logs_cleared"
            })

    async def run_command(self, session: WebFeedbackSession, command: str):
        if session.process:
            await self.stop_command(session)
            
        if not command.strip():
            await session.websocket.send_json({
                "type": "log",
                "data": "Please enter a command to run\n"
            })
            return
            
        session.command_logs.append(f"$ {command}\n")
        await session.websocket.send_json({
            "type": "log", 
            "data": f"$ {command}\n"
        })
        
        try:
            session.process = subprocess.Popen(
                command,
                shell=True,
                cwd=session.project_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="ignore"
            )
            
            # Start threads to read output
            threading.Thread(
                target=self.read_process_output,
                args=(session, session.process.stdout),
                daemon=True
            ).start()
            
            threading.Thread(
                target=self.read_process_output, 
                args=(session, session.process.stderr),
                daemon=True
            ).start()
            
            # Monitor process completion
            threading.Thread(
                target=self.monitor_process,
                args=(session,),
                daemon=True
            ).start()
            
        except Exception as e:
            error_msg = f"Error running command: {str(e)}\n"
            session.command_logs.append(error_msg)
            await session.websocket.send_json({
                "type": "log",
                "data": error_msg
            })

    def read_process_output(self, session: WebFeedbackSession, pipe):
        try:
            for line in iter(pipe.readline, ""):
                if not line:
                    break
                session.command_logs.append(line)
                if session.websocket:
                    # Use threading to send async message
                    threading.Thread(
                        target=self._send_websocket_message,
                        args=(session.websocket, {
                            "type": "log",
                            "data": line
                        }),
                        daemon=True
                    ).start()
        except Exception:
            pass

    def monitor_process(self, session: WebFeedbackSession):
        if session.process:
            exit_code = session.process.wait()
            completion_msg = f"\nProcess exited with code {exit_code}\n"
            session.command_logs.append(completion_msg)
            
            if session.websocket:
                threading.Thread(
                    target=self._send_websocket_message,
                    args=(session.websocket, {
                        "type": "log",
                        "data": completion_msg
                    }),
                    daemon=True
                ).start()
                
                threading.Thread(
                    target=self._send_websocket_message,
                    args=(session.websocket, {
                        "type": "process_completed",
                        "exit_code": exit_code
                    }),
                    daemon=True
                ).start()
            
            session.process = None

    def _send_websocket_message(self, websocket: WebSocket, message: dict):
        """Helper to send websocket message from thread"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(websocket.send_json(message))
            loop.close()
        except Exception:
            pass

    async def stop_command(self, session: WebFeedbackSession):
        if session.process:
            try:
                # Kill process tree
                parent = psutil.Process(session.process.pid)
                for child in parent.children(recursive=True):
                    try:
                        child.kill()
                    except psutil.Error:
                        pass
                parent.kill()
                session.process = None
                
                await session.websocket.send_json({
                    "type": "log",
                    "data": "\nProcess stopped\n"
                })
                
            except Exception as e:
                await session.websocket.send_json({
                    "type": "log", 
                    "data": f"\nError stopping process: {str(e)}\n"
                })

    def create_session(self, project_directory: str, summary: str) -> str:
        session_id = str(uuid.uuid4())
        session = WebFeedbackSession(session_id, project_directory, summary)
        self.sessions[session_id] = session
        return session_id

    def start_server(self):
        """Start the web server in a separate thread"""
        if self.server_process is not None:
            return  # Server already running
            
        def run_server():
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="error",
                access_log=False
            )
            
        self.server_process = threading.Thread(target=run_server, daemon=True)
        self.server_process.start()
        
        # Wait a moment for server to start
        time.sleep(1)

    def open_browser(self, session_id: str):
        """Open browser to the session page"""
        url = f"http://{self.host}:{self.port}/session/{session_id}"
        try:
            webbrowser.open(url)
        except Exception:
            print(f"Please open your browser and navigate to: {url}")

    def wait_for_feedback(self, session_id: str, timeout: int = 300) -> dict:
        """Wait for user feedback with timeout"""
        session = self.sessions.get(session_id)
        if not session:
            return {"command_logs": "", "interactive_feedback": "Session not found"}
            
        # Wait for feedback with timeout
        start_time = time.time()
        while not session.completed:
            if time.time() - start_time > timeout:
                return {"command_logs": "", "interactive_feedback": "Timeout waiting for feedback"}
            time.sleep(0.1)
            
        result = {
            "command_logs": "".join(session.command_logs),
            "interactive_feedback": session.feedback_result or ""
        }
        
        # Clean up session
        del self.sessions[session_id]
        
        return result

# Global instance
web_ui_manager = WebUIManager()

def launch_web_feedback_ui(project_directory: str, summary: str) -> dict:
    """Launch web UI and wait for feedback"""
    
    # Start server if not running
    web_ui_manager.start_server()
    
    # Create new session
    session_id = web_ui_manager.create_session(project_directory, summary)
    
    # Open browser
    web_ui_manager.open_browser(session_id)
    
    # Wait for feedback
    return web_ui_manager.wait_for_feedback(session_id) 