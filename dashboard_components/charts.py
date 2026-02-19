"""
DictaPilot Dashboard Chart Components
Custom QPainter-based chart widgets with theme integration.

MIT License
Copyright (c) 2026 Rehan
"""

from typing import List, Dict, Optional, Tuple
from PySide6.QtCore import Qt, QRect, QPoint, QTimer, Signal
from PySide6.QtWidgets import QWidget, QToolTip
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QFontMetrics
import math

from dashboard_themes import get_theme_manager


class ChartWidget(QWidget):
    """Base class for chart widgets with common functionality"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.setMinimumSize(320, 160)
        self._hover_index = -1
    
    def get_color(self, token: str) -> QColor:
        """Get QColor from theme token"""
        hex_color = self.theme_manager.get_color(token)
        return QColor(hex_color)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for hover effects"""
        super().mouseMoveEvent(event)
        self.update()


class BarChartWidget(ChartWidget):
    """Vertical bar chart with hover tooltips"""
    
    clicked = Signal(int)  # Emits bar index when clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data: List[Tuple[str, float]] = []  # [(label, value), ...]
        self.max_value = 100
        self.bar_color = "accent-blue"
        self.setMouseTracking(True)
    
    def set_data(self, data: List[Tuple[str, float]]):
        """Set chart data as list of (label, value) tuples"""
        self.data = data
        self.max_value = max([v for _, v in data], default=100)
        self.update()
    
    def paintEvent(self, event):
        """Paint the bar chart"""
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get colors
        bg_color = self.get_color("bg-surface0")
        bar_color = self.get_color(self.bar_color)
        text_color = self.get_color("text-secondary")
        hover_color = QColor(bar_color)
        hover_color.setAlpha(200)
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        padding = 40
        chart_height = height - padding * 2
        chart_width = width - padding * 2
        
        bar_count = len(self.data)
        bar_width = (chart_width / bar_count) * 0.7
        bar_spacing = (chart_width / bar_count) * 0.3
        
        # Draw bars
        for i, (label, value) in enumerate(self.data):
            bar_height = (value / self.max_value) * chart_height if self.max_value > 0 else 0
            x = padding + i * (bar_width + bar_spacing)
            y = height - padding - bar_height
            
            # Check if mouse is over this bar
            mouse_pos = self.mapFromGlobal(self.cursor().pos())
            is_hover = (x <= mouse_pos.x() <= x + bar_width and 
                        y <= mouse_pos.y() <= height - padding)
            
            # Draw bar
            painter.setBrush(QBrush(hover_color if is_hover else bar_color))
            painter.setPen(Qt.NoPen)
            
            # Rounded top corners
            path = QPainterPath()
            rect = QRect(int(x), int(y), int(bar_width), int(bar_height))
            path.addRoundedRect(rect, 4, 4)
            painter.drawPath(path)
            
            # Draw label
            painter.setPen(QPen(text_color))
            font = QFont()
            font.setPixelSize(11)
            painter.setFont(font)
            
            label_rect = QRect(int(x), height - padding + 5, int(bar_width), 20)
            painter.drawText(label_rect, Qt.AlignCenter, label)
            
            # Show tooltip on hover
            if is_hover:
                QToolTip.showText(self.cursor().pos(), f"{label}: {int(value)}")
    
    def mousePressEvent(self, event):
        """Handle bar clicks"""
        if event.button() == Qt.LeftButton:
            # Find which bar was clicked
            width = self.width()
            height = self.height()
            padding = 40
            chart_width = width - padding * 2
            
            bar_count = len(self.data)
            bar_width = (chart_width / bar_count) * 0.7
            bar_spacing = (chart_width / bar_count) * 0.3
            
            for i in range(bar_count):
                x = padding + i * (bar_width + bar_spacing)
                if x <= event.pos().x() <= x + bar_width:
                    self.clicked.emit(i)
                    break


