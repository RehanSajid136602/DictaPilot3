"""
DictaPilot GUI Main Window
Primary application window with transcription UI
"""

import os
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QToolBar, QMessageBox,
    QFileDialog, QApplication, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QIcon, QFont, QPalette, QColor

from ..config.settings import get_settings
from ..audio.recorder import AudioRecorder, RecorderError
from ..stt.transcriber import Transcriber, TranscriptionWorker
from .settings_dialog import SettingsDialog


# Modern WhisperFlow-like stylesheet
MODERN_STYLE = """
QMainWindow {
    background-color: #f8f9fa;
}

QWidget {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}

QTextEdit {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 12px;
    padding: 16px;
    font-size: 14px;
    line-height: 1.6;
    selection-background-color: #4dabf7;
}

QTextEdit:focus {
    border: 2px solid #4dabf7;
}

QPushButton {
    background-color: #339af0;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
    min-width: 120px;
}

QPushButton:hover {
    background-color: #228be6;
}

QPushButton:pressed {
    background-color: #1971c2;
}

QPushButton:disabled {
    background-color: #dee2e6;
    color: #868e96;
}

QPushButton#recordButton {
    background-color: #40c057;
    font-size: 16px;
    font-weight: 600;
    padding: 16px 32px;
    min-width: 160px;
    min-height: 50px;
}

QPushButton#recordButton:hover {
    background-color: #37b24d;
}

QPushButton#recordButton:pressed {
    background-color: #2f9e44;
}

QPushButton#recordButton[recording="true"] {
    background-color: #fa5252;
}

QPushButton#recordButton[recording="true"]:hover {
    background-color: #f03e3e;
}

QPushButton#recordButton[transcribing="true"] {
    background-color: #fab005;
}

QPushButton#recordButton[transcribing="true"]:hover {
    background-color: #f59f00;
}

QLabel#statusLabel {
    color: #868e96;
    font-size: 12px;
    font-weight: 500;
}

QLabel#statusLabel[recording="true"] {
    color: #fa5252;
}

QLabel#statusLabel[transcribing="true"] {
    color: #fab005;
}

QToolBar {
    background-color: #ffffff;
    border: none;
    border-bottom: 1px solid #dee2e6;
    padding: 8px 16px;
    spacing: 8px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}

QToolButton:hover {
    background-color: #f1f3f5;
    border-color: #ced4da;
}

QFrame#divider {
    background-color: #dee2e6;
    max-height: 1px;
}
"""


