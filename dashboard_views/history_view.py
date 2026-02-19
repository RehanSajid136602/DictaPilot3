"""
DictaPilot Dashboard History View
Enhanced history view with master-detail layout, filtering, and search.
 
MIT License
Copyright (c) 2026 Rehan
"""
 
from typing import List, Optional
from datetime import datetime, timedelta
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QLabel, QPushButton,
    QFrame, QScrollArea, QFileDialog, QMessageBox
)
from PySide6.QtGui import QFont, QClipboard
 
from dashboard_themes import get_theme_manager
from dashboard_components.widgets import SearchBar, StyledComboBox, StyledButton
from dashboard_components.notifications import EmptyStateWidget
from transcription_store import TranscriptionStore, TranscriptionEntry
from config import DictaPilotConfig
import csv
 
 
class HistoryView(QWidget):
    """Enhanced history view with master-detail layout"""
     
    def __init__(self, config: DictaPilotConfig, store: TranscriptionStore, parent=None):
        super().__init__(parent)
        self.config = config
        self.store = store
        self.theme_manager = get_theme_manager()
         
        self.current_page = 0
        self.items_per_page = 25
        self.selected_entry: Optional[TranscriptionEntry] = None
         
         # Filters
        self.search_text = ""
        self.filter_tag = ""
        self.filter_quality = ""
        self.filter_app = ""
        self.filter_date_range = ""
         
        self._init_ui()
        self._load_transcriptions()
     
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
         
         # Header with search and filters
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
         
         # Search bar
        self.search_bar = SearchBar("Search transcriptions...", 200)
        self.search_bar.search_triggered.connect(self._on_search)
        header_layout.addWidget(self.search_bar, 1)
         
         # Filter: Tags
        self.tag_filter = StyledComboBox()
        self.tag_filter.addItem("All Tags")
        self.tag_filter.currentTextChanged.connect(self._on_filter_changed)
        header_layout.addWidget(self.tag_filter)
         
         # Filter: Quality
        self.quality_filter = StyledComboBox()
        self.quality_filter.addItems(["All Quality", "Excellent (>0.9)", "Good (0.7-0.9)", "Fair (0.5-0.7)", "Poor (<0.5)"])
        self.quality_filter.currentTextChanged.connect(self._on_filter_changed)
        header_layout.addWidget(self.quality_filter)
         
         # Filter: App
        self.app_filter = StyledComboBox()
        self.app_filter.addItem("All Apps")
        self.app_filter.currentTextChanged.connect(self._on_filter_changed)
        header_layout.addWidget(self.app_filter)
         
         # Filter: Date Range
        self.date_filter = StyledComboBox()
        self.date_filter.addItems(["All Time", "Today", "Last 7 Days", "Last 30 Days", "Last 90 Days"])
        self.date_filter.currentTextChanged.connect(self._on_filter_changed)
        header_layout.addWidget(self.date_filter)
         
         # Clear filters button
        clear_btn = StyledButton("Clear", "ghost")
        clear_btn.clicked.connect(self._clear_filters)
        header_layout.addWidget(clear_btn)
         
         # Export button
        export_btn = StyledButton("Export CSV", "secondary")
        export_btn.clicked.connect(self._export_csv)
        header_layout.addWidget(export_btn)
         
        layout.addLayout(header_layout)
         
         # Master-detail splitter
        self.splitter = QSplitter(Qt.Horizontal)
         
         # Left panel: Transcription list
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_selected)
        self._apply_list_style()
        self.splitter.addWidget(self.list_widget)
         
         # Right panel: Detail view
        self.detail_panel = self._create_detail_panel()
        self.splitter.addWidget(self.detail_panel)
         
         # Set splitter proportions (40% list, 60% detail)
        self.splitter.setSizes([400, 600])
         
        layout.addWidget(self.splitter, 1)
         
         # Pagination controls
        pagination_layout = QHBoxLayout()
        pagination_layout.setSpacing(8)
         
        self.prev_btn = StyledButton("← Previous", "secondary")
        self.prev_btn.clicked.connect(self._prev_page)
        pagination_layout.addWidget(self.prev_btn)
         
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet(f"color: {self.theme_manager.get_color('text-secondary')}; font-size: 14px;")
        pagination_layout.addWidget(self.page_label, 1)
         
        self.next_btn = StyledButton("Next →", "secondary")
        self.next_btn.clicked.connect(self._next_page)
        pagination_layout.addWidget(self.next_btn)
         
        layout.addLayout(pagination_layout)
     
    def _create_detail_panel(self) -> QWidget:
        """Create the detail panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
         
         # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
         
        self.detail_content = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_content)
        self.detail_layout.setSpacing(12)
         
         # Empty state
        self.empty_detail = EmptyStateWidget("📄", "Select a transcription to view details")
        self.detail_layout.addWidget(self.empty_detail)
         
        scroll.setWidget(self.detail_content)
        layout.addWidget(scroll, 1)
         
         # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
         
        self.copy_btn = StyledButton("Copy", "primary")
        self.copy_btn.clicked.connect(self._copy_transcription)
        self.copy_btn.setEnabled(False)
        actions_layout.addWidget(self.copy_btn)
         
        self.tag_btn = StyledButton("Tag", "secondary")
        self.tag_btn.clicked.connect(self._tag_transcription)
        self.tag_btn.setEnabled(False)
        actions_layout.addWidget(self.tag_btn)
         
        self.delete_btn = StyledButton("Delete", "destructive")
        self.delete_btn.clicked.connect(self._delete_transcription)
        self.delete_btn.setEnabled(False)
        actions_layout.addWidget(self.delete_btn)
         
        actions_layout.addStretch()
         
        layout.addLayout(actions_layout)
         
        self._apply_detail_style(panel)
        return panel
     
    def _apply_list_style(self):
        """Apply styling to list widget"""
        tokens = self.theme_manager.get_current_tokens()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {tokens["bg-surface0"]};
                border: 1px solid {tokens["bg-surface2"]};
                border-radius: 8px;
                padding: 8px;
            }}
            QListWidget::item {{
                background-color: {tokens["bg-base"]};
                color: {tokens["text-primary"]};
                border-radius: 6px;
                padding: 12px;
                margin-bottom: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {tokens["bg-surface1"]};
            }}
            QListWidget::item:selected {{
                background-color: {tokens["accent-blue"]};
                color: {tokens["bg-base"]};
            }}
        """)
     
    def _apply_detail_style(self, widget: QWidget):
        """Apply styling to detail panel"""
        tokens = self.theme_manager.get_current_tokens()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {tokens["bg-surface0"]};
                border: 1px solid {tokens["bg-surface2"]};
                border-radius: 8px;
            }}
        """)
     
    def _load_transcriptions(self):
        """Load and display transcriptions"""
         # Get all transcriptions
        all_entries = self.store.get_all_transcriptions()
         
         # Apply filters
        filtered = self._apply_filters(all_entries)
         
         # Update filter dropdowns
        self._update_filter_options(all_entries)
         
         # Paginate
        total_pages = max(1, (len(filtered) + self.items_per_page - 1) // self.items_per_page)
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_entries = filtered[start_idx:end_idx]
         
         # Update list
        self.list_widget.clear()
         
        if not page_entries:
             # Show empty state
            if self.search_text or any([self.filter_tag, self.filter_quality, self.filter_app, self.filter_date_range]):
                empty_widget = EmptyStateWidget("🔍", "No transcriptions found matching your filters", "Clear Filters")
                empty_widget.action_clicked.connect(self._clear_filters)
            else:
                empty_widget = EmptyStateWidget("📝", "No transcriptions yet", "Start Dictating")
             
            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(empty_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, empty_widget)
        else:
            for entry in page_entries:
                item = QListWidgetItem()
                 
                 # Format timestamp
                timestamp = datetime.fromisoformat(entry.timestamp).strftime("%Y-%m-%d %H:%M")
                 
                 # Truncate text
                text = entry.processed_text or entry.original_text
                truncated = text[:80] + "..." if len(text) > 80 else text
                 
                item.setText(f"{timestamp}\n{truncated}")
                item.setData(Qt.UserRole, entry)
                 
                self.list_widget.addItem(item)
         
         # Update pagination
        self.page_label.setText(f"Page {self.current_page + 1} of {total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)
     
    def _apply_filters(self, entries: List[TranscriptionEntry]) -> List[TranscriptionEntry]:
        """Apply filters to transcription list"""
        filtered = entries
         
         # Search filter
        if self.search_text:
            search_lower = self.search_text.lower()
            filtered = [e for e in filtered if search_lower in (e.original_text or "").lower() or search_lower in (e.processed_text or "").lower()]
         
         # Tag filter
        if self.filter_tag and self.filter_tag != "All Tags":
            filtered = [e for e in filtered if self.filter_tag in (e.tags or [])]
         
         # Quality filter
        if self.filter_quality and self.filter_quality != "All Quality":
            if "Excellent" in self.filter_quality:
                filtered = [e for e in filtered if (e.quality_score or 0) > 0.9]
            elif "Good" in self.filter_quality:
                filtered = [e for e in filtered if 0.7 <= (e.quality_score or 0) <= 0.9]
            elif "Fair" in self.filter_quality:
                filtered = [e for e in filtered if 0.5 <= (e.quality_score or 0) < 0.7]
            elif "Poor" in self.filter_quality:
                filtered = [e for e in filtered if (e.quality_score or 0) < 0.5]
         
         # App filter
        if self.filter_app and self.filter_app != "All Apps":
            filtered = [e for e in filtered if e.source_app == self.filter_app]
         
         # Date range filter
        if self.filter_date_range and self.filter_date_range != "All Time":
            now = datetime.now()
            if self.filter_date_range == "Today":
                cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif self.filter_date_range == "Last 7 Days":
                cutoff = now - timedelta(days=7)
            elif self.filter_date_range == "Last 30 Days":
                cutoff = now - timedelta(days=30)
            elif self.filter_date_range == "Last 90 Days":
                cutoff = now - timedelta(days=90)
            else:
                cutoff = None
             
            if cutoff:
                filtered = [e for e in filtered if datetime.fromisoformat(e.timestamp) >= cutoff]
         
        return filtered
     
    def _update_filter_options(self, entries: List[TranscriptionEntry]):
        """Update filter dropdown options based on available data"""
         # Tags
        all_tags = set()
        for entry in entries:
            if entry.tags:
                all_tags.update(entry.tags)
         
        current_tag = self.tag_filter.currentText()
        self.tag_filter.clear()
        self.tag_filter.addItem("All Tags")
        self.tag_filter.addItems(sorted(all_tags))
        if current_tag in all_tags or current_tag == "All Tags":
            self.tag_filter.setCurrentText(current_tag)
         
         # Apps
        all_apps = set(e.source_app for e in entries if e.source_app)
         
        current_app = self.app_filter.currentText()
        self.app_filter.clear()
        self.app_filter.addItem("All Apps")
        self.app_filter.addItems(sorted(all_apps))
        if current_app in all_apps or current_app == "All Apps":
            self.app_filter.setCurrentText(current_app)
     
    def _on_search(self, text: str):
        """Handle search"""
        self.search_text = text
        self.current_page = 0
        self._load_transcriptions()
     
    def _on_filter_changed(self):
        """Handle filter change"""
        self.filter_tag = self.tag_filter.currentText()
        self.filter_quality = self.quality_filter.currentText()
        self.filter_app = self.app_filter.currentText()
        self.filter_date_range = self.date_filter.currentText()
        self.current_page = 0
        self._load_transcriptions()
     
    def _clear_filters(self):
        """Clear all filters"""
        self.search_bar.clear()
        self.tag_filter.setCurrentIndex(0)
        self.quality_filter.setCurrentIndex(0)
        self.app_filter.setCurrentIndex(0)
        self.date_filter.setCurrentIndex(0)
        self.search_text = ""
        self.filter_tag = ""
        self.filter_quality = ""
        self.filter_app = ""
        self.filter_date_range = ""
        self.current_page = 0
        self._load_transcriptions()
     
    def _prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self._load_transcriptions()
     
    def _next_page(self):
        """Go to next page"""
        self.current_page += 1
        self._load_transcriptions()
     
    def _on_item_selected(self, item: QListWidgetItem):
        """Handle item selection"""
        entry = item.data(Qt.UserRole)
        if not entry:
            return
         
        self.selected_entry = entry
        self._display_detail(entry)
         
         # Enable action buttons
        self.copy_btn.setEnabled(True)
        self.tag_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
     
    def _display_detail(self, entry: TranscriptionEntry):
        """Display transcription details"""
         # Clear existing content
        while self.detail_layout.count():
            item = self.detail_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
         
        tokens = self.theme_manager.get_current_tokens()
         
         # Timestamp
        timestamp = datetime.fromisoformat(entry.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        timestamp_label = QLabel(f"📅 {timestamp}")
        timestamp_label.setStyleSheet(f"color: {tokens['text-secondary']}; font-size: 13px;")
        self.detail_layout.addWidget(timestamp_label)
         
         # Original text
        orig_label = QLabel("Original Text")
        font = QFont()
        font.setBold(True)
        orig_label.setFont(font)
        orig_label.setStyleSheet(f"color: {tokens['text-primary']}; font-size: 14px; margin-top: 8px;")
        self.detail_layout.addWidget(orig_label)
         
        orig_text = QLabel(entry.original_text or "N/A")
        orig_text.setWordWrap(True)
        orig_text.setStyleSheet(f"color: {tokens['text-primary']}; font-size: 14px; padding: 8px; background-color: {tokens['bg-base']}; border-radius: 4px;")
        self.detail_layout.addWidget(orig_text)
         
         # Processed text
        if entry.processed_text:
            proc_label = QLabel("Processed Text")
            proc_label.setFont(font)
            proc_label.setStyleSheet(f"color: {tokens['text-primary']}; font-size: 14px; margin-top: 8px;")
            self.detail_layout.addWidget(proc_label)
             
            proc_text = QLabel(entry.processed_text)
            proc_text.setWordWrap(True)
            proc_text.setStyleSheet(f"color: {tokens['text-primary']}; font-size: 14px; padding: 8px; background-color: {tokens['bg-base']}; border-radius: 4px;")
            self.detail_layout.addWidget(proc_text)
         
         # Metadata
        meta_label = QLabel("Metadata")
        meta_label.setFont(font)
        meta_label.setStyleSheet(f"color: {tokens['text-primary']}; font-size: 14px; margin-top: 8px;")
        self.detail_layout.addWidget(meta_label)
         
        meta_text = f"""
        Word Count: {entry.word_count or 0}
        WPM: {entry.wpm or 0:.1f}
        Quality Score: {entry.quality_score or 0:.2f}
        Source App: {entry.source_app or "N/A"}
        Tags: {", ".join(entry.tags) if entry.tags else "None"}
        """
         
        meta_display = QLabel(meta_text.strip())
        meta_display.setStyleSheet(f"color: {tokens['text-secondary']}; font-size: 13px; padding: 8px; background-color: {tokens['bg-base']}; border-radius: 4px;")
        self.detail_layout.addWidget(meta_display)
         
        self.detail_layout.addStretch()
     
    def _copy_transcription(self):
        """Copy transcription to clipboard"""
        if not self.selected_entry:
            return
         
        text = self.selected_entry.processed_text or self.selected_entry.original_text
        clipboard = QClipboard()
        clipboard.setText(text)
     
    def _tag_transcription(self):
        """Add tag to transcription"""
        if not self.selected_entry:
            return
         
        from PySide6.QtWidgets import QInputDialog
        tag, ok = QInputDialog.getText(self, "Add Tag", "Enter tag name:")
         
        if ok and tag:
            if not self.selected_entry.tags:
                self.selected_entry.tags = []
            if tag not in self.selected_entry.tags:
                self.selected_entry.tags.append(tag)
                self.store.save_transcriptions()
                self._display_detail(self.selected_entry)
                self._load_transcriptions()
     
    def _delete_transcription(self):
        """Delete transcription"""
        if not self.selected_entry:
            return
         
        reply = QMessageBox.question(
            self,
            "Delete Transcription",
            "Are you sure you want to delete this transcription?",
            QMessageBox.Yes | QMessageBox.No
        )
         
        if reply == QMessageBox.Yes:
            self.store.delete_transcription(self.selected_entry.id)
            self.selected_entry = None
             
             # Clear detail panel
            while self.detail_layout.count():
                item = self.detail_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
             
            self.empty_detail = EmptyStateWidget("📄", "Select a transcription to view details")
            self.detail_layout.addWidget(self.empty_detail)
             
             # Disable action buttons
            self.copy_btn.setEnabled(False)
            self.tag_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
             
            self._load_transcriptions()
     
    def _export_csv(self):
        """Export filtered transcriptions to CSV"""
        all_entries = self.store.get_all_transcriptions()
        filtered = self._apply_filters(all_entries)
         
        if not filtered:
            QMessageBox.information(self, "Export", "No transcriptions to export.")
            return
         
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Transcriptions",
            "transcriptions.csv",
            "CSV Files (*.csv)"
        )
         
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Original Text', 'Processed Text', 'Word Count', 'WPM', 'Quality Score', 'Source App', 'Tags'])
                     
                    for entry in filtered:
                        writer.writerow([
                            entry.timestamp,
                            entry.original_text,
                            entry.processed_text or "",
                            entry.word_count or 0,
                            entry.wpm or 0,
                            entry.quality_score or 0,
                            entry.source_app or "",
                            ", ".join(entry.tags) if entry.tags else ""
                        ])
                 
                QMessageBox.information(self, "Export", f"Exported {len(filtered)} transcriptions to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
