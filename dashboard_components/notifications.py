"""
DictaPilot Dashboard Notification Components
Toast notifications and modal dialogs.

MIT License
Copyright (c) 2026 Rehan
"""

from typing import Optional, List
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QDialog, QApplication
)
from PySide6.QtGui import QFont

from dashboard_themes import get_theme_manager
from dashboard_components.accessibility import FocusTrap, detect_reduced_motion


class ToastNotification(QFrame):
    """Toast notification with auto-dismiss"""
    
    closed = Signal()
    
    def __init__(self, message: str, toast_type: str = "info", duration: int = 5000, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.toast_type = toast_type
        self.duration = duration
        self.reduced_motion = detect_reduced_motion()
        
        self._init_ui(message)
        self._setup_auto_dismiss()
    
    def _init_ui(self, message: str):
        """Initialize UI"""
        self.setFixedWidth(360)
        self.setMaximumHeight(100)
        
        # Style based on type
        border_colors = {
            "success": self.theme_manager.get_color("accent-green"),
            "warning": self.theme_manager.get_color("accent-yellow"),
            "error": self.theme_manager.get_color("accent-red"),
            "info": self.theme_manager.get_color("accent-blue"),
        }
        
        icons = {
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "info": "ℹ️",
        }
        
        border_color = border_colors.get(self.toast_type, border_colors["info"])
        icon = icons.get(self.toast_type, icons["info"])
        
        bg_color = self.theme_manager.get_color("bg-surface0")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-left: 3px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"color: {self.theme_manager.get_color('text-primary')}; font-size: 14px;")
        layout.addWidget(message_label, 1)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.theme_manager.get_color('text-secondary')};
                border: none;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: {self.theme_manager.get_color('text-primary')};
            }}
        """)
        close_btn.clicked.connect(self._close)
        layout.addWidget(close_btn)
        
        # Set accessible name
        self.setAccessibleName(f"{self.toast_type} notification: {message}")
    
    def _setup_auto_dismiss(self):
        """Setup auto-dismiss timer"""
        if self.duration > 0:
            QTimer.singleShot(self.duration, self._close)
    
    def _close(self):
        """Close the toast"""
        self.closed.emit()
        self.deleteLater()


class ToastManager(QWidget):
    """Manages toast notifications with stacking"""
    
    MAX_TOASTS = 3
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.toasts: List[ToastNotification] = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.layout.addStretch()
        
        self._position_window()
    
    def _position_window(self):
        """Position window in bottom-right corner"""
        if self.parent():
            parent_rect = self.parent().geometry()
            self.setGeometry(
                parent_rect.right() - 380,
                parent_rect.bottom() - 400,
                380,
                400
            )
    
    def show_toast(self, message: str, toast_type: str = "info", duration: int = 5000):
        """Show a toast notification"""
        # Remove oldest if at max
        if len(self.toasts) >= self.MAX_TOASTS:
            oldest = self.toasts.pop(0)
            oldest.deleteLater()
        
        # Create new toast
        toast = ToastNotification(message, toast_type, duration)
        toast.closed.connect(lambda: self._remove_toast(toast))
        
        self.toasts.append(toast)
        self.layout.insertWidget(self.layout.count() - 1, toast)
        
        self.show()
        self.raise_()
    
    def _remove_toast(self, toast: ToastNotification):
        """Remove a toast from the list"""
        if toast in self.toasts:
            self.toasts.remove(toast)
        
        if not self.toasts:
            self.hide()


class Modal(QDialog):
    """Modal dialog with backdrop"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.setWindowTitle(title)
        self._init_ui(title)
        self.focus_trap = FocusTrap(self)
    
    def _init_ui(self, title: str):
        """Initialize UI"""
        self.setModal(True)
        self.setFixedWidth(480)
        
        # Style
        bg_color = self.theme_manager.get_color("bg-surface0")
        text_color = self.theme_manager.get_color("text-primary")
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                border-radius: 12px;
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setStyleSheet(f"color: {text_color};")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.theme_manager.get_color('text-secondary')};
                border: none;
                font-size: 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: {text_color};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        
        main_layout.addLayout(header_layout)
        
        # Content area (to be filled by subclasses)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        main_layout.addLayout(self.content_layout)
        
        # Footer with buttons (to be filled by subclasses)
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setSpacing(12)
        self.footer_layout.addStretch()
        main_layout.addLayout(self.footer_layout)
        
        # Set accessible name
        self.setAccessibleName(f"Modal dialog: {title}")
    
    def add_content(self, widget: QWidget):
        """Add widget to content area"""
        self.content_layout.addWidget(widget)
    
    def add_button(self, text: str, variant: str = "secondary", callback=None) -> QPushButton:
        """Add button to footer"""
        btn = QPushButton(text)
        btn.setProperty("variant", variant)
        btn.setMinimumWidth(80)
        
        if callback:
            btn.clicked.connect(callback)
        
        self.footer_layout.addWidget(btn)
        return btn
    
    def showEvent(self, event):
        """Handle show event - save focus"""
        super().showEvent(event)
        self.focus_trap.activate()
    
    def closeEvent(self, event):
        """Handle close event - restore focus"""
        super().closeEvent(event)
        self.focus_trap.deactivate()
    
    def keyPressEvent(self, event):
        """Handle key press - Escape to close"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


class ConfirmDialog(Modal):
    """Confirmation dialog"""
    
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(title, parent)
        
        # Add message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"color: {self.theme_manager.get_color('text-primary')}; font-size: 14px;")
        self.add_content(message_label)
        
        # Add buttons
        self.add_button("Cancel", "secondary", self.reject)
        self.add_button("Confirm", "primary", self.accept)


class SpinnerWidget(QWidget):
    """Inline spinner widget"""
    
    def __init__(self, size: int = 20, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.size = size
        self.angle = 0
        
        self.setFixedSize(size, size)
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._rotate)
        self.timer.start(50)  # 20fps
    
    def _rotate(self):
        """Rotate animation"""
        self.angle = (self.angle + 30) % 360
        self.update()
    
    def paintEvent(self, event):
        """Paint the spinner"""
        from PySide6.QtGui import QPainter, QPen
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        color = self.theme_manager.get_color("accent-blue")
        pen = QPen(color)
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Draw arc
        rect = QRect(2, 2, self.size - 4, self.size - 4)
        painter.drawArc(rect, self.angle * 16, 120 * 16)


class EmptyStateWidget(QWidget):
    """Empty state widget with icon, message, and action button"""
    
    action_clicked = Signal()
    
    def __init__(self, icon: str, message: str, action_text: str = "", parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self._init_ui(icon, message, action_text)
        
        # Accessibility
        self.setAccessibleName(f"Empty state: {message}")
    
    def _init_ui(self, icon: str, message: str, action_text: str):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            font-size: 48px;
            color: {self.theme_manager.get_color('text-tertiary')};
        """)
        layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            color: {self.theme_manager.get_color('text-secondary')};
            font-size: 16px;
        """)
        layout.addWidget(message_label)
        
        # Action button (optional)
        if action_text:
            action_btn = QPushButton(action_text)
            action_btn.setAccessibleName(f"{action_text} button")
            action_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme_manager.get_color('accent-blue')};
                    color: {self.theme_manager.get_color('bg-base')};
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {self.theme_manager.get_color('accent-mauve')};
                }}
                QPushButton:focus {{
                    outline: 2px solid {self.theme_manager.get_color('accent-blue')};
                    outline-offset: 2px;
                }}
            """)
            action_btn.clicked.connect(self.action_clicked.emit)
            layout.addWidget(action_btn, alignment=Qt.AlignCenter)


