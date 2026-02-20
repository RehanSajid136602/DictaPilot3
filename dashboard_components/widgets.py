"""
DictaPilot Dashboard Reusable Widgets
Button variants, dropdowns, search bars, checkboxes, toggles, and sliders.

MIT License
Copyright (c) 2026 Rehan
"""

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QPushButton, QLineEdit, QComboBox, QCheckBox,
    QSlider, QWidget, QHBoxLayout, QLabel
)
from PySide6.QtGui import QIcon
from dashboard_themes import get_theme_manager
from dashboard_components.accessibility import apply_focus_style, set_accessible_properties


class StyledButton(QPushButton):
    """Button with variants: primary, secondary, destructive, ghost"""
     
    def __init__(self, text: str = "", variant: str = "primary", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.theme_manager = get_theme_manager()
        self._apply_style()
         
         # Accessibility
        self.setAccessibleName(f"{text} button")
        self.setAccessibleDescription(f"{variant} button")
     
    def _apply_style(self):
        """Apply variant-specific styling"""
        tokens = self.theme_manager.get_current_tokens()
         
        if self.variant == "primary":
            bg = tokens["accent-blue"]
            text_color = tokens["bg-base"]
            hover_bg = tokens["accent-mauve"]
        elif self.variant == "secondary":
            bg = tokens["bg-surface1"]
            text_color = tokens["text-primary"]
            hover_bg = tokens["bg-surface2"]
        elif self.variant == "destructive":
            bg = tokens["accent-red"]
            text_color = tokens["bg-base"]
            hover_bg = "#e06c84"
        elif self.variant == "ghost":
            bg = "transparent"
            text_color = tokens["text-primary"]
            hover_bg = tokens["bg-surface0"]
        else:
            bg = tokens["bg-surface1"]
            text_color = tokens["text-primary"]
            hover_bg = tokens["bg-surface2"]
         
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {tokens["bg-surface2"]};
            }}
            QPushButton:disabled {{
                background-color: {tokens["bg-surface0"]};
                color: {tokens["text-tertiary"]};
            }}
            QPushButton:focus {{
                outline: 2px solid {tokens["accent-blue"]};
                outline-offset: 2px;
            }}
        """)
 
 
class StyledComboBox(QComboBox):
    """Styled dropdown/combobox component"""
     
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self._apply_style()
         
         # Accessibility
        self.setAccessibleName("Dropdown menu")
     
    def _apply_style(self):
        """Apply theme-based styling"""
        tokens = self.theme_manager.get_current_tokens()
         
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {tokens["bg-surface0"]};
                color: {tokens["text-primary"]};
                border: none;
                border-bottom: 2px solid transparent;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
            }}
            QComboBox:hover {{
                border-bottom: 2px solid {tokens["accent-blue"]};
            }}
            QComboBox:focus {{
                border-bottom: 2px solid {tokens["accent-blue"]};
                outline: 2px solid {tokens["accent-blue"]};
                outline-offset: 2px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {tokens["text-secondary"]};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {tokens["bg-surface0"]};
                color: {tokens["text-primary"]};
                border: none;
                selection-background-color: {tokens["accent-blue"]};
                selection-color: {tokens["bg-base"]};
            }}
        """)
 
 
