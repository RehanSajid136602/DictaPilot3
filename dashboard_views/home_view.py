"""
DictaPilot Home Dashboard View
Main dashboard view with status, stats, and recent activity.

MIT License
Copyright (c) 2026 Rehan
"""

from datetime import datetime, timedelta
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QFrame
)
from PySide6.QtGui import QFont

from dashboard_themes import get_theme_manager
from dashboard_components.cards import StatusCard, QuickStatsCard
from dashboard_components.charts import WaveformWidget, BarChartWidget
from config import DictaPilotConfig, load_config
from transcription_store import (
    get_recent_transcriptions, get_transcription_count_by_date,
    get_total_word_count, get_average_wpm, get_transcriptions_by_day,
    get_store
)


class HomeView(QWidget):
    """Home dashboard view"""
    
    start_recording = Signal()
    navigate_to_history = Signal(str)  # Emits transcription ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.config = load_config()
        self.recording_state = "idle"
        
        self._init_ui()
        self._setup_refresh_timer()
        self._load_data()
    
    def _init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # Hero banner
        banner = self._create_banner()
        main_layout.addWidget(banner)
        
        # 2-column grid
        grid = QGridLayout()
        grid.setSpacing(16)
        
        # Row 1: Status card + Quick stats card
        self.status_card = StatusCard()
        self.status_card.setMinimumHeight(180)
        grid.addWidget(self.status_card, 0, 0)
        
        self.stats_card = QuickStatsCard()
        self.stats_card.setMinimumHeight(180)
        grid.addWidget(self.stats_card, 0, 1)
        
        # Row 2: Recent transcriptions (2 columns)
        self.recent_widget = self._create_recent_transcriptions()
        grid.addWidget(self.recent_widget, 1, 0, 1, 2)
        
        # Row 3: Waveform + Activity chart
        self.waveform = WaveformWidget()
        self.waveform.setMinimumHeight(160)
        self.waveform.set_state("idle")
        grid.addWidget(self.waveform, 2, 0)
        
        self.activity_chart = BarChartWidget()
        self.activity_chart.setMinimumHeight(160)
        grid.addWidget(self.activity_chart, 2, 1)
        
        main_layout.addLayout(grid)
        main_layout.addStretch()
    
    def _create_banner(self) -> QFrame:
        """Create hero banner"""
        banner = QFrame()
        banner.setProperty("card", True)
        banner.setMinimumHeight(80)
        
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(24, 16, 24, 16)
        
        # Text
        text_layout = QVBoxLayout()
        
        title = QLabel("Welcome to DictaPilot")
        font = QFont()
        font.setPixelSize(24)
        font.setBold(True)
        title.setFont(font)
        text_layout.addWidget(title)
        
        subtitle = QLabel("Press F9 to start dictating")
        subtitle.setStyleSheet(f"color: {self.theme_manager.get_color('text-secondary')}; font-size: 14px;")
        text_layout.addWidget(subtitle)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        # Start button
        self.start_btn = QPushButton("▶ Start Dictating")
        self.start_btn.setProperty("variant", "primary")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setMinimumWidth(150)
        self.start_btn.clicked.connect(self.start_recording.emit)
        self.start_btn.setAccessibleName("Start dictating")
        layout.addWidget(self.start_btn)
        
        return banner
    
    def _create_recent_transcriptions(self) -> QFrame:
        """Create recent transcriptions list"""
        frame = QFrame()
        frame.setProperty("card", True)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Recent Transcriptions")
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        title.setFont(font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        view_all_btn = QPushButton("View All History →")
        view_all_btn.setProperty("variant", "ghost")
        view_all_btn.clicked.connect(lambda: self.navigate_to_history.emit(""))
        header_layout.addWidget(view_all_btn)
        
        layout.addLayout(header_layout)
        
        # List
        self.recent_list = QListWidget()
        self.recent_list.setMinimumHeight(200)
        self.recent_list.itemClicked.connect(self._on_recent_item_clicked)
        layout.addWidget(self.recent_list)
        
        # Empty state
        self.empty_state = QLabel("No transcriptions yet\nPress F9 to start dictating")
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.empty_state.setStyleSheet(f"color: {self.theme_manager.get_color('text-tertiary')}; font-size: 14px;")
        self.empty_state.hide()
        layout.addWidget(self.empty_state)
        
        return frame
    
    def _setup_refresh_timer(self):
        """Setup auto-refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._load_data)
        self.refresh_timer.start(2000)  # Refresh every 2 seconds
    
    def _load_data(self):
        """Load dashboard data"""
        self._update_status_card()
        self._update_stats_card()
        self._update_recent_transcriptions()
        self._update_activity_chart()
    
    def _update_status_card(self):
        """Update status card"""
        self.status_card.clear_rows()
        
        # Recording state
        recording_status = "gray" if self.recording_state == "idle" else "green"
        recording_value = self.recording_state.title()
        self.status_card.add_status_row("Recording", recording_value, recording_status)
        
        # API connection (check if API key exists)
        api_status = "green" if self.config.api_key else "red"
        api_value = "Connected" if self.config.api_key else "No Key"
        self.status_card.add_status_row("API", api_value, api_status)
        
        # Microphone
        mic_status = "green" if self.config.audio_device else "gray"
        mic_value = self.config.audio_device or "Default"
        self.status_card.add_status_row("Microphone", mic_value, mic_status)
        
        # Profile
        profile_value = self.config.active_profile or "default"
        self.status_card.add_status_row("Profile", profile_value, "gray")
    
    def _update_stats_card(self):
        """Update quick stats card"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now()
        
        # Transcriptions today
        count_today = get_transcription_count_by_date(today_start, today_end)
        self.stats_card.set_stat("stat1", str(count_today), "Transcriptions today")
        
        # Total words today
        words_today = get_total_word_count(today_start, today_end)
        self.stats_card.set_stat("stat2", str(words_today), "Total words")
        
        # Average WPM
        avg_wpm = get_average_wpm(today_start, today_end)
        self.stats_card.set_stat("stat3", str(int(avg_wpm)), "Avg WPM")
        
        # Average quality
        store = get_store()
        if store.entries:
            avg_quality = sum(e.quality_score for e in store.entries) / len(store.entries)
            quality_pct = int(avg_quality * 100)
        else:
            quality_pct = 0
        self.stats_card.set_stat("stat4", f"{quality_pct}%", "Avg quality")
    
    def _update_recent_transcriptions(self):
        """Update recent transcriptions list"""
        recent = get_recent_transcriptions(5)
        
        self.recent_list.clear()
        
        if not recent:
            self.recent_list.hide()
            self.empty_state.show()
            return
        
        self.recent_list.show()
        self.empty_state.hide()
        
        for entry in recent:
            # Format timestamp
            dt = datetime.fromtimestamp(entry.timestamp_unix)
            now = datetime.now()
            diff = now - dt
            
            if diff.total_seconds() < 60:
                time_str = f"{int(diff.total_seconds())}s ago"
            elif diff.total_seconds() < 3600:
                time_str = f"{int(diff.total_seconds() / 60)}m ago"
            elif diff.total_seconds() < 86400:
                time_str = f"{int(diff.total_seconds() / 3600)}h ago"
            else:
                time_str = f"{int(diff.total_seconds() / 86400)}d ago"
            
            # Truncate text
            text = entry.processed_text or entry.original_text
            if len(text) > 120:
                text = text[:120] + "..."
            
            # Create item
            item_text = f"{time_str}  —  {text}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, entry.id)
            self.recent_list.addItem(item)
    
    def _update_activity_chart(self):
        """Update 7-day activity chart"""
        activity_data = get_transcriptions_by_day(7)
        
        # Convert to chart format (label, value)
        chart_data = []
        for i in range(6, -1, -1):
            day = datetime.now() - timedelta(days=i)
            day_key = day.strftime("%Y-%m-%d")
            count = activity_data.get(day_key, 0)
            label = day.strftime("%a")  # Mon, Tue, etc.
            chart_data.append((label, float(count)))
        
        self.activity_chart.set_data(chart_data)
    
    def _on_recent_item_clicked(self, item: QListWidgetItem):
        """Handle recent item click"""
        transcription_id = item.data(Qt.UserRole)
        self.navigate_to_history.emit(transcription_id)
    
    def set_recording_state(self, state: str):
        """Set recording state (idle, recording, processing)"""
        self.recording_state = state
        self.waveform.set_state(state)
        self._update_status_card()
    
    def update_waveform(self, amplitudes: list):
        """Update waveform amplitudes"""
        self.waveform.set_amplitudes(amplitudes)
    
    def showEvent(self, event):
        """Handle show event - refresh data"""
        super().showEvent(event)
        self._load_data()
    
    def hideEvent(self, event):
        """Handle hide event - stop refresh timer"""
        super().hideEvent(event)
        # Keep timer running for now, could optimize later
