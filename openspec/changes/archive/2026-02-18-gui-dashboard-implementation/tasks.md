## 1. Foundation and File Structure

 - [x] 1.1 Create dashboard_themes.py with color token system and ThemeManager class
 - [x] 1.2 Create dashboard_components/ directory with __init__.py
 - [x] 1.3 Create dashboard_views/ directory with __init__.py
 - [x] 1.4 Create dashboard_main.py with DictaPilotMainDashboard(QMainWindow) class
 - [x] 1.5 Add pyqtgraph to requirements-dev.txt as optional dependency

## 2. Theme System Implementation

 - [x] 2.1 Implement color token dictionaries for dark and light themes in dashboard_themes.py
 - [x] 2.2 Implement typography scale tokens (display, heading-1, heading-2, body, body-small, caption, mono)
 - [x] 2.3 Implement spacing system tokens (xs, sm, md, lg, xl, 2xl)
 - [x] 2.4 Create ThemeManager class with get_token() and apply_theme() methods
 - [x] 2.5 Extend existing DARK_THEME and LIGHT_THEME QSS with new component styles using token injection
 - [x] 2.6 Implement system theme detection on startup

## 3. Main Dashboard Window and Navigation

 - [x] 3.1 Implement main window layout with toolbar, sidebar, breadcrumb bar, content area, and status bar
 - [x] 3.2 Create sidebar widget with navigation buttons (Home, Settings, Statistics, History, Dictionary, Agent, Profiles, Diagnostics, Help)
 - [x] 3.3 Implement sidebar collapse/expand functionality (220px ↔ 56px)
 - [x] 3.4 Add navigation icons and labels with hover tooltips in collapsed mode
 - [x] 3.5 Implement active view indicator (3px blue left border + surface1 background)
 - [x] 3.6 Create QStackedWidget for view routing in main content area
 - [x] 3.7 Implement breadcrumb bar with clickable navigation path
 - [x] 3.8 Add keyboard shortcuts (Ctrl+H, Ctrl+,, Ctrl+F, Ctrl+D, arrow keys, Escape)
- [x] 3.9 Implement hamburger menu for compact layout (<768px)

## 4. Chart Components

 - [x] 4.1 Create dashboard_components/charts.py with base ChartWidget(QWidget) class
 - [x] 4.2 Implement BarChartWidget with vertical bars, axis labels, and hover tooltips
 - [x] 4.3 Implement LineChartWidget with line, area fill, data points, and gridlines
 - [x] 4.4 Implement DonutChartWidget with segments, center label, and hover interaction
 - [x] 4.5 Implement WaveformWidget with real-time amplitude bars and 60fps throttling
 - [x] 4.6 Add theme integration to all chart components
 - [x] 4.7 Implement idle/breathing animation for waveform

## 5. Reusable UI Components

- [x] 5.1 Create dashboard_components/widgets.py
- [x] 5.2 Implement button variants (primary, secondary, destructive, ghost) with hover and disabled states
- [x] 5.3 Implement styled dropdown/combobox components
- [x] 5.4 Implement search bar with debouncing (200ms) and clear button
- [x] 5.5 Implement styled checkboxes and toggle switches
- [x] 5.6 Implement slider components
 - [x] 5.7 Create dashboard_components/cards.py with StatusCard and KPICard widgets
 - [x] 5.8 Create dashboard_components/notifications.py with ToastNotification and Modal classes

## 6. State Pattern Components

 - [x] 6.1 Implement skeleton screen widgets for cards, lists, and charts with pulsing animation
 - [x] 6.2 Implement inline spinner widget (20px diameter, accent-blue)
- [x] 6.3 Implement empty state widget with icon, message, and action button
- [x] 6.4 Implement error banner widget with icon, message, and action buttons
 - [x] 6.5 Implement toast notification system with auto-dismiss (5s) and manual dismiss
- [x] 6.6 Implement notification bell with badge count and dropdown
 - [x] 6.7 Add toast stacking (max 3 visible)

## 7. Data Aggregation in Transcription Store

 - [x] 7.1 Add get_transcription_count_by_date(start_date, end_date) method to transcription_store.py
 - [x] 7.2 Add get_total_word_count(start_date, end_date) method
 - [x] 7.3 Add get_average_wpm(start_date, end_date) method
 - [x] 7.4 Add get_quality_distribution() method
 - [x] 7.5 Add get_recent_transcriptions(limit) method
 - [x] 7.6 Implement simple caching with 5-minute TTL for aggregation results
 - [x] 7.7 Add cache invalidation on new transcription

## 8. Home Dashboard View

 - [x] 8.1 Create dashboard_views/home_view.py with HomeView(QWidget) class
 - [x] 8.2 Implement 2-column grid layout with responsive behavior
 - [x] 8.3 Implement status card showing recording state, API connection, microphone, and profile
 - [x] 8.4 Implement quick stats card with transcriptions today, total words, avg WPM, avg quality
 - [x] 8.5 Implement recent transcriptions list (5 items) with click navigation to History
 - [x] 8.6 Implement audio waveform preview with idle/recording/processing states
 - [x] 8.7 Implement 7-day activity bar chart with hover tooltips
 - [x] 8.8 Add "Start Dictating" button with action handler
 - [x] 8.9 Implement empty state for recent transcriptions
 - [x] 8.10 Connect to config and transcription store for data

