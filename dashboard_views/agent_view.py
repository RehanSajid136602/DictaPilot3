"""
DictaPilot Dashboard Agent Mode View
Agent mode configuration and status display.
 
MIT License
Copyright (c) 2026 Rehan
"""
 
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QTextEdit, QLineEdit
)
from PySide6.QtGui import QFont
 
from dashboard_themes import get_theme_manager
from dashboard_components.widgets import ToggleSwitch, StyledComboBox, StyledCheckBox
from dashboard_components.cards import StatusCard
from config import DictaPilotConfig
import re
 
 
class AgentView(QWidget):
    """Agent mode configuration view"""
     
    config_changed = Signal()
     
    def __init__(self, config: DictaPilotConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.theme_manager = get_theme_manager()
         
        self._init_ui()
        self._load_config()
     
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
         
         # Header
        header_label = QLabel("Agent Mode Configuration")
        font = QFont()
        font.setPixelSize(24)
        font.setBold(True)
        header_label.setFont(font)
        header_label.setStyleSheet(f"color: {self.theme_manager.get_color('text-primary')};")
        layout.addWidget(header_label)
         
         # Status section
        status_layout = QHBoxLayout()
        status_layout.setSpacing(16)
         
        self.mode_card = StatusCard("Agent Mode", "Disabled", "🤖")
        status_layout.addWidget(self.mode_card)
         
        self.autodetect_card = StatusCard("Auto-Detect", "Disabled", "🔍")
        status_layout.addWidget(self.autodetect_card)
         
        self.ide_card = StatusCard("IDE Integration", "Disabled", "💻")
        status_layout.addWidget(self.ide_card)
         
        self.format_card = StatusCard("Output Format", "Plain", "📄")
        status_layout.addWidget(self.format_card)
         
        layout.addLayout(status_layout)
         
         # Agent mode toggle
        toggle_group = self._create_group("Enable Agent Mode")
        toggle_layout = QHBoxLayout()
         
        toggle_label = QLabel("Agent mode transforms dictation for coding workflows")
        toggle_label.setStyleSheet(f"color: {self.theme_manager.get_color('text-secondary')}; font-size: 14px;")
        toggle_layout.addWidget(toggle_label)
         
        toggle_layout.addStretch()
         
        self.agent_toggle = ToggleSwitch()
        self.agent_toggle.toggled.connect(self._on_agent_toggled)
        toggle_layout.addWidget(self.agent_toggle)
         
        toggle_group.layout().addLayout(toggle_layout)
        layout.addWidget(toggle_group)
         
         # Output preview
        preview_group = self._create_group("Output Preview")
         
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        self._apply_preview_style()
         
        preview_group.layout().addWidget(self.preview_text)
        layout.addWidget(preview_group)
         
         # Configuration groups
        config_layout = QHBoxLayout()
        config_layout.setSpacing(16)
         
         # Output format group
        format_group = self._create_group("Output Format")
         
        self.format_combo = StyledComboBox()
        self.format_combo.addItems(["Plain Text", "Markdown", "Structured JSON"])
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        format_group.layout().addWidget(self.format_combo)
         
        config_layout.addWidget(format_group)
         
         # IDE integration group
        ide_group = self._create_group("IDE Integration")
         
        self.ide_enabled = StyledCheckBox("Enable IDE integration")
        self.ide_enabled.stateChanged.connect(self._on_ide_toggled)
        ide_group.layout().addWidget(self.ide_enabled)
         
        self.ide_type = StyledComboBox()
        self.ide_type.addItems(["VS Code", "PyCharm", "Sublime Text", "Vim", "Emacs"])
        self.ide_type.currentTextChanged.connect(self._on_config_changed)
        self.ide_type.setEnabled(False)
        ide_group.layout().addWidget(self.ide_type)
         
        config_layout.addWidget(ide_group)
         
        layout.addLayout(config_layout)
         
         # Webhook group
        webhook_group = self._create_group("Webhook Configuration")
         
        webhook_label = QLabel("Webhook URL:")
        webhook_label.setStyleSheet(f"color: {self.theme_manager.get_color('text-primary')}; font-size: 14px;")
        webhook_group.layout().addWidget(webhook_label)
         
        self.webhook_input = QLineEdit()
        self.webhook_input.setPlaceholderText("https://example.com/webhook")
        self.webhook_input.textChanged.connect(self._on_webhook_changed)
        self._apply_input_style(self.webhook_input)
        webhook_group.layout().addWidget(self.webhook_input)
         
        self.webhook_status = QLabel("")
        self.webhook_status.setStyleSheet(f"color: {self.theme_manager.get_color('text-tertiary')}; font-size: 12px;")
        webhook_group.layout().addWidget(self.webhook_status)
         
        layout.addWidget(webhook_group)
         
         # Triggers group
        triggers_group = self._create_group("Auto-Detect Triggers")
         
        self.autodetect_enabled = StyledCheckBox("Enable auto-detect for coding context")
        self.autodetect_enabled.stateChanged.connect(self._on_config_changed)
        triggers_group.layout().addWidget(self.autodetect_enabled)
         
        self.detect_code = StyledCheckBox("Detect code snippets")
        self.detect_code.stateChanged.connect(self._on_config_changed)
        triggers_group.layout().addWidget(self.detect_code)
         
        self.detect_commands = StyledCheckBox("Detect terminal commands")
        self.detect_commands.stateChanged.connect(self._on_config_changed)
        triggers_group.layout().addWidget(self.detect_commands)
         
        layout.addWidget(triggers_group)
         
        layout.addStretch()
     
    def _create_group(self, title: str) -> QGroupBox:
        """Create a styled group box"""
        group = QGroupBox(title)
        group.setLayout(QVBoxLayout())
        group.layout().setSpacing(12)
         
        tokens = self.theme_manager.get_current_tokens()
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {tokens["bg-surface0"]};
                border: 1px solid {tokens["bg-surface2"]};
                border-radius: 8px;
                padding: 16px;
                margin-top: 12px;
                font-size: 14px;
                font-weight: bold;
                color: {tokens["text-primary"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: {tokens["text-primary"]};
            }}
        """)
         
        return group
     
    def _apply_preview_style(self):
        """Apply styling to preview text"""
        tokens = self.theme_manager.get_current_tokens()
        self.preview_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {tokens["bg-base"]};
                color: {tokens["text-primary"]};
                border: 1px solid {tokens["bg-surface2"]};
                border-radius: 6px;
                padding: 12px;
                font-family: monospace;
                font-size: 13px;
            }}
        """)
     
    def _apply_input_style(self, widget: QLineEdit):
        """Apply styling to input field"""
        tokens = self.theme_manager.get_current_tokens()
        widget.setStyleSheet(f"""
            QLineEdit {{
                background-color: {tokens["bg-base"]};
                color: {tokens["text-primary"]};
                border: 1px solid {tokens["bg-surface2"]};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QLineEdit:hover {{
                border-color: {tokens["accent-blue"]};
            }}
            QLineEdit:focus {{
                border-color: {tokens["accent-blue"]};
                outline: 2px solid {tokens["accent-blue"]};
                outline-offset: 2px;
            }}
        """)
     
    def _load_config(self):
        """Load configuration from config"""
         # Agent mode
        agent_enabled = getattr(self.config, 'agent_mode_enabled', False)
        self.agent_toggle.setChecked(agent_enabled)
         
         # Output format
        output_format = getattr(self.config, 'agent_output_format', 'plain')
        if output_format == 'plain':
            self.format_combo.setCurrentText("Plain Text")
        elif output_format == 'markdown':
            self.format_combo.setCurrentText("Markdown")
        elif output_format == 'structured':
            self.format_combo.setCurrentText("Structured JSON")
         
         # IDE integration
        ide_enabled = getattr(self.config, 'ide_integration_enabled', False)
        self.ide_enabled.setChecked(ide_enabled)
        self.ide_type.setEnabled(ide_enabled)
         
        ide_type = getattr(self.config, 'ide_type', 'VS Code')
        self.ide_type.setCurrentText(ide_type)
         
         # Webhook
        webhook_url = getattr(self.config, 'agent_webhook_url', '')
        self.webhook_input.setText(webhook_url)
         
         # Auto-detect
        autodetect = getattr(self.config, 'agent_autodetect_enabled', False)
        self.autodetect_enabled.setChecked(autodetect)
         
        detect_code = getattr(self.config, 'agent_detect_code', True)
        self.detect_code.setChecked(detect_code)
         
        detect_commands = getattr(self.config, 'agent_detect_commands', True)
        self.detect_commands.setChecked(detect_commands)
         
        self._update_status()
        self._update_preview()
     
    def _on_agent_toggled(self, checked: bool):
        """Handle agent mode toggle"""
        self.config.agent_mode_enabled = checked
        self._update_status()
        self._on_config_changed()
     
    def _on_format_changed(self, text: str):
        """Handle format change"""
        if text == "Plain Text":
            self.config.agent_output_format = 'plain'
        elif text == "Markdown":
            self.config.agent_output_format = 'markdown'
        elif text == "Structured JSON":
            self.config.agent_output_format = 'structured'
         
        self._update_status()
        self._update_preview()
        self._on_config_changed()
     
    def _on_ide_toggled(self, state):
        """Handle IDE integration toggle"""
        enabled = state == Qt.Checked
        self.config.ide_integration_enabled = enabled
        self.ide_type.setEnabled(enabled)
        self._update_status()
        self._on_config_changed()
     
    def _on_webhook_changed(self, text: str):
        """Handle webhook URL change"""
        self.config.agent_webhook_url = text
        self._validate_webhook(text)
        self._on_config_changed()
     
    def _validate_webhook(self, url: str):
        """Validate webhook URL"""
        if not url:
            self.webhook_status.setText("")
            return
         
         # Simple URL validation
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
         
        if url_pattern.match(url):
            self.webhook_status.setText("✓ Valid URL")
            self.webhook_status.setStyleSheet(f"color: {self.theme_manager.get_color('accent-green')}; font-size: 12px;")
        else:
            self.webhook_status.setText("✗ Invalid URL format")
            self.webhook_status.setStyleSheet(f"color: {self.theme_manager.get_color('accent-red')}; font-size: 12px;")
     
    def _on_config_changed(self):
        """Handle configuration change"""
         # Save auto-detect settings
        self.config.agent_autodetect_enabled = self.autodetect_enabled.isChecked()
        self.config.agent_detect_code = self.detect_code.isChecked()
        self.config.agent_detect_commands = self.detect_commands.isChecked()
        self.config.ide_type = self.ide_type.currentText()
         
        self._update_status()
        self.config_changed.emit()
     
    def _update_status(self):
        """Update status cards"""
         # Agent mode
        agent_enabled = getattr(self.config, 'agent_mode_enabled', False)
        self.mode_card.set_value("Enabled" if agent_enabled else "Disabled")
         
         # Auto-detect
        autodetect = getattr(self.config, 'agent_autodetect_enabled', False)
        self.autodetect_card.set_value("Enabled" if autodetect else "Disabled")
         
         # IDE integration
        ide_enabled = getattr(self.config, 'ide_integration_enabled', False)
        ide_type = getattr(self.config, 'ide_type', 'VS Code')
        self.ide_card.set_value(f"{ide_type}" if ide_enabled else "Disabled")
         
         # Output format
        output_format = getattr(self.config, 'agent_output_format', 'plain')
        format_map = {'plain': 'Plain', 'markdown': 'Markdown', 'structured': 'JSON'}
        self.format_card.set_value(format_map.get(output_format, 'Plain'))
     
    def _update_preview(self):
        """Update output preview"""
        output_format = getattr(self.config, 'agent_output_format', 'plain')
         
        sample_text = "create a function to calculate fibonacci numbers"
         
        if output_format == 'plain':
            preview = f"def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
        elif output_format == 'markdown':
            preview = f"```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```"
        elif output_format == 'structured':
            preview = '''{
    "action": "create_function",
    "language": "python",
    "name": "fibonacci",
    "code": "def fibonacci(n):\\n    if n <= 1:\\n        return n\\n    return fibonacci(n-1) + fibonacci(n-2)"
}'''
        else:
            preview = sample_text
         
        self.preview_text.setPlainText(preview)
