## Context

DictaPilot currently has a functional settings interface built with PySide6/Qt6 in `settings_dashboard.py` using a QTabWidget-based layout. The existing implementation includes:
- Tab-based navigation (General, Audio, Smart Editing, Advanced, History, Dictionary, Snippets, Profiles)
- Catppuccin Mocha dark/light theme system with QSS stylesheets
- Configuration management via `config.py` (DictaPilotConfig dataclass)
- Transcription storage via `transcription_store.py` (TranscriptionEntry dataclass)
- Health diagnostics via HealthChecker class

The current architecture works but lacks:
- Visual hierarchy for status information
- Analytics and insights into usage patterns
- Quick access to recent transcriptions
- Real-time system health visibility
- Modern dashboard UX patterns

Constraints:
- Must preserve all existing settings functionality
- Must maintain compatibility with existing config.json and transcriptions.json
- Must work on Linux (Wayland/X11), Windows, and macOS
- Must maintain existing theme system and extend it
- Cannot break existing recording/transcription workflows

## Goals / Non-Goals

**Goals:**
- Create a modern dashboard UI with sidebar navigation and multiple specialized views
- Provide at-a-glance visibility into system status, recording state, and health
- Add analytics views for transcription patterns (volume, quality, WPM trends)
- Enhance history browsing with master-detail layout and advanced filtering
- Implement responsive design supporting desktop, tablet, and compact layouts
- Extend theme system with token-based styling for consistency
- Add reusable chart components for data visualization
- Maintain WCAG 2.1 AA accessibility compliance
- Preserve all existing settings functionality within new architecture

**Non-Goals:**
- Changing core recording, transcription, or paste functionality
- Modifying external API integrations (NVIDIA NIM, OpenAI)
- Replacing the floating indicator bar (it remains as minimal recording UI)
- Adding new transcription features (focus is UI/UX only)
- Supporting mobile platforms (responsive down to ~900px minimum)
- Real-time collaborative features or cloud sync

## Decisions

### 1. Architecture: Wrapper Pattern vs. Full Rewrite

**Decision:** Wrap existing settings tabs within new dashboard architecture rather than full rewrite.

**Rationale:**
- Existing settings tabs are well-tested and functional
- Reduces risk and development time
- Allows incremental migration if needed
- Preserves all existing functionality automatically

**Alternative Considered:** Full rewrite of settings UI
- Rejected: High risk, time-consuming, potential for regression bugs

**Implementation:**
- Create new `DictaPilotMainDashboard(QMainWindow)` class
- Use QStackedWidget for view routing in main content area
- Embed existing `DictaPilotDashboard` (settings tabs) as one view
- New views (Home, Statistics, History, Agent, Diagnostics) are separate widgets

### 2. Navigation: Sidebar vs. Top Navigation

**Decision:** Left sidebar with icon-based navigation, collapsible to icon-only mode.

**Rationale:**
- Vertical space is more abundant than horizontal on modern displays
- Sidebar allows more navigation items without crowding
- Icon-only mode provides space efficiency for smaller screens
- Matches modern dashboard UX patterns (VS Code, Notion, Linear)

**Alternative Considered:** Top horizontal navigation bar
- Rejected: Limited space for navigation items, less scalable

**Implementation:**
- QFrame-based sidebar (220px expanded, 56px collapsed)
- QVBoxLayout with navigation buttons
- Hover tooltips in collapsed mode
- Keyboard shortcuts (Ctrl+1-9) for quick navigation

### 3. Data Visualization: pyqtgraph vs. Custom QPainter vs. QtCharts

**Decision:** Use custom QPainter widgets for simple charts, with pyqtgraph as optional enhancement.

**Rationale:**
- pyqtgraph is not in standard Python distributions, adds dependency
- Custom QPainter gives full control and matches theme system perfectly
- Simple charts (bar, line, donut) are straightforward with QPainter
- Can add pyqtgraph later for advanced features if needed

**Alternative Considered:** QtCharts module
- Rejected: Not included in PySide6 by default, requires separate installation

**Implementation:**
- Create base `ChartWidget(QWidget)` class with common painting logic
- Subclasses: `BarChartWidget`, `LineChartWidget`, `DonutChartWidget`, `WaveformWidget`
- Use theme tokens for colors, consistent styling
- Add pyqtgraph support as optional fallback in requirements-dev.txt