## 9. Statistics & Analytics View

 - [x] 9.1 Create dashboard_views/statistics_view.py with StatisticsView(QWidget) class
 - [x] 9.2 Implement KPI cards row (total transcriptions, total words, avg WPM, avg quality)
 - [x] 9.3 Add trend indicators (↑/↓ with percentage) to KPI cards
 - [x] 9.4 Implement volume line chart with time range toggle (30 days, 7 days, 24 hours)
 - [x] 9.5 Implement word count histogram with 5 bins (0-10, 10-50, 50-100, 100-500, 500+)
 - [x] 9.6 Implement quality score donut chart with 4 segments (Excellent, Good, Fair, Poor)
 - [x] 9.7 Implement voice commands table with sorting and "Show more" functionality
 - [x] 9.8 Connect to transcription store aggregation methods

## 10. Enhanced History View

- [x] 10.1 Create dashboard_views/history_view.py with HistoryView(QWidget) class
- [x] 10.2 Implement master-detail layout with QSplitter (40% list, 60% detail)
- [x] 10.3 Implement transcription list with timestamp and truncated text
- [x] 10.4 Implement detail panel showing original text, processed text, and metadata
- [x] 10.5 Add search bar with debouncing (200ms) and clear button
- [x] 10.6 Add filter dropdowns (tags, quality, app, date range)
- [x] 10.7 Implement pagination (25 items per page) with page controls
- [x] 10.8 Add action buttons (Copy, Delete, Tag) in detail panel
- [x] 10.9 Implement CSV export functionality
- [x] 10.10 Implement empty state for no transcriptions and no search results

## 11. Agent Mode View

- [x] 11.1 Create dashboard_views/agent_view.py with AgentView(QWidget) class
- [x] 11.2 Implement status section showing mode, auto-detect, IDE integration, output format
- [x] 11.3 Add agent mode toggle switch
- [x] 11.4 Implement output preview panel with format-specific samples
- [x] 11.5 Create configuration groups (Output Format, IDE Integration, Webhook, Triggers)
- [x] 11.6 Connect to config for agent mode settings
- [x] 11.7 Add webhook URL validation

## 12. Diagnostics View

 - [x] 12.1 Create dashboard_views/diagnostics_view.py with DiagnosticsView(QWidget) class
 - [x] 12.2 Implement diagnostic results list with icons, names, messages, and severity colors
 - [x] 12.3 Add "Run All Checks" button with loading state
 - [x] 12.4 Display "Last checked" timestamp
 - [x] 12.5 Implement expandable detailed logs section
 - [x] 12.6 Connect to HealthChecker for diagnostic data
 - [x] 12.7 Implement auto-refresh on view open if last check > 5 minutes

## 13. Settings View Integration

 - [x] 13.1 Create dashboard_views/settings_view.py with SettingsView(QWidget) wrapper
 - [x] 13.2 Embed existing DictaPilotDashboard (settings tabs) into wrapper
 - [x] 13.3 Add settings search bar at top (full-width)
 - [x] 13.4 Implement unsaved changes bar with Revert and Save buttons
 - [x] 13.5 Connect settings search to filter visible QGroupBox widgets
 - [x] 13.6 Preserve all existing settings functionality

## 14. Responsive Layout Implementation

 - [x] 14.1 Override resizeEvent in DictaPilotMainDashboard
 - [x] 14.2 Define breakpoints (desktop ≥1024px, tablet 768-1023px, compact <768px)
 - [x] 14.3 Implement desktop layout (full sidebar, 2-column grid)
 - [x] 14.4 Implement tablet layout (collapsed sidebar, single column)
 - [x] 14.5 Implement compact layout (hidden sidebar, hamburger menu, single column)
 - [x] 14.6 Set minimum window size (900x700)
 - [x] 14.7 Adjust chart dimensions based on available space (min 320px width)

## 15. Accessibility Implementation

- [x] 15.1 Add setAccessibleName() to all interactive widgets
- [x] 15.2 Add setAccessibleDescription() to all widgets needing context
- [x] 15.3 Implement focus indicators (2px accent-blue outline with 2px offset)
- [x] 15.4 Verify Tab/Shift+Tab navigation order
- [x] 15.5 Implement modal focus trap
- [x] 15.6 Implement focus return on modal close
- [x] 15.7 Add reduced motion detection and disable animations when enabled
- [x] 15.8 Verify color contrast ratios (4.5:1 for text, 3:1 for UI components)
- [x] 15.9 Ensure error identification uses icon + text + color

## 16. Configuration and Integration

 - [x] 16.1 Add dashboard preference fields to config.py (sidebar_collapsed, default_view, chart_time_ranges)
 - [x] 16.2 Update app.py to launch DictaPilotMainDashboard instead of DictaPilotDashboard
 - [x] 16.3 Add --legacy-ui command-line flag to launch old settings window
 - [x] 16.4 Add use_legacy_ui config option
- [x] 16.5 Implement signal connections between dashboard and recording state
- [x] 16.6 Connect dashboard to floating indicator bar for state synchronization
 - [x] 16.7 Implement auto-refresh for recent transcriptions (poll every 2s when dashboard visible)

## 17. Testing and Polish

 - [x] 17.1 Test all navigation paths (sidebar, breadcrumb, keyboard shortcuts)
 - [x] 17.2 Test theme switching (dark ↔ light)
 - [x] 17.3 Test responsive behavior at all breakpoints
 - [x] 17.4 Test with empty data (no transcriptions)
 - [x] 17.5 Test with large dataset (10,000+ transcriptions)
 - [x] 17.6 Test all chart interactions (hover, click, tooltips)
 - [x] 17.7 Test keyboard navigation and accessibility with screen reader
 - [x] 17.8 Test modal dialogs and toast notifications
 - [x] 17.9 Test settings save/load functionality
- [x] 17.10 Fix any visual inconsistencies or bugs
- [x] 17.11 Update CHANGELOG.md with new dashboard feature
- [x] 17.12 Update documentation with screenshots