class ErrorBanner(QFrame):
    """Error banner widget with icon, message, and action buttons"""
    
    action_clicked = Signal(str)  # Emits action name
    dismissed = Signal()
    
    def __init__(self, message: str, actions: List[tuple] = None, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self._init_ui(message, actions or [])
        
        # Accessibility
        self.setAccessibleName(f"Error: {message}")
        self.setAccessibleDescription("Error banner with actions")
    
    def _init_ui(self, message: str, actions: List[tuple]):
        """Initialize UI
        
        Args:
            message: Error message to display
            actions: List of (action_name, button_text) tuples
        """
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme_manager.get_color('accent-red')};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            color: {self.theme_manager.get_color('bg-base')};
            font-size: 14px;
            font-weight: 500;
        """)
        layout.addWidget(message_label, 1)
        
        # Action buttons
        for action_name, button_text in actions:
            btn = QPushButton(button_text)
            btn.setAccessibleName(f"{button_text} button")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme_manager.get_color('bg-base')};
                    color: {self.theme_manager.get_color('accent-red')};
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {self.theme_manager.get_color('bg-surface0')};
                }}
                QPushButton:focus {{
                    outline: 2px solid {self.theme_manager.get_color('bg-base')};
                    outline-offset: 2px;
                }}
            """)
            btn.clicked.connect(lambda checked=False, name=action_name: self.action_clicked.emit(name))
            layout.addWidget(btn)
        
        # Dismiss button
        dismiss_btn = QPushButton("×")
        dismiss_btn.setFixedSize(24, 24)
        dismiss_btn.setAccessibleName("Dismiss error banner")
        dismiss_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.theme_manager.get_color('bg-base')};
                border: none;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.2);
            }}
        """)
        dismiss_btn.clicked.connect(self._dismiss)
        layout.addWidget(dismiss_btn)
        
    def _dismiss(self):
        """Dismiss the banner"""
        self.dismissed.emit()
        self.deleteLater()


class NotificationBell(QWidget):
    """Notification bell with badge count and dropdown"""
    
    clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self._count = 0
        self.setFixedSize(40, 40)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self._update_accessible_name()
     
    def _update_accessible_name(self):
        """Update accessible name with current count"""
        if self._count == 0:
            self.setAccessibleName("Notifications: No unread notifications")
        elif self._count == 1:
            self.setAccessibleName("Notifications: 1 unread notification")
        else:
            self.setAccessibleName(f"Notifications: {self._count} unread notifications")
    
    def set_count(self, count: int):
        """Set notification count"""
        self._count = count
        self._update_accessible_name()
        self.update()
    
    def get_count(self) -> int:
        """Get notification count"""
        return self._count
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        self.clicked.emit()
     
    def keyPressEvent(self, event):
        """Handle keyboard activation"""
        if event.key() in (Qt.Key_Space, Qt.Key_Return):
            self.clicked.emit()
        else:
            super().keyPressEvent(event)
    
    def paintEvent(self, event):
        """Paint the notification bell"""
        from PySide6.QtGui import QPainter, QColor, QPen, QFont
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        tokens = self.theme_manager.get_current_tokens()
        
        # Draw bell icon (simplified)
        bell_color = QColor(tokens["text-secondary"])
        painter.setPen(QPen(bell_color, 2))
        painter.setBrush(Qt.NoBrush)
        
        # Bell body
        painter.drawEllipse(10, 8, 20, 20)
        # Bell top
        painter.drawLine(20, 8, 20, 5)
        
        # Draw badge if count > 0
        if self._count > 0:
            badge_color = QColor(tokens["accent-red"])
            painter.setPen(Qt.NoPen)
            painter.setBrush(badge_color)
           
           # Badge circle
            badge_size = 16
            painter.drawEllipse(24, 4, badge_size, badge_size)
           
           # Badge text
            painter.setPen(QColor(tokens["bg-base"]))
            font = QFont()
            font.setPixelSize(10)
            font.setBold(True)
            painter.setFont(font)
           
            count_text = str(self._count) if self._count < 100 else "99+"
            painter.drawText(24, 4, badge_size, badge_size, Qt.AlignCenter, count_text)
        
        # Draw focus indicator
        if self.hasFocus():
            focus_color = QColor(tokens["accent-blue"])
            painter.setPen(QPen(focus_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(2, 2, 36, 36, 4, 4)