class LineChartWidget(ChartWidget):
    """Line chart with area fill and data points"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data: List[Tuple[str, float]] = []  # [(label, value), ...]
        self.max_value = 100
        self.line_color = "accent-blue"
        self.setMouseTracking(True)
    
    def set_data(self, data: List[Tuple[str, float]]):
        """Set chart data as list of (label, value) tuples"""
        self.data = data
        self.max_value = max([v for _, v in data], default=100)
        self.update()
    
    def paintEvent(self, event):
        """Paint the line chart"""
        if not self.data or len(self.data) < 2:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get colors
        line_color = self.get_color(self.line_color)
        fill_color = QColor(line_color)
        fill_color.setAlpha(25)
        grid_color = self.get_color("bg-surface1")
        text_color = self.get_color("text-secondary")
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        padding = 40
        chart_height = height - padding * 2
        chart_width = width - padding * 2
        
        # Draw gridlines
        painter.setPen(QPen(grid_color, 1))
        for i in range(5):
            y = padding + (chart_height / 4) * i
            painter.drawLine(padding, int(y), width - padding, int(y))
        
        # Calculate points
        points = []
        for i, (label, value) in enumerate(self.data):
            x = padding + (chart_width / (len(self.data) - 1)) * i
            y = height - padding - (value / self.max_value) * chart_height if self.max_value > 0 else height - padding
            points.append(QPoint(int(x), int(y)))
        
        # Draw area fill
        path = QPainterPath()
        path.moveTo(points[0].x(), height - padding)
        for point in points:
            path.lineTo(point)
        path.lineTo(points[-1].x(), height - padding)
        path.closeSubpath()
        
        painter.setBrush(QBrush(fill_color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)
        
        # Draw line
        painter.setPen(QPen(line_color, 2))
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])
        
        # Draw data points on hover
        mouse_pos = self.mapFromGlobal(self.cursor().pos())
        for i, point in enumerate(points):
            distance = math.sqrt((point.x() - mouse_pos.x())**2 + (point.y() - mouse_pos.y())**2)
            if distance < 20:
                painter.setBrush(QBrush(line_color))
                painter.drawEllipse(point, 6, 6)
                
                # Show tooltip
                label, value = self.data[i]
                QToolTip.showText(self.cursor().pos(), f"{label}: {int(value)}")
        
        # Draw X-axis labels (show every nth label to avoid crowding)
        painter.setPen(QPen(text_color))
        font = QFont()
        font.setPixelSize(10)
        painter.setFont(font)
        
        step = max(1, len(self.data) // 8)
        for i in range(0, len(self.data), step):
            label, _ = self.data[i]
            x = padding + (chart_width / (len(self.data) - 1)) * i
            label_rect = QRect(int(x) - 30, height - padding + 5, 60, 20)
            painter.drawText(label_rect, Qt.AlignCenter, label)


class DonutChartWidget(ChartWidget):
    """Donut chart with segments and center label"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data: Dict[str, float] = {}  # {label: value}
        self.colors: Dict[str, str] = {}  # {label: color_token}
        self.center_label = ""
        self.setMouseTracking(True)
    
    def set_data(self, data: Dict[str, float], colors: Dict[str, str], center_label: str = ""):
        """Set chart data with colors for each segment"""
        self.data = data
        self.colors = colors
        self.center_label = center_label
        self.update()
    
    def paintEvent(self, event):
        """Paint the donut chart"""
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        size = min(width, height) - 40
        center_x = width // 2
        center_y = height // 2
        
        # Calculate total
        total = sum(self.data.values())
        if total == 0:
            return
        
        # Draw segments
        start_angle = 90 * 16  # Start at top (Qt uses 1/16th degree units)
        
        for label, value in self.data.items():
            span_angle = int((value / total) * 360 * 16)
            
            color_token = self.colors.get(label, "accent-blue")
            color = self.get_color(color_token)
            
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            
            # Draw pie segment
            rect = QRect(center_x - size // 2, center_y - size // 2, size, size)
            painter.drawPie(rect, start_angle, span_angle)
            
            start_angle += span_angle
        
        # Draw center circle (creates donut hole)
        center_size = int(size * 0.6)
        bg_color = self.get_color("bg-base")
        painter.setBrush(QBrush(bg_color))
        painter.drawEllipse(center_x - center_size // 2, center_y - center_size // 2, 
                            center_size, center_size)
        
        # Draw center label
        if self.center_label:
            text_color = self.get_color("text-primary")
            painter.setPen(QPen(text_color))
            font = QFont()
            font.setPixelSize(24)
            font.setBold(True)
            painter.setFont(font)
            
            label_rect = QRect(center_x - 50, center_y - 15, 100, 30)
            painter.drawText(label_rect, Qt.AlignCenter, self.center_label)


class WaveformWidget(ChartWidget):
    """Real-time waveform with amplitude bars"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.amplitudes: List[float] = [0.0] * 64  # 64 bars
        self.state = "idle"  # idle, recording, processing
        self.animation_phase = 0.0
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)  # ~60fps
    
    def set_amplitudes(self, amplitudes: List[float]):
        """Set amplitude values (0.0 to 1.0)"""
        self.amplitudes = amplitudes[:64]
        while len(self.amplitudes) < 64:
            self.amplitudes.append(0.0)
        self.update()
    
    def set_state(self, state: str):
        """Set waveform state: idle, recording, processing"""
        self.state = state
        self.update()
    
    def _animate(self):
        """Animation tick"""
        self.animation_phase += 0.05
        if self.animation_phase > 2 * math.pi:
            self.animation_phase = 0.0
        
        if self.state == "idle":
            self.update()
    
    def paintEvent(self, event):
        """Paint the waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get colors based on state
        if self.state == "recording":
            bar_color = self.get_color("accent-green")
        elif self.state == "processing":
            bar_color = self.get_color("accent-yellow")
        else:
            bar_color = self.get_color("bg-surface1")
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        bar_count = len(self.amplitudes)
        bar_width = (width / bar_count) * 0.8
        bar_spacing = (width / bar_count) * 0.2
        
        # Draw bars
        for i, amplitude in enumerate(self.amplitudes):
            x = i * (bar_width + bar_spacing)
            
            # Add breathing animation for idle state
            if self.state == "idle":
                amplitude = 0.1 + 0.05 * math.sin(self.animation_phase + i * 0.1)
            
            bar_height = amplitude * (height * 0.8)
            y = (height - bar_height) / 2
            
            painter.setBrush(QBrush(bar_color))
            painter.setPen(Qt.NoPen)
            
            rect = QRect(int(x), int(y), int(bar_width), int(bar_height))
            painter.drawRect(rect)