class SearchBar(QWidget):
    """Search bar with debouncing and clear button"""
     
    search_triggered = Signal(str)
     
    def __init__(self, placeholder: str = "Search...", debounce_ms: int = 200, parent=None):
        super().__init__(parent)
        self.debounce_ms = debounce_ms
        self.theme_manager = get_theme_manager()
         
        self._init_ui(placeholder)
        self._setup_debounce()
         
         # Accessibility
        self.setAccessibleName(f"Search bar: {placeholder}")
     
    def _init_ui(self, placeholder: str):
        """Initialize UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
         
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.textChanged.connect(self._on_text_changed)
         
        self.clear_button = QPushButton("×")
        self.clear_button.setFixedSize(24, 24)
        self.clear_button.clicked.connect(self.clear)
        self.clear_button.setVisible(False)
        self.clear_button.setAccessibleName("Clear search")
         
        layout.addWidget(self.line_edit)
        layout.addWidget(self.clear_button)
         
        self._apply_style()
     
    def _apply_style(self):
        """Apply theme-based styling"""
        tokens = self.theme_manager.get_current_tokens()
         
        self.line_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {tokens["bg-surface0"]};
                color: {tokens["text-primary"]};
                border: none;
                border-bottom: 2px solid transparent;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QLineEdit:hover {{
                border-bottom: 2px solid {tokens["accent-blue"]};
            }}
            QLineEdit:focus {{
                border-bottom: 2px solid {tokens["accent-blue"]};
                outline: 2px solid {tokens["accent-blue"]};
                outline-offset: 2px;
            }}
        """)
         
        self.clear_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {tokens["text-secondary"]};
                border: none;
                border-radius: 12px;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {tokens["bg-surface1"]};
                color: {tokens["text-primary"]};
            }}
        """)
     
    def _setup_debounce(self):
        """Setup debounce timer"""
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._emit_search)
     
    def _on_text_changed(self, text: str):
        """Handle text change with debouncing"""
        self.clear_button.setVisible(bool(text))
        self.debounce_timer.stop()
        self.debounce_timer.start(self.debounce_ms)
     
    def _emit_search(self):
        """Emit search signal"""
        self.search_triggered.emit(self.line_edit.text())
     
    def clear(self):
        """Clear search text"""
        self.line_edit.clear()
        self.search_triggered.emit("")
     
    def text(self) -> str:
        """Get current text"""
        return self.line_edit.text()
 
 
class StyledCheckBox(QCheckBox):
    """Styled checkbox component"""
     
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.theme_manager = get_theme_manager()
        self._apply_style()
         
         # Accessibility
        self.setAccessibleName(f"Checkbox: {text}")
     
    def _apply_style(self):
        """Apply theme-based styling"""
        tokens = self.theme_manager.get_current_tokens()
         
        self.setStyleSheet(f"""
            QCheckBox {{
                color: {tokens["text-primary"]};
                font-size: 14px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: none;
                border-radius: 4px;
                background-color: {tokens["bg-surface0"]};
            }}
            QCheckBox::indicator:hover {{
                background-color: {tokens["bg-surface1"]};
            }}
            QCheckBox::indicator:checked {{
                background-color: {tokens["accent-blue"]};
                border: none;
                image: none;
            }}
            QCheckBox::indicator:checked::after {{
                content: "✓";
            }}
            QCheckBox:focus {{
                outline: 2px solid {tokens["accent-blue"]};
                outline-offset: 2px;
            }}
        """)
 
 
class ToggleSwitch(QWidget):
    """Toggle switch component"""
     
    toggled = Signal(bool)
     
    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self._checked = checked
        self.theme_manager = get_theme_manager()
         
        self.setFixedSize(44, 24)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
         
         # Accessibility
        self.setAccessibleName("Toggle switch")
        self._update_accessible_state()
     
    def _update_accessible_state(self):
        """Update accessible state description"""
        state = "on" if self._checked else "off"
        self.setAccessibleDescription(f"Toggle switch is {state}")
     
    def mousePressEvent(self, event):
        """Handle mouse press"""
        self._checked = not self._checked
        self.toggled.emit(self._checked)
        self._update_accessible_state()
        self.update()
     
    def keyPressEvent(self, event):
        """Handle keyboard activation"""
        if event.key() in (Qt.Key_Space, Qt.Key_Return):
            self._checked = not self._checked
            self.toggled.emit(self._checked)
            self._update_accessible_state()
            self.update()
        else:
            super().keyPressEvent(event)
     
    def paintEvent(self, event):
        """Paint the toggle switch"""
        from PySide6.QtGui import QPainter, QColor, QPen
         
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
         
        tokens = self.theme_manager.get_current_tokens()
         
         # Draw track
        track_color = QColor(tokens["accent-blue"] if self._checked else tokens["bg-surface2"])
        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(0, 0, 44, 24, 12, 12)
         
         # Draw thumb
        thumb_x = 22 if self._checked else 2
        thumb_color = QColor(tokens["bg-base"])
        painter.setBrush(thumb_color)
        painter.drawEllipse(thumb_x, 2, 20, 20)
         
         # Draw focus indicator
        if self.hasFocus():
            focus_color = QColor(tokens["accent-blue"])
            painter.setPen(QPen(focus_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(0, 0, 44, 24, 12, 12)
     
    def isChecked(self) -> bool:
        """Get checked state"""
        return self._checked
     
    def setChecked(self, checked: bool):
        """Set checked state"""
        if self._checked != checked:
            self._checked = checked
            self.toggled.emit(self._checked)
            self._update_accessible_state()
            self.update()
 
 
class StyledSlider(QWidget):
    """Styled slider component with value label"""
     
    valueChanged = Signal(int)
     
    def __init__(self, minimum: int = 0, maximum: int = 100, value: int = 50, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
         
        self._init_ui(minimum, maximum, value)
         
         # Accessibility
        self.setAccessibleName(f"Slider: value {value}")
     
    def _init_ui(self, minimum: int, maximum: int, value: int):
        """Initialize UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
         
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.slider.setValue(value)
        self.slider.valueChanged.connect(self._on_value_changed)
        self.slider.setAccessibleName(f"Slider from {minimum} to {maximum}")
         
        self.value_label = QLabel(str(value))
        self.value_label.setFixedWidth(40)
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
         
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.value_label)
         
        self._apply_style()
     
    def _apply_style(self):
        """Apply theme-based styling"""
        tokens = self.theme_manager.get_current_tokens()
         
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {tokens["bg-surface1"]};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {tokens["accent-blue"]};
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {tokens["accent-mauve"]};
            }}
            QSlider::sub-page:horizontal {{
                background: {tokens["accent-blue"]};
                border-radius: 3px;
            }}
        """)
         
        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {tokens["text-secondary"]};
                font-size: 14px;
            }}
        """)
     
    def _on_value_changed(self, value: int):
        """Handle value change"""
        self.value_label.setText(str(value))
        self.valueChanged.emit(value)
        self.setAccessibleName(f"Slider: value {value}")
     
    def value(self) -> int:
        """Get current value"""
        return self.slider.value()
     
    def setValue(self, value: int):
        """Set value"""
        self.slider.setValue(value)
