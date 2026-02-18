"""
DictaPilot IDE Integration
Provides integration with popular IDEs and editors

Original by: Rohan Sharvesh
Fork maintained by: Rehan

MIT License
Copyright (c) 2026 Rohan Sharvesh
Copyright (c) 2026 Rehan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import json
import subprocess
import socket
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class IDEInfo:
    """Information about detected IDE"""
    name: str
    running: bool
    version: Optional[str] = None
    port: Optional[int] = None
    extension_installed: bool = False


class IDEDetector:
    """Detects running IDEs and their status"""

    # Common process names for IDEs
    IDE_PROCESSES = {
        'vscode': ['code', 'Code', 'code-oss', 'VSCodium'],
        'cursor': ['cursor', 'Cursor'],
        'windsurf': ['windsurf', 'Windsurf'],
        'jetbrains': ['idea', 'pycharm', 'clion', 'goland', 'webstorm', 'rider'],
        'sublime': ['subl', 'sublime_text'],
        'vim': ['vim', 'nvim', 'neovim'],
        'emacs': ['emacs'],
    }

    # VS Code extension ports (commonly used)
    VSCODE_PORTS = [9333, 9334, 9335, 9999]

    def __init__(self):
        self._cached_processes = None
        self._cache_time = 0

    def get_running_processes(self) -> List[str]:
        """Get list of running process names"""
        # Cache for 5 seconds
        if self._cached_processes and time.time() - self._cache_time < 5:
            return self._cached_processes

        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )
            processes = []
            for line in result.stdout.split('\n'):
                parts = line.split()
                if len(parts) >= 11:
                    proc_name = parts[10]
                    processes.append(proc_name)
            self._cached_processes = processes
            self._cache_time = time.time()
            return processes
        except Exception:
            return []

    def detect_ide(self, ide_type: str) -> IDEInfo:
        """Detect if a specific IDE is running"""
        processes = self.get_running_processes()
        ide_names = self.IDE_PROCESSES.get(ide_type, [])

        running = False
        for proc in processes:
            for name in ide_names:
                if name.lower() in proc.lower():
                    running = True
                    break
            if running:
                break

        return IDEInfo(
            name=ide_type,
            running=running,
        )

    def detect_all(self) -> Dict[str, IDEInfo]:
        """Detect all supported IDEs"""
        results = {}
        for ide_type in self.IDE_PROCESSES:
            results[ide_type] = self.detect_ide(ide_type)
        return results

    def get_active_ide(self) -> Optional[str]:
        """Get the most likely active IDE"""
        ides = self.detect_all()
        for ide_name, info in ides.items():
            if info.running:
                return ide_name
        return None


class VSCodeIntegration:
    """Integration with VS Code and VS Code-based editors"""

    def __init__(self, port: int = 9333):
        self.port = port
        self.host = 'localhost'

    def is_extension_running(self) -> bool:
        """Check if VS Code extension is running and listening"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def send_task(self, task_data: Dict[str, Any]) -> bool:
        """Send a task to the VS Code extension"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.host, self.port))

            message = json.dumps(task_data) + '\n'
            sock.sendall(message.encode('utf-8'))

            response = sock.recv(4096).decode('utf-8')
            sock.close()

            return 'success' in response.lower()
        except Exception as e:
            print(f"VS Code integration error: {e}", file=__import__('sys').stderr)
            return False

    def open_file(self, file_path: str, line: int = 0) -> bool:
        """Request VS Code to open a file"""
        return self.send_task({
            'action': 'open_file',
            'path': file_path,
            'line': line,
        })

    def insert_text(self, text: str, position: Optional[Dict] = None) -> bool:
        """Request VS Code to insert text at cursor or position"""
        task = {
            'action': 'insert_text',
            'text': text,
        }
        if position:
            task['position'] = position
        return self.send_task(task)


class WebhookIntegration:
    """Generic webhook integration for agent mode"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_prompt(self, prompt_data: Dict[str, Any]) -> bool:
        """Send formatted prompt to webhook"""
        if not self.webhook_url:
            return False

        try:
            import urllib.request
            import json

            data = json.dumps(prompt_data).encode('utf-8')
            req = urllib.request.Request(
                self.webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200
        except Exception as e:
            print(f"Webhook error: {e}", file=__import__('sys').stderr)
            return False


class IDEIntegrationManager:
    """Manages all IDE integrations"""

    def __init__(self, webhook_url: str = "", vscode_port: int = 9333):
        self.detector = IDEDetector()
        self.vscode = VSCodeIntegration(port=vscode_port)
        self.webhook = WebhookIntegration(webhook_url)
        self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self, webhook_url: str = ""):
        """Enable IDE integration"""
        self._enabled = True
        if webhook_url:
            self.webhook = WebhookIntegration(webhook_url)

    def disable(self):
        """Disable IDE integration"""
        self._enabled = False

    def get_active_ide(self) -> Optional[str]:
        """Get the currently active IDE"""
        if not self._enabled:
            return None
        return self.detector.get_active_ide()

    def send_agent_task(self, formatted_prompt: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Send a formatted agent task to the appropriate destination

        Args:
            formatted_prompt: The formatted task prompt
            metadata: Additional metadata (priority, complexity, etc.)

        Returns:
            True if successfully sent
        """
        if not self._enabled:
            return False

        # Try VS Code integration first
        if self.vscode.is_extension_running():
            task_data = {
                'prompt': formatted_prompt,
                'timestamp': time.time(),
                'source': 'dictapilot',
            }
            if metadata:
                task_data['metadata'] = metadata
            return self.vscode.send_task(task_data)

        # Fall back to webhook
        if self.webhook.webhook_url:
            task_data = {
                'prompt': formatted_prompt,
                'timestamp': time.time(),
                'source': 'dictapilot',
            }
            if metadata:
                task_data['metadata'] = metadata
            return self.webhook.send_prompt(task_data)

        return False

    def get_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        return {
            'enabled': self._enabled,
            'active_ide': self.get_active_ide(),
            'vscode_connected': self.vscode.is_extension_running() if self._enabled else False,
            'webhook_configured': bool(self.webhook.webhook_url),
            'detected_ides': {
                name: info.running
                for name, info in self.detector.detect_all().items()
            },
        }


# Singleton instance
_integration_manager: Optional[IDEIntegrationManager] = None


def get_integration_manager(webhook_url: str = "") -> IDEIntegrationManager:
    """Get the global IDE integration manager"""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = IDEIntegrationManager(webhook_url)
    elif webhook_url:
        _integration_manager.webhook = WebhookIntegration(webhook_url)
    return _integration_manager


def send_to_ide(prompt: str, metadata: Dict[str, Any] = None) -> bool:
    """Convenience function to send prompt to IDE"""
    manager = get_integration_manager()
    if not manager.enabled:
        return False
    return manager.send_agent_task(prompt, metadata)


# CLI usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IDE Integration Utilities")
    parser.add_argument('--detect', action='store_true', help='Detect running IDEs')
    parser.add_argument('--status', action='store_true', help='Show integration status')
    parser.add_argument('--test-webhook', type=str, metavar='URL', help='Test webhook connection')

    args = parser.parse_args()

    if args.detect:
        detector = IDEDetector()
        ides = detector.detect_all()
        print("Detected IDEs:")
        for name, info in ides.items():
            status = "running" if info.running else "not running"
            print(f"  {name}: {status}")

    elif args.status:
        manager = get_integration_manager()
        manager.enable()
        status = manager.get_status()
        print(json.dumps(status, indent=2))

    elif args.test_webhook:
        webhook = WebhookIntegration(args.test_webhook)
        success = webhook.send_prompt({
            'test': True,
            'message': 'Hello from DictaPilot!',
            'timestamp': time.time(),
        })
        print(f"Webhook test: {'success' if success else 'failed'}")

    else:
        parser.print_help()
