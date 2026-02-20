"""
DictaPilot Dashboard Theme System
Token-based color, typography, and spacing system extending Catppuccin Mocha themes.

MIT License
Copyright (c) 2026 Rehan
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

# Color Tokens - Dark Theme (Catppuccin Mocha)
DARK_TOKENS = {
    # Backgrounds
    "bg-base": "#1e1e2e",
    "bg-mantle": "#181825",
    "bg-surface0": "#313244",
    "bg-surface1": "#45475a",
    "bg-surface2": "#585b70",
    
    # Text
    "text-primary": "#cdd6f4",
    "text-secondary": "#a6adc8",
    "text-tertiary": "#6c7086",
    
    # Accents
    "accent-blue": "#89b4fa",
    "accent-green": "#a6e3a1",
    "accent-yellow": "#f9e2af",
    "accent-red": "#f38ba8",
    "accent-peach": "#fab387",
    "accent-mauve": "#cba6f7",
}

# Color Tokens - Light Theme
LIGHT_TOKENS = {
    # Backgrounds
    "bg-base": "#f5f5f5",
    "bg-mantle": "#e8e8e8",
    "bg-surface0": "#ffffff",
    "bg-surface1": "#e0e0e0",
    "bg-surface2": "#d0d0d0",
    
    # Text
    "text-primary": "#1e1e2e",
    "text-secondary": "#555555",
    "text-tertiary": "#888888",
    
    # Accents
    "accent-blue": "#2196f3",
    "accent-green": "#2e7d32",
    "accent-yellow": "#e65100",
    "accent-red": "#c62828",
    "accent-peach": "#ff6f00",
    "accent-mauve": "#7b1fa2",
}

# Typography Scale
TYPOGRAPHY_TOKENS = {
    "display": {"size": 24, "weight": 700, "line_height": 32},
    "heading-1": {"size": 18, "weight": 700, "line_height": 26},
    "heading-2": {"size": 16, "weight": 600, "line_height": 24},
    "body": {"size": 14, "weight": 400, "line_height": 22},
    "body-small": {"size": 12, "weight": 400, "line_height": 18},
    "caption": {"size": 11, "weight": 400, "line_height": 16},
    "mono": {"size": 13, "weight": 400, "line_height": 20},
}

# Spacing Scale (base-4)
SPACING_TOKENS = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "2xl": 32,
}

# Border Radius
RADIUS_TOKENS = {
    "small": 6,
    "medium": 8,
    "large": 12,
}


class ThemeManager:
    """Manages theme tokens and application of themes"""
    
    def __init__(self, theme: str = "dark"):
        self.current_theme = theme
        self._color_tokens = DARK_TOKENS if theme == "dark" else LIGHT_TOKENS
        self._typography_tokens = TYPOGRAPHY_TOKENS
        self._spacing_tokens = SPACING_TOKENS
        self._radius_tokens = RADIUS_TOKENS
    
    def get_color(self, token_name: str) -> str:
        """Get color value by token name"""
        return self._color_tokens.get(token_name, "#000000")
    
    def get_typography(self, token_name: str) -> Dict[str, Any]:
        """Get typography values by token name"""
        return self._typography_tokens.get(token_name, {"size": 14, "weight": 400, "line_height": 22})
    
    def get_spacing(self, token_name: str) -> int:
        """Get spacing value by token name"""
        return self._spacing_tokens.get(token_name, 8)
    
    def get_radius(self, token_name: str) -> int:
        """Get border radius value by token name"""
        return self._radius_tokens.get(token_name, 6)
    
    def switch_theme(self, theme: str):
        """Switch between dark and light themes"""
        self.current_theme = theme
        self._color_tokens = DARK_TOKENS if theme == "dark" else LIGHT_TOKENS
    
    def get_stylesheet(self) -> str:
        """Generate complete QSS stylesheet with token injection"""
        c = self._color_tokens
        
        return f"""
QMainWindow, QWidget {{
    background-color: {c['bg-base']};
    color: {c['text-primary']};
    font-size: 14px;
}}

/* Sidebar */
QFrame#sidebar {{
    background-color: {c['bg-mantle']};
    border: none;
}}

QPushButton#nav-button {{
    background-color: transparent;
    color: {c['text-secondary']};
    border: none;
    text-align: left;
    padding: 14px 16px;
    margin: 4px 8px;
    border-radius: 8px;
    border-left: 3px solid transparent;
}}

QPushButton#nav-button:hover {{
    background-color: {c['bg-surface2']};
}}

QPushButton#nav-button[active="true"] {{
    background-color: {c['bg-surface0']};
    color: {c['text-primary']};
    border-left: none;
    font-weight: bold;
}}

/* Buttons */
QPushButton {{
    min-width: 80px;
    height: 36px;
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 400;
}}

QPushButton[variant="primary"] {{
    background-color: {c['accent-blue']};
    color: white;
    border: none;
}}

QPushButton[variant="primary"]:hover {{
    background-color: #7aa8f0;
}}

