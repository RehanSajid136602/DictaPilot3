"""
DictaPilot Dashboard Accessibility Utilities
Focus management, reduced motion detection, and accessibility helpers.

MIT License
Copyright (c) 2026 Rehan
"""

from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPalette
from dashboard_themes import get_theme_manager


def detect_reduced_motion() -> bool:
    """Detect if user prefers reduced motion"""
    settings = QSettings()
    reduced_motion = settings.value("accessibility/reduced_motion", False, type=bool)
    return reduced_motion


def apply_focus_style(widget: QWidget):
    """Apply focus indicator styling to a widget"""
    theme_manager = get_theme_manager()
    tokens = theme_manager.get_current_tokens()
    
    existing_style = widget.styleSheet()
    focus_style = f"""
        *:focus {{
            outline: 2px solid {tokens["accent-blue"]};
            outline-offset: 2px;
        }}
    """
    widget.setStyleSheet(existing_style + focus_style)


def set_accessible_properties(widget: QWidget, name: str, description: str = ""):
    """Set accessible name and description for a widget"""
    widget.setAccessibleName(name)
    if description:
        widget.setAccessibleDescription(description)


class FocusTrap:
    """Focus trap for modal dialogs"""
    
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.previous_focus = None
        self.focusable_widgets = []
    
    def activate(self):
        """Activate focus trap"""
        self.previous_focus = QApplication.focusWidget()
        self.focusable_widgets = self._find_focusable_widgets(self.widget)
        
        if self.focusable_widgets:
            self.focusable_widgets[0].setFocus()
        
        self.widget.installEventFilter(self)
    
    def deactivate(self):
        """Deactivate focus trap and restore previous focus"""
        self.widget.removeEventFilter(self)
        
        if self.previous_focus:
            self.previous_focus.setFocus()
    
    def _find_focusable_widgets(self, parent: QWidget) -> list:
        """Find all focusable widgets in a container"""
        focusable = []
        
        for child in parent.findChildren(QWidget):
            if child.focusPolicy() != Qt.NoFocus and child.isVisible() and child.isEnabled():
                focusable.append(child)
        
        return focusable
    
    def eventFilter(self, obj, event):
        """Filter Tab key events to trap focus"""
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QKeyEvent
        
        if event.type() == QEvent.KeyPress:
            key_event = QKeyEvent(event)
            
            if key_event.key() == Qt.Key_Tab:
                current = QApplication.focusWidget()
                if current in self.focusable_widgets:
                    current_idx = self.focusable_widgets.index(current)
                    
                    if key_event.modifiers() & Qt.ShiftModifier:
                        next_idx = (current_idx - 1) % len(self.focusable_widgets)
                    else:
                        next_idx = (current_idx + 1) % len(self.focusable_widgets)
                    
                    self.focusable_widgets[next_idx].setFocus()
                    return True
        
        return False
