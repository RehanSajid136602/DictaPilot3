"""
DictaPilot Settings Dashboard
Comprehensive Qt6-based settings management interface.

MIT License
Copyright (c) 2026 Rehan
"""

import os
import sys
import json
import platform
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, asdict

try:
    from PySide6.QtCore import Qt, Signal, QSize, QTimer
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QLabel, QLineEdit, QPushButton, QComboBox,
        QCheckBox, QSpinBox, QDoubleSpinBox, QSlider,
        QListWidget, QListWidgetItem, QTextEdit, QGroupBox,
        QFormLayout, QScrollArea, QMessageBox, QFileDialog,
        QInputDialog, QSplitter, QFrame, QToolBar, QStatusBar,
        QSystemTrayIcon, QMenu, QApplication, QSizePolicy
    )
    from PySide6.QtGui import (
        QFont, QIcon, QPixmap, QColor, QPalette, QAction,
        QKeySequence, QShortcut
    )
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    QMainWindow = object

import sounddevice as sd

from config import DictaPilotConfig, load_config, get_config_path, get_config_dir
from transcription_store import get_store, save_store, TranscriptionEntry


# ============================================================================
# Theme Styles
# ============================================================================

DARK_THEME = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QTabWidget::pane {
    border: 1px solid #45475a;
    background-color: #1e1e2e;
    border-radius: 8px;
}
QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background-color: #45475a;
    color: #cdd6f4;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #3b3b4f;
}
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #89b4fa;
}
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px;
    color: #cdd6f4;
    selection-background-color: #45475a;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #89b4fa;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #89b4fa;
}
QPushButton {
    background-color: #45475a;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    color: #cdd6f4;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #585b70;
}
QPushButton:pressed {
    background-color: #313244;
}
QPushButton:disabled {
    background-color: #313244;
    color: #585b70;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #45475a;
    background-color: #313244;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QSlider::groove:horizontal {
    height: 8px;
    background: #313244;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #89b4fa;
    border: none;
    width: 18px;
    margin: -5px 0;
    border-radius: 9px;
}
QListWidget {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #45475a;
}
QListWidget::item:hover:!selected {
    background-color: #3b3b4f;
}
QScrollBar:vertical {
    background: #1e1e2e;
    width: 12px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 6px;
    min-height: 20px;
}
QLabel {
    color: #cdd6f4;
}
QLabel[heading="true"] {
    font-size: 16px;
    font-weight: bold;
    color: #89b4fa;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
}
QToolBar {
    background-color: #181825;
    border: none;
    spacing: 8px;
}
QMenu {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #45475a;
}
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px;
}
"""

LIGHT_THEME = """
QMainWindow, QWidget {
    background-color: #f5f5f5;
    color: #1e1e2e;
}
QTabWidget::pane {
    border: 1px solid #ddd;
    background-color: #ffffff;
    border-radius: 8px;
}
QTabBar::tab {
    background-color: #e0e0e0;
    color: #555;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    color: #1e1e2e;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #d0d0d0;
}
QGroupBox {
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #2196f3;
}
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px;
    color: #1e1e2e;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #2196f3;
}
QPushButton {
    background-color: #2196f3;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    color: #ffffff;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1976d2;
}
QPushButton:pressed {
    background-color: #1565c0;
}
QPushButton:disabled {
    background-color: #bdbdbd;
    color: #757575;
}
QCheckBox::indicator:checked {
    background-color: #2196f3;
    border-color: #2196f3;
}
QSlider::handle:horizontal {
    background: #2196f3;
}
QListWidget {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 6px;
}
QListWidget::item:selected {
    background-color: #e3f2fd;
    color: #1e1e2e;
}
QStatusBar {
    background-color: #e0e0e0;
    color: #555;
}
QToolBar {
    background-color: #e0e0e0;
}
"""


# ============================================================================
# Base Tab Widget
# ============================================================================

class BaseSettingsTab(QWidget):
    """Base class for settings tabs with common functionality."""
    
    config_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = None
        self._widgets = {}
        
        # Create scroll area for content
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Content widget
        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)
        
        self.scroll.setWidget(self.content)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)
        self.setLayout(main_layout)
    
    def set_config(self, config: DictaPilotConfig):
        """Set configuration and update widgets."""
        self._config = config
        self._load_config()
    
    def _load_config(self):
        """Override to load config into widgets."""
        pass
    
    def get_config(self) -> DictaPilotConfig:
        """Override to get config from widgets."""
        return self._config
    
    def add_heading(self, text: str):
        """Add a section heading."""
        label = QLabel(text)
        label.setProperty("heading", True)
        label.setStyleSheet("font-size: 16px; font-weight: bold; color: #89b4fa; margin-top: 8px;")
        self.layout.addWidget(label)
    
    def add_widget(self, name: str, widget: QWidget, label: str = None):
        """Add a widget with optional label."""
        if label:
            form_layout = QFormLayout()
            form_layout.addRow(label, widget)
            container = QWidget()
            container.setLayout(form_layout)
            self.layout.addWidget(container)
        else:
            self.layout.addWidget(widget)
        self._widgets[name] = widget
    
    def add_group(self, title: str) -> QGroupBox:
        """Add a group box."""
        group = QGroupBox(title)
        group.setLayout(QVBoxLayout())
        self.layout.addWidget(group)
        return group
    
    def add_stretch(self):
        """Add stretch to push content up."""
        self.layout.addStretch()


# ============================================================================
# General Settings Tab
# ============================================================================

class GeneralSettingsTab(BaseSettingsTab):
    """General settings: hotkeys, models, modes."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        # Mode Selection
        mode_group = self.add_group("Mode Selection")
        mode_layout = mode_group.layout()
        
        mode_form = QFormLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["dictation", "agent"])
        self.mode_combo.setToolTip("Dictation: standard text input\nAgent: structured coding tasks")
        mode_form.addRow("Mode:", self.mode_combo)
        
        self.agent_auto_detect = QCheckBox("Auto-detect agent mode from speech")
        self.agent_auto_detect.setToolTip("Automatically switch to agent mode when speech contains coding keywords")
        mode_form.addRow("", self.agent_auto_detect)
        
        mode_layout.addLayout(mode_form)
        
        # Hotkey Settings
        hotkey_group = self.add_group("Hotkey Settings")
        hotkey_layout = hotkey_group.layout()
        
        hotkey_form = QFormLayout()
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems(["f9", "f10", "f11", "f12", "ctrl+shift+d", "alt+space"])
        self.hotkey_combo.setEditable(True)
        hotkey_form.addRow("Recording Hotkey:", self.hotkey_combo)
        
        self.hold_to_talk = QCheckBox("Hold to talk (uncheck for toggle mode)")
        hotkey_form.addRow("", self.hold_to_talk)
        
        hotkey_layout.addLayout(hotkey_form)
        
        # Model Settings
        model_group = self.add_group("Model Settings")
        model_layout = model_group.layout()
        
        model_form = QFormLayout()
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "whisper-large-v3-turbo",
            "whisper-large-v3",
            "whisper-medium",
            "whisper-small",
            "whisper-tiny"
        ])
        self.model_combo.setEditable(True)
        model_form.addRow("Whisper Model:", self.model_combo)
        
        self.whisper_backend = QComboBox()
        self.whisper_backend.addItems(["groq", "local"])
        model_form.addRow("Backend:", self.whisper_backend)
        
        model_layout.addLayout(model_form)
        
        # Paste Settings
        paste_group = self.add_group("Paste Settings")
        paste_layout = paste_group.layout()
        
        paste_form = QFormLayout()
        self.paste_mode = QComboBox()
        self.paste_mode.addItems(["delta", "full"])
        self.paste_mode.setToolTip("Delta: only paste changed characters\nFull: select all and replace")
        paste_form.addRow("Paste Mode:", self.paste_mode)
        
        self.paste_backend = QComboBox()
        self.paste_backend.addItems(["auto", "wayland", "x11", "pynput", "xdotool", "keyboard"])
        paste_form.addRow("Paste Backend:", self.paste_backend)
        
        self.paste_policy = QComboBox()
        self.paste_policy.addItems(["final_only", "live_preview"])
        self.paste_policy.setToolTip("Final only: paste after recording\nLive preview: show partial results")
        paste_form.addRow("Paste Policy:", self.paste_policy)
        
        paste_layout.addLayout(paste_form)
        
        # UI Settings
        ui_group = self.add_group("UI Settings")
        ui_layout = ui_group.layout()
        
        ui_form = QFormLayout()
        self.ui_theme = QComboBox()
        self.ui_theme.addItems(["dark", "light"])
        self.ui_theme.currentTextChanged.connect(self._on_theme_change)
        ui_form.addRow("Theme:", self.ui_theme)
        
        self.auto_copy = QCheckBox("Auto-copy on finalize")
        ui_form.addRow("", self.auto_copy)
        
        self.voice_commands = QCheckBox("Voice commands enabled")
        self.voice_commands.setToolTip("Process voice commands like 'delete that', 'new paragraph'")
        ui_form.addRow("", self.voice_commands)
        
        ui_layout.addLayout(ui_form)
        
        self.add_stretch()
    
    def _on_theme_change(self, theme: str):
        """Emit signal when theme changes."""
        self.config_changed.emit()
    
    def _load_config(self):
        if not self._config:
            return
        
        self.mode_combo.setCurrentText(self._config.mode)
        self.agent_auto_detect.setChecked(self._config.agent_auto_detect)
        self.hotkey_combo.setCurrentText(self._config.hotkey)
        self.hold_to_talk.setChecked(self._config.hold_to_talk)
        self.model_combo.setCurrentText(self._config.model)
        self.whisper_backend.setCurrentText(self._config.whisper_backend)
        self.paste_mode.setCurrentText(self._config.paste_mode)
        self.paste_backend.setCurrentText(self._config.paste_backend)
        self.paste_policy.setCurrentText(self._config.paste_policy)
        self.ui_theme.setCurrentText(self._config.ui_theme)
        self.auto_copy.setChecked(self._config.auto_copy_on_finalize)
        self.voice_commands.setChecked(self._config.voice_commands_enabled)
    
    def get_config(self) -> DictaPilotConfig:
        if not self._config:
            return None
        
        self._config.mode = self.mode_combo.currentText()
        self._config.agent_auto_detect = self.agent_auto_detect.isChecked()
        self._config.hotkey = self.hotkey_combo.currentText()
        self._config.hold_to_talk = self.hold_to_talk.isChecked()
        self._config.model = self.model_combo.currentText()
        self._config.whisper_backend = self.whisper_backend.currentText()
        self._config.paste_mode = self.paste_mode.currentText()
        self._config.paste_backend = self.paste_backend.currentText()
        self._config.paste_policy = self.paste_policy.currentText()
        self._config.ui_theme = self.ui_theme.currentText()
        self._config.auto_copy_on_finalize = self.auto_copy.isChecked()
        self._config.voice_commands_enabled = self.voice_commands.isChecked()
        
        return self._config