QPushButton[variant="primary"]:pressed {{
    background-color: #6b9ae0;
}}

QPushButton[variant="secondary"] {{
    background-color: {c['bg-surface1']};
    color: {c['text-primary']};
    border: none;
}}

QPushButton[variant="secondary"]:hover {{
    background-color: {c['bg-surface2']};
}}

QPushButton[variant="destructive"] {{
    background-color: {c['accent-red']};
    color: white;
    border: none;
}}

QPushButton[variant="destructive"]:hover {{
    background-color: #e07a96;
}}

QPushButton[variant="ghost"] {{
    background-color: transparent;
    color: {c['text-secondary']};
    border: none;
}}

QPushButton[variant="ghost"]:hover {{
    background-color: {c['bg-surface1']};
}}

QPushButton:disabled {{
    opacity: 0.5;
}}

QPushButton:focus {{
    outline: 2px solid {c['accent-blue']};
    outline-offset: 2px;
}}

/* Cards and Group Boxes */
QGroupBox {{
    border: none;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {c['accent-blue']};
}}

QFrame[card="true"] {{
    background-color: {c['bg-surface0']};
    border: none;
    border-radius: 12px;
    padding: 16px;
}}

/* Input Fields */
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {c['bg-surface0']};
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 6px;
    padding: 8px;
    color: {c['text-primary']};
    selection-background-color: {c['bg-surface1']};
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border-bottom: 2px solid {c['accent-blue']};
}}

QLineEdit::placeholder {{
    color: {c['text-tertiary']};
}}

/* Checkboxes */
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
}}

QCheckBox::indicator:unchecked {{
    background-color: {c['bg-surface0']};
    border: none;
}}

QCheckBox::indicator:checked {{
    background-color: {c['accent-blue']};
    border: none;
}}

/* Lists */
QListWidget {{
    background-color: {c['bg-surface0']};
    border: none;
    border-radius: 6px;
}}

QListWidget::item {{
    padding: 8px;
    border: none;
}}

QListWidget::item:hover {{
    background-color: {c['bg-surface2']};
}}

QListWidget::item:selected {{
    background-color: {c['bg-surface1']};
    color: {c['text-primary']};
}}

/* Scrollbars */
QScrollBar:vertical {{
    background-color: {c['bg-surface0']};
    width: 8px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {c['bg-surface1']};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {c['bg-surface2']};
}}

QScrollBar:horizontal {{
    background-color: {c['bg-surface0']};
    height: 8px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {c['bg-surface1']};
    border-radius: 6px;
    min-width: 20px;
}}

/* Tooltips */
QToolTip {{
    background-color: {c['bg-surface0']};
    border: none;
    border-radius: 4px;
    color: {c['text-primary']};
    padding: 4px 8px;
}}

/* Status Bar */
QStatusBar {{
    background-color: {c['bg-mantle']};
    color: {c['text-secondary']};
    border: none;
}}

/* Toolbar */
QToolBar {{
    background-color: {c['bg-mantle']};
    border: none;
    spacing: 8px;
    padding: 8px;
}}

/* Breadcrumb */
QLabel[breadcrumb="true"] {{
    color: {c['text-secondary']};
    font-size: 12px;
}}

QLabel[breadcrumb="true"][clickable="true"] {{
    color: {c['accent-blue']};
}}

QLabel[breadcrumb="true"][clickable="true"]:hover {{
    text-decoration: underline;
}}

/* Badges */
QLabel[badge="success"] {{
    background-color: rgba(166, 227, 161, 0.15);
    color: {c['accent-green']};
    border-radius: 11px;
    padding: 2px 8px;
    font-size: 11px;
}}

QLabel[badge="warning"] {{
    background-color: rgba(249, 226, 175, 0.15);
    color: {c['accent-yellow']};
    border-radius: 11px;
    padding: 2px 8px;
    font-size: 11px;
}}

QLabel[badge="error"] {{
    background-color: rgba(243, 139, 168, 0.15);
    color: {c['accent-red']};
    border-radius: 11px;
    padding: 2px 8px;
    font-size: 11px;
}}

QLabel[badge="info"] {{
    background-color: rgba(137, 180, 250, 0.15);
    color: {c['accent-blue']};
    border-radius: 11px;
    padding: 2px 8px;
    font-size: 11px;
}}
"""
    
    @staticmethod
    def detect_system_theme() -> str:
        """Detect system theme preference (dark or light)"""
        try:
            app = QApplication.instance()
            if app:
                palette = app.palette()
                bg_color = palette.color(QPalette.Window)
                # If background is dark (luminance < 128), use dark theme
                luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue())
                return "dark" if luminance < 128 else "light"
        except Exception:
            pass
        return "dark"  # Default to dark


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get or create global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        system_theme = ThemeManager.detect_system_theme()
        _theme_manager = ThemeManager(theme=system_theme)
    return _theme_manager


def set_theme(theme: str):
    """Set global theme (dark or light)"""
    manager = get_theme_manager()
    manager.switch_theme(theme)
