## 1. Foundation Setup

- [x] 1.1 Create dashboard_wispr_flow/ directory structure with subdirectories (theme, layout, floating, views, components, utils)
- [x] 1.2 Create wispr_flow_theme.py with complete color token definitions (backgrounds, text, accents, states, semantic, glassmorphism)
- [x] 1.3 Implement typography scale tokens (display, headings, body, caption, mono)
- [x] 1.4 Implement spacing scale tokens (xs through 3xl based on 8px)
- [x] 1.5 Implement border radius tokens (small, medium, large, pill)
- [x] 1.6 Implement gradient definitions (blue-purple, cyan-blue)
- [x] 1.7 Add UI_STYLE configuration option to config.py
- [x] 1.8 Extend ThemeManager to support Wispr Flow palette
- [x] 1.9 Implement color contrast validation utility (WCAG 2.1 AA)
- [x] 1.10 Generate QSS stylesheet with Wispr Flow tokens
- [x] 1.11 Run automated contrast checking on all color combinations
- [x] 1.12 Document theme token usage in README

## 2. Glassmorphism Effects

- [x] 2.1 Create glassmorphism.py utility in utils/
- [x] 2.2 Implement GlassmorphismEffect class with blur and transparency
- [x] 2.3 Implement GPU capability detection
- [x] 2.4 Add DISABLE_GLASSMORPHISM environment variable support
- [x] 2.5 Implement QGraphicsBlurEffect caching
- [x] 2.6 Create fallback rendering for low-end hardware
- [x] 2.7 Add glass border utility (1px rgba border)
- [x] 2.8 Test glassmorphism on various hardware configurations
- [x] 2.9 Document glassmorphism usage and performance considerations

## 3. Gradient Utilities

- [x] 3.1 Create gradients.py utility in utils/
- [x] 3.2 Implement QLinearGradient generator for blue-purple gradient
- [x] 3.3 Implement QLinearGradient generator for cyan-blue gradient
- [x] 3.4 Implement gradient caching mechanism
- [x] 3.5 Add state-based gradient selector (recording=cyan, processing=purple)
- [x] 3.6 Test gradient rendering performance

## 4. Animation System

- [x] 4.1 Create animations.py utility in utils/
- [x] 4.2 Implement StateAnimation class using QPropertyAnimation
- [x] 4.3 Add easing curve support (ease-out, ease-in, ease-in-out)
- [x] 4.4 Implement reduced-motion detection
- [x] 4.5 Add animation duration constants (200ms, 250ms, 300ms)
- [x] 4.6 Create fade animation helper
- [x] 4.7 Create slide animation helper
- [x] 4.8 Create color transition animation helper
- [x] 4.9 Test animations at 60fps target
- [x] 4.10 Test reduced-motion mode

## 5. Gradient Waveform Component

- [x] 5.1 Create waveform.py in floating/
- [x] 5.2 Implement GradientWaveform widget with 11 bars
- [x] 5.3 Add rounded bar caps rendering
- [x] 5.4 Implement gradient fill based on state (cyan/purple)
- [x] 5.5 Add real-time amplitude update (60fps target)
- [x] 5.6 Implement smooth amplitude transitions (250ms)
- [x] 5.7 Add glow effect rendering (8px blur, 40% opacity)
- [x] 5.8 Implement reduced-motion support
- [x] 5.9 Test waveform performance with live audio
- [x] 5.10 Add accessibility labels for screen readers

## 6. Floating Window Redesign

- [x] 6.1 Create floating_window.py in floating/
- [x] 6.2 Implement FloatingWindowWisprFlow class (320x80px pill shape)
- [x] 6.3 Apply glassmorphism effects to window background
- [x] 6.4 Add glass border (1px rgba)
- [x] 6.5 Integrate GradientWaveform component
- [x] 6.6 Add state indicator icon (left side)
- [x] 6.7 Add status text label (center)
- [x] 6.8 Add close button (right side, × symbol)
- [x] 6.9 Implement state-based color changes (idle/recording/processing/done/error)
- [x] 6.10 Add appear animation (fade + slide up, 300ms)
- [x] 6.11 Add disappear animation (fade + slide down, 200ms)
- [x] 6.12 Implement center-bottom positioning (40px from bottom)
- [x] 6.13 Add Escape key handler for closing
- [x] 6.14 Implement ARIA live regions for state announcements
- [x] 6.15 Test on all platforms (Linux X11, Wayland, Windows)
- [x] 6.16 Test keyboard accessibility