# ============================================================================
# Audio Settings Tab
# ============================================================================

class AudioSettingsTab(BaseSettingsTab):
    """Audio settings: device, VAD, sample rate."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        # Audio Device
        device_group = self.add_group("Audio Device")
        device_layout = device_group.layout()
        
        device_form = QFormLayout()
        
        device_row = QHBoxLayout()
        self.device_combo = QComboBox()
        self._populate_devices()
        device_row.addWidget(self.device_combo)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._populate_devices)
        device_row.addWidget(refresh_btn)
        
        device_form.addRow("Microphone:", device_row)
        
        # Test button
        test_row = QHBoxLayout()
        self.test_btn = QPushButton("Test Microphone")
        self.test_btn.clicked.connect(self._test_microphone)
        test_row.addWidget(self.test_btn)
        self.test_result = QLabel()
        test_row.addWidget(self.test_result)
        test_row.addStretch()
        device_form.addRow("", test_row)
        
        device_layout.addLayout(device_form)
        
        # VAD Settings
        vad_group = self.add_group("Voice Activity Detection (VAD)")
        vad_layout = vad_group.layout()
        
        vad_form = QFormLayout()
        self.vad_enabled = QCheckBox("Enable VAD")
        self.vad_enabled.setToolTip("Automatically detect speech start/end")
        vad_form.addRow("", self.vad_enabled)
        
        self.chunk_duration = QDoubleSpinBox()
        self.chunk_duration.setRange(0.1, 5.0)
        self.chunk_duration.setSingleStep(0.1)
        self.chunk_duration.setValue(0.5)
        self.chunk_duration.setToolTip("Duration of audio chunks for processing")
        vad_form.addRow("Chunk Duration (s):", self.chunk_duration)
        
        vad_layout.addLayout(vad_form)
        
        # Streaming Settings
        stream_group = self.add_group("Streaming Transcription")
        stream_layout = stream_group.layout()
        
        stream_form = QFormLayout()
        
        self.streaming_enabled = QCheckBox("Enable streaming")
        self.streaming_enabled.setToolTip("Show partial results while speaking")
        stream_form.addRow("", self.streaming_enabled)
        
        self.stream_chunk_duration = QDoubleSpinBox()
        self.stream_chunk_duration.setRange(0.5, 5.0)
        self.stream_chunk_duration.setSingleStep(0.1)
        self.stream_chunk_duration.setValue(1.5)
        stream_form.addRow("Stream Chunk (s):", self.stream_chunk_duration)
        
        self.stream_overlap = QDoubleSpinBox()
        self.stream_overlap.setRange(0.1, 1.0)
        self.stream_overlap.setSingleStep(0.1)
        self.stream_overlap.setValue(0.3)
        stream_form.addRow("Overlap (s):", self.stream_overlap)
        
        self.stream_min_chunks = QSpinBox()
        self.stream_min_chunks.setRange(1, 10)
        self.stream_min_chunks.setValue(2)
        stream_form.addRow("Min Chunks:", self.stream_min_chunks)
        
        self.stream_final_pass = QCheckBox("Run final accuracy pass")
        stream_form.addRow("", self.stream_final_pass)
        
        stream_layout.addLayout(stream_form)
        
        self.add_stretch()
    
    def _populate_devices(self):
        """Populate audio device list."""
        self.device_combo.clear()
        self.device_combo.addItem("Default Device", "")
        
        try:
            devices = sd.query_devices()
            for idx, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    self.device_combo.addItem(f"{idx}: {device['name']}", str(idx))
        except Exception as e:
            self.test_result.setText(f"Error: {e}")
            self.test_result.setStyleSheet("color: red;")
    
    def _test_microphone(self):
        """Test selected microphone."""
        device_data = self.device_combo.currentData()
        device_idx = int(device_data) if device_data else None
        
        try:
            self.test_result.setText("Recording 2s...")
            self.test_result.setStyleSheet("color: #89b4fa;")
            
            duration = 2
            sample_rate = 16000
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                device=device_idx
            )
            sd.wait()
            
            import numpy as np
            max_amp = np.max(np.abs(recording))
            
            if max_amp > 0.01:
                self.test_result.setText(f"Working! Level: {max_amp:.2f}")
                self.test_result.setStyleSheet("color: green;")
            else:
                self.test_result.setText("No audio detected")
                self.test_result.setStyleSheet("color: orange;")
        except Exception as e:
            self.test_result.setText(f"Error: {e}")
            self.test_result.setStyleSheet("color: red;")
    
    def _load_config(self):
        if not self._config:
            return
        
        # Set device
        idx = self.device_combo.findData(self._config.audio_device)
        if idx >= 0:
            self.device_combo.setCurrentIndex(idx)
        
        self.vad_enabled.setChecked(self._config.vad_enabled)
        self.chunk_duration.setValue(self._config.chunk_duration)
        self.streaming_enabled.setChecked(self._config.streaming_enabled)
        self.stream_chunk_duration.setValue(self._config.streaming_chunk_duration)
        self.stream_overlap.setValue(self._config.streaming_chunk_overlap)
        self.stream_min_chunks.setValue(self._config.streaming_min_chunks)
        self.stream_final_pass.setChecked(self._config.streaming_final_pass)
    
    def get_config(self) -> DictaPilotConfig:
        if not self._config:
            return None
        
        self._config.audio_device = self.device_combo.currentData() or ""
        self._config.vad_enabled = self.vad_enabled.isChecked()
        self._config.chunk_duration = self.chunk_duration.value()
        self._config.streaming_enabled = self.streaming_enabled.isChecked()
        self._config.streaming_chunk_duration = self.stream_chunk_duration.value()
        self._config.streaming_chunk_overlap = self.stream_overlap.value()
        self._config.streaming_min_chunks = self.stream_min_chunks.value()
        self._config.streaming_final_pass = self.stream_final_pass.isChecked()
        
        return self._config


# ============================================================================
# Smart Editing Tab
# ============================================================================

class SmartEditingTab(BaseSettingsTab):
    """Smart editing settings: cleanup, LLM, commands."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        # Smart Edit Settings
        edit_group = self.add_group("Smart Editing")
        edit_layout = edit_group.layout()
        
        edit_form = QFormLayout()
        
        self.smart_edit = QCheckBox("Enable smart editing")
        self.smart_edit.setToolTip("Apply intelligent text cleanup")
        edit_form.addRow("", self.smart_edit)
        
        self.smart_mode = QComboBox()
        self.smart_mode.addItems(["llm", "heuristic", "hybrid"])
        edit_form.addRow("Mode:", self.smart_mode)
        
        self.llm_always_clean = QCheckBox("Always clean with LLM")
        edit_form.addRow("", self.llm_always_clean)
        
        edit_layout.addLayout(edit_form)
        
        # Cleanup Settings
        cleanup_group = self.add_group("Cleanup Settings")
        cleanup_layout = cleanup_group.layout()
        
        cleanup_form = QFormLayout()
        
        self.cleanup_strictness = QComboBox()
        self.cleanup_strictness.addItems(["conservative", "balanced", "aggressive"])
        self.cleanup_strictness.setToolTip("Conservative: minimal changes\nBalanced: moderate cleanup\nAggressive: thorough cleanup")
        cleanup_form.addRow("Strictness:", self.cleanup_strictness)
        
        self.user_adaptation = QCheckBox("Enable user adaptation")
        self.user_adaptation.setToolTip("Learn from your corrections over time")
        cleanup_form.addRow("", self.user_adaptation)
        
        cleanup_layout.addLayout(cleanup_form)
        
        # Confidence Settings
        conf_group = self.add_group("Confidence Thresholds")
        conf_layout = conf_group.layout()
        
        conf_form = QFormLayout()
        
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(65)
        self.confidence_label = QLabel("0.65")
        self.confidence_slider.valueChanged.connect(
            lambda v: self.confidence_label.setText(f"{v/100:.2f}")
        )
        conf_row = QHBoxLayout()
        conf_row.addWidget(self.confidence_slider)
        conf_row.addWidget(self.confidence_label)
        conf_form.addRow("Threshold:", conf_row)
        
        conf_layout.addLayout(conf_form)
        
        # Voice Commands Reference
        cmd_group = self.add_group("Voice Commands")
        cmd_layout = cmd_group.layout()
        
        cmd_text = QTextEdit()
        cmd_text.setReadOnly(True)
        cmd_text.setMaximumHeight(200)
        cmd_text.setHtml("""
        <style>
            li { margin: 4px 0; }
            b { color: #89b4fa; }
        </style>
        <h4>Available Commands:</h4>
        <ul>
            <li><b>"delete that"</b> - Remove last utterance</li>
            <li><b>"new paragraph"</b> - Insert paragraph break</li>
            <li><b>"new line"</b> - Insert line break</li>
            <li><b>"capitalize [word]"</b> - Capitalize next/last word</li>
            <li><b>"replace X with Y"</b> - Replace text</li>
            <li><b>"scratch that"</b> - Delete last sentence</li>
            <li><b>"comma" / "period"</b> - Insert punctuation</li>
        </ul>
        """)
        cmd_layout.addWidget(cmd_text)
        
        self.add_stretch()
    
    def _load_config(self):
        if not self._config:
            return
        
        self.smart_edit.setChecked(self._config.smart_edit)
        self.smart_mode.setCurrentText(self._config.smart_mode)
        self.llm_always_clean.setChecked(self._config.llm_always_clean)
        self.cleanup_strictness.setCurrentText(self._config.cleanup_strictness)
        self.user_adaptation.setChecked(self._config.user_adaptation)
        self.confidence_slider.setValue(int(self._config.confidence_threshold * 100))
    
    def get_config(self) -> DictaPilotConfig:
        if not self._config:
            return None
        
        self._config.smart_edit = self.smart_edit.isChecked()
        self._config.smart_mode = self.smart_mode.currentText()
        self._config.llm_always_clean = self.llm_always_clean.isChecked()
        self._config.cleanup_strictness = self.cleanup_strictness.currentText()
        self._config.user_adaptation = self.user_adaptation.isChecked()
        self._config.confidence_threshold = self.confidence_slider.value() / 100
        
        return self._config


