 """
 DictaPilot Animation Utilities
 Reusable animation helpers for smooth UI transitions.
 
 MIT License
 Copyright (c) 2026 Rehan
 """
 
 from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QTimer, Property
 from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect
 from PySide6.QtGui import QPainter, QColor
 
 
 class FadeAnimation:
     """Fade in/out animation helper"""
     
     @staticmethod
     def fade_in(widget: QWidget, duration: int = 200, on_finished=None):
         """Fade in a widget"""
         effect = QGraphicsOpacityEffect(widget)
         widget.setGraphicsEffect(effect)
         
         animation = QPropertyAnimation(effect, b"opacity")
         animation.setDuration(duration)
         animation.setStartValue(0.0)
         animation.setEndValue(1.0)
         animation.setEasingCurve(QEasingCurve.OutCubic)
         
         if on_finished:
             animation.finished.connect(on_finished)
         
         animation.start()
         return animation
     
     @staticmethod
     def fade_out(widget: QWidget, duration: int = 200, on_finished=None):
         """Fade out a widget"""
         effect = widget.graphicsEffect()
         if not effect:
             effect = QGraphicsOpacityEffect(widget)
             widget.setGraphicsEffect(effect)
         
         animation = QPropertyAnimation(effect, b"opacity")
         animation.setDuration(duration)
         animation.setStartValue(1.0)
         animation.setEndValue(0.0)
         animation.setEasingCurve(QEasingCurve.InCubic)
         
         if on_finished:
             animation.finished.connect(on_finished)
         
         animation.start()
         return animation
 
 
 class SlideAnimation:
     """Slide animation helper"""
     
     @staticmethod
     def slide_in(widget: QWidget, direction: str = "left", distance: int = 20, duration: int = 200):
         """Slide in a widget from a direction"""
         start_pos = widget.pos()
         
         if direction == "left":
             offset = QPoint(-distance, 0)
         elif direction == "right":
             offset = QPoint(distance, 0)
         elif direction == "up":
             offset = QPoint(0, -distance)
         else:  # down
             offset = QPoint(0, distance)
         
         widget.move(start_pos + offset)
         
         animation = QPropertyAnimation(widget, b"pos")
         animation.setDuration(duration)
         animation.setStartValue(start_pos + offset)
         animation.setEndValue(start_pos)
         animation.setEasingCurve(QEasingCurve.OutCubic)
         animation.start()
         
         return animation
 
 
 class ScaleAnimation:
     """Scale animation helper for hover effects"""
     
     @staticmethod
     def scale_on_hover(widget: QWidget, scale: float = 1.02):
         """Add scale effect on hover (requires custom widget with scale property)"""
         # This is a placeholder - actual implementation would need custom widget
         pass
 
 
 class LoadingSpinner(QWidget):
     """Animated loading spinner widget"""
     
     def __init__(self, size: int = 24, parent=None):
         super().__init__(parent)
         self.size = size
         self.angle = 0
         self.setFixedSize(size, size)
         
         self.timer = QTimer(self)
         self.timer.timeout.connect(self._rotate)
         self.timer.setInterval(16)  # ~60fps
     
     def start(self):
         """Start spinning"""
         self.timer.start()
         self.show()
     
     def stop(self):
         """Stop spinning"""
         self.timer.stop()
         self.hide()
     
     def _rotate(self):
         """Rotate the spinner"""
         self.angle = (self.angle + 10) % 360
         self.update()
     
     def paintEvent(self, event):
         """Paint the spinner"""
         painter = QPainter(self)
         painter.setRenderHint(QPainter.Antialiasing)
         
         # Draw spinning arc
         from dashboard_themes import get_theme_manager
         theme = get_theme_manager()
         color = QColor(theme.get_color("accent-blue"))
         
         painter.setPen(color)
         painter.translate(self.size / 2, self.size / 2)
         painter.rotate(self.angle)
         
         # Draw arc
         rect = (-self.size / 2 + 2, -self.size / 2 + 2, self.size - 4, self.size - 4)
         painter.drawArc(*rect, 0, 270 * 16)
 
 
 class PulseAnimation:
     """Pulse animation for attention-grabbing"""
     
     @staticmethod
     def pulse(widget: QWidget, duration: int = 1000, scale_factor: float = 1.05):
         """Create a pulsing effect"""
         # Placeholder for pulse animation
         pass
 
 
 def create_fade_transition(old_widget: QWidget, new_widget: QWidget, duration: int = 200, on_finished=None):
     """Create a cross-fade transition between two widgets"""
     
     def on_fade_out_finished():
         old_widget.hide()
         new_widget.show()
         FadeAnimation.fade_in(new_widget, duration, on_finished)
     
     FadeAnimation.fade_out(old_widget, duration, on_fade_out_finished)
