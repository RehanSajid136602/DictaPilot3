"""
DictaPilot Diagnostics View
Displays system health checks and diagnostic information.

MIT License
Copyright (c) 2026 Rehan
"""

from datetime import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QListWidget, QListWidgetItem,
    QTextEdit
)
from PySide6.QtGui import QFont

from dashboard_themes import get_theme_manager


class DiagnosticsView(QWidget):
    """Diagnostics view"""
    
    run_diagnostics = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.last_checked = None
        self.diagnostic_results = []
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("System Health")
        font = QFont()
        font.setPixelSize(24)
        font.setBold(True)
        title.setFont(font)
        header.addWidget(title)
        
        header.addStretch()
        
        self.run_btn = QPushButton("Run All Checks")
        self.run_btn.setProperty("variant", "primary")
        self.run_btn.clicked.connect(self._on_run_checks)
        header.addWidget(self.run_btn)
        
        main_layout.addLayout(header)
        
        # Diagnostic results list
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(300)
        main_layout.addWidget(self.results_list)
        
        # Last checked timestamp
        self.timestamp_label = QLabel("Last checked: Never")
        self.timestamp_label.setStyleSheet(f"color: {self.theme_manager.get_color('text-secondary')}; font-size: 12px;")
        main_layout.addWidget(self.timestamp_label)
        
        # Detailed logs (expandable)
        logs_frame = QFrame()
        logs_frame.setProperty("card", True)
        
        logs_layout = QVBoxLayout(logs_frame)
        logs_layout.setContentsMargins(16, 16, 16, 16)
        logs_layout.setSpacing(12)
        
        logs_header = QHBoxLayout()
        
        logs_title = QLabel("Detailed Logs")
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        logs_title.setFont(font)
        logs_header.addWidget(logs_title)
        
        logs_header.addStretch()
        
        self.expand_btn = QPushButton("▸ Expand")
        self.expand_btn.setProperty("variant", "ghost")
        self.expand_btn.clicked.connect(self._toggle_logs)
        logs_header.addWidget(self.expand_btn)
        
        logs_layout.addLayout(logs_header)
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setMaximumHeight(200)
        self.logs_text.hide()
        logs_layout.addWidget(self.logs_text)
        
        main_layout.addWidget(logs_frame)
        main_layout.addStretch()
        
        # Load placeholder data
        self._load_placeholder_data()
    
    def _on_run_checks(self):
        """Handle run checks button click"""
        self.run_diagnostics.emit()
        self.last_checked = datetime.now()
        self._update_timestamp()
    
    def _toggle_logs(self):
        """Toggle detailed logs visibility"""
        if self.logs_text.isVisible():
            self.logs_text.hide()
            self.expand_btn.setText("▸ Expand")
        else:
            self.logs_text.show()
            self.expand_btn.setText("▾ Collapse")
    
    def _update_timestamp(self):
        """Update last checked timestamp"""
        if self.last_checked:
            now = datetime.now()
            diff = now - self.last_checked
            
            if diff.total_seconds() < 60:
                time_str = "just now"
            elif diff.total_seconds() < 3600:
                time_str = f"{int(diff.total_seconds() / 60)} minutes ago"
            else:
                time_str = f"{int(diff.total_seconds() / 3600)} hours ago"
            
            self.timestamp_label.setText(f"Last checked: {time_str}")
    
    def set_diagnostic_results(self, results: list):
        """Set diagnostic results
        
        Args:
            results: List of dicts with keys: name, status, message, severity
        """
        self.diagnostic_results = results
        self._display_results()
    
    def _display_results(self):
        """Display diagnostic results"""
        self.results_list.clear()
        
        for result in self.diagnostic_results:
            name = result.get("name", "Unknown")
            status = result.get("status", "unknown")
            message = result.get("message", "")
            severity = result.get("severity", "info")
            
            # Create item
            item_text = f"{self._get_icon(severity)}  {name}: {message}"
            item = QListWidgetItem(item_text)
            
            # Set color based on severity
            if severity == "passed":
                color = self.theme_manager.get_color("accent-green")
            elif severity == "warning":
                color = self.theme_manager.get_color("accent-yellow")
            elif severity == "error":
                color = self.theme_manager.get_color("accent-red")
            else:
                color = self.theme_manager.get_color("text-secondary")
            
            item.setForeground(color)
            self.results_list.addItem(item)
    
    def _get_icon(self, severity: str) -> str:
        """Get icon for severity"""
        icons = {
            "passed": "✅",
            "warning": "⚠️",
            "error": "❌",
            "info": "ℹ️",
        }
        return icons.get(severity, "●")
    
    def _load_placeholder_data(self):
        """Load placeholder diagnostic data"""
        placeholder_results = [
            {
                "name": "API Key",
                "status": "valid",
                "message": "Valid, connected",
                "severity": "passed"
            },
            {
                "name": "Microphone",
                "status": "available",
                "message": "Blue Yeti, 16kHz",
                "severity": "passed"
            },
            {
                "name": "Display Server",
                "status": "detected",
                "message": "Wayland (limited clipboard)",
                "severity": "warning"
            },
            {
                "name": "Paste Backend",
                "status": "available",
                "message": "wl-copy available",
                "severity": "passed"
            },
            {
                "name": "Dependencies",
                "status": "satisfied",
                "message": "All satisfied",
                "severity": "passed"
            },
        ]
        
        self.set_diagnostic_results(placeholder_results)
        
        # Set placeholder logs
        self.logs_text.setPlainText("""
Diagnostic Check Results
========================

API Key Check:
- Status: Valid
- Connection: Successful
- Endpoint: https://api.groq.com/v1

Microphone Check:
- Device: Blue Yeti
- Sample Rate: 16000 Hz
- Channels: 1 (Mono)
- Status: Available

Display Server Check:
- Type: Wayland
- Compositor: GNOME Shell
- Clipboard: Limited (using wl-copy)

Paste Backend Check:
- Primary: wl-copy
- Fallback: xdotool
- Status: Available

Dependencies Check:
- PySide6: 6.6.0 ✓
- sounddevice: 0.4.6 ✓
- numpy: 1.24.3 ✓
- All required packages installed
        """.strip())
    
    def showEvent(self, event):
        """Handle show event - auto-refresh if needed"""
        super().showEvent(event)
        
        # Auto-refresh if last check was more than 5 minutes ago
        if self.last_checked:
            now = datetime.now()
            diff = now - self.last_checked
            if diff.total_seconds() > 300:  # 5 minutes
                self._on_run_checks()
        else:
            # First time showing, run checks
            self._on_run_checks()
