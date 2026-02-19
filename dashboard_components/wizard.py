 """
 DictaPilot Modern Wizard Components
 Custom wizard components for modern onboarding experience.
 
 MIT License
 Copyright (c) 2026 Rehan
 """
 
 from typing import Optional, Callable, List, Dict
 from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
 from PySide6.QtWidgets import (
     QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
     QPushButton, QStackedWidget, QGraphicsOpacityEffect
 )
 from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath
 
 from dashboard_themes import get_theme_manager
 from dashboard_components.widgets import StyledButton
 from dashboard_components.animations import FadeAnimation
 
 
 class StepIndicator(QWidget):
     """Modern horizontal step progress indicator"""
     
     def __init__(self, steps: List[Dict], parent=None):
         super().__init__(parent)
         self.steps = steps  # [{"icon": "🔑", "label": "API Key"}, ...]
         self.current_step = 0
         self.completed_steps = set()
         self.theme_manager = get_theme_manager()
         self.setFixedHeight(80)
         self._init_ui()
     
     def _init_ui(self):
         """Initialize UI"""
         layout = QHBoxLayout(self)
         layout.setContentsMargins(32, 16, 32, 16)
         layout.setSpacing(0)
         
         self.step_widgets = []
         
         for i, step in enumerate(self.steps):
             # Step widget
             step_widget = self._create_step_widget(i, step)
             self.step_widgets.append(step_widget)
             layout.addWidget(step_widget)
             
             # Connecting line (except after last step)
             if i < len(self.steps) - 1:
                 line = self._create_connecting_line()
                 layout.addWidget(line, 1)
     
     def _create_step_widget(self, index: int, step: Dict) -> QWidget:
         """Create a single step widget"""
         widget = QWidget()
         layout = QVBoxLayout(widget)
         layout.setContentsMargins(0, 0, 0, 0)
         layout.setSpacing(8)
         layout.setAlignment(Qt.AlignCenter)
         
         # Circle with number/icon
         circle = StepCircle(index + 1, step.get("icon", ""), self)
         circle.setObjectName(f"step_{index}")
         layout.addWidget(circle, alignment=Qt.AlignCenter)
         
         # Label
         label = QLabel(step.get("label", f"Step {index + 1}"))
         label.setAlignment(Qt.AlignCenter)
         label.setStyleSheet(f"""
             color: {self.theme_manager.get_color('text-secondary')};
             font-size: 12px;
         """)
         label.setObjectName(f"label_{index}")
         layout.addWidget(label)
         
         return widget
     
     def _create_connecting_line(self) -> QFrame:
         """Create connecting line between steps"""
         line = QFrame()
         line.setFrameShape(QFrame.HLine)
         line.setFixedHeight(2)
         line.setStyleSheet(f"""
             background-color: {self.theme_manager.get_color('bg-surface1')};
             border: none;
         """)
         line.setObjectName("connecting_line")
         return line
     
     def set_current_step(self, index: int):
         """Update current step with visual feedback"""
         old_step = self.current_step
         self.current_step = index
         
         # Mark previous steps as completed
         for i in range(index):
             self.completed_steps.add(i)
         
         # Update all step visuals
         self._update_step_visuals()
     
     def _update_step_visuals(self):
         """Update visual state of all steps"""
         for i, step_widget in enumerate(self.step_widgets):
             circle = step_widget.findChild(StepCircle, f"step_{i}")
             label = step_widget.findChild(QLabel, f"label_{i}")
             
             if circle:
                 if i in self.completed_steps:
                     circle.set_state("completed")
                 elif i == self.current_step:
                     circle.set_state("active")
                 else:
                     circle.set_state("pending")
             
             if label:
                 if i == self.current_step:
                     label.setStyleSheet(f"""
                         color: {self.theme_manager.get_color('text-primary')};
                         font-size: 12px;
                         font-weight: 600;
                     """)
                 else:
                     label.setStyleSheet(f"""
                         color: {self.theme_manager.get_color('text-secondary')};
                         font-size: 12px;
                     """)
 
 
 class StepCircle(QWidget):
     """Circular step indicator with number/icon"""
     
     def __init__(self, number: int, icon: str = "", parent=None):
         super().__init__(parent)
         self.number = number
         self.icon = icon
         self.state = "pending"  # pending, active, completed
         self.theme_manager = get_theme_manager()
         self.setFixedSize(40, 40)
     
     def set_state(self, state: str):
         """Set the state of the step circle"""
         if state != self.state:
             self.state = state
             self.update()
     
     def paintEvent(self, event):
         """Paint the step circle"""
         painter = QPainter(self)
         painter.setRenderHint(QPainter.Antialiasing)
         
         tokens = self.theme_manager._color_tokens
         
         # Determine colors based on state
         if self.state == "completed":
             bg_color = QColor(tokens["accent-green"])
             border_color = QColor(tokens["accent-green"])
             text_color = QColor("#ffffff")
             text = "✓"
         elif self.state == "active":
             bg_color = QColor(tokens["accent-blue"])
             border_color = QColor(tokens["accent-blue"])
             text_color = QColor("#ffffff")
             text = self.icon if self.icon else str(self.number)
         else:  # pending
             bg_color = QColor(tokens["bg-surface0"])
             border_color = QColor(tokens["bg-surface2"])
             text_color = QColor(tokens["text-tertiary"])
             text = str(self.number)
         
         # Draw circle
         painter.setPen(QPen(border_color, 2))
         painter.setBrush(bg_color)
         painter.drawEllipse(2, 2, 36, 36)
         
         # Draw text/icon
         painter.setPen(text_color)
         font = QFont()
         font.setPixelSize(16 if text == "✓" else 14)
         font.setBold(True)
         painter.setFont(font)
         painter.drawText(self.rect(), Qt.AlignCenter, text)
 
 
 class WizardPage(QFrame):
     """Base class for wizard pages with consistent styling"""
     
     def __init__(self, parent=None):
         super().__init__(parent)
         self.theme_manager = get_theme_manager()
         self.setProperty("card", True)
         self._init_base_ui()
     
     def _init_base_ui(self):
         """Initialize base UI structure"""
         self.main_layout = QVBoxLayout(self)
         self.main_layout.setContentsMargins(32, 32, 32, 32)
         self.main_layout.setSpacing(24)
     
     def validate_page(self) -> bool:
         """Override to add validation logic"""
         return True
     
     def on_show(self):
         """Called when page is shown"""
         pass
     
     def on_hide(self):
         """Called when page is hidden"""
         pass
 
 
 class ModernWizard(QWidget):
     """Custom wizard with modern stepper navigation"""
     
     finished = Signal(bool)  # True if completed, False if cancelled
     
     def __init__(self, title: str = "Setup Wizard", parent=None):
         super().__init__(parent)
         self.title = title
         self.pages: List[WizardPage] = []
         self.step_info: List[Dict] = []
         self.current_page_index = 0
         self.theme_manager = get_theme_manager()
         self._init_ui()
     
     def _init_ui(self):
         """Initialize UI"""
         layout = QVBoxLayout(self)
         layout.setContentsMargins(0, 0, 0, 0)
         layout.setSpacing(0)
         
         # Header with title
         header = self._create_header()
         layout.addWidget(header)
         
         # Step indicator (will be populated when pages are added)
         self.step_indicator = None
         
         # Page container
         self.page_container = QStackedWidget()
         layout.addWidget(self.page_container, 1)
         
         # Navigation buttons
         nav_bar = self._create_navigation_bar()
         layout.addWidget(nav_bar)
     
     def _create_header(self) -> QWidget:
         """Create header with title"""
         header = QFrame()
         header.setStyleSheet(f"""
             QFrame {{
                 background-color: {self.theme_manager.get_color('bg-mantle')};
                 border-bottom: 1px solid {self.theme_manager.get_color('bg-surface1')};
             }}
         """)
         
         layout = QVBoxLayout(header)
         layout.setContentsMargins(32, 24, 32, 16)
         layout.setSpacing(8)
         
         # Title
         title_label = QLabel(self.title)
         font = QFont()
         font.setPixelSize(24)
         font.setBold(True)
         title_label.setFont(font)
         title_label.setStyleSheet(f"color: {self.theme_manager.get_color('text-primary')};")
         layout.addWidget(title_label)
         
         return header
     
     def _create_navigation_bar(self) -> QWidget:
         """Create navigation bar with buttons"""
         nav_bar = QFrame()
         nav_bar.setStyleSheet(f"""
             QFrame {{
                 background-color: {self.theme_manager.get_color('bg-mantle')};
                 border-top: 1px solid {self.theme_manager.get_color('bg-surface1')};
             }}
         """)
         
         layout = QHBoxLayout(nav_bar)
         layout.setContentsMargins(32, 16, 32, 16)
         layout.setSpacing(12)
         
         # Back button
         self.back_button = StyledButton("Back", variant="secondary")
         self.back_button.clicked.connect(self._go_back)
         self.back_button.setMinimumWidth(100)
         layout.addWidget(self.back_button)
         
         layout.addStretch()
         
         # Cancel button
         self.cancel_button = StyledButton("Cancel", variant="ghost")
         self.cancel_button.clicked.connect(self._cancel)
         self.cancel_button.setMinimumWidth(100)
         layout.addWidget(self.cancel_button)
         
         # Next/Finish button
         self.next_button = StyledButton("Next", variant="primary")
         self.next_button.clicked.connect(self._go_next)
         self.next_button.setMinimumWidth(100)
         layout.addWidget(self.next_button)
         
         return nav_bar
     
     def add_page(self, page: WizardPage, step_info: Dict):
         """Add a page to the wizard
         
         Args:
             page: WizardPage instance
             step_info: Dict with "icon" and "label" keys
         """
         self.pages.append(page)
         self.step_info.append(step_info)
         self.page_container.addWidget(page)
         
         # Create/update step indicator
         if self.step_indicator:
             self.step_indicator.deleteLater()
         
         self.step_indicator = StepIndicator(self.step_info)
         # Insert after header (index 1)
         self.layout().insertWidget(1, self.step_indicator)
     
     def _update_navigation_buttons(self):
         """Update navigation button states"""
         is_first = self.current_page_index == 0
         is_last = self.current_page_index == len(self.pages) - 1
         
         self.back_button.setEnabled(not is_first)
         self.next_button.setText("Finish" if is_last else "Next")
     
     def _go_back(self):
         """Go to previous page"""
         if self.current_page_index > 0:
             self._change_page(self.current_page_index - 1)
     
     def _go_next(self):
         """Go to next page or finish"""
         current_page = self.pages[self.current_page_index]
         
         # Validate current page
         if not current_page.validate_page():
             return
         
         if self.current_page_index < len(self.pages) - 1:
             self._change_page(self.current_page_index + 1)
         else:
             self._finish()
     
     def _change_page(self, new_index: int):
         """Change to a different page with animation"""
         if new_index < 0 or new_index >= len(self.pages):
             return
         
         old_page = self.pages[self.current_page_index]
         new_page = self.pages[new_index]
         
         # Call lifecycle methods
         old_page.on_hide()
         
         # Update index
         self.current_page_index = new_index
         
         # Update step indicator
         if self.step_indicator:
             self.step_indicator.set_current_step(new_index)
         
         # Change page with fade animation
         self.page_container.setCurrentWidget(new_page)
         FadeAnimation.fade_in(new_page, duration=200)
         
         # Call lifecycle method
         new_page.on_show()
         
         # Update buttons
         self._update_navigation_buttons()
     
     def _cancel(self):
         """Cancel the wizard"""
         self.finished.emit(False)
         self.close()
     
     def _finish(self):
         """Finish the wizard"""
         self.finished.emit(True)
         self.close()
     
     def start(self):
         """Start the wizard"""
         if self.pages:
             self._change_page(0)
             self._update_navigation_buttons()
 
 
 class ToastNotification(QWidget):
     """Non-blocking toast notification"""
     
     def __init__(self, message: str, variant: str = "info", parent=None):
         super().__init__(parent)
         self.message = message
         self.variant = variant  # info, success, warning, error
         self.theme_manager = get_theme_manager()
         self._init_ui()
         self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
         self.setAttribute(Qt.WA_TranslucentBackground)
     
     def _init_ui(self):
         """Initialize UI"""
         layout = QHBoxLayout(self)
         layout.setContentsMargins(16, 12, 16, 12)
         layout.setSpacing(12)
         
         # Icon
         icon_map = {
             "success": "✓",
             "warning": "⚠",
             "error": "✗",
             "info": "ℹ"
         }
         icon = QLabel(icon_map.get(self.variant, "ℹ"))
         icon.setStyleSheet("font-size: 18px;")
         layout.addWidget(icon)
         
         # Message
         message_label = QLabel(self.message)
         message_label.setWordWrap(True)
         layout.addWidget(message_label, 1)
         
         # Styling
         color_map = {
             "success": self.theme_manager.get_color("accent-green"),
             "warning": self.theme_manager.get_color("accent-yellow"),
             "error": self.theme_manager.get_color("accent-red"),
             "info": self.theme_manager.get_color("accent-blue")
         }
         
         bg_color = self.theme_manager.get_color("bg-surface0")
         accent_color = color_map.get(self.variant, color_map["info"])
         
         self.setStyleSheet(f"""
             QWidget {{
                 background-color: {bg_color};
                 border-left: 4px solid {accent_color};
                 border-radius: 6px;
             }}
             QLabel {{
                 color: {self.theme_manager.get_color('text-primary')};
             }}
         """)
     
     def show_toast(self, duration: int = 3000):
         """Show toast and auto-dismiss after duration"""
         self.show()
         FadeAnimation.fade_in(self, duration=200)
         
         # Auto-dismiss
         QTimer.singleShot(duration, self._dismiss)
     
     def _dismiss(self):
         """Dismiss the toast"""
         FadeAnimation.fade_out(self, duration=200, on_finished=self.deleteLater)
