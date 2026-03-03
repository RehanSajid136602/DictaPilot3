## Context

DictaPilot currently uses a Qt6-based dashboard with Catppuccin Mocha theming and a traditional vertical sidebar layout. The application has a well-established component architecture with:
- Theme system (`dashboard_themes.py`) using token-based colors
- Main dashboard (`dashboard_main.py`) with sidebar navigation
- Multiple views (Home, Settings, History, Dictionary, Statistics, Diagnostics)
- Reusable components (cards, charts, widgets, buttons)
- Floating recording window with waveform visualization

The current design is functional but visually dated. Wispr Flow represents a modern design language with icy blues/purples, glassmorphism effects, and minimal aesthetics. This redesign aims to modernize DictaPilot's appearance while maintaining all existing functionality and improving accessibility.

**Constraints:**
- Must maintain Qt6/PySide6 compatibility (no new dependencies)
- Must preserve all existing functionality
- Must support accessibility standards (WCAG 2.1 AA)
- Must perform well on mid-range hardware (avoid excessive GPU usage)
- Must provide migration path for users (parallel implementation)

**Stakeholders:**
- End users (dictation workflow must not be disrupted)
- Developers (maintainable, well-documented code)
- Accessibility users (screen readers, keyboard navigation, reduced motion)

## Goals / Non-Goals

**Goals:**
- Implement Wispr Flow visual design language (colors, typography, spacing)
- Create glassmorphism effects for cards and floating window
- Redesign floating recording window with gradient waveform
- Restructure dashboard layout with horizontal top navigation
- Update all views with new styling (Home, Settings, History, Dictionary, Statistics)
- Maintain 100% feature parity with current implementation
- Achieve WCAG 2.1 AA accessibility compliance
- Provide smooth animations with reduced-motion support
- Support parallel implementation (classic vs Wispr Flow themes)

**Non-Goals:**
- Adding new features beyond visual redesign
- Changing core dictation functionality or transcription logic
- Rewriting existing business logic
- Supporting themes beyond Wispr Flow and classic (no theme marketplace)
- Mobile/responsive design (desktop-focused)
- Internationalization of new UI text (use existing i18n system)

## Decisions

### Decision 1: Parallel Implementation with Feature Flag

**Choice:** Implement Wispr Flow components alongside existing components, controlled by `UI_STYLE` config flag.

**Rationale:**
- Allows gradual rollout and user testing
- Provides fallback if issues arise
- Enables A/B testing for user feedback
- Reduces risk of breaking existing workflows

**Alternatives Considered:**
- Direct replacement: Too risky, no rollback path
- Separate branch: Difficult to maintain, merge conflicts
- Plugin system: Over-engineered for this use case

**Implementation:**
```python
# config.py
UI_STYLE = os.getenv("UI_STYLE", "wispr_flow")  # "wispr_flow" or "classic"

# dashboard_main.py
if config.UI_STYLE == "wispr_flow":
    from dashboard_wispr_flow.layout import MainLayout
else:
    from dashboard_main import DictaPilotMainDashboard as MainLayout
```

### Decision 2: Glassmorphism Implementation Strategy

**Choice:** Use QGraphicsBlurEffect with performance fallbacks and caching.

**Rationale:**
- Native Qt6 support, no external dependencies
- Hardware-accelerated when available
- Can detect performance issues and disable automatically
- Provides graceful degradation

**Alternatives Considered:**
- CSS-style backdrop-filter: Not available in Qt6
- Pre-rendered blur textures: Static, not adaptive
- No glassmorphism: Loses key visual element

**Implementation:**
```python
# dashboard_wispr_flow/utils/glassmorphism.py
class GlassmorphismEffect:
    def __init__(self, blur_radius=20, opacity=0.7):
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(blur_radius)
        self.opacity = opacity
        self.enabled = self._check_performance()
    
    def _check_performance(self):
        # Detect GPU capabilities, disable on low-end hardware
        return not os.getenv("DISABLE_GLASSMORPHISM", False)
```

### Decision 3: Color Token System Extension

**Choice:** Extend existing ThemeManager to support multiple palettes rather than replacing it.

**Rationale:**
- Preserves existing theme infrastructure
- Allows easy switching between palettes
- Maintains backward compatibility
- Reuses token-based architecture

**Alternatives Considered:**
- New theme system: Duplicate code, harder to maintain
- Hard-coded colors: Not maintainable, no flexibility
- CSS-in-Python: Verbose, harder to debug

**Implementation:**
```python
# dashboard_wispr_flow/theme.py
WISPR_FLOW_TOKENS = {
    "bg-base": "#0f1419",
    "accent-blue": "#3b82f6",
    # ... full palette
}

# dashboard_themes.py (extended)
class ThemeManager:
    def __init__(self, palette="wispr_flow"):
        if palette == "wispr_flow":
            self.tokens = WISPR_FLOW_TOKENS
        elif palette == "catppuccin":
            self.tokens = DARK_TOKENS
```