# ============================================================================
# Profiles Tab
# ============================================================================

class ProfilesTab(BaseSettingsTab):
    """Context-aware profile management."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._profiles = {}
        self._build_ui()
        self._load_profiles()
    
    def _build_ui(self):
        # Main layout with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - profile list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.profile_list = QListWidget()
        self.profile_list.currentItemChanged.connect(self._on_profile_select)
        left_layout.addWidget(QLabel("Profiles:"))
        left_layout.addWidget(self.profile_list)
        
        # Profile buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_profile)
        btn_layout.addWidget(add_btn)
        
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self._delete_profile)
        btn_layout.addWidget(del_btn)
        left_layout.addLayout(btn_layout)
        
        # Right panel - profile details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Profile name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.profile_name = QLineEdit()
        name_layout.addWidget(self.profile_name)
        right_layout.addLayout(name_layout)
        
        # Profile settings
        self.profile_settings = QTextEdit()
        self.profile_settings.setPlaceholderText("Profile settings in JSON format...")
        right_layout.addWidget(QLabel("Settings:"))
        right_layout.addWidget(self.profile_settings)
        
        # Trigger apps
        self.trigger_apps = QTextEdit()
        self.trigger_apps.setPlaceholderText("One app name per line (e.g., code, vim, cursor)")
        self.trigger_apps.setMaximumHeight(100)
        right_layout.addWidget(QLabel("Trigger Apps:"))
        right_layout.addWidget(self.trigger_apps)
        
        # Save button
        save_btn = QPushButton("Save Profile")
        save_btn.clicked.connect(self._save_profile)
        right_layout.addWidget(save_btn)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 400])
        
        self.layout.addWidget(splitter)
        
        # Active profile
        active_group = self.add_group("Active Profile")
        active_layout = active_group.layout()
        
        active_form = QFormLayout()
        self.active_profile_combo = QComboBox()
        active_form.addRow("Active Profile:", self.active_profile_combo)
        active_layout.addLayout(active_form)
    
    def _load_profiles(self):
        """Load profiles from config directory."""
        profile_dir = get_config_dir() / "profiles"
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        # Load default profile
        self._profiles = {"default": {"settings": {}, "triggers": []}}
        
        # Load saved profiles
        for profile_file in profile_dir.glob("*.json"):
            try:
                with open(profile_file) as f:
                    data = json.load(f)
                name = profile_file.stem
                self._profiles[name] = data
            except Exception:
                pass
        
        self._refresh_list()
    
    def _refresh_list(self):
        """Refresh profile list."""
        self.profile_list.clear()
        self.active_profile_combo.clear()
        
        for name in sorted(self._profiles.keys()):
            self.profile_list.addItem(name)
            self.active_profile_combo.addItem(name)
    
    def _on_profile_select(self, current, previous):
        """Handle profile selection."""
        if not current:
            return
        
        name = current.text()
        profile = self._profiles.get(name, {})
        
        self.profile_name.setText(name)
        self.profile_settings.setPlainText(
            json.dumps(profile.get("settings", {}), indent=2)
        )
        self.trigger_apps.setPlainText(
            "\n".join(profile.get("triggers", []))
        )
    
    def _add_profile(self):
        """Add new profile."""
        name, ok = QInputDialog.getText(self, "New Profile", "Profile name:")
        if ok and name:
            if name in self._profiles:
                QMessageBox.warning(self, "Error", "Profile already exists")
                return
            
            self._profiles[name] = {"settings": {}, "triggers": []}
            self._refresh_list()
            self._save_profile_to_disk(name)
    
    def _delete_profile(self):
        """Delete selected profile."""
        current = self.profile_list.currentItem()
        if not current:
            return
        
        name = current.text()
        if name == "default":
            QMessageBox.warning(self, "Error", "Cannot delete default profile")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete profile '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self._profiles[name]
            self._refresh_list()
            
            # Delete file
            profile_file = get_config_dir() / "profiles" / f"{name}.json"
            if profile_file.exists():
                profile_file.unlink()
    
    def _save_profile(self):
        """Save current profile."""
        name = self.profile_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Profile name required")
            return
        
        try:
            settings = json.loads(self.profile_settings.toPlainText())
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", "Invalid JSON in settings")
            return
        
        triggers = [
            line.strip()
            for line in self.trigger_apps.toPlainText().split("\n")
            if line.strip()
        ]
        
        self._profiles[name] = {"settings": settings, "triggers": triggers}
        self._save_profile_to_disk(name)
        self._refresh_list()
        
        QMessageBox.information(self, "Saved", f"Profile '{name}' saved")
    
    def _save_profile_to_disk(self, name: str):
        """Save profile to disk."""
        profile_dir = get_config_dir() / "profiles"
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        profile_file = profile_dir / f"{name}.json"
        with open(profile_file, "w") as f:
            json.dump(self._profiles[name], f, indent=2)
    
    def _load_config(self):
        if not self._config:
            return
        
        idx = self.active_profile_combo.findText(self._config.active_profile)
        if idx >= 0:
            self.active_profile_combo.setCurrentIndex(idx)
    
    def get_config(self) -> DictaPilotConfig:
        if not self._config:
            return None
        
        self._config.active_profile = self.active_profile_combo.currentText()
        return self._config


# ============================================================================
# Dictionary Tab
# ============================================================================

class DictionaryTab(BaseSettingsTab):
    """Personal dictionary management."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dictionary = {}
        self._build_ui()
        self._load_dictionary()
    
    def _build_ui(self):
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search dictionary...")
        self.search_input.textChanged.connect(self._filter_dictionary)
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)
        
        # Dictionary list
        self.dict_list = QListWidget()
        self.dict_list.currentItemChanged.connect(self._on_entry_select)
        self.layout.addWidget(self.dict_list)
        
        # Entry editor
        entry_group = self.add_group("Entry")
        entry_layout = entry_group.layout()
        
        entry_form = QFormLayout()
        self.entry_word = QLineEdit()
        self.entry_word.setPlaceholderText("Word/phrase")
        entry_form.addRow("Word:", self.entry_word)
        
        self.entry_replacement = QLineEdit()
        self.entry_replacement.setPlaceholderText("Replacement (optional)")
        entry_form.addRow("Replacement:", self.entry_replacement)
        
        entry_layout.addLayout(entry_form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_entry)
        btn_layout.addWidget(add_btn)
        
        update_btn = QPushButton("Update")
        update_btn.clicked.connect(self._update_entry)
        btn_layout.addWidget(update_btn)
        
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self._delete_entry)
        btn_layout.addWidget(del_btn)
        
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self._import_dictionary)
        btn_layout.addWidget(import_btn)
        
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self._export_dictionary)
        btn_layout.addWidget(export_btn)
        
        self.layout.addLayout(btn_layout)
        
        # Info
        info = QLabel("Dictionary entries are used to correct common transcription errors.")
        info.setWordWrap(True)
        self.layout.addWidget(info)
        
        self.add_stretch()
    
    def _load_dictionary(self):
        """Load dictionary from file."""
        dict_file = get_config_dir() / "dictionary.json"
        if dict_file.exists():
            try:
                with open(dict_file) as f:
                    self._dictionary = json.load(f)
            except Exception:
                self._dictionary = {}
        self._refresh_list()
    
    def _save_dictionary(self):
        """Save dictionary to file."""
        dict_file = get_config_dir() / "dictionary.json"
        with open(dict_file, "w") as f:
            json.dump(self._dictionary, f, indent=2)
    
    def _refresh_list(self):
        """Refresh dictionary list."""
        self.dict_list.clear()
        for word, replacement in sorted(self._dictionary.items()):
            item = QListWidgetItem(f"{word} → {replacement}")
            item.setData(Qt.UserRole, word)
            self.dict_list.addItem(item)
    
    def _filter_dictionary(self, text: str):
        """Filter dictionary list."""
        text = text.lower()
        for i in range(self.dict_list.count()):
            item = self.dict_list.item(i)
            item.setHidden(text not in item.text().lower())
    
    def _on_entry_select(self, current, previous):
        """Handle entry selection."""
        if not current:
            return
        
        word = current.data(Qt.UserRole)
        self.entry_word.setText(word)
        self.entry_replacement.setText(self._dictionary.get(word, ""))
    
    def _add_entry(self):
        """Add new dictionary entry."""
        word = self.entry_word.text().strip()
        replacement = self.entry_replacement.text().strip()
        
        if not word:
            QMessageBox.warning(self, "Error", "Word required")
            return
        
        self._dictionary[word] = replacement
        self._save_dictionary()
        self._refresh_list()
    
    def _update_entry(self):
        """Update selected entry."""
        self._add_entry()
    
    def _delete_entry(self):
        """Delete selected entry."""
        current = self.dict_list.currentItem()
        if not current:
            return
        
        word = current.data(Qt.UserRole)
        del self._dictionary[word]
        self._save_dictionary()
        self._refresh_list()
    
    def _import_dictionary(self):
        """Import dictionary from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Dictionary", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path) as f:
                    imported = json.load(f)
                self._dictionary.update(imported)
                self._save_dictionary()
                self._refresh_list()
                QMessageBox.information(self, "Success", "Dictionary imported")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Import failed: {e}")
    
    def _export_dictionary(self):
        """Export dictionary to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Dictionary", "dictionary.json", "JSON Files (*.json)"
        )
        if file_path:
            with open(file_path, "w") as f:
                json.dump(self._dictionary, f, indent=2)
            QMessageBox.information(self, "Success", "Dictionary exported")


