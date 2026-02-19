"""
DictaPilot Settings View Wrapper
Wraps existing settings tabs into the new dashboard architecture.

MIT License
Copyright (c) 2026 Rehan
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QFrame, QLabel
)
from PySide6.QtGui import QFont

from dashboard_themes import get_theme_manager
from settings_dashboard import DictaPilotDashboard
from config import DictaPilotConfig


class SettingsView(QWidget):
    """Settings view wrapper"""
    
    def __init__(self, config: DictaPilotConfig = None, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.config = config
        self.has_unsaved_changes = False
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Search bar at top
        search_bar = self._create_search_bar()
        main_layout.addWidget(search_bar)
        
        # Embedded settings dashboard
        self.settings_dashboard = DictaPilotDashboard(self.config)
        main_layout.addWidget(self.settings_dashboard, 1)
        
        # Unsaved changes bar (hidden by default)
        self.unsaved_bar = self._create_unsaved_bar()
        self.unsaved_bar.hide()
        main_layout.addWidget(self.unsaved_bar)
    
    def _create_search_bar(self) -> QFrame:
        """Create settings search bar"""
        bar = QFrame()
        bar.setFixedHeight(60)
        bar.setStyleSheet(f"background-color: {self.theme_manager.get_color('bg-base')};")
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 12, 24, 12)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search settings... (Ctrl+F)")
        self.search_input.setMinimumWidth(400)
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.setAccessibleName("Search settings")
        layout.addWidget(self.search_input)
        
        layout.addStretch()
        
        return bar
    
    def _create_unsaved_bar(self) -> QFrame:
        """Create unsaved changes bar"""
        bar = QFrame()
        bar.setFixedHeight(48)
        
        bg_color = self.theme_manager.get_color("accent-yellow")
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(249, 226, 175, 0.15);
                border-top: 1px solid {bg_color};
            }}
        """)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 8, 24, 8)
        
        # Warning indicator
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {bg_color}; font-size: 16px;")
        layout.addWidget(dot)
        
        # Message
        message = QLabel("Unsaved changes")
        message.setStyleSheet(f"color: {self.theme_manager.get_color('text-primary')}; font-weight: 600;")
        layout.addWidget(message)
        
        layout.addStretch()
        
        # Revert button
        revert_btn = QPushButton("Revert")
        revert_btn.setProperty("variant", "secondary")
        revert_btn.clicked.connect(self._on_revert)
        layout.addWidget(revert_btn)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.setProperty("variant", "primary")
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)
        
        return bar
    
    def _on_search_changed(self, text: str):
        """Handle search text change with debouncing"""
        # Debounce search
        if hasattr(self, '_search_timer'):
            self._search_timer.stop()
        
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(lambda: self._filter_settings(text))
        self._search_timer.start(200)
    
    def _filter_settings(self, query: str):
        """Filter visible settings based on search query"""
        if not query:
            # Show all
            self._show_all_settings()
            return
        
        query_lower = query.lower()
        
        # Find all QGroupBox widgets in settings dashboard
        from PySide6.QtWidgets import QGroupBox
        group_boxes = self.settings_dashboard.findChildren(QGroupBox)
        
        for group_box in group_boxes:
            # Check if group title or any child widget text matches
            title = group_box.title().lower()
            matches = query_lower in title
            
            if not matches:
                # Check child widgets
                from PySide6.QtWidgets import QLabel, QCheckBox
                labels = group_box.findChildren(QLabel)
                checkboxes = group_box.findChildren(QCheckBox)
                
                for label in labels:
                    if query_lower in label.text().lower():
                        matches = True
                        break
                
                if not matches:
                    for checkbox in checkboxes:
                        if query_lower in checkbox.text().lower():
                            matches = True
                            break
            
            group_box.setVisible(matches)
    
    def _show_all_settings(self):
        """Show all settings groups"""
        from PySide6.QtWidgets import QGroupBox
        group_boxes = self.settings_dashboard.findChildren(QGroupBox)
        for group_box in group_boxes:
            group_box.setVisible(True)
    
    def _on_revert(self):
        """Handle revert button click"""
        # Reload settings from config
        self.settings_dashboard.load_from_config()
        self.has_unsaved_changes = False
        self.unsaved_bar.hide()
    
    def _on_save(self):
        """Handle save button click"""
        # Save settings
        self.settings_dashboard.save_config()
        self.has_unsaved_changes = False
        self.unsaved_bar.hide()
    
    def show_unsaved_changes(self):
        """Show unsaved changes bar"""
        self.has_unsaved_changes = True
        self.unsaved_bar.show()
    
    def focus_search(self):
        """Focus the search input"""
        self.search_input.setFocus()