### 4. State Management: Signals/Slots vs. Central State Store

**Decision:** Continue using Qt signals/slots pattern, no central state store.

**Rationale:**
- Qt signals/slots is idiomatic for PySide6/Qt6
- Existing codebase already uses this pattern
- No need for Redux-like complexity in desktop app
- Direct widget-to-widget communication is sufficient

**Alternative Considered:** Central state management (Redux-like)
- Rejected: Overkill for desktop app, adds complexity

**Implementation:**
- Views emit signals for state changes
- Main dashboard connects signals to update other views
- Config changes trigger `config_changed` signal
- Transcription updates trigger `transcription_added` signal

### 5. Responsive Behavior: Media Queries vs. Resize Events

**Decision:** Use QMainWindow.resizeEvent() to detect breakpoints and adjust layout.

**Rationale:**
- Qt doesn't have CSS media queries
- resizeEvent is the standard Qt approach
- Allows programmatic layout changes based on window size

**Implementation:**
- Define breakpoints: desktop (≥1024px), tablet (768-1023px), compact (<768px)
- Override resizeEvent in main dashboard
- Adjust sidebar width, grid columns, and widget visibility based on breakpoint
- Store current breakpoint state to avoid redundant layout changes

### 6. Theme System: Extend QSS vs. Token-Based System

**Decision:** Extend existing QSS stylesheets with token-based color system in Python.

**Rationale:**
- Existing DARK_THEME and LIGHT_THEME QSS work well
- QSS doesn't support CSS variables, but we can use Python string formatting
- Token system provides consistency and easy theme switching

**Implementation:**
- Create `dashboard_themes.py` with color token dictionaries
- Use f-strings to inject tokens into QSS: `f"background-color: {TOKENS['bg-base']};"`
- Extend existing DARK_THEME and LIGHT_THEME with new component styles
- Add `ThemeManager` class to handle theme switching and token access

### 7. File Structure: Monolithic vs. Modular

**Decision:** Modular structure with separate files for views and components.

**Rationale:**
- `settings_dashboard.py` is already 2000+ lines
- Modular structure improves maintainability
- Easier to test individual components
- Follows separation of concerns

**Implementation:**
```
dashboard_main.py              # Main dashboard window, sidebar, routing
dashboard_themes.py            # Theme tokens and manager
dashboard_components/
  __init__.py
  charts.py                    # Chart widgets (bar, line, donut, waveform)
  cards.py                     # Status cards, KPI cards
  widgets.py                   # Reusable widgets (search, buttons, badges)
  notifications.py             # Toast notifications, modals
dashboard_views/
  __init__.py
  home_view.py                 # Home dashboard view
  statistics_view.py           # Statistics & analytics view
  history_view.py              # Enhanced history view
  agent_view.py                # Agent mode configuration view
  diagnostics_view.py          # System diagnostics view
  settings_view.py             # Wrapper for existing settings tabs
```

### 8. Data Aggregation: Real-time vs. Cached

**Decision:** Compute statistics on-demand with simple caching (5-minute TTL).

**Rationale:**
- Transcription data is relatively small (thousands of entries, not millions)
- On-demand computation is fast enough for desktop app
- Simple caching avoids stale data issues
- No need for background workers or complex caching

**Implementation:**
- Add aggregation methods to `transcription_store.py`:
  - `get_transcription_count_by_date(start_date, end_date)`
  - `get_total_word_count(start_date, end_date)`
  - `get_average_wpm(start_date, end_date)`
  - `get_quality_distribution()`
- Cache results in memory with timestamp
- Invalidate cache on new transcription or after 5 minutes

## Risks / Trade-offs

### Risk: Performance with Large Transcription History
**Description:** Users with 10,000+ transcriptions may experience slow statistics loading.

**Mitigation:**
- Implement pagination in history view (25 items per page)
- Add date range filters to limit query scope
- Use Python generators for large result sets
- Add loading spinners for operations >200ms
- Consider SQLite migration in future if JSON becomes bottleneck

### Risk: Chart Rendering Performance
**Description:** Custom QPainter charts may be slow with large datasets or frequent updates.