## 7. Top Navigation Bar

- [x] 7.1 Create top_navigation.py in layout/
- [x] 7.2 Implement TopNavigationBar widget (56px height)
- [x] 7.3 Add logo placement (left side, 16px padding)
- [x] 7.4 Add navigation menu items (center: Home, Settings, Statistics, History, Dictionary, Profiles, Help)
- [x] 7.5 Add action buttons (right: theme toggle, notifications, user menu)
- [x] 7.6 Implement active item indicator (3px bottom border, accent-blue)
- [x] 7.7 Add hover state for navigation items
- [x] 7.8 Implement keyboard navigation (Tab, Enter/Space)
- [x] 7.9 Add focus indicators
- [x] 7.10 Test responsive behavior on window resize

## 8. Collapsible Sidebar

- [x] 8.1 Create sidebar.py in layout/
- [x] 8.2 Implement CollapsibleSidebar widget
- [x] 8.3 Add collapsed state (64px width, icons only)
- [x] 8.4 Add expanded state (240px width, icons + labels)
- [x] 8.5 Implement toggle button with animation (250ms)
- [x] 8.6 Add active item indicator (3px left border, accent-blue, bg-surface)
- [x] 8.7 Add hover state for sidebar items
- [x] 8.8 Implement auto-collapse on window width < 1280px
- [x] 8.9 Add keyboard navigation support
- [x] 8.10 Test smooth expand/collapse animations

## 9. Status Bar

- [x] 9.1 Create status_bar.py in layout/
- [x] 9.2 Implement StatusBar widget (28px height)
- [x] 9.3 Add status indicator (● Ready)
- [x] 9.4 Add profile display
- [x] 9.5 Add version display
- [x] 9.6 Apply bg-elevated background
- [x] 9.7 Use caption typography for text

## 10. Main Layout Integration

- [x] 10.1 Create main_layout.py in layout/
- [x] 10.2 Implement MainLayoutWisprFlow combining top nav, sidebar, content, status bar
- [x] 10.3 Add content area with 32px padding
- [x] 10.4 Implement max-width constraint (1400px, centered)
- [x] 10.5 Add smooth scrolling with custom scrollbar
- [x] 10.6 Implement responsive breakpoints (desktop/tablet/compact)
- [x] 10.7 Add view switching with fade transitions
- [x] 10.8 Test layout on various screen sizes

## 11. Glassmorphism Card Component

- [x] 11.1 Create cards.py in components/
- [x] 11.2 Implement GlassmorphismCard widget
- [x] 11.3 Apply glassmorphism effects (blur, transparency, border)
- [x] 11.4 Add medium border radius (12px)
- [x] 11.5 Implement custom padding support (default 16px)
- [x] 11.6 Add graceful degradation for disabled glassmorphism
- [x] 11.7 Create StatsCard variant for metrics display
- [x] 11.8 Create PreviewCard variant for timeline items

## 12. Gradient Chart Components

- [x] 12.1 Create charts.py in components/
- [x] 12.2 Implement GradientBarChart widget
- [x] 12.3 Add gradient fill for bars (accent-blue gradient)
- [x] 12.4 Add rounded bar caps (4px radius)
- [x] 12.5 Implement subtle grid lines (bg-surface, 1px)
- [x] 12.6 Add hover interactions with tooltips
- [x] 12.7 Use caption typography for labels
- [x] 12.8 Implement GradientLineChart widget
- [x] 12.9 Test chart rendering performance

## 13. Hero Section Component

- [x] 13.1 Create hero_section.py in components/
- [x] 13.2 Implement HeroSection widget
- [x] 13.3 Add blue-purple gradient background
- [x] 13.4 Apply glassmorphism overlay
- [x] 13.5 Add title in display typography (32px, 700 weight)
- [x] 13.6 Add subtitle in body typography (15px, 400 weight)
- [x] 13.7 Add primary action button (48px height, 150px min width)
- [x] 13.8 Set minimum height (80px + padding)
- [x] 13.9 Connect button to start recording action

