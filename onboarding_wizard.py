"""
DictaPilot Onboarding Wizard
Interactive setup wizard for first-time users.

MIT License
Copyright (c) 2026 Rehan
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtWidgets import (
        QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QComboBox,
        QTextEdit, QCheckBox, QMessageBox, QScrollArea, QWidget
    )
    from PySide6.QtGui import QFont, QPixmap
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    QWizard = QWizardPage = object

import sounddevice as sd
from dotenv import load_dotenv, set_key

# Load environment
load_dotenv()


class WelcomePage(QWizardPage):
    """Welcome page with project overview."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to DictaPilot3")
        self.setSubTitle("Let's get you set up in under 5 minutes")
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Logo/Image (if available)
        logo_path = Path(__file__).parent / "Dictepilot.png"
        if logo_path.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # Description
        desc = QLabel(
            "<h3>What is DictaPilot3?</h3>"
            "<p>Cross-platform voice dictation with smart editing.</p>"
            "<ul>"
            "<li><b>Hold-to-Talk:</b> Press F9, speak, release</li>"
            "<li><b>Smart Commands:</b> 'delete that', 'replace X with Y'</li>"
            "<li><b>Delta Paste:</b> Fast, minimal text updates</li>"
            "<li><b>Context-Aware:</b> Different settings per app</li>"
            "<li><b>Privacy-First:</b> Local storage, open source</li>"
            "</ul>"
            "<p>This wizard will help you configure:</p>"
            "<ul>"
            "<li>Groq API key (required for transcription)</li>"
            "<li>Hotkey for recording</li>"
            "<li>Audio device selection</li>"
            "</ul>"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        # Main layout for the page
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)


