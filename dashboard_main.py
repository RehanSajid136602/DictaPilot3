"""
DictaPilot Main Dashboard
Modern dashboard UI with sidebar navigation and multiple views.

MIT License
Copyright (c) 2026 Rehan
"""

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QFrame, QPushButton, QLabel,
    QToolBar, QStatusBar, QSizePolicy
)
from PySide6.QtGui import QKeySequence, QShortcut

from dashboard_themes import get_theme_manager
from config import DictaPilotConfig, load_config
from dashboard_views.home_view import HomeView
from dashboard_views.settings_view import SettingsView
from dashboard_views.statistics_view import StatisticsView
from dashboard_views.diagnostics_view import DiagnosticsView


class DictaPilotMainDashboard(QMainWindow):
    """Main dashboard window with sidebar navigation"""
    
    # Signals
    view_changed = Signal(str)  # Emitted when view changes
    theme_changed = Signal(str)  # Emitted when theme changes
    
    def __init__(self, config: DictaPilotConfig = None):
        super().__init__()
        
        self.config = config or load_config()
        self.theme_manager = get_theme_manager()
        self.current_view = "home"
        self.sidebar_collapsed = False
        self.current_breakpoint = "desktop"  # desktop, tablet, compact
        
        self._init_ui()
        self._apply_theme()
        self._setup_shortcuts()
        
        # Set minimum size
        self.setMinimumSize(900, 700)
        self.resize(1280, 800)
    
    def _init_ui(self):
        """Initialize the UI layout"""
        self.setWindowTitle("DictaPilot Dashboard")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create right side (breadcrumb + content)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Breadcrumb bar
        self.breadcrumb_bar = self._create_breadcrumb_bar()
        right_layout.addWidget(self.breadcrumb_bar)
        
        # Content area (stacked widget for views)
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("content-stack")
        right_layout.addWidget(self.content_stack)
        
        main_layout.addWidget(right_widget, 1)
        
        # Create toolbar
        self._create_toolbar()
        
        # Create status bar
        self._create_status_bar()
        
        # Initialize views (placeholders for now)
        self._init_views()
    
    def _create_sidebar(self) -> QFrame:
        """Create the sidebar navigation"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("home", "🏠 Home"),
            ("settings", "⚙️ Settings"),
            ("statistics", "📊 Statistics"),
            ("history", "📝 History"),
            ("dictionary", "📖 Dictionary"),
            ("agent", "🤖 Agent"),
            ("profiles", "👤 Profiles"),
            ("diagnostics", "🏥 Diagnostics"),
            ("help", "❓ Help"),
        ]
        
        for view_id, label in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav-button")
            btn.setProperty("active", view_id == "home")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=view_id: self._navigate_to(v))
            btn.setAccessibleName(f"Navigate to {label}")
            layout.addWidget(btn)
            self.nav_buttons[view_id] = btn
        
        layout.addStretch()
        
        # Collapse button at bottom
        self.collapse_btn = QPushButton("◀")
        self.collapse_btn.setObjectName("nav-button")
        self.collapse_btn.setToolTip("Collapse sidebar")
        self.collapse_btn.clicked.connect(self._toggle_sidebar)
        layout.addWidget(self.collapse_btn)
        
        return sidebar
    
    def _create_breadcrumb_bar(self) -> QFrame:
        """Create the breadcrumb navigation bar"""
        breadcrumb = QFrame()
        breadcrumb.setObjectName("breadcrumb-bar")
        breadcrumb.setFixedHeight(32)
        
        layout = QHBoxLayout(breadcrumb)
        layout.setContentsMargins(16, 0, 16, 0)
        
        self.breadcrumb_label = QLabel("Home")
        self.breadcrumb_label.setProperty("breadcrumb", True)
        layout.addWidget(self.breadcrumb_label)
        layout.addStretch()
        
        return breadcrumb
    
    def _create_toolbar(self):
        """Create the top toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFixedHeight(48)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # Logo/Title
        title_label = QLabel("DictaPilot")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 0 16px;")
        toolbar.addWidget(title_label)
        
        toolbar.addStretch()
        
        # Theme toggle button
        self.theme_btn = QPushButton("🌙" if self.theme_manager.current_theme == "dark" else "☀️")
        self.theme_btn.setToolTip("Toggle theme")
        self.theme_btn.clicked.connect(self._toggle_theme)
        toolbar.addWidget(self.theme_btn)
    
    def _create_status_bar(self):
        """Create the bottom status bar"""
        status_bar = QStatusBar()
        status_bar.setFixedHeight(24)
        self.setStatusBar(status_bar)
        
        # Default status message
        status_bar.showMessage("● Ready | Profile: default | v3.0")
    
    def _init_views(self):
        """Initialize view widgets (placeholders)"""
        # Create actual views
        home_view = HomeView()
        home_view.start_recording.connect(self._on_start_recording)
        home_view.navigate_to_history.connect(self._on_navigate_to_history)
        
        settings_view = SettingsView(self.config)
        
        statistics_view = StatisticsView()
        
        diagnostics_view = DiagnosticsView()
        diagnostics_view.run_diagnostics.connect(self._on_run_diagnostics)
        
        views = {
            "home": home_view,
            "settings": settings_view,
            "statistics": statistics_view,
            "history": QLabel("History View - Coming Soon"),
            "dictionary": QLabel("Dictionary View - Coming Soon"),
            "agent": QLabel("Agent View - Coming Soon"),
            "profiles": QLabel("Profiles View - Coming Soon"),
            "diagnostics": diagnostics_view,
            "help": QLabel("Help View - Coming Soon"),
        }
        
        # Add placeholder styling only to label widgets
        for view_id, widget in views.items():
            if isinstance(widget, QLabel):
                widget.setAlignment(Qt.AlignCenter)
                widget.setStyleSheet("font-size: 24px; color: #a6adc8;")
            self.content_stack.addWidget(widget)
    
    def _on_start_recording(self):
        """Handle start recording signal from home view"""
        # TODO: Connect to actual recording functionality
        print("Start recording requested")
    
    def _on_navigate_to_history(self, transcription_id: str):
        """Handle navigation to history view"""
        self._navigate_to("history")
        # TODO: Select specific transcription if ID provided
    
    def _on_run_diagnostics(self):
        """Handle run diagnostics signal"""
        # TODO: Connect to actual HealthChecker
        print("Run diagnostics requested")
    
    def _navigate_to(self, view_id: str):
        """Navigate to a specific view"""
        # Update active button
        for vid, btn in self.nav_buttons.items():
            btn.setProperty("active", vid == view_id)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        # Update breadcrumb
        view_names = {
            "home": "Home",
            "settings": "Settings",
            "statistics": "Statistics & Analytics",
            "history": "History & Transcriptions",
            "dictionary": "Dictionary & Snippets",
            "agent": "Agent Mode",
            "profiles": "Profiles",
            "diagnostics": "Diagnostics",
            "help": "Help",
        }
        self.breadcrumb_label.setText(view_names.get(view_id, view_id.title()))
        
        # Switch view (for now just cycle through placeholder widgets)
        view_index = list(self.nav_buttons.keys()).index(view_id)
        self.content_stack.setCurrentIndex(view_index)
        
        self.current_view = view_id
        self.view_changed.emit(view_id)
    
    def _toggle_sidebar(self):
        """Toggle sidebar collapsed/expanded state"""
        self.sidebar_collapsed = not self.sidebar_collapsed
        
        if self.sidebar_collapsed:
            self.sidebar.setFixedWidth(56)
            self.collapse_btn.setText("▶")
            self.collapse_btn.setToolTip("Expand sidebar")
            # Hide button text, show only icons
            for btn in self.nav_buttons.values():
                text = btn.text()
                icon = text.split()[0] if text else ""
                btn.setText(icon)
                btn.setToolTip(text)
        else:
            self.sidebar.setFixedWidth(220)
            self.collapse_btn.setText("◀")
            self.collapse_btn.setToolTip("Collapse sidebar")
            # Restore full text
            nav_items = [
                ("home", "🏠 Home"),
                ("settings", "⚙️ Settings"),
                ("statistics", "📊 Statistics"),
                ("history", "📝 History"),
                ("dictionary", "📖 Dictionary"),
                ("agent", "🤖 Agent"),
                ("profiles", "👤 Profiles"),
                ("diagnostics", "🏥 Diagnostics"),
                ("help", "❓ Help"),
            ]
            for view_id, label in nav_items:
                self.nav_buttons[view_id].setText(label)
                self.nav_buttons[view_id].setToolTip("")
    
    def _toggle_theme(self):
        """Toggle between dark and light themes"""
        new_theme = "light" if self.theme_manager.current_theme == "dark" else "dark"
        self.theme_manager.switch_theme(new_theme)
        self._apply_theme()
        self.theme_btn.setText("🌙" if new_theme == "dark" else "☀️")
        self.theme_changed.emit(new_theme)
    
    def _apply_theme(self):
        """Apply the current theme stylesheet"""
        stylesheet = self.theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+H - Home
        QShortcut(QKeySequence("Ctrl+H"), self, lambda: self._navigate_to("home"))
        
        # Ctrl+, - Settings
        QShortcut(QKeySequence("Ctrl+,"), self, lambda: self._navigate_to("settings"))
        
        # Ctrl+D - Diagnostics
        QShortcut(QKeySequence("Ctrl+D"), self, lambda: self._navigate_to("diagnostics"))
        
        # Escape - Collapse sidebar
        QShortcut(QKeySequence("Escape"), self, self._collapse_sidebar_if_expanded)
    
    def _collapse_sidebar_if_expanded(self):
        """Collapse sidebar if it's expanded"""
        if not self.sidebar_collapsed:
            self._toggle_sidebar()
    
    def resizeEvent(self, event):
        """Handle window resize for responsive behavior"""
        super().resizeEvent(event)
        
        width = event.size().width()
        
        # Determine breakpoint
        if width >= 1024:
            new_breakpoint = "desktop"
        elif width >= 768:
            new_breakpoint = "tablet"
        else:
            new_breakpoint = "compact"
        
        # Apply breakpoint changes if changed
        if new_breakpoint != self.current_breakpoint:
            self.current_breakpoint = new_breakpoint
            self._apply_breakpoint()
    
    def _apply_breakpoint(self):
        """Apply layout changes based on current breakpoint"""
        if self.current_breakpoint == "desktop":
            # Full sidebar if not manually collapsed
            if not self.sidebar_collapsed:
                self.sidebar.setFixedWidth(220)
        elif self.current_breakpoint == "tablet":
            # Auto-collapse sidebar
            if not self.sidebar_collapsed:
                self._toggle_sidebar()
        elif self.current_breakpoint == "compact":
            # Hide sidebar (would need hamburger menu implementation)
            if not self.sidebar_collapsed:
                self._toggle_sidebar()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dashboard = DictaPilotMainDashboard()
    dashboard.show()
    sys.exit(app.exec())