### Decision 4: Waveform Gradient Rendering

**Choice:** Use QLinearGradient with cached gradient objects, updated per-frame for amplitude.

**Rationale:**
- Efficient rendering (GPU-accelerated)
- Smooth 60fps animation possible
- Low memory overhead with caching
- Native Qt6 support

**Alternatives Considered:**
- Canvas-based rendering: Slower, more CPU-intensive
- Pre-rendered sprites: Not dynamic enough
- SVG gradients: Parsing overhead

**Implementation:**
```python
# dashboard_wispr_flow/floating/waveform.py
class GradientWaveform(QWidget):
    def __init__(self):
        self.gradient = QLinearGradient(0, 0, 0, self.height())
        self.gradient.setColorAt(0, QColor("#06b6d4"))
        self.gradient.setColorAt(1, QColor("#22d3ee"))
        self._gradient_cache = {}
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(self.gradient)
        # Draw bars with amplitudes
```

### Decision 5: Layout Restructuring Approach

**Choice:** Create new layout components in `dashboard_wispr_flow/layout/` rather than modifying existing files.

**Rationale:**
- Clean separation of concerns
- Easier to test and maintain
- Supports parallel implementation
- Clear migration path

**Alternatives Considered:**
- Modify existing layout: Breaks classic theme
- Conditional rendering in same file: Too complex, hard to read
- Separate application: Duplicate business logic

**Implementation:**
```
dashboard_wispr_flow/
├── layout/
│   ├── main_layout.py       # New horizontal top nav + sidebar
│   ├── top_navigation.py    # Horizontal nav bar
│   ├── sidebar.py           # Collapsible left sidebar
│   └── status_bar.py        # Bottom status bar
```

### Decision 6: Animation System

**Choice:** Use QPropertyAnimation with easing curves, respecting system reduced-motion preferences.

**Rationale:**
- Native Qt6 animation framework
- Hardware-accelerated
- Easy to control timing and easing
- Built-in reduced-motion detection

**Alternatives Considered:**
- Manual frame-by-frame: Too complex, not smooth
- CSS animations: Not available in Qt6
- Third-party library: Unnecessary dependency

**Implementation:**
```python
# dashboard_wispr_flow/utils/animations.py
class StateAnimation:
    def __init__(self, widget, property_name, duration=250):
        self.animation = QPropertyAnimation(widget, property_name.encode())
        self.animation.setDuration(duration)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Respect reduced motion
        if self._is_reduced_motion():
            self.animation.setDuration(0)
```

### Decision 7: Component Architecture

**Choice:** Create new component library in `dashboard_wispr_flow/components/` with composition over inheritance.

**Rationale:**
- Reusable, testable components
- Clear API boundaries
- Easy to document and maintain
- Follows Qt6 best practices

**Implementation:**
```python
# dashboard_wispr_flow/components/cards.py
class GlassmorphismCard(QFrame):
    def __init__(self, blur_radius=20, opacity=0.7):
        super().__init__()
        self.setProperty("card", True)
        self._apply_glass_effect(blur_radius, opacity)
```

## Risks / Trade-offs

### Risk 1: Performance Degradation with Glassmorphism
**Impact:** High - Could make UI sluggish on low-end hardware

**Mitigation:**
- Implement performance detection on startup
- Provide `DISABLE_GLASSMORPHISM` environment variable
- Cache blur effects where possible
- Add "Performance Mode" setting to disable effects
- Test on low-end hardware (Intel integrated graphics)

### Risk 2: Accessibility Regressions
**Impact:** High - Could exclude users with disabilities

**Mitigation:**
- Automated contrast checking in CI/CD
- Manual screen reader testing (NVDA, JAWS)
- Keyboard navigation testing for all features
- High contrast mode support
- Reduced motion mode implementation
- ARIA labels on all interactive elements

### Risk 3: User Resistance to Design Change
**Impact:** Medium - Users may prefer familiar interface

**Mitigation:**
- Parallel implementation allows choice
- Gradual rollout with user feedback
- Clear documentation of changes
- Onboarding tour for new design
- Keep classic theme available for 2+ releases

### Risk 4: Animation Jank on Low-End Hardware
**Impact:** Medium - Choppy animations hurt user experience

**Mitigation:**
- Target 60fps, measure actual performance
- Reduce animation complexity if needed
- Provide reduced-motion mode
- Test on various hardware configurations
- Use hardware-accelerated rendering where possible

### Risk 5: Cross-Platform Rendering Differences
**Impact:** Medium - Design may look different on Windows/Linux/macOS

**Mitigation:**
- Test on all supported platforms
- Use platform-agnostic Qt6 features
- Avoid platform-specific hacks
- Document known differences
- Provide platform-specific overrides if needed

### Risk 6: Increased Memory Usage
**Impact:** Low - Blur effects and gradients use more memory