class APIKeyPage(QWizardPage):
    """API key configuration page."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Groq API Key")
        self.setSubTitle("Enter your free Groq API key for transcription")
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Instructions
        instructions = QLabel(
            "<p>DictaPilot3 uses Groq's Whisper API for transcription.</p>"
            "<p><b>To get your free API key:</b></p>"
            "<ol>"
            "<li>Visit <a href='https://console.groq.com'>console.groq.com</a></li>"
            "<li>Sign up or log in (free)</li>"
            "<li>Create a new API key</li>"
            "<li>Copy the key (starts with 'gsk_')</li>"
            "</ol>"
        )
        instructions.setWordWrap(True)
        instructions.setOpenExternalLinks(True)
        layout.addWidget(instructions)
        
        # API key input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("gsk_...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.textChanged.connect(self._validate_key)
        key_layout.addWidget(self.api_key_input)
        
        # Show/hide button
        self.show_key_btn = QPushButton("Show")
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.toggled.connect(self._toggle_key_visibility)
        key_layout.addWidget(self.show_key_btn)
        
        layout.addLayout(key_layout)
        
        # Validation message
        self.validation_label = QLabel()
        self.validation_label.setStyleSheet("color: red;")
        layout.addWidget(self.validation_label)
        
        # Test button
        self.test_btn = QPushButton("Test API Key")
        self.test_btn.clicked.connect(self._test_api_key)
        self.test_btn.setEnabled(False)
        layout.addWidget(self.test_btn)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        # Main layout for the page
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
        # Register field for validation
        self.registerField("api_key*", self.api_key_input)
    
    def _validate_key(self, text):
        """Validate API key format."""
        if not text:
            self.validation_label.setText("")
            self.test_btn.setEnabled(False)
            return
        
        if not text.startswith("gsk_"):
            self.validation_label.setText("⚠ API key should start with 'gsk_'")
            self.test_btn.setEnabled(False)
        elif len(text) < 20:
            self.validation_label.setText("⚠ API key seems too short")
            self.test_btn.setEnabled(False)
        else:
            self.validation_label.setText("✓ Format looks good")
            self.validation_label.setStyleSheet("color: green;")
            self.test_btn.setEnabled(True)
    
    def _toggle_key_visibility(self, checked):
        """Toggle API key visibility."""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.show_key_btn.setText("Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.show_key_btn.setText("Show")
    
    def _test_api_key(self):
        """Test API key with Groq."""
        api_key = self.api_key_input.text()
        
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            # Simple test - list models
            models = client.models.list()
            QMessageBox.information(
                self,
                "Success",
                "✓ API key is valid!\n\nYou can proceed to the next step."
            )
            self.validation_label.setText("✓ API key verified")
            self.validation_label.setStyleSheet("color: green;")
        except Exception as e:
            QMessageBox.warning(
                self,
                "API Key Test Failed",
                f"Could not verify API key:\n\n{str(e)}\n\n"
                "Please check your key and internet connection."
            )
            self.validation_label.setText("✗ Verification failed")
            self.validation_label.setStyleSheet("color: red;")


class HotkeyPage(QWizardPage):
    """Hotkey configuration page."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Hotkey Configuration")
        self.setSubTitle("Choose your recording hotkey")
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Instructions
        instructions = QLabel(
            "<p>Select the hotkey you'll press and hold to record.</p>"
            "<p><b>Default:</b> F9 (recommended)</p>"
            "<p>You can change this later in the configuration.</p>"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Hotkey selection
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(QLabel("Hotkey:"))
        
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems([
            "f9 (recommended)",
            "f10",
            "f11",
            "f12",
            "ctrl+shift+d",
            "alt+space",
        ])
        hotkey_layout.addWidget(self.hotkey_combo)
        hotkey_layout.addStretch()
        
        layout.addLayout(hotkey_layout)
        
        # Warning about conflicts
        warning = QLabel(
            "⚠ <b>Note:</b> Make sure the hotkey doesn't conflict with other applications."
        )
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        # Main layout for the page
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
        self.registerField("hotkey", self.hotkey_combo, "currentText")
    
    def get_hotkey(self):
        """Get selected hotkey (without description)."""
        text = self.hotkey_combo.currentText()
        return text.split(" ")[0]  # Remove "(recommended)" etc.


class AudioDevicePage(QWizardPage):
    """Audio device selection page."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Audio Device")
        self.setSubTitle("Select your microphone")
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Instructions
        instructions = QLabel(
            "<p>Select the microphone you want to use for dictation.</p>"
            "<p>If you're not sure, the default device usually works fine.</p>"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Device selection
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Microphone:"))
        
        self.device_combo = QComboBox()
        self._populate_devices()
        device_layout.addWidget(self.device_combo)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._populate_devices)
        device_layout.addWidget(refresh_btn)
        
        layout.addLayout(device_layout)
        
        # Test recording
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test Microphone")
        self.test_btn.clicked.connect(self._test_microphone)
        test_layout.addWidget(self.test_btn)
        test_layout.addStretch()
        layout.addLayout(test_layout)
        
        self.test_result = QLabel()
        layout.addWidget(self.test_result)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        # Main layout for the page
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
        self.registerField("audio_device", self.device_combo, "currentText")
    
    def _populate_devices(self):
        """Populate audio device list."""
        self.device_combo.clear()
        self.device_combo.addItem("Default Device", -1)
        
        try:
            devices = sd.query_devices()
            for idx, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    name = device['name']
                    self.device_combo.addItem(f"{idx}: {name}", idx)
        except Exception as e:
            self.test_result.setText(f"⚠ Could not list devices: {e}")
            self.test_result.setStyleSheet("color: orange;")
    
    def _test_microphone(self):
        """Test selected microphone."""
        device_idx = self.device_combo.currentData()
        
        try:
            self.test_result.setText("Recording 2 seconds...")
            self.test_result.setStyleSheet("color: blue;")
            
            # Record 2 seconds
            duration = 2
            sample_rate = 16000
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                device=device_idx if device_idx != -1 else None
            )
            sd.wait()
            
            # Check if audio was captured
            import numpy as np
            max_amplitude = np.max(np.abs(recording))
            
            if max_amplitude > 0.01:
                self.test_result.setText(f"✓ Microphone working! (level: {max_amplitude:.2f})")
                self.test_result.setStyleSheet("color: green;")
            else:
                self.test_result.setText("⚠ No audio detected. Try speaking louder or select a different device.")
                self.test_result.setStyleSheet("color: orange;")
                
        except Exception as e:
            self.test_result.setText(f"✗ Test failed: {e}")
            self.test_result.setStyleSheet("color: red;")
    
    def get_device_index(self):
        """Get selected device index."""
        return self.device_combo.currentData()


class CompletePage(QWizardPage):
    """Completion page with summary."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Setup Complete!")
        self.setSubTitle("You're ready to start dictating")
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Success message
        success = QLabel(
            "<h3>✓ Configuration Saved</h3>"
            "<p>DictaPilot3 is now configured and ready to use.</p>"
        )
        layout.addWidget(success)
        
        # Summary
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(150)
        layout.addWidget(QLabel("<b>Your Configuration:</b>"))
        layout.addWidget(self.summary_text)
        
        # Next steps
        next_steps = QLabel(
            "<h4>Next Steps:</h4>"
            "<ol>"
            "<li>Click <b>Finish</b> to close this wizard</li>"
            "<li>DictaPilot will start automatically</li>"
            "<li>Open any text editor</li>"
            "<li>Hold <b>F9</b> (or your chosen hotkey)</li>"
            "<li>Speak naturally</li>"
            "<li>Release the hotkey</li>"
            "<li>Your text appears!</li>"
            "</ol>"
            "<p><b>Learn more:</b></p>"
            "<ul>"
            "<li><a href='file:///docs/voice-commands.md'>Voice Commands Reference</a></li>"
            "<li><a href='file:///docs/troubleshooting.md'>Troubleshooting Guide</a></li>"
            "<li><a href='file:///docs/faq.md'>FAQ</a></li>"
            "</ul>"
        )
        next_steps.setWordWrap(True)
        next_steps.setOpenExternalLinks(True)
        layout.addWidget(next_steps)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        # Main layout for the page
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def initializePage(self):
        """Initialize page with configuration summary."""
        wizard = self.wizard()
        
        # Get configuration
        api_key = wizard.field("api_key")
        hotkey = wizard.page(2).get_hotkey()  # HotkeyPage
        device_idx = wizard.page(3).get_device_index()  # AudioDevicePage
        
        # Build summary
        summary = f"""
API Key: {api_key[:10]}...{api_key[-4:]}
Hotkey: {hotkey}
Audio Device: {"Default" if device_idx == -1 else f"Device {device_idx}"}
        """.strip()
        
        self.summary_text.setPlainText(summary)