class MainWindow(QMainWindow):
    """
    Main application window for DictaPilot GUI
    Features a modern, WhisperFlow-like interface
    """
    
    # Signals for thread-safe UI updates
    transcription_ready = Signal(str)
    transcription_error = Signal(str)
    status_update = Signal(str)
    record_button_state = Signal(str)  # idle, recording, transcribing
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DictaPilot")
        self.setMinimumSize(800, 600)
        
        # Load settings
        self.settings = get_settings()
        self.resize(self.settings.window_width, self.settings.window_height)
        
        # Initialize components
        self.recorder: AudioRecorder = None
        self.transcriber: Transcriber = None
        self.transcription_worker: TranscriptionWorker = None
        self._audio_file_path: str = None
        
        # State
        self._is_recording = False
        self._is_transcribing = False
        
        # Setup UI
        self._setup_ui()
        self._apply_styles()
        self._connect_signals()
        
        # Initialize components
        self._init_recorder()
        self._init_transcriber()
        
        # Show welcome message
        self._show_welcome()
    
    def _setup_ui(self):
        """Setup the main UI components"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 16, 24, 24)
        
        # Toolbar
        self._setup_toolbar()
        
        # Transcription text area
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            "Transcription will appear here...\n\n"
            "Click the Record button to start."
        )
        self.text_edit.setAcceptRichText(False)
        self._update_font()
        layout.addWidget(self.text_edit, 1)  # Stretch to fill space
        
        # Divider
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.HLine)
        layout.addWidget(divider)
        
        # Bottom section with record button and status
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(12)
        bottom_layout.setAlignment(Qt.AlignCenter)
        
        # Record button
        self.record_btn = QPushButton("🎙️  Record")
        self.record_btn.setObjectName("recordButton")
        self.record_btn.setCursor(Qt.PointingHandCursor)
        self.record_btn.clicked.connect(self._on_record_clicked)
        bottom_layout.addWidget(self.record_btn, alignment=Qt.AlignCenter)
        
        # Status label
        self.status_label = QLabel("Idle")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(self.status_label)
        
        layout.addLayout(bottom_layout)
    
    def _setup_toolbar(self):
        """Setup the top toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Clear action
        clear_action = QAction("🗑️  Clear", self)
        clear_action.setToolTip("Clear transcription (Ctrl+L)")
        clear_action.setShortcut("Ctrl+L")
        clear_action.triggered.connect(self._on_clear)
        toolbar.addAction(clear_action)
        
        # Copy action
        copy_action = QAction("📋  Copy", self)
        copy_action.setToolTip("Copy to clipboard (Ctrl+C)")
        copy_action.setShortcut("Ctrl+Shift+C")
        copy_action.triggered.connect(self._on_copy)
        toolbar.addAction(copy_action)
        
        # Save action
        save_action = QAction("💾  Save", self)
        save_action.setToolTip("Save as text file (Ctrl+S)")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Settings action
        settings_action = QAction("⚙️  Settings", self)
        settings_action.setToolTip("Open settings (Ctrl+,)")
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._on_settings)
        toolbar.addAction(settings_action)
    
    def _apply_styles(self):
        """Apply modern stylesheet"""
        self.setStyleSheet(MODERN_STYLE)
    
    def _connect_signals(self):
        """Connect signals for thread-safe updates"""
        self.transcription_ready.connect(self._on_transcription_ready)
        self.transcription_error.connect(self._on_transcription_error)
        self.status_update.connect(self._update_status)
        self.record_button_state.connect(self._update_record_button)
    
    def _init_recorder(self):
        """Initialize audio recorder"""
        try:
            from ..audio.recorder import AudioConfig
            config = AudioConfig(
                sample_rate=self.settings.sample_rate,
                channels=self.settings.channels
            )
            self.recorder = AudioRecorder(config)
            self.recorder.on_level_update = self._on_audio_level
            self.recorder.on_error = self._on_recorder_error
        except Exception as e:
            self._show_error(
                "Audio Error",
                f"Failed to initialize audio recorder:\n{str(e)}\n\n"
                "Please ensure portaudio is installed:\n"
                "  Ubuntu/Debian: sudo apt-get install portaudio19-dev\n"
                "  Fedora: sudo dnf install portaudio-devel"
            )
    
    def _init_transcriber(self):
        """Initialize transcriber (lazy loading)"""
        # Will be created on first use with current settings
        pass
    
    def _get_transcriber(self) -> Transcriber:
        """Get or create transcriber with current settings"""
        if self.transcriber is None:
            self.transcriber = Transcriber(
                model_size=self.settings.model,
                device=self.settings.device
            )
        return self.transcriber
    
    def _show_welcome(self):
        """Show welcome message in text area"""
        welcome_text = """Welcome to DictaPilot! 🎙️

Click the "Record" button below to start transcribing speech to text.

Quick Tips:
• Use the toolbar above to Clear, Copy, or Save your transcriptions
• Open Settings (⚙️) to change the model, language, or device
• The app supports multiple languages including English, Urdu, and more

Keyboard Shortcuts:
• Ctrl+L: Clear text
• Ctrl+Shift+C: Copy to clipboard
• Ctrl+S: Save to file
• Ctrl+,: Open settings
"""
        self.text_edit.setText(welcome_text)
    
    # ===== Signal Handlers =====
    
    @Slot(str)
    def _on_transcription_ready(self, text: str):
        """Handle transcription completion"""
        self._is_transcribing = False
        
        # Clear welcome message if present
        current_text = self.text_edit.toPlainText()
        if "Welcome to DictaPilot" in current_text:
            self.text_edit.setText(text)
        else:
            # Append with spacing
            if current_text and not current_text.endswith('\n'):
                self.text_edit.append('')
            self.text_edit.append(text)
        
        # Update UI state
        self.record_button_state.emit("idle")
        self.status_update.emit("Idle")
        self._cleanup_temp_file()
    
    @Slot(str)
    def _on_transcription_error(self, error: str):
        """Handle transcription error"""
        self._is_transcribing = False
        self.record_button_state.emit("idle")
        self.status_update.emit("Error")
        self._show_error("Transcription Error", error)
        self._cleanup_temp_file()
    
    @Slot(str)
    def _update_status(self, status: str):
        """Update status label"""
        self.status_label.setText(status)
        
        # Update property for styling
        if "Recording" in status:
            self.status_label.setProperty("recording", "true")
        elif "Transcribing" in status:
            self.status_label.setProperty("transcribing", "true")
        else:
            self.status_label.setProperty("recording", "")
            self.status_label.setProperty("transcribing", "")
        
        # Refresh style
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
    
    @Slot(str)
    def _update_record_button(self, state: str):
        """Update record button appearance"""
        self.record_btn.setProperty("recording", "")
        self.record_btn.setProperty("transcribing", "")
        
        if state == "recording":
            self.record_btn.setText("⏹  Stop")
            self.record_btn.setProperty("recording", "true")
        elif state == "transcribing":
            self.record_btn.setText("⏳  Transcribing…")
            self.record_btn.setProperty("transcribing", "true")
            self.record_btn.setEnabled(False)
        else:  # idle
            self.record_btn.setText("🎙️  Record")
            self.record_btn.setEnabled(True)
        
        # Refresh style
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
    
    def _on_audio_level(self, level: float):
        """Handle audio level update"""
        # Could update a visualizer here
        pass
    
    def _on_recorder_error(self, error: str):
        """Handle recorder error"""
        self.status_update.emit(f"Error: {error}")
    
    # ===== Action Handlers =====
    
    def _on_record_clicked(self):
        """Handle record button click"""
        if not self._is_recording:
            self._start_recording()
        else:
            self._stop_recording()
    
    def _start_recording(self):
        """Start audio recording"""
        if not self.recorder:
            self._show_error(
                "Audio Error",
                "Audio recorder not initialized. Please restart the application."
            )
            return
        
        try:
            success = self.recorder.start_recording()
            if success:
                self._is_recording = True
                self.record_button_state.emit("recording")
                self.status_update.emit("Recording… Click Stop to finish")
        except Exception as e:
            self._show_error("Recording Error", str(e))
    
    def _stop_recording(self):
        """Stop recording and start transcription"""
        if not self.recorder:
            return
        
        self._is_recording = False
        self.record_button_state.emit("transcribing")
        self.status_update.emit("Transcribing… Please wait")
        
        # Stop recording in background thread to avoid UI freeze
        import threading
        def stop_and_transcribe():
            try:
                audio_path = self.recorder.stop_recording()
                if audio_path:
                    self._audio_file_path = audio_path
                    self._run_transcription(audio_path)
                else:
                    self.status_update.emit("No audio recorded")
                    self.record_button_state.emit("idle")
            except Exception as e:
                self.transcription_error.emit(str(e))
        
        thread = threading.Thread(target=stop_and_transcribe, daemon=True)
        thread.start()
    
    def _run_transcription(self, audio_path: str):
        """Run transcription in background"""
        try:
            transcriber = self._get_transcriber()
            
            # Create worker thread
            self.transcription_worker = TranscriptionWorker(
                transcriber=transcriber,
                audio_path=audio_path,
                language=self.settings.language,
                translate=self.settings.translate_to_english,
                on_result=self._on_transcription_result,
                on_error=self._on_transcription_error_worker,
                on_progress=self._on_transcription_progress
            )
            self.transcription_worker.start()
            
        except Exception as e:
            self.transcription_error.emit(str(e))
    
    def _on_transcription_result(self, result):
        """Callback from transcription worker"""
        self.transcription_ready.emit(result.text)
    
    def _on_transcription_error_worker(self, error: str):
        """Error callback from transcription worker"""
        self.transcription_error.emit(error)
    
    def _on_transcription_progress(self, message: str):
        """Progress callback from transcription worker"""
        self.status_update.emit(f"Transcribing… {message}")
    
    def _on_clear(self):
        """Clear transcription text"""
        self.text_edit.clear()
        self.status_update.emit("Cleared")
    
    def _on_copy(self):
        """Copy transcription to clipboard"""
        text = self.text_edit.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.status_update.emit("Copied to clipboard")
        else:
            self.status_update.emit("Nothing to copy")
    
    def _on_save(self):
        """Save transcription to file"""
        text = self.text_edit.toPlainText()
        if not text:
            self.status_update.emit("Nothing to save")
            return
        
        default_name = f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Transcription",
            str(Path(self.settings.last_save_dir) / default_name),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.settings.last_save_dir = str(Path(path).parent)
                self.settings.save()
                self.status_update.emit(f"Saved to {Path(path).name}")
            except Exception as e:
                self._show_error("Save Error", f"Failed to save file:\n{str(e)}")
    
    def _on_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == SettingsDialog.Accepted:
            # Settings were saved, reload
            self.settings = get_settings()
            self._update_font()
            self._update_transcriber()
            self.status_update.emit("Settings updated")
    
    def _update_font(self):
        """Update text edit font based on settings"""
        font = QFont()
        if self.settings.monospace_font:
            font.setFamily("Consolas, Monaco, 'Courier New', monospace")
        font.setPointSize(11)
        self.text_edit.setFont(font)
    
    def _update_transcriber(self):
        """Update transcriber with new settings"""
        # Will be recreated on next use with new settings
        self.transcriber = None
    
    def _cleanup_temp_file(self):
        """Clean up temporary audio file"""
        if self._audio_file_path and os.path.exists(self._audio_file_path):
            try:
                os.remove(self._audio_file_path)
            except OSError:
                pass
            self._audio_file_path = None
    
    def _show_error(self, title: str, message: str):
        """Show error dialog"""
        QMessageBox.critical(self, title, message)
    
    def closeEvent(self, event):
        """Handle window close"""
        # Save window size
        self.settings.window_width = self.width()
        self.settings.window_height = self.height()
        self.settings.save()
        
        # Cleanup
        if self.recorder:
            self.recorder.cleanup()
        self._cleanup_temp_file()
        
        event.accept()