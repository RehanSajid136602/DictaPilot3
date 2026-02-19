"""
DictaPilot Dashboard Card Components
Reusable card widgets for status and KPI display.

MIT License
Copyright (c) 2026 Rehan
"""

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtGui import QFont

from dashboard_themes import get_theme_manager


class StatusCard(QFrame):
    """Card displaying system status with colored indicators"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.setProperty("card", True)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("System Status")
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Status rows container
        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(8)
        layout.addLayout(self.rows_layout)
        
        layout.addStretch()
    
    def add_status_row(self, label: str, value: str, status: str = "gray"):
        """Add a status row with colored indicator
        
        Args:
            label: Status label (e.g., "Recording")
            value: Status value (e.g., "Idle")
            status: Color indicator - "green", "yellow", "red", "gray"
        """
        row = QHBoxLayout()
        row.setSpacing(8)
        
        # Colored dot indicator
        dot = QLabel("●")
        dot.setFixedSize(10, 10)
        
        color_map = {
            "green": self.theme_manager.get_color("accent-green"),
            "yellow": self.theme_manager.get_color("accent-yellow"),
            "red": self.theme_manager.get_color("accent-red"),
            "gray": self.theme_manager.get_color("text-tertiary"),
        }
        
        dot_color = color_map.get(status, color_map["gray"])
        dot.setStyleSheet(f"color: {dot_color}; font-size: 16px;")
        row.addWidget(dot)
        
        # Label
        label_widget = QLabel(label + ":")
        label_widget.setStyleSheet(f"color: {self.theme_manager.get_color('text-secondary')};")
        row.addWidget(label_widget)
        
        # Value
        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"color: {self.theme_manager.get_color('text-primary')}; font-weight: 600;")
        row.addWidget(value_widget)
        
        row.addStretch()
        
        self.rows_layout.addLayout(row)
    
    def clear_rows(self):
        """Clear all status rows"""
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            if item.layout():
                while item.layout().count():
                    widget = item.layout().takeAt(0).widget()
                    if widget:
                        widget.deleteLater()


class KPICard(QFrame):
    """Card displaying a key performance indicator with trend"""
    
    def __init__(self, label: str, value: str, trend: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.setProperty("card", True)
        self._init_ui(label, value, trend)
    
    def _init_ui(self, label: str, value: str, trend: Optional[str]):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Large value
        self.value_label = QLabel(value)
        font = QFont()
        font.setPixelSize(32)
        font.setBold(True)
        self.value_label.setFont(font)
        self.value_label.setStyleSheet(f"color: {self.theme_manager.get_color('accent-blue')};")
        layout.addWidget(self.value_label)
        
        # Label
        self.label_widget = QLabel(label)
        self.label_widget.setStyleSheet(f"color: {self.theme_manager.get_color('text-secondary')}; font-size: 12px;")
        layout.addWidget(self.label_widget)
        
        # Trend indicator
        if trend:
            self.trend_label = QLabel(trend)
            
            # Determine color based on trend direction
            if trend.startswith("↑"):
                color = self.theme_manager.get_color("accent-green")
            elif trend.startswith("↓"):
                color = self.theme_manager.get_color("accent-red")
            else:
                color = self.theme_manager.get_color("text-tertiary")
            
            self.trend_label.setStyleSheet(f"color: {color}; font-size: 11px;")
            layout.addWidget(self.trend_label)
        else:
            self.trend_label = None
        
        layout.addStretch()
    
    def update_value(self, value: str, trend: Optional[str] = None):
        """Update the KPI value and trend"""
        self.value_label.setText(value)
        
        if trend and self.trend_label:
            self.trend_label.setText(trend)
            
            # Update color
            if trend.startswith("↑"):
                color = self.theme_manager.get_color("accent-green")
            elif trend.startswith("↓"):
                color = self.theme_manager.get_color("accent-red")
            else:
                color = self.theme_manager.get_color("text-tertiary")
            
            self.trend_label.setStyleSheet(f"color: {color}; font-size: 11px;")


class QuickStatsCard(QFrame):
    """Card displaying multiple quick statistics in a grid"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.setProperty("card", True)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Quick Stats")
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Stats grid (2x2)
        self.stats_widgets = {}
        
        # Row 1
        row1 = QHBoxLayout()
        row1.setSpacing(16)
        
        self.stats_widgets["stat1"] = self._create_stat_tile()
        self.stats_widgets["stat2"] = self._create_stat_tile()
        row1.addWidget(self.stats_widgets["stat1"])
        row1.addWidget(self.stats_widgets["stat2"])
        
        layout.addLayout(row1)
        
        # Row 2
        row2 = QHBoxLayout()
        row2.setSpacing(16)
        
        self.stats_widgets["stat3"] = self._create_stat_tile()
        self.stats_widgets["stat4"] = self._create_stat_tile()
        row2.addWidget(self.stats_widgets["stat3"])
        row2.addWidget(self.stats_widgets["stat4"])
        
        layout.addLayout(row2)
        
        layout.addStretch()
    
    def _create_stat_tile(self) -> QWidget:
        """Create a single stat tile"""
        tile = QWidget()
        tile_layout = QVBoxLayout(tile)
        tile_layout.setContentsMargins(0, 0, 0, 0)
        tile_layout.setSpacing(4)
        
        # Value
        value_label = QLabel("0")
        font = QFont()
        font.setPixelSize(24)
        font.setBold(True)
        value_label.setFont(font)
        value_label.setStyleSheet(f"color: {self.theme_manager.get_color('accent-blue')};")
        value_label.setObjectName("value")
        tile_layout.addWidget(value_label)
        
        # Label
        label_widget = QLabel("Metric")
        label_widget.setStyleSheet(f"color: {self.theme_manager.get_color('text-secondary')}; font-size: 11px;")
        label_widget.setObjectName("label")
        tile_layout.addWidget(label_widget)
        
        return tile
    
    def set_stat(self, stat_id: str, value: str, label: str):
        """Set a stat value and label
        
        Args:
            stat_id: One of "stat1", "stat2", "stat3", "stat4"
            value: The stat value to display
            label: The stat label
        """
        if stat_id in self.stats_widgets:
            tile = self.stats_widgets[stat_id]
            value_label = tile.findChild(QLabel, "value")
            label_widget = tile.findChild(QLabel, "label")
            
            if value_label:
                value_label.setText(value)
            if label_widget:
                label_widget.setText(label)
