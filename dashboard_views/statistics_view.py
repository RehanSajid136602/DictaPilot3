"""
DictaPilot Statistics & Analytics View
Displays KPI cards, charts, and usage analytics.

MIT License
Copyright (c) 2026 Rehan
"""

from datetime import datetime, timedelta
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QScrollArea,
)
from PySide6.QtGui import QFont

from dashboard_themes import get_theme_manager
from dashboard_components.cards import KPICard
from dashboard_components.charts import (
    LineChartWidget,
    BarChartWidget,
    DonutChartWidget,
)
from transcription_store import (
    get_transcription_count_by_date,
    get_total_word_count,
    get_average_wpm,
    get_quality_distribution,
    get_transcriptions_by_day,
    get_store,
)


class StatisticsView(QWidget):
    """Statistics and analytics view"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.time_range = "7days"  # 30days, 7days, 24hours

        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """Initialize UI"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setObjectName("statisticsScrollArea")

        # Create content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(24)

        # Title
        title = QLabel("Statistics & Analytics")
        font = QFont()
        font.setPixelSize(24)
        font.setBold(True)
        title.setFont(font)
        content_layout.addWidget(title)

        # KPI Cards row
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(16)

        self.kpi_transcriptions = KPICard("Total Transcriptions", "0", "↑ 0%")
        self.kpi_words = KPICard("Total Words", "0", "↑ 0%")
        self.kpi_wpm = KPICard("Average WPM", "0", "↓ 0%")
        self.kpi_quality = KPICard("Average Quality", "0%", "↑ 0%")

        kpi_layout.addWidget(self.kpi_transcriptions)
        kpi_layout.addWidget(self.kpi_words)
        kpi_layout.addWidget(self.kpi_wpm)
        kpi_layout.addWidget(self.kpi_quality)

        content_layout.addLayout(kpi_layout)

        # Volume line chart with time range toggle
        volume_frame = self._create_volume_chart()
        content_layout.addWidget(volume_frame)

        # Grid for histograms
        grid = QGridLayout()
        grid.setSpacing(16)

        # Word count histogram
        word_hist_frame = self._create_word_histogram()
        grid.addWidget(word_hist_frame, 0, 0)

        # Quality donut chart
        quality_frame = self._create_quality_chart()
        grid.addWidget(quality_frame, 0, 1)

        content_layout.addLayout(grid)

        # Voice commands table (placeholder for now)
        commands_frame = self._create_commands_table()
        content_layout.addWidget(commands_frame)

        content_layout.addStretch()

        # Set scroll area widget
        scroll.setWidget(content)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(scroll)

    def _create_volume_chart(self) -> QFrame:
        """Create volume line chart with time range toggle"""
        frame = QFrame()
        frame.setProperty("card", True)
        frame.setMinimumHeight(280)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header with time range buttons
        header = QHBoxLayout()

        title = QLabel("Transcription Volume")
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        title.setFont(font)
        header.addWidget(title)

        header.addStretch()

        # Time range buttons
        self.time_range_group = QButtonGroup()

        btn_30d = QPushButton("30 days")
        btn_30d.setProperty("variant", "secondary")
        btn_30d.setCheckable(True)
        btn_30d.clicked.connect(lambda: self._set_time_range("30days"))
        self.time_range_group.addButton(btn_30d, 0)
        header.addWidget(btn_30d)

        btn_7d = QPushButton("7 days")
        btn_7d.setProperty("variant", "secondary")
        btn_7d.setCheckable(True)
        btn_7d.setChecked(True)
        btn_7d.clicked.connect(lambda: self._set_time_range("7days"))
        self.time_range_group.addButton(btn_7d, 1)
        header.addWidget(btn_7d)

        btn_24h = QPushButton("24 hours")
        btn_24h.setProperty("variant", "secondary")
        btn_24h.setCheckable(True)
        btn_24h.clicked.connect(lambda: self._set_time_range("24hours"))
        self.time_range_group.addButton(btn_24h, 2)
        header.addWidget(btn_24h)

        layout.addLayout(header)

        # Line chart
        self.volume_chart = LineChartWidget()
        self.volume_chart.setMinimumHeight(200)
        layout.addWidget(self.volume_chart)

        return frame

    def _create_word_histogram(self) -> QFrame:
        """Create word count histogram"""
        frame = QFrame()
        frame.setProperty("card", True)
        frame.setMinimumHeight(240)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Word Count Distribution")
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        self.word_histogram = BarChartWidget()
        self.word_histogram.bar_color = "accent-mauve"
        self.word_histogram.setMinimumHeight(180)
        layout.addWidget(self.word_histogram)

        return frame

    def _create_quality_chart(self) -> QFrame:
        """Create quality score donut chart"""
        frame = QFrame()
        frame.setProperty("card", True)
        frame.setMinimumHeight(240)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Quality Score Distribution")
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        self.quality_chart = DonutChartWidget()
        self.quality_chart.setMinimumHeight(180)
        layout.addWidget(self.quality_chart)

        return frame

    def _create_commands_table(self) -> QFrame:
        """Create voice commands table"""
        frame = QFrame()
        frame.setProperty("card", True)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()

        title = QLabel("Top Voice Commands")
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        title.setFont(font)
        header.addWidget(title)

        header.addStretch()

        show_more_btn = QPushButton("Show more")
        show_more_btn.setProperty("variant", "ghost")
        header.addWidget(show_more_btn)

        layout.addLayout(header)

        # Table
        self.commands_table = QTableWidget()
        self.commands_table.setColumnCount(3)
        self.commands_table.setHorizontalHeaderLabels(["Command", "Count", "Last Used"])
        self.commands_table.horizontalHeader().setStretchLastSection(True)
        self.commands_table.setMaximumHeight(200)
        self.commands_table.setRowCount(5)

        # Placeholder data
        commands = [
            ("delete that", "87", "5 min ago"),
            ("new paragraph", "54", "12 min ago"),
            ("undo that", "42", "1 hour ago"),
            ("select all", "38", "2 hours ago"),
            ("copy that", "31", "3 hours ago"),
        ]

        for row, (cmd, count, last_used) in enumerate(commands):
            self.commands_table.setItem(row, 0, QTableWidgetItem(cmd))
            self.commands_table.setItem(row, 1, QTableWidgetItem(count))
            self.commands_table.setItem(row, 2, QTableWidgetItem(last_used))

        layout.addWidget(self.commands_table)

        return frame

    def _set_time_range(self, range_id: str):
        """Set time range and reload data"""
        self.time_range = range_id
        self._load_volume_data()

    def _load_data(self):
        """Load all statistics data"""
        self._load_kpi_data()
        self._load_volume_data()
        self._load_word_histogram_data()
        self._load_quality_data()

    def _load_kpi_data(self):
        """Load KPI card data"""
        # Get current period data
        now = datetime.now()

        if self.time_range == "30days":
            start = now - timedelta(days=30)
            prev_start = now - timedelta(days=60)
            prev_end = now - timedelta(days=30)
        elif self.time_range == "24hours":
            start = now - timedelta(hours=24)
            prev_start = now - timedelta(hours=48)
            prev_end = now - timedelta(hours=24)
        else:  # 7days
            start = now - timedelta(days=7)
            prev_start = now - timedelta(days=14)
            prev_end = now - timedelta(days=7)

        # Current period
        count_current = get_transcription_count_by_date(start, now)
        words_current = get_total_word_count(start, now)
        wpm_current = get_average_wpm(start, now)

        # Previous period
        count_prev = get_transcription_count_by_date(prev_start, prev_end)
        words_prev = get_total_word_count(prev_start, prev_end)
        wpm_prev = get_average_wpm(prev_start, prev_end)

        # Calculate trends
        count_trend = self._calculate_trend(count_current, count_prev)
        words_trend = self._calculate_trend(words_current, words_prev)
        wpm_trend = self._calculate_trend(wpm_current, wpm_prev)

        # Quality (overall average)
        store = get_store()
        if store.entries:
            avg_quality = sum(e.quality_score for e in store.entries) / len(
                store.entries
            )
            quality_pct = int(avg_quality * 100)
        else:
            avg_quality = 0
            quality_pct = 0

        # Update KPI cards
        self.kpi_transcriptions.update_value(str(count_current), count_trend)
        self.kpi_words.update_value(str(words_current), words_trend)
        self.kpi_wpm.update_value(str(int(wpm_current)), wpm_trend)
        self.kpi_quality.update_value(f"{quality_pct}%", "")

    def _calculate_trend(self, current: float, previous: float) -> str:
        """Calculate trend percentage"""
        if previous == 0:
            if current > 0:
                return "↑ 100%"
            return ""

        change = ((current - previous) / previous) * 100
        if change > 0:
            return f"↑ {int(change)}%"
        elif change < 0:
            return f"↓ {int(abs(change))}%"
        return ""

    def _load_volume_data(self):
        """Load volume chart data"""
        if self.time_range == "30days":
            days = 30
        elif self.time_range == "24hours":
            days = 1
        else:
            days = 7

        activity_data = get_transcriptions_by_day(days)

        # Convert to chart format
        chart_data = []
        for i in range(days - 1, -1, -1):
            day = datetime.now() - timedelta(days=i)
            day_key = day.strftime("%Y-%m-%d")
            count = activity_data.get(day_key, 0)

            if self.time_range == "24hours":
                label = day.strftime("%H:00")
            else:
                label = day.strftime("%m/%d")

            chart_data.append((label, float(count)))

        self.volume_chart.set_data(chart_data)

    def _load_word_histogram_data(self):
        """Load word count histogram data"""
        store = get_store()

        # Count entries in each bin
        bins = {
            "0-10": 0,
            "10-50": 0,
            "50-100": 0,
            "100-500": 0,
            "500+": 0,
        }

        for entry in store.entries:
            wc = entry.word_count
            if wc <= 10:
                bins["0-10"] += 1
            elif wc <= 50:
                bins["10-50"] += 1
            elif wc <= 100:
                bins["50-100"] += 1
            elif wc <= 500:
                bins["100-500"] += 1
            else:
                bins["500+"] += 1

        chart_data = [(label, float(count)) for label, count in bins.items()]
        self.word_histogram.set_data(chart_data)

    def _load_quality_data(self):
        """Load quality distribution data"""
        distribution = get_quality_distribution()

        # Calculate total and average
        total = sum(distribution.values())
        if total > 0:
            excellent_pct = (distribution["excellent"] / total) * 100
            avg_pct = int(excellent_pct)
        else:
            avg_pct = 0

        # Prepare data for donut chart
        data = {
            "Excellent": float(distribution["excellent"]),
            "Good": float(distribution["good"]),
            "Fair": float(distribution["fair"]),
            "Poor": float(distribution["poor"]),
        }

        colors = {
            "Excellent": "accent-green",
            "Good": "accent-blue",
            "Fair": "accent-yellow",
            "Poor": "accent-red",
        }

        self.quality_chart.set_data(data, colors, f"{avg_pct}%")

    def showEvent(self, event):
        """Handle show event - refresh data"""
        super().showEvent(event)
        self._load_data()
