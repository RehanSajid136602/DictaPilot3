"""
DictaPilot Agent Orchestrator
Manages connections and communication with IDE agents and external services

Original by: Rohan Sharvesh
Fork maintained by: Rehan

MIT License
Copyright (c) 2026 Rohan Sharvesh
Copyright (c) 2026 Rehan
"""

import json
import requests
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum


class AgentType(Enum):
    """Types of agents"""
    CURSOR = "cursor"
    WINDSURF = "windsurf"
    CLINE = "cline"
    GITHUB_COPILOT = "github_copilot"
    LUNA = "luna"
    OPENAI_CODEX = "openai_codex"
    CLAUDE = "claude"
    CUSTOM = "custom"


@dataclass
class AgentConnection:
    """Connection information for an agent"""
    agent_type: AgentType
    name: str
    endpoint: str
    api_key: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = None


@dataclass
class AgentResponse:
    """Response from an agent"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentOrchestrator:
    """Orchestrates communication with IDE agents and external services"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.connections: Dict[str, AgentConnection] = {}
        self.config_path = config_path
        if config_path and config_path.exists():
            self._load_connections()
    
    def _load_connections(self):
        """Load agent connections from config"""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            for conn_data in data.get("connections", []):
                agent_type = AgentType(conn_data["agent_type"])
                conn = AgentConnection(
                    agent_type=agent_type,
                    name=conn_data["name"],
                    endpoint=conn_data["endpoint"],
                    api_key=conn_data.get("api_key"),
                    enabled=conn_data.get("enabled", True),
                    metadata=conn_data.get("metadata", {})
                )
                self.connections[conn.name] = conn
        except Exception as e:
            print(f"Error loading connections: {e}")
    
    def _save_connections(self):
        """Save agent connections to config"""
        if not self.config_path:
            return
        
        try:
            data = {
                "connections": [
                    {
                        "agent_type": conn.agent_type.value,
                        "name": conn.name,
                        "endpoint": conn.endpoint,
                        "api_key": conn.api_key,
                        "enabled": conn.enabled,
                        "metadata": conn.metadata or {}
                    }
                    for conn in self.connections.values()
                ]
            }
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving connections: {e}")
    
    def add_connection(self, connection: AgentConnection) -> bool:
        """Add a new agent connection"""
        self.connections[connection.name] = connection
        self._save_connections()
        return True
    
    def remove_connection(self, name: str) -> bool:
        """Remove an agent connection"""
        if name in self.connections:
            del self.connections[name]
            self._save_connections()
            return True
        return False
    
    def get_connection(self, name: str) -> Optional[AgentConnection]:
        """Get connection by name"""
        return self.connections.get(name)
    
    def list_connections(self) -> List[AgentConnection]:
        """List all connections"""
        return list(self.connections.values())
    
    def send_to_agent(
        self, 
        agent_name: str, 
        content: str, 
        format_type: str = "markdown"
    ) -> AgentResponse:
        """Send content to a specific agent"""
        conn = self.get_connection(agent_name)
        if not conn:
            return AgentResponse(
                success=False,
                message=f"Agent '{agent_name}' not found",
                error="CONNECTION_NOT_FOUND"
            )
        
        if not conn.enabled:
            return AgentResponse(
                success=False,
                message=f"Agent '{agent_name}' is disabled",
                error="AGENT_DISABLED"
            )
        
        # Route to appropriate handler based on agent type
        if conn.agent_type == AgentType.CURSOR:
            return self._send_to_cursor(conn, content)
        elif conn.agent_type == AgentType.WINDSURF:
            return self._send_to_windsurf(conn, content)
        elif conn.agent_type == AgentType.CLINE:
            return self._send_to_cline(conn, content)
        elif conn.agent_type == AgentType.LUNA:
            return self._send_to_luna(conn, content, format_type)
        elif conn.agent_type == AgentType.CUSTOM:
            return self._send_to_webhook(conn, content, format_type)
        else:
            return AgentResponse(
                success=False,
                message=f"Agent type '{conn.agent_type.value}' not implemented",
                error="NOT_IMPLEMENTED"
            )
    
    def _send_to_cursor(self, conn: AgentConnection, content: str) -> AgentResponse:
        """Send content to Cursor IDE"""
        try:
            # Cursor typically uses a local server or file-based communication
            # Try to open Cursor with the content
            cursor_file = Path.home() / ".cursor" / "dictapilot_input.md"
            cursor_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cursor_file, 'w') as f:
                f.write(content)
            
            # Try to trigger Cursor to open the file
            try:
                subprocess.run(['cursor', str(cursor_file)], check=False)
            except FileNotFoundError:
                pass
            
            return AgentResponse(
                success=True,
                message="Content sent to Cursor",
                data={"file": str(cursor_file)}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                message="Failed to send to Cursor",
                error=str(e)
            )
    
    def _send_to_windsurf(self, conn: AgentConnection, content: str) -> AgentResponse:
        """Send content to Windsurf IDE"""
        try:
            # Similar approach to Cursor
            windsurf_file = Path.home() / ".windsurf" / "dictapilot_input.md"
            windsurf_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(windsurf_file, 'w') as f:
                f.write(content)
            
            try:
                subprocess.run(['windsurf', str(windsurf_file)], check=False)
            except FileNotFoundError:
                pass
            
            return AgentResponse(
                success=True,
                message="Content sent to Windsurf",
                data={"file": str(windsurf_file)}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                message="Failed to send to Windsurf",
                error=str(e)
            )
    
    def _send_to_cline(self, conn: AgentConnection, content: str) -> AgentResponse:
        """Send content to Cline"""
        try:
            # Cline might use VS Code extension API
            cline_file = Path.home() / ".vscode" / "cline" / "dictapilot_input.md"
            cline_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cline_file, 'w') as f:
                f.write(content)
            
            return AgentResponse(
                success=True,
                message="Content sent to Cline",
                data={"file": str(cline_file)}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                message="Failed to send to Cline",
                error=str(e)
            )
    
    def _send_to_luna(
        self, 
        conn: AgentConnection, 
        content: str, 
        format_type: str
    ) -> AgentResponse:
        """Send content to Luna Drive API"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            if conn.api_key:
                headers["Authorization"] = f"Bearer {conn.api_key}"
            
            payload = {
                "specification": content,
                "format": format_type
            }
            
            response = requests.post(
                conn.endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return AgentResponse(
                    success=True,
                    message="Content sent to Luna Drive",
                    data=response.json()
                )
            else:
                return AgentResponse(
                    success=False,
                    message=f"Luna API error: {response.status_code}",
                    error=response.text
                )
        except Exception as e:
            return AgentResponse(
                success=False,
                message="Failed to send to Luna Drive",
                error=str(e)
            )
    
    def _send_to_webhook(
        self, 
        conn: AgentConnection, 
        content: str, 
        format_type: str
    ) -> AgentResponse:
        """Send content to custom webhook"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            if conn.api_key:
                headers["Authorization"] = f"Bearer {conn.api_key}"
            
            payload = {
                "content": content,
                "format": format_type,
                "source": "dictapilot"
            }
            
            response = requests.post(
                conn.endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                return AgentResponse(
                    success=True,
                    message="Content sent to webhook",
                    data=response.json() if response.text else None
                )
            else:
                return AgentResponse(
                    success=False,
                    message=f"Webhook error: {response.status_code}",
                    error=response.text
                )
        except Exception as e:
            return AgentResponse(
                success=False,
                message="Failed to send to webhook",
                error=str(e)
            )
    
    def test_connection(self, agent_name: str) -> AgentResponse:
        """Test connection to an agent"""
        conn = self.get_connection(agent_name)
        if not conn:
            return AgentResponse(
                success=False,
                message=f"Agent '{agent_name}' not found",
                error="CONNECTION_NOT_FOUND"
            )
        
        # Simple test - try to send a ping
        test_content = "# Test Connection\n\nThis is a test from DictaPilot."
        return self.send_to_agent(agent_name, test_content)