**Mitigation:**
- Cache gradient objects
- Reuse blur effects
- Monitor memory usage in testing
- Set reasonable limits (target <100MB increase)
- Profile with Qt profiler tools

### Risk 7: Color Contrast Issues
**Impact:** High - Poor contrast affects readability

**Mitigation:**
- Automated contrast checking (WCAG 2.1 AA: 4.5:1 ratio)
- Manual review of all color combinations
- Test with color blindness simulators
- Provide high contrast mode
- Document color usage guidelines

## Migration Plan

### Phase 1: Foundation (Week 1-2)
1. Create `dashboard_wispr_flow/` directory structure
2. Implement theme system with Wispr Flow tokens
3. Add `UI_STYLE` configuration option
4. Update `ThemeManager` to support multiple palettes
5. Create base component classes (cards, buttons, inputs)
6. Run accessibility audit on new colors

**Validation:**
- All color tokens defined and documented
- Contrast ratios meet WCAG 2.1 AA
- Theme switching works without restart
- No regressions in existing functionality

### Phase 2: Floating Window (Week 3)
1. Create `dashboard_wispr_flow/floating/` components
2. Implement glassmorphism effects with fallbacks
3. Build gradient waveform component
4. Add state-based color transitions (cyan/purple)
5. Implement smooth animations (appear/disappear)
6. Add accessibility features (ARIA, keyboard)

**Validation:**
- Floating window renders correctly on all platforms
- Waveform animates at 60fps
- Glassmorphism degrades gracefully on low-end hardware
- Keyboard shortcuts work (Escape to close)
- Screen reader announces state changes

### Phase 3: Dashboard Layout (Week 4-5)
1. Create `dashboard_wispr_flow/layout/` components
2. Implement horizontal top navigation bar
3. Build collapsible left sidebar
4. Update status bar styling
5. Add responsive breakpoints
6. Implement smooth view transitions

**Validation:**
- Navigation works on all screen sizes
- Sidebar collapse/expand is smooth
- All views accessible from navigation
- Keyboard navigation works (Tab, Arrow keys)
- No layout shifts or jank

### Phase 4: Views & Components (Week 6-8)
1. Redesign Home view (hero, stats, recent, charts)
2. Update Settings view (tabs, forms, toggles)
3. Transform History view (timeline, cards)
4. Enhance Dictionary view (search, FAB, inline edit)
5. Update Statistics view (gradient charts)
6. Polish all animations and transitions

**Validation:**
- All views render correctly
- No feature regressions
- Animations are smooth
- Accessibility maintained
- User testing feedback positive

### Rollout Strategy

**Week 9: Beta Testing**
- Enable Wispr Flow by default for internal testing
- Gather feedback from team and early adopters
- Fix critical bugs and polish rough edges
- Performance testing on various hardware

**Week 10: Soft Launch**
- Release with `UI_STYLE=classic` as default
- Add setting to switch to Wispr Flow
- Monitor user feedback and bug reports
- Iterate based on feedback

**Release +1 Month: Default Switch**
- Make Wispr Flow the default (`UI_STYLE=wispr_flow`)
- Keep classic theme available
- Announce deprecation timeline for classic

**Release +3 Months: Deprecation**
- Remove classic theme option
- Clean up parallel implementation code
- Archive old components
- Update documentation

### Rollback Strategy

If critical issues arise:
1. Change default back to `UI_STYLE=classic`
2. Disable Wispr Flow option in settings
3. Fix issues in separate branch
4. Re-test thoroughly before re-enabling
5. Communicate clearly with users

**Rollback Triggers:**
- Critical accessibility issues
- Performance degradation >20%
- Widespread user complaints
- Data loss or corruption (unlikely for UI-only change)

## Open Questions

1. **Typography**: Should we bundle a specific sans-serif font (e.g., Inter, Geist) or rely on system fonts?
   - **Leaning toward:** System fonts for smaller bundle size, fallback to common fonts

2. **Glassmorphism intensity**: What blur radius provides best balance of aesthetics and performance?
   - **Leaning toward:** 20px blur with user-configurable intensity (0.5x - 1.5x)

3. **Animation duration**: What timing feels most responsive without being jarring?
   - **Leaning toward:** 250ms for state changes, 300ms for view transitions, 200ms for micro-interactions

4. **Sidebar default state**: Should sidebar start collapsed or expanded on first launch?
   - **Leaning toward:** Expanded on desktop (>1280px), collapsed on smaller screens

5. **Classic theme support duration**: How long should we maintain parallel implementation?
   - **Leaning toward:** 2 major releases (~6 months) before deprecation

6. **Performance mode**: Should we auto-detect low-end hardware and disable effects, or require manual toggle?
   - **Leaning toward:** Auto-detect with manual override option

7. **Gradient complexity**: Should charts use simple 2-color gradients or more complex multi-stop gradients?
   - **Leaning toward:** 2-color gradients for performance, 3-stop for hero sections only