class OnboardingWizard(QWizard):
    """Main onboarding wizard."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("DictaPilot3 Setup Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.HaveHelpButton, False)
        self.setOption(QWizard.CancelButtonOnLeft, True)
        
        # Add pages
        self.welcome_page = WelcomePage()
        self.api_key_page = APIKeyPage()
        self.hotkey_page = HotkeyPage()
        self.audio_device_page = AudioDevicePage()
        self.complete_page = CompletePage()
        
        self.addPage(self.welcome_page)
        self.addPage(self.api_key_page)
        self.addPage(self.hotkey_page)
        self.addPage(self.audio_device_page)
        self.addPage(self.complete_page)
        
        # Set minimum size
        self.setMinimumSize(700, 600)
        self.resize(750, 650)
    
    def accept(self):
        """Save configuration when wizard is completed."""
        try:
            self._save_configuration()
            super().accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Configuration Error",
                f"Failed to save configuration:\n\n{e}"
            )
    
    def _save_configuration(self):
        """Save configuration to .env file."""
        env_path = Path(__file__).parent / ".env"
        
        # Get values
        api_key = self.field("api_key")
        hotkey = self.hotkey_page.get_hotkey()
        device_idx = self.audio_device_page.get_device_index()
        
        # Create or update .env
        if not env_path.exists():
            env_path.touch()
        
        # Set values
        set_key(str(env_path), "GROQ_API_KEY", api_key)
        set_key(str(env_path), "HOTKEY", hotkey)
        
        if device_idx != -1:
            set_key(str(env_path), "AUDIO_DEVICE", str(device_idx))
        
        # Mark setup as completed
        set_key(str(env_path), "SETUP_COMPLETED", "1")


def run_wizard():
    """Run the onboarding wizard."""
    if not PYSIDE6_AVAILABLE:
        print("Error: PySide6 not available. Cannot run wizard.")
        print("Install with: pip install PySide6")
        return False
    
    from PySide6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    wizard = OnboardingWizard()
    result = wizard.exec()
    
    return result == QWizard.Accepted


if __name__ == "__main__":
    success = run_wizard()
    sys.exit(0 if success else 1)