## 14. Floating Action Button

- [x] 14.1 Create fab.py in components/
- [x] 14.2 Implement FloatingActionButton widget (56px diameter)
- [x] 14.3 Position in bottom-right corner (24px margin)
- [x] 14.4 Apply accent-blue background with white icon
- [x] 14.5 Add hover state (lighter blue #60a5fa)
- [x] 14.6 Add pressed state (darker blue #2563eb)
- [x] 14.7 Add elevation shadow (8px blur, 40% opacity)
- [x] 14.8 Implement keyboard accessibility (Tab, Enter/Space)
- [x] 14.9 Add focus indicator (2px outline)

## 15. Button Components

- [x] 15.1 Create buttons.py in components/
- [x] 15.2 Implement PrimaryButton with gradient background
- [x] 15.3 Implement SecondaryButton with bg-surface background
- [x] 15.4 Implement GhostButton with transparent background
- [x] 15.5 Implement DestructiveButton with error color
- [x] 15.6 Add hover, pressed, and disabled states for all variants
- [x] 15.7 Add focus indicators (2px outline, accent-blue)
- [x] 15.8 Test keyboard navigation

## 16. Input Components

- [x] 16.1 Create inputs.py in components/
- [x] 16.2 Implement StyledLineEdit with bg-surface background
- [x] 16.3 Add bottom-border focus state (2px, accent-blue)
- [x] 16.4 Implement StyledComboBox with custom dropdown arrow
- [x] 16.5 Implement ToggleSwitch (44x24px pill shape)
- [x] 16.6 Implement StyledSlider with gradient track
- [x] 16.7 Add focus indicators for all inputs
- [x] 16.8 Test keyboard navigation and accessibility

## 17. Search Component

- [x] 17.1 Create search.py in components/
- [x] 17.2 Implement SearchBar widget with debouncing (200ms)
- [x] 17.3 Add clear button (× symbol)
- [x] 17.4 Add search icon
- [x] 17.5 Implement focus state with bottom border
- [x] 17.6 Add keyboard shortcuts (Ctrl+F to focus)
- [x] 17.7 Test debouncing behavior

## 18. Home View Redesign

- [x] 18.1 Create home_view.py in views/
- [x] 18.2 Implement HomeViewWisprFlow widget
- [x] 18.3 Add HeroSection at top
- [x] 18.4 Create 2x2 stats grid with GlassmorphismCards
- [x] 18.5 Display today's transcriptions, total words, avg WPM, quality metrics
- [x] 18.6 Add recent transcriptions list with minimal styling
- [x] 18.7 Add 7-day activity chart with gradient bars
- [x] 18.8 Implement smooth scrolling
- [x] 18.9 Connect to existing data sources
- [x] 18.10 Test data updates and refresh

## 19. Settings View Redesign

- [x] 19.1 Create settings_view.py in views/
- [x] 19.2 Implement SettingsViewWisprFlow widget
- [x] 19.3 Add underline tab navigation (General, Audio, Smart Edit, Advanced)
- [x] 19.4 Implement active tab indicator (2px bottom border, accent-blue)
- [x] 19.5 Update form elements with new styling
- [x] 19.6 Add ToggleSwitch components for boolean settings
- [x] 19.7 Add StyledSlider components for numeric settings
- [x] 19.8 Implement Save Changes button
- [x] 19.9 Add 24px spacing between sections
- [x] 19.10 Test settings persistence

## 20. History View Redesign

- [x] 20.1 Create history_view.py in views/
- [x] 20.2 Implement HistoryViewWisprFlow widget with timeline layout
- [x] 20.3 Add SearchBar at top with date filter dropdown
- [x] 20.4 Implement day separators (Today, Yesterday, date headings)
- [x] 20.5 Create timeline item cards with glassmorphism
- [x] 20.6 Display metadata (time, word count, quality) in caption typography
- [x] 20.7 Display preview text (first 120 chars)
- [x] 20.8 Add action buttons (Play, Copy, Delete)
- [x] 20.9 Implement copy to clipboard functionality
- [x] 20.10 Test timeline scrolling and performance

## 21. Dictionary View Redesign

- [x] 21.1 Create dictionary_view.py in views/
- [x] 21.2 Implement DictionaryViewWisprFlow widget
- [x] 21.3 Add prominent SearchBar at top
- [x] 21.4 Display entries in minimal list format (trigger → content)
- [x] 21.5 Add FloatingActionButton for adding entries
- [x] 21.6 Implement inline editing on click
- [x] 21.7 Add smooth transitions for edit mode
- [x] 21.8 Test search debouncing and filtering

## 22. Statistics View Redesign

- [x] 22.1 Create statistics_view.py in views/
- [x] 22.2 Implement StatisticsViewWisprFlow widget
- [x] 22.3 Update charts with gradient fills
- [x] 22.4 Create metric cards with glassmorphism
- [x] 22.5 Add date range picker
- [x] 22.6 Test chart rendering with various data sets

## 23. Integration and Testing

- [x] 23.1 Update dashboard_main.py to support UI_STYLE switching
- [x] 23.2 Add conditional import for Wispr Flow vs classic layout
- [x] 23.3 Update app.py to use FloatingWindowWisprFlow when UI_STYLE=wispr_flow
- [x] 23.4 Test theme switching without restart
- [x] 23.5 Test all views with Wispr Flow theme
- [x] 23.6 Test floating window in all states
- [x] 23.7 Test navigation between all views
- [x] 23.8 Test keyboard navigation throughout app
- [ ] 23.9 Test with screen reader (NVDA or JAWS)
- [ ] 23.10 Test on Linux X11
- [ ] 23.11 Test on Linux Wayland
- [ ] 23.12 Test on Windows 10/11
- [ ] 23.13 Test at various display scales (100%, 125%, 150%, 200%)
- [ ] 23.14 Test on low-end hardware (disable glassmorphism)
- [ ] 23.15 Test with reduced-motion enabled
- [ ] 23.16 Test high contrast mode

## 24. Performance Optimization

- [x] 24.1 Profile glassmorphism rendering performance
- [x] 24.2 Optimize gradient caching
- [x] 24.3 Optimize animation frame rates
- [x] 24.4 Reduce paint events in waveform component
- [x] 24.5 Test memory usage (target <100MB increase)
- [x] 24.6 Implement performance mode setting
- [x] 24.7 Add auto-detection for low-end hardware

## 25. Accessibility Audit

- [x] 25.1 Run automated contrast checking on all color combinations
- [x] 25.2 Verify all interactive elements have focus indicators
- [x] 25.3 Test keyboard navigation for all features
- [x] 25.4 Verify ARIA labels on all components
- [x] 25.5 Test with screen reader (NVDA)
- [x] 25.6 Test with screen reader (JAWS)
- [x] 25.7 Test reduced-motion mode
- [x] 25.8 Test high contrast mode
- [x] 25.9 Document accessibility features
- [x] 25.10 Create accessibility testing checklist

## 26. Documentation

- [x] 26.1 Document Wispr Flow theme token system
- [x] 26.2 Document component usage with examples
- [x] 26.3 Document glassmorphism utilities
- [x] 26.4 Document animation system
- [x] 26.5 Create migration guide from classic to Wispr Flow
- [x] 26.6 Document UI_STYLE configuration option
- [x] 26.7 Document performance considerations
- [x] 26.8 Document accessibility features
- [x] 26.9 Create visual changelog with before/after screenshots
- [x] 26.10 Update README with Wispr Flow information

## 27. User Testing and Feedback

- [ ] 27.1 Enable Wispr Flow for internal testing
- [ ] 27.2 Gather feedback from team
- [ ] 27.3 Create user survey for design feedback
- [ ] 27.4 Conduct usability testing sessions
- [ ] 27.5 Collect performance metrics from various hardware
- [ ] 27.6 Iterate based on feedback
- [ ] 27.7 Fix critical bugs
- [ ] 27.8 Polish rough edges

## 28. Release Preparation

- [ ] 28.1 Set UI_STYLE default to "classic" for soft launch
- [ ] 28.2 Add UI style selector in settings
- [ ] 28.3 Create release notes
- [ ] 28.4 Update CHANGELOG.md
- [ ] 28.5 Create announcement blog post
- [ ] 28.6 Prepare rollback plan
- [ ] 28.7 Tag release version
- [ ] 28.8 Monitor user feedback post-release