**Mitigation:**
- Limit chart data points (e.g., max 100 points on line chart, aggregate if needed)
- Use QPixmap caching for static chart elements
- Debounce real-time waveform updates to 60fps max
- Add pyqtgraph as optional dependency for users needing high-performance charts

### Risk: Responsive Layout Complexity
**Description:** Managing three breakpoints with Qt layouts is more complex than CSS media queries.

**Mitigation:**
- Start with desktop layout only, add responsive behavior incrementally
- Use QSplitter for resizable panels (user can adjust manually)
- Set minimum window size (900x700) to avoid extreme edge cases
- Test on multiple screen sizes during development

### Risk: Breaking Existing Settings Functionality
**Description:** Wrapping existing settings tabs could introduce bugs or break workflows.

**Mitigation:**
- Preserve existing `DictaPilotDashboard` class unchanged
- Embed it as-is in new architecture (no modifications)
- Add integration tests for settings save/load
- Provide fallback to old settings window if needed (command-line flag)

### Risk: Accessibility Compliance
**Description:** Custom widgets may not be accessible without explicit ARIA-like attributes.

**Mitigation:**
- Use `setAccessibleName()` and `setAccessibleDescription()` on all interactive widgets
- Test with screen readers (Orca on Linux, NVDA on Windows)
- Ensure all functionality is keyboard-accessible
- Add focus indicators (2px outline) on all focusable elements
- Follow Qt accessibility best practices

### Trade-off: Custom Charts vs. Library
**Description:** Custom QPainter charts give control but require more code than using a library.

**Acceptance:**
- Custom charts are simpler for our use case (4-5 chart types)
- Full control over theming and styling
- No external dependency issues
- Can add pyqtgraph later if needed

### Trade-off: Modular Structure vs. Single File
**Description:** Multiple files increase complexity but improve maintainability.

**Acceptance:**
- Better long-term maintainability outweighs initial complexity
- Easier to test and debug individual components
- Follows Python best practices for larger projects

## Migration Plan

### Phase 1: Foundation (Week 1)
1. Create new file structure (`dashboard_main.py`, `dashboard_themes.py`, directories)
2. Implement theme token system and extend QSS stylesheets
3. Build main dashboard window with sidebar navigation
4. Add routing with QStackedWidget
5. Embed existing settings tabs as one view

### Phase 2: Core Views (Week 2)
1. Implement Home Dashboard view with status cards and quick stats
2. Add chart components (bar, line, donut, waveform)
3. Implement Statistics view with KPI cards and charts
4. Add aggregation methods to `transcription_store.py`

### Phase 3: Enhanced Views (Week 3)
1. Implement enhanced History view with master-detail layout
2. Add filtering and search functionality
3. Implement Agent Mode view
4. Implement Diagnostics view

### Phase 4: Polish (Week 4)
1. Add responsive behavior (breakpoints, layout adjustments)
2. Implement toast notifications and modals
3. Add keyboard shortcuts and accessibility features
4. Add loading, empty, and error states
5. Testing and bug fixes

### Deployment
- Update `app.py` to launch new dashboard instead of old settings window
- Keep old settings window accessible via `--legacy-ui` flag for one release
- Update documentation and screenshots
- Add migration notes to CHANGELOG.md

### Rollback Strategy
- Old settings window remains in codebase for one release
- Users can revert to old UI via config flag: `"use_legacy_ui": true`
- No data migration needed (config and transcriptions format unchanged)

## Open Questions

1. **Should we add export functionality for statistics?**
   - CSV export for transcription history?
   - PNG export for charts?
   - Decision: Add to backlog, not critical for MVP

2. **Should we add real-time updates when recording?**
   - Live waveform in Home view?
   - Auto-refresh recent transcriptions?
   - Decision: Yes for waveform, yes for transcriptions (poll every 2s when dashboard is visible)

3. **Should we support custom dashboard layouts?**
   - Drag-and-drop widgets?
   - Customizable card positions?
   - Decision: No for MVP, too complex. Fixed layouts only.

4. **Should we add dark/light theme auto-switching based on system?**
   - Detect system theme preference?
   - Auto-switch at sunrise/sunset?
   - Decision: Yes, detect system theme on startup, add toggle in settings

5. **Should we add keyboard shortcuts for all views?**
   - Ctrl+1-9 for navigation?
   - Ctrl+F for search?
   - Decision: Yes, add shortcuts for all major views and actions
