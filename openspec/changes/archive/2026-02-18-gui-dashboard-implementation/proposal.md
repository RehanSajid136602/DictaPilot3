## Why

DictaPilot currently uses a tab-based settings interface that lacks visual hierarchy and makes it difficult to access key information at a glance. Users need a modern dashboard that provides immediate visibility into recording status, system health, transcription history, and analytics while maintaining easy access to configuration options. A well-designed dashboard will improve user experience, reduce cognitive load, and enable data-driven insights into dictation patterns.

## What Changes

- Replace tab-only navigation with a **sidebar + main content layout** featuring icon-based navigation
- Add a **Home Dashboard** view with status cards, quick stats, recent transcriptions, and live audio waveform
- Add a **Statistics & Analytics** view with KPI cards, volume charts, word count histograms, and quality score distributions
- Enhance the **History & Transcriptions** view with master-detail layout, advanced filtering, and search
- Add a dedicated **Agent Mode** view for agent/coding workflow configuration
- Add a **Diagnostics** view displaying system health checks from the existing HealthChecker
- Implement **responsive behavior** with three breakpoints (desktop, tablet, compact)
- Add **theme support** extending the existing Catppuccin Mocha dark/light themes
- Implement **keyboard navigation** and **accessibility features** (WCAG 2.1 AA compliance)
- Add **data visualization components** (charts, graphs, waveforms) using pyqtgraph or custom QPainter widgets
- Implement **state patterns** for loading, empty, and error states across all views
- Add **toast notifications** and **modal dialogs** for user feedback
- Preserve all existing settings functionality while wrapping it in the new dashboard architecture

## Capabilities

### New Capabilities
- `dashboard-navigation`: Sidebar navigation system with collapsible icon-only mode, breadcrumb bar, and keyboard shortcuts
- `dashboard-home-view`: Home dashboard with status cards, quick stats, recent transcriptions list, audio waveform preview, and activity charts
- `dashboard-statistics-view`: Statistics and analytics view with KPI cards, volume line charts, word count histograms, quality distributions, and voice commands table
- `dashboard-history-view`: Enhanced history view with master-detail layout, advanced filtering (tags, quality, app), search, and pagination
- `dashboard-agent-view`: Agent mode configuration view with status display, output preview, and configuration groups
- `dashboard-diagnostics-view`: System diagnostics view displaying health check results from HealthChecker
- `dashboard-data-visualization`: Reusable chart components (line, bar, donut, waveform) with consistent theming
- `dashboard-responsive-layout`: Responsive grid system with three breakpoints and adaptive component sizing
- `dashboard-theme-system`: Extended theme system with CSS-like tokens, semantic colors, and typography scale
- `dashboard-interactive-components`: Reusable UI components (buttons, dropdowns, search bars, toggles, sliders, modals, tooltips, context menus)
- `dashboard-state-patterns`: Loading states (skeleton screens, spinners), empty states, error states, and toast notifications
- `dashboard-accessibility`: Keyboard navigation, screen reader labels, focus management, and WCAG 2.1 AA compliance

### Modified Capabilities
- `live-preview-ui`: Requirements change to integrate the existing floating indicator bar with the new dashboard architecture, ensuring the minimal recording indicator remains while the dashboard serves as the control center

## Impact

**Affected Code:**
- `settings_dashboard.py` — Major refactoring to wrap existing tab-based settings into new dashboard architecture
- `transcription_store.py` — Add query methods for statistics aggregation (count by date, word count sums, WPM averages, quality scores)
- `config.py` — Potentially add new config fields for dashboard preferences (sidebar collapsed state, default view, chart time ranges)
- `app.py` — Update to launch the new dashboard instead of the old settings window

**New Files:**
- `dashboard_main.py` — Main dashboard window with sidebar and content area routing
- `dashboard_views/` — Directory containing view modules (home, statistics, history, agent, diagnostics)
- `dashboard_components/` — Directory containing reusable UI components (charts, cards, widgets)
- `dashboard_themes.py` — Extended theme system with token-based styling

**Dependencies:**
- Add `pyqtgraph` for high-performance chart rendering (or use custom QPainter widgets as fallback)
- Existing PySide6/Qt6 dependency remains primary UI framework

**APIs:**
- No external API changes
- Internal: Add aggregation methods to transcription_store.py for statistics queries

**Systems:**
- No impact on recording, transcription, or paste functionality
- Dashboard is purely a UI enhancement layer over existing functionality
