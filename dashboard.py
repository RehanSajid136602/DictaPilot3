"""
DictaPilot Dashboard - Modern PySide6 GUI for the DictaPilot engine.
Provides:
  - Auto-start of app.py as a background subprocess
  - System tray integration (minimize-to-tray on close)
  - Settings dialog that reads/writes the .env file
  - Clean subprocess lifecycle management (no zombie processes)
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

# Important: install using `pip install pyqtdarktheme python-dotenv PySide6`
import qdarktheme
from dotenv import set_key, load_dotenv

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTabWidget, QFormLayout, QLineEdit, QComboBox, 
    QCheckBox, QPushButton, QSystemTrayIcon, QMenu, QMessageBox,
    QGroupBox, QScrollArea, QFrame, QSizePolicy, QSpacerItem
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

ENV_FILE = Path(".env")
BASE_DIR = Path(__file__).resolve().parent
APP_SCRIPT = BASE_DIR / "app.py"
LOG_FILE = BASE_DIR / "engine.log"

class DictaPilotDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DictaPilot Dashboard")
        self.setMinimumSize(540, 560)
        
        # Load existing .env or create empty
        load_dotenv(ENV_FILE)
        
        self.app_process = None
        self.tray_icon = None
        
        self.init_ui()
        self.init_tray()
        
        # Engine health polling
        self.health_timer = QTimer(self)
        self.health_timer.timeout.connect(self._poll_engine)
        self.health_timer.start(2000)
        
        # Give UI a moment to show, then start engine automatically
        QTimer.singleShot(200, self.start_engine)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Main Title Header
        title_label = QLabel("DictaPilot")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #4facfe; margin-bottom: 5px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Engine Status Area
        status_group = QGroupBox("Engine Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        status_layout = QHBoxLayout(status_group)
        status_layout.setContentsMargins(15, 15, 15, 15)
        
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("font-size: 15px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.toggle_engine_btn = QPushButton("Start Engine")
        self.toggle_engine_btn.setMinimumHeight(35)
        self.toggle_engine_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_engine_btn.clicked.connect(self.toggle_engine)
        status_layout.addWidget(self.toggle_engine_btn)
        
        main_layout.addWidget(status_group)

        # Tab Widget for Settings
        tabs = QTabWidget()
        settings_tab = QWidget()
        self.init_settings_tab(settings_tab)
        tabs.addTab(settings_tab, "Settings")
        main_layout.addWidget(tabs)
        
        # Application Controls
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("Save Settings & Apply")
        save_btn.setMinimumHeight(40)
        save_btn.setMinimumWidth(180)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setProperty("theme", "primary") # Allow qdarktheme to style it
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)

    def init_settings_tab(self, tab_widget):
        # We use a ScrollArea to ensure it doesn't break on smaller screens
        scroll = QScrollArea(tab_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_content = QWidget()
        layout = QFormLayout(scroll_content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Inputs Dictionary for easy saving
        self.inputs = {}

        def add_line_edit(key, label, default="", echo_mode=QLineEdit.EchoMode.Normal):
            le = QLineEdit(os.getenv(key, default))
            le.setEchoMode(echo_mode)
            layout.addRow(label, le)
            self.inputs[key] = le
            
        def add_combo(key, label, options, default=""):
            cb = QComboBox()
            cb.addItems(options)
            cb.setCurrentText(os.getenv(key, default))
            layout.addRow(label, cb)
            self.inputs[key] = cb
            
        def add_toggle(key, label, default=True):
            chk = QCheckBox(label)
            val = os.getenv(key, "1" if default else "0").lower()
            chk.setChecked(val not in {"0", "false", "no"})
            layout.addRow("", chk)
            self.inputs[key] = chk

        add_line_edit("GROQ_API_KEY", "GROQ API Key:", echo_mode=QLineEdit.EchoMode.Password)
        add_line_edit("HOTKEY", "Capture Hotkey:", default="f9")
        add_combo("SMART_MODE", "Smart Mode:", ["llm", "heuristic"], "llm")
        add_combo("PASTE_MODE", "Paste Mode:", ["delta", "full"], "delta")
        add_combo("DICTATION_MODE", "Dictation Mode:", ["speed", "balanced", "accurate"], "accurate")
        add_combo("FLOATING_UI_STYLE", "Floating UI Style:", ["modern", "classic"], "modern")
        add_combo("FLOATING_ACCENT_COLOR", "Accent Color:", ["blue", "purple", "green", "cyan", "magenta"], "blue")
        add_toggle("STREAMING_ENABLED", "Enable Streaming Transcription", default=True)

        scroll.setWidget(scroll_content)
        
        # Add scroll to tab
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0,0,0,0)
        tab_layout.addWidget(scroll)

    def init_tray(self):
        icon_path = Path("Dictepilot.png")
        if icon_path.exists():
            icon = QIcon(str(icon_path))
        else:
            # Fallback icon if logo is missing
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
            
        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("DictaPilot")
        
        tray_menu = QMenu()
        
        self.restore_action = QAction("Open Dashboard", self)
        self.restore_action.triggered.connect(self.showNormal)
        tray_menu.addAction(self.restore_action)
        
        tray_menu.addSeparator()
        
        self.quit_action = QAction("Quit DictaPilot", self)
        self.quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def closeEvent(self, event):
        """Intercept the 'X' button to minimize to tray."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "DictaPilot is running",
            "The dashboard is minimized to the system tray. The background engine is still running.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def save_settings(self):
        try:
            if not ENV_FILE.exists():
                ENV_FILE.touch()
                
            for key, widget in self.inputs.items():
                if isinstance(widget, QLineEdit):
                    val = widget.text().strip()
                elif isinstance(widget, QComboBox):
                    val = widget.currentText()
                elif isinstance(widget, QCheckBox):
                    val = "1" if widget.isChecked() else "0"
                set_key(str(ENV_FILE), key, val)
            
            QMessageBox.information(self, "Success", "Settings saved successfully! The engine will now restart to apply changes.")
            self.restart_engine()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def toggle_engine(self):
        if self.app_process and self.app_process.poll() is None:
            self.kill_engine()
        else:
            self.start_engine()

    def start_engine(self):
        if self.app_process is not None and self.app_process.poll() is None:
            logging.info("Engine is already running.")
            return

        logging.info("Starting app.py engine...")
        
        creation_flags = 0
        if sys.platform == "win32":
            # Prevent console window from popping up
            creation_flags = subprocess.CREATE_NO_WINDOW
            
        try:
            self.log_file = open(LOG_FILE, "a", encoding="utf-8")
            self.app_process = subprocess.Popen(
                [sys.executable, str(APP_SCRIPT)],
                creationflags=creation_flags,
                cwd=str(BASE_DIR),
                stdout=self.log_file,
                stderr=subprocess.STDOUT
            )
            self.status_label.setText("Engine Status: <span style='color: #10B981;'>Running</span>")
            self.toggle_engine_btn.setText("Stop Engine")
        except Exception as e:
            QMessageBox.critical(self, "Failed to Start", f"Could not start engine: {e}")
            self.status_label.setText("Engine Status: <span style='color: #EF4444;'>Error</span>")

    def kill_engine(self):
        if self.app_process is not None:
            logging.info("Terminating app.py engine...")
            try:
                self.app_process.terminate()
                self.app_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.app_process.kill()
            except Exception as e:
                logging.error(f"Error terminating process: {e}")
            
            self.app_process = None
            if hasattr(self, 'log_file') and self.log_file:
                try:
                    self.log_file.close()
                except Exception:
                    pass
            
        self.status_label.setText("Engine Status: <span style='color: #EF4444;'>Stopped</span>")
        self.toggle_engine_btn.setText("Start Engine")

    def _poll_engine(self):
        if self.app_process is not None:
            retcode = self.app_process.poll()
            if retcode is not None:
                logging.warning(f"Engine process exited unexpectedly with code {retcode}")
                self.app_process = None
                if hasattr(self, 'log_file') and self.log_file:
                    try:
                        self.log_file.close()
                    except Exception:
                        pass
                self.status_label.setText("Engine Status: <span style='color: #EF4444;'>Error (Exited)</span>")
                self.toggle_engine_btn.setText("Start Engine")

    def restart_engine(self):
        self.kill_engine()
        # Small delay before starting again
        QTimer.singleShot(500, self.start_engine)

    def quit_app(self):
        """Clean teardown: stop subprocess, remove tray icon, and quit application."""
        logging.info("Quitting DictaPilot completely...")
        self.kill_engine()
        self.tray_icon.hide()
        QApplication.quit()

def main():
    app = QApplication(sys.argv)
    
    # Required to prevent the app from quitting when dashboard is closed (minimized to tray)
    app.setQuitOnLastWindowClosed(False)
    
    # Apply a modern dark theme using qdarktheme
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    
    dashboard = DictaPilotDashboard()
    dashboard.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
