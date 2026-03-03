## Why

DictaPilot's current GUI uses the Catppuccin color scheme and a traditional sidebar layout. To modernize the application and align with contemporary design trends, we're integrating Wispr Flow's design language—featuring icy blues/purples, glassmorphism effects, and a minimal "invisible design" philosophy. This will make DictaPilot more visually appealing, improve user experience with smoother animations and better visual feedback, and position it as a modern, professional dictation tool that rivals commercial alternatives.

## What Changes

- **Complete color palette migration** from Catppuccin to Wispr Flow (icy blues `#3b82f6`, purples `#8b5cf6`, darker base `#0f1419`)
- **Floating recording window redesign** with pill shape, glassmorphism effects, and gradient waveform visualization
- **Dashboard layout restructuring** with horizontal top navigation bar and collapsible left sidebar
- **New typography system** with modern sans-serif fonts and updated spacing scale (8px base)
- **Glassmorphism card components** with blur effects and subtle transparency
- **Gradient-based charts and visualizations** replacing solid colors
- **State-aware color system** (cyan for recording, purple for processing)
- **Smooth animations** for state transitions, view changes, and component interactions
- **Enhanced waveform visualization** with 11 bars, rounded caps, and glow effects
- **Redesigned views**: Home (hero section with gradient), Settings (underline tabs), History (timeline), Dictionary (FAB), Statistics (gradient charts)
- **Accessibility improvements** with WCAG 2.1 AA compliance, focus indicators, and reduced motion support

## Capabilities

### New Capabilities

- `wispr-flow-theme`: Complete theme system with Wispr Flow color tokens, typography scale, spacing system, and gradient definitions
- `glassmorphism-effects`: Reusable glassmorphism utilities for blur effects, transparency, and glass-style borders
- `floating-window-wispr`: Redesigned floating recording window with pill shape, glassmorphism, and gradient waveform
- `gradient-waveform`: Enhanced waveform visualization with gradient fills, glow effects, and smooth animations
- `horizontal-navigation`: Top navigation bar with horizontal menu items and active state indicators
- `collapsible-sidebar`: Icon-based left sidebar that expands to show labels
- `glassmorphism-cards`: Card components with glass effects for stats, recent items, and content containers
- `gradient-charts`: Chart components with gradient fills for bars, lines, and areas
- `hero-section`: Large hero banner with gradient background for home view
- `timeline-view`: Timeline-based history view with day separators and preview cards
- `floating-action-button`: FAB component for primary actions (e.g., add dictionary entry)
- `state-animations`: Animation system for smooth state transitions and view changes

### Modified Capabilities

- `theme-system`: Extend existing theme manager to support Wispr Flow palette alongside current themes (migration path)
- `dashboard-layout`: Restructure main dashboard from vertical sidebar to horizontal top nav + collapsible left sidebar
- `home-view`: Redesign with hero section, glassmorphism stats grid, and gradient activity chart
- `settings-view`: Update with underline tab navigation and new form element styling
- `history-view`: Transform from list view to timeline view with glassmorphism cards
- `dictionary-view`: Add search bar prominence, FAB for adding entries, and inline editing
- `statistics-view`: Update charts with gradient fills and glassmorphism metric cards
- `button-components`: Add new button variants matching Wispr Flow style (primary with gradients)
- `input-components`: Update form inputs with bottom-border focus states and glassmorphism
- `waveform-component`: Enhance existing waveform with gradient support and state-based colors

## Impact

**Affected Code:**
- `dashboard_themes.py` - Theme system extended with Wispr Flow tokens
- `dashboard_main.py` - Layout restructured for horizontal navigation
- `dashboard_views/*.py` - All views redesigned (home, settings, history, dictionary, statistics)
- `dashboard_components/*.py` - Components updated with new styling (cards, widgets, charts)
- `app.py` - Floating window redesigned with glassmorphism
- `config.py` - New configuration options for UI style, glassmorphism, animations

**New Files:**
- `dashboard_wispr_flow/theme.py` - Wispr Flow theme tokens and utilities
- `dashboard_wispr_flow/layout/*.py` - New layout components (top nav, sidebar, status bar)
- `dashboard_wispr_flow/floating/*.py` - Redesigned floating window components
- `dashboard_wispr_flow/components/*.py` - New glassmorphism and gradient components
- `dashboard_wispr_flow/utils/*.py` - Glassmorphism, gradient, and animation utilities

**Dependencies:**
- PySide6 (existing) - No new dependencies required
- Qt6 graphics effects for glassmorphism (QGraphicsBlurEffect)

**User Impact:**
- **Visual**: Complete UI refresh with modern design language
- **Performance**: Potential slight increase in GPU usage for glassmorphism effects (mitigated with fallbacks)
- **Learning Curve**: Minimal - layout changes are intuitive, existing workflows preserved
- **Accessibility**: Improved with better contrast, focus indicators, and reduced motion support
- **Configuration**: New settings for UI style, enabling users to choose between classic and Wispr Flow designs during transition period

**Migration Strategy:**
- Parallel implementation with feature flag (`UI_STYLE=wispr_flow` or `classic`)
- Both styles available for 2 releases to gather feedback
- Classic style deprecated after user acceptance
- No data migration required - purely UI changes