# ============================================================================
# Snippets Tab
# ============================================================================

class SnippetsTab(BaseSettingsTab):
    """Text snippet management."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._snippets = {}
        self._build_ui()
        self._load_snippets()
    
    def _build_ui(self):
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search snippets...")
        self.search_input.textChanged.connect(self._filter_snippets)
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)
        
        # Snippet list
        self.snippet_list = QListWidget()
        self.snippet_list.currentItemChanged.connect(self._on_snippet_select)
        self.layout.addWidget(self.snippet_list)
        
        # Snippet editor
        snippet_group = self.add_group("Snippet")
        snippet_layout = snippet_group.layout()
        
        snippet_form = QFormLayout()
        self.snippet_trigger = QLineEdit()
        self.snippet_trigger.setPlaceholderText("Trigger phrase (e.g., 'my email')")
        snippet_form.addRow("Trigger:", self.snippet_trigger)
        
        snippet_layout.addLayout(snippet_form)
        
        self.snippet_content = QTextEdit()
        self.snippet_content.setPlaceholderText("Snippet content...")
        snippet_layout.addWidget(QLabel("Content:"))
        snippet_layout.addWidget(self.snippet_content)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_snippet)
        btn_layout.addWidget(add_btn)
        
        update_btn = QPushButton("Update")
        update_btn.clicked.connect(self._update_snippet)
        btn_layout.addWidget(update_btn)
        
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self._delete_snippet)
        btn_layout.addWidget(del_btn)
        
        self.layout.addLayout(btn_layout)
        
        # Info
        info = QLabel("Say the trigger phrase to insert the snippet content.")
        info.setWordWrap(True)
        self.layout.addWidget(info)
        
        self.add_stretch()
    
    def _load_snippets(self):
        """Load snippets from file."""
        snippet_file = get_config_dir() / "snippets.json"
        if snippet_file.exists():
            try:
                with open(snippet_file) as f:
                    self._snippets = json.load(f)
            except Exception:
                self._snippets = {}
        self._refresh_list()
    
    def _save_snippets(self):
        """Save snippets to file."""
        snippet_file = get_config_dir() / "snippets.json"
        with open(snippet_file, "w") as f:
            json.dump(self._snippets, f, indent=2)
    
    def _refresh_list(self):
        """Refresh snippet list."""
        self.snippet_list.clear()
        for trigger, content in sorted(self._snippets.items()):
            preview = content[:50] + "..." if len(content) > 50 else content
            item = QListWidgetItem(f"{trigger}: {preview}")
            item.setData(Qt.UserRole, trigger)
            self.snippet_list.addItem(item)
    
    def _filter_snippets(self, text: str):
        """Filter snippet list."""
        text = text.lower()
        for i in range(self.snippet_list.count()):
            item = self.snippet_list.item(i)
            item.setHidden(text not in item.text().lower())
    
    def _on_snippet_select(self, current, previous):
        """Handle snippet selection."""
        if not current:
            return
        
        trigger = current.data(Qt.UserRole)
        self.snippet_trigger.setText(trigger)
        self.snippet_content.setPlainText(self._snippets.get(trigger, ""))
    
    def _add_snippet(self):
        """Add new snippet."""
        trigger = self.snippet_trigger.text().strip()
        content = self.snippet_content.toPlainText()
        
        if not trigger:
            QMessageBox.warning(self, "Error", "Trigger required")
            return
        
        self._snippets[trigger] = content
        self._save_snippets()
        self._refresh_list()
    
    def _update_snippet(self):
        """Update selected snippet."""
        self._add_snippet()
    
    def _delete_snippet(self):
        """Delete selected snippet."""
        current = self.snippet_list.currentItem()
        if not current:
            return
        
        trigger = current.data(Qt.UserRole)
        del self._snippets[trigger]
        self._save_snippets()
        self._refresh_list()


# ============================================================================
# History Tab
# ============================================================================

class HistoryTab(BaseSettingsTab):
    """Transcription history browser."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._store = None
        self._build_ui()
    
    def _build_ui(self):
        # Search and filter
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search transcriptions...")
        self.search_input.textChanged.connect(self._search)
        filter_layout.addWidget(self.search_input)
        
        self.date_filter = QComboBox()
        self.date_filter.addItems(["All Time", "Today", "This Week", "This Month"])
        self.date_filter.currentTextChanged.connect(self._filter_by_date)
        filter_layout.addWidget(self.date_filter)
        
        self.layout.addLayout(filter_layout)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.currentItemChanged.connect(self._on_entry_select)
        self.layout.addWidget(self.history_list)
        
        # Entry viewer
        viewer_group = self.add_group("Transcription Details")
        viewer_layout = viewer_group.layout()
        
        self.entry_viewer = QTextEdit()
        self.entry_viewer.setReadOnly(True)
        viewer_layout.addWidget(self.entry_viewer)
        
        # Actions
        btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Copy Text")
        copy_btn.clicked.connect(self._copy_entry)
        btn_layout.addWidget(copy_btn)
        
        export_btn = QPushButton("Export All")
        export_btn.clicked.connect(self._export_history)
        btn_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self._clear_history)
        btn_layout.addWidget(clear_btn)
        
        self.layout.addLayout(btn_layout)
        
        # Stats
        self.stats_label = QLabel()
        self.layout.addWidget(self.stats_label)
        
        self._load_history()
    
    def _load_history(self):
        """Load transcription history."""
        self._store = get_store()
        self._refresh_list()
        self._update_stats()
    
    def _refresh_list(self, entries=None):
        """Refresh history list."""
        self.history_list.clear()
        
        entries = entries or self._store.get_all()
        for entry in reversed(entries):
            preview = entry.display_text[:60] + "..." if len(entry.display_text) > 60 else entry.display_text
            item = QListWidgetItem(f"[{entry.timestamp[:10]}] {preview}")
            item.setData(Qt.UserRole, entry.id)
            self.history_list.addItem(item)
    
    def _update_stats(self):
        """Update statistics display."""
        stats = self._store.get_statistics()
        self.stats_label.setText(
            f"Total: {stats['total_transcriptions']} transcriptions, "
            f"{stats['total_words']} words, {stats['total_characters']} characters"
        )
    
    def _search(self, text: str):
        """Search transcriptions."""
        if not text:
            self._refresh_list()
            return
        
        results = self._store.search(text)
        self._refresh_list(results)
    
    def _filter_by_date(self, period: str):
        """Filter by date range."""
        from datetime import datetime, timedelta
        
        if period == "All Time":
            self._refresh_list()
            return
        
        now = datetime.now()
        if period == "Today":
            cutoff = now.strftime("%Y-%m-%d")
        elif period == "This Week":
            cutoff = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        elif period == "This Month":
            cutoff = (now - timedelta(days=30)).strftime("%Y-%m-%d")
        else:
            self._refresh_list()
            return
        
        entries = [
            e for e in self._store.get_all()
            if e.timestamp >= cutoff
        ]
        self._refresh_list(entries)
    
    def _on_entry_select(self, current, previous):
        """Handle entry selection."""
        if not current:
            return
        
        entry_id = current.data(Qt.UserRole)
        entry = next((e for e in self._store.get_all() if e.id == entry_id), None)
        
        if entry:
            self.entry_viewer.setHtml(f"""
            <style>
                .label {{ color: #89b4fa; font-weight: bold; }}
                .value {{ color: #cdd6f4; }}
            </style>
            <p><span class="label">Timestamp:</span> <span class="value">{entry.timestamp}</span></p>
            <p><span class="label">Action:</span> <span class="value">{entry.action}</span></p>
            <p><span class="label">Words:</span> <span class="value">{entry.word_count}</span></p>
            <hr>
            <p class="label">Text:</p>
            <p class="value">{entry.display_text}</p>
            """)
    
    def _copy_entry(self):
        """Copy selected entry text."""
        current = self.history_list.currentItem()
        if not current:
            return
        
        entry_id = current.data(Qt.UserRole)
        entry = next((e for e in self._store.get_all() if e.id == entry_id), None)
        
        if entry:
            QApplication.clipboard().setText(entry.display_text)
    
    def _export_history(self):
        """Export history to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export History", "transcriptions.txt", "Text Files (*.txt)"
        )
        if file_path:
            text = self._store.export_to_text(include_metadata=True)
            with open(file_path, "w") as f:
                f.write(text)
            QMessageBox.information(self, "Success", "History exported")
    
    def _clear_history(self):
        """Clear all history."""
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Clear all transcription history?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._store.clear_session()
            save_store()
            self._refresh_list()
            self._update_stats()


# ============================================================================
# Advanced Tab
# ============================================================================

class AdvancedTab(BaseSettingsTab):
    """Advanced settings: backends, debugging, experimental."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        # Display Server
        display_group = self.add_group("Display Server")
        display_layout = display_group.layout()
        
        display_form = QFormLayout()
        self.display_server = QComboBox()
        self.display_server.addItems(["auto", "wayland", "x11"])
        self.display_server.setToolTip("Force specific display server backend")
        display_form.addRow("Display Server:", self.display_server)
        
        self.wayland_compositor = QComboBox()
        self.wayland_compositor.addItems(["auto", "gnome", "kde", "sway"])
        display_form.addRow("Wayland Compositor:", self.wayland_compositor)
        
        display_layout.addLayout(display_form)
        
        # Agent Integration
        agent_group = self.add_group("Agent Integration")
        agent_layout = agent_group.layout()
        
        agent_form = QFormLayout()
        self.agent_output_format = QComboBox()
        self.agent_output_format.addItems(["structured", "markdown", "plain"])
        agent_form.addRow("Output Format:", self.agent_output_format)
        
        self.agent_webhook_url = QLineEdit()
        self.agent_webhook_url.setPlaceholderText("https://...")
        self.agent_webhook_url.setToolTip("Webhook URL to receive formatted agent tasks")
        agent_form.addRow("Webhook URL:", self.agent_webhook_url)
        
        self.agent_ide_integration = QCheckBox("Enable IDE integration")
        agent_form.addRow("", self.agent_ide_integration)
        
        agent_layout.addLayout(agent_form)
        
        # Experimental
        exp_group = self.add_group("Experimental Features")
        exp_layout = exp_group.layout()
        
        exp_form = QFormLayout()
        
        self.reset_each_recording = QCheckBox("Reset transcript each recording")
        exp_form.addRow("", self.reset_each_recording)
        
        exp_layout.addLayout(exp_form)
        
        # Config Management
        config_group = self.add_group("Configuration")
        config_layout = config_group.layout()
        
        config_btns = QHBoxLayout()
        
        import_btn = QPushButton("Import Config")
        import_btn.clicked.connect(self._import_config)
        config_btns.addWidget(import_btn)
        
        export_btn = QPushButton("Export Config")
        export_btn.clicked.connect(self._export_config)
        config_btns.addWidget(export_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_config)
        config_btns.addWidget(reset_btn)
        
        config_layout.addLayout(config_btns)
        
        # Config file info
        config_path = get_config_path()
        path_label = QLabel(f"Config file: {config_path}")
        path_label.setWordWrap(True)
        config_layout.addWidget(path_label)
        
        # Debug
        debug_group = self.add_group("Debugging")
        debug_layout = debug_group.layout()
        
        debug_btns = QHBoxLayout()
        
        test_btn = QPushButton("Test Audio")
        test_btn.clicked.connect(self._test_audio)
        debug_btns.addWidget(test_btn)
        
        test_paste_btn = QPushButton("Test Paste")
        test_paste_btn.clicked.connect(self._test_paste)
        debug_btns.addWidget(test_paste_btn)
        
        debug_layout.addLayout(debug_btns)
        
        self.add_stretch()
    
    def _load_config(self):
        if not self._config:
            return
        
        self.display_server.setCurrentText(self._config.display_server)
        self.wayland_compositor.setCurrentText(self._config.wayland_compositor)
        self.agent_output_format.setCurrentText(self._config.agent_output_format)
        self.agent_webhook_url.setText(self._config.agent_webhook_url)
        self.agent_ide_integration.setChecked(self._config.agent_ide_integration)
        self.reset_each_recording.setChecked(self._config.reset_transcript_each_recording)
    
    def get_config(self) -> DictaPilotConfig:
        if not self._config:
            return None
        
        self._config.display_server = self.display_server.currentText()
        self._config.wayland_compositor = self.wayland_compositor.currentText()
        self._config.agent_output_format = self.agent_output_format.currentText()
        self._config.agent_webhook_url = self.agent_webhook_url.text()
        self._config.agent_ide_integration = self.agent_ide_integration.isChecked()
        self._config.reset_transcript_each_recording = self.reset_each_recording.isChecked()
        
        return self._config
    
    def _import_config(self):
        """Import configuration from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                config = DictaPilotConfig.from_dict(data)
                self.set_config(config)
                QMessageBox.information(self, "Success", "Configuration imported")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Import failed: {e}")
    
    def _export_config(self):
        """Export configuration to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Configuration", "config.json", "JSON Files (*.json)"
        )
        if file_path:
            config = self.get_config()
            if config:
                with open(file_path, "w") as f:
                    json.dump(config.to_dict(), f, indent=2)
                QMessageBox.information(self, "Success", "Configuration exported")
    
    def _reset_config(self):
        """Reset configuration to defaults."""
        reply = QMessageBox.question(
            self, "Confirm Reset",
            "Reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.set_config(DictaPilotConfig())
            self.config_changed.emit()
    
    def _test_audio(self):
        """Test audio system."""
        try:
            devices = sd.query_devices()
            default_input = sd.query_devices(kind='input')
            QMessageBox.information(
                self, "Audio Test",
                f"Audio system working!\n\n"
                f"Default input: {default_input['name']}\n"
                f"Sample rate: {default_input['default_samplerate']} Hz\n"
                f"Channels: {default_input['max_input_channels']}"
            )
        except Exception as e:
            QMessageBox.warning(self, "Audio Test Failed", str(e))
    
    def _test_paste(self):
        """Test paste functionality."""
        from paste_utils import paste_text
        
        try:
            # Copy test text to clipboard
            QApplication.clipboard().setText("DictaPilot test successful!")
            QMessageBox.information(
                self, "Paste Test",
                "Test text copied to clipboard.\n\n"
                "Click OK then press Ctrl+V in a text editor to verify."
            )
        except Exception as e:
            QMessageBox.warning(self, "Paste Test Failed", str(e))


# ============================================================================
# Main Dashboard Window
# ============================================================================

class DictaPilotDashboard(QMainWindow):
    """Main settings dashboard window."""
    
    config_saved = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("DictaPilot Settings")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        
        # Load config
        self._config = load_config()
        
        # Build UI
        self._build_ui()
        self._build_toolbar()
        self._build_statusbar()
        
        # Apply theme
        self._apply_theme()
        
        # Create tray icon
        self._create_tray_icon()
    
    def _build_ui(self):
        """Build main UI."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(8, 8, 8, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search settings... (Ctrl+F)")
        self.search_input.textChanged.connect(self._search_settings)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        
        # Create tabs
        self.general_tab = GeneralSettingsTab()
        self.audio_tab = AudioSettingsTab()
        self.smart_edit_tab = SmartEditingTab()
        self.profiles_tab = ProfilesTab()
        self.dictionary_tab = DictionaryTab()
        self.snippets_tab = SnippetsTab()
        self.history_tab = HistoryTab()
        self.advanced_tab = AdvancedTab()
        
        # Connect config changed signals
        for tab in [self.general_tab, self.audio_tab, self.smart_edit_tab,
                    self.profiles_tab, self.advanced_tab]:
            tab.config_changed.connect(self._on_config_changed)
        
        # Add tabs
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.audio_tab, "Audio")
        self.tabs.addTab(self.smart_edit_tab, "Smart Editing")
        self.tabs.addTab(self.profiles_tab, "Profiles")
        self.tabs.addTab(self.dictionary_tab, "Dictionary")
        self.tabs.addTab(self.snippets_tab, "Snippets")
        self.tabs.addTab(self.history_tab, "History")
        self.tabs.addTab(self.advanced_tab, "Advanced")
        
        layout.addWidget(self.tabs)
        
        # Load config into tabs
        self._load_config()
        
        # Keyboard shortcut for search
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.search_input.setFocus)
        
        # Save shortcut
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_config)
    
    def _build_toolbar(self):
        """Build toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Save action
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_config)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Reset action
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self._reset_config)
        toolbar.addAction(reset_action)
        
        toolbar.addSeparator()
        
        # Help action
        help_action = QAction("Help", self)
        help_action.triggered.connect(self._show_help)
        toolbar.addAction(help_action)
    
    def _build_statusbar(self):
        """Build status bar."""
        self.statusBar().showMessage("Ready")
    
    def _apply_theme(self):
        """Apply theme based on config."""
        theme = self._config.ui_theme
        if theme == "dark":
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet(LIGHT_THEME)
    
    def _create_tray_icon(self):
        """Create system tray icon."""
        # Use application icon if available
        icon_path = Path(__file__).parent / "Dictepilot.png"
        if icon_path.exists():
            icon = QIcon(str(icon_path))
        else:
            icon = self.style().standardIcon(
                self.style().SP_ComputerIcon
            )
        
        self.tray_icon = QSystemTrayIcon(icon, self)
        
        # Tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show Dashboard", self)
        show_action.triggered.connect(self._show_and_activate)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()
    
    def _show_and_activate(self):
        """Show, raise, and activate the window."""
        self.show()
        self.raise_()
        self.activateWindow()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_and_activate()
    
    def _load_config(self):
        """Load configuration into tabs."""
        for tab in [self.general_tab, self.audio_tab, self.smart_edit_tab,
                    self.profiles_tab, self.advanced_tab]:
            tab.set_config(self._config)
    
    def save_config(self):
        """Save configuration from all tabs."""
        # Collect config from tabs
        self._config = self.general_tab.get_config() or self._config
        self._config = self.audio_tab.get_config() or self._config
        self._config = self.smart_edit_tab.get_config() or self._config
        self._config = self.profiles_tab.get_config() or self._config
        self._config = self.advanced_tab.get_config() or self._config
        
        # Save to file
        self._config.save()
        
        # Apply theme if changed
        self._apply_theme()
        
        self.statusBar().showMessage("Configuration saved", 3000)
        self.config_saved.emit()
    
    def _on_config_changed(self):
        """Handle config change signal."""
        self.statusBar().showMessage("Unsaved changes", 0)
    
    def _search_settings(self, text: str):
        """Search settings across tabs."""
        # Highlight matching items in current tab
        # This is a simple implementation - could be enhanced
        pass
    
    def _reset_config(self):
        """Reset configuration."""
        reply = QMessageBox.question(
            self, "Confirm Reset",
            "Reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._config = DictaPilotConfig()
            self._load_config()
            self._apply_theme()
            self.statusBar().showMessage("Configuration reset", 3000)
    
    def _show_help(self):
        """Show help dialog."""
        QMessageBox.information(
            self, "Help",
            "<h3>DictaPilot Settings</h3>"
            "<p>Configure your voice dictation settings using the tabs above.</p>"
            "<h4>Keyboard Shortcuts:</h4>"
            "<ul>"
            "<li><b>Ctrl+S</b> - Save settings</li>"
            "<li><b>Ctrl+F</b> - Search settings</li>"
            "</ul>"
            "<h4>Tabs:</h4>"
            "<ul>"
            "<li><b>General</b> - Mode, hotkeys, models, paste settings</li>"
            "<li><b>Audio</b> - Microphone, VAD, streaming</li>"
            "<li><b>Smart Editing</b> - Cleanup, LLM settings</li>"
            "<li><b>Profiles</b> - Context-aware profiles</li>"
            "<li><b>Dictionary</b> - Custom word corrections</li>"
            "<li><b>Snippets</b> - Text snippets</li>"
            "<li><b>History</b> - Transcription history</li>"
            "<li><b>Advanced</b> - Display server, debugging</li>"
            "</ul>"
        )
    
    def closeEvent(self, event):
        """Handle close event."""
        # Check for unsaved changes
        if self.statusBar().currentMessage() == "Unsaved changes":
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Save changes before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_config()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        # Hide to tray instead of closing
        self.hide()
        event.ignore()
    
    def quit_app(self):
        """Actually quit the application."""
        self.tray_icon.hide()
        QApplication.quit()


# ============================================================================
# Launch Functions
# ============================================================================

def run_dashboard():
    """Run the settings dashboard."""
    if not PYSIDE6_AVAILABLE:
        print("Error: PySide6 not available. Cannot run dashboard.")
        print("Install with: pip install PySide6")
        return False
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    dashboard = DictaPilotDashboard()
    dashboard.show()
    dashboard.raise_()
    dashboard.activateWindow()
    
    # Ensure window is visible and focused
    from PySide6.QtCore import Qt
    dashboard.setWindowState(dashboard.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
    
    return app.exec()


if __name__ == "__main__":
    success = run_dashboard()
    sys.exit(0 if success else 1)
