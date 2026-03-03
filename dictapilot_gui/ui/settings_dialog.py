"""
DictaPilot GUI Settings Dialog
Modal dialog for configuring application settings
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QGroupBox, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt

from ..config.settings import Settings, get_settings
from ..stt.transcriber import Transcriber


class SettingsDialog(QDialog):
    """
    Settings dialog for DictaPilot GUI
    Allows configuration of model, language, device, and UI options
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(450)
        self.setModal(True)
        
        self.settings = get_settings()
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Model Settings Group
        model_group = QGroupBox("Model Settings")
        model_layout = QFormLayout(model_group)
        model_layout.setSpacing(12)
        
        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.settings.get_available_models())
        self.model_combo.setToolTip(
            "Select Whisper model size.\n"
            "tiny: Fastest, lowest accuracy\n"
            "base: Good balance for most use cases\n"
            "small: Better accuracy, slower\n"
            "medium: Best accuracy, slowest"
        )
        model_layout.addRow("Model:", self.model_combo)
        
        # Language selection
        self.language_combo = QComboBox()
        for code, name in self.settings.get_available_languages():
            self.language_combo.addItem(name, code)
        self.language_combo.setToolTip("Select transcription language or auto-detect")
        model_layout.addRow("Language:", self.language_combo)
        
        # Translate to English
        self.translate_check = QCheckBox("Translate to English")
        self.translate_check.setToolTip(
            "Translate non-English speech to English text"
        )
        model_layout.addRow("", self.translate_check)
        
        layout.addWidget(model_group)
        
        # Device Settings Group
        device_group = QGroupBox("Device Settings")
        device_layout = QFormLayout(device_group)
        device_layout.setSpacing(12)
        
        # Device selection
        self.device_combo = QComboBox()
        devices = self.settings.get_available_devices()
        for value, label in devices:
            self.device_combo.addItem(label, value)
        
        # Disable CUDA if not available
        if len(devices) == 1:
            self.device_combo.setEnabled(False)
            self.device_combo.setToolTip("CUDA not available on this system")
        else:
            self.device_combo.setToolTip(
                "Select compute device for transcription\n"
                "CPU: Works everywhere, slower\n"
                "CUDA: Requires NVIDIA GPU, much faster"
            )
        device_layout.addRow("Device:", self.device_combo)
        
        layout.addWidget(device_group)
        
        # UI Settings Group
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout(ui_group)
        ui_layout.setSpacing(12)
        
        # Monospace font option
        self.monospace_check = QCheckBox("Use monospace font for transcription")
        self.monospace_check.setToolTip(
            "Use monospace font (better for code)"
        )
        ui_layout.addRow("", self.monospace_check)
        
        layout.addWidget(ui_group)
        
        # Add stretch to push buttons to bottom
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.setToolTip("Reset all settings to default values")
        self.reset_btn.clicked.connect(self._reset_defaults)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def _load_settings(self):
        """Load current settings into UI"""
        # Model
        index = self.model_combo.findText(self.settings.model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        
        # Language
        lang_index = self.language_combo.findData(self.settings.language)
        if lang_index >= 0:
            self.language_combo.setCurrentIndex(lang_index)
        
        # Translate
        self.translate_check.setChecked(self.settings.translate_to_english)
        
        # Device
        device_index = self.device_combo.findData(self.settings.device)
        if device_index >= 0:
            self.device_combo.setCurrentIndex(device_index)
        
        # UI
        self.monospace_check.setChecked(self.settings.monospace_font)
    
    def _save_settings(self):
        """Save settings from UI"""
        try:
            # Update settings object
            self.settings.model = self.model_combo.currentText()
            self.settings.language = self.language_combo.currentData()
            self.settings.translate_to_english = self.translate_check.isChecked()
            self.settings.device = self.device_combo.currentData()
            self.settings.monospace_font = self.monospace_check.isChecked()
            
            # Save to file
            self.settings.save()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings: {str(e)}"
            )
    
    def _reset_defaults(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.settings = Settings()  # Create new with defaults
            self._load_settings()
