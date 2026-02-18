## Context

DictaPilot3 currently has comprehensive but overwhelming documentation. The README contains 40+ configuration options without progressive disclosure, making it difficult for new users to get started. There are no visual guides, video tutorials, or structured onboarding flow. Setup takes 15+ minutes and generates significant support questions.

**Current State:**
- Single README.md with all documentation
- No visual aids (screenshots, GIFs, videos)
- No platform-specific guides
- No in-app onboarding experience
- No centralized documentation website
- High barrier to entry for new users

**Constraints:**
- Must maintain backward compatibility with existing documentation
- Should not add runtime dependencies for core functionality
- Documentation site should be free to host (GitHub Pages)
- Onboarding wizard should be optional (can be skipped)
- Must work offline (local docs accessible without internet)

**Stakeholders:**
- New users (need quick start and guidance)
- Existing users (need comprehensive reference)
- Contributors (need developer documentation)
- Maintainers (need reduced support burden)

## Goals / Non-Goals

**Goals:**
- Reduce setup time from 15+ minutes to <5 minutes
- Achieve 95%+ setup success rate
- Reduce support questions by 50%
- Provide multiple documentation formats (text, visual, video)
- Create searchable, navigable documentation website
- Add interactive first-run onboarding wizard
- Separate quick start from comprehensive reference
- Provide platform-specific troubleshooting

**Non-Goals:**
- Not replacing existing README entirely (restructure only)
- Not creating interactive tutorials (just documentation)
- Not building a full help system in the app (just first-run wizard)
- Not translating documentation to other languages (English only for now)
- Not creating extensive API documentation for internal modules (focus on user-facing features)

## Decisions

### Decision 1: Documentation Structure

**Choice:** Multi-file documentation with progressive disclosure

**Rationale:**
- Separates quick start from comprehensive reference
- Allows users to find information without scrolling through 1000+ lines
- Enables better organization by topic
- Supports documentation website generation

**Alternatives Considered:**
- Single README with collapsible sections: Still overwhelming, poor navigation
- Wiki-only: Requires internet, harder to version control
- In-app help system: Too complex, adds dependencies

**Structure:**
```
docs/
├── quick-start.md              # 5-step guide to first dictation
├── voice-commands.md           # Comprehensive command reference
├── troubleshooting.md          # Common issues and solutions
├── faq.md                      # Frequently asked questions
├── platform-guides/
│   ├── linux.md               # Linux-specific setup
│   ├── macos.md               # macOS-specific setup
│   └── windows.md             # Windows-specific setup
├── developer/
│   ├── architecture.md        # System architecture
│   ├── api-reference.md       # Public API documentation
│   └── contributing.md        # Contribution guidelines
└── assets/
    ├── screenshots/           # Feature screenshots
    └── gifs/                  # Animated demos
```

### Decision 2: Documentation Website Technology

**Choice:** MkDocs with Material theme

**Rationale:**
- Simple Markdown-based (no HTML/CSS required)
- Beautiful, responsive Material Design theme
- Built-in search functionality
- Easy GitHub Pages deployment
- Supports versioning
- Active community and good documentation

**Alternatives Considered:**
- Sphinx: More complex, Python-centric, steeper learning curve
- Docusaurus: Requires Node.js, more complex setup
- Jekyll: Less feature-rich, requires Ruby
- VuePress: Requires Node.js, Vue knowledge
- Plain HTML: Too much maintenance, no search

**Configuration:**
```yaml
# mkdocs.yml
site_name: DictaPilot3 Documentation
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - search.suggest
    - search.highlight
nav:
  - Home: index.md
  - Quick Start: quick-start.md
  - Voice Commands: voice-commands.md
  - Platform Guides:
    - Linux: platform-guides/linux.md
    - macOS: platform-guides/macos.md
    - Windows: platform-guides/windows.md
  - Troubleshooting: troubleshooting.md
  - FAQ: faq.md
  - Developer:
    - Architecture: developer/architecture.md
    - API Reference: developer/api-reference.md
    - Contributing: developer/contributing.md
```

### Decision 3: Onboarding Wizard Implementation

**Choice:** Qt6-based wizard using existing PySide6 dependency

**Rationale:**
- Already using PySide6 for floating window
- No new dependencies required
- Native look and feel on all platforms
- Can reuse existing config.py infrastructure
- Easy to integrate with app.py startup flow

**Alternatives Considered:**
- Web-based wizard (Electron): Adds massive dependency, overkill
- Tkinter: Less modern, inconsistent cross-platform appearance
- Terminal-based wizard (questionary): Not visual, less user-friendly
- Separate installer: Complex, requires packaging changes

**Implementation Approach:**
```python
# onboarding_wizard.py
class OnboardingWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.addPage(WelcomePage())
        self.addPage(APIKeyPage())
        self.addPage(HotkeyPage())
        self.addPage(AudioDevicePage())
        self.addPage(CompletePage())
    
    def accept(self):
        # Save configuration
        config = self.collect_config()
        config.save()
        super().accept()
```

**First-run Detection:**
```python
# In app.py
def main():
    config = load_config()
    
    if not config.get('setup_completed', False):
        wizard = OnboardingWizard()
        if wizard.exec() == QDialog.Accepted:
            config['setup_completed'] = True
            config.save()
        else:
            sys.exit(0)  # User cancelled setup
    
    # Continue with normal app startup
    start_dictation_app()
```

### Decision 4: Video Tutorial Hosting

**Choice:** YouTube with embedded links in documentation

**Rationale:**
- Free hosting with unlimited bandwidth
- Good video player with quality selection
- Accessible on all devices
- Supports captions/subtitles
- Easy to embed in documentation
- No storage costs

**Alternatives Considered:**
- Self-hosted: Expensive bandwidth, requires CDN
- Vimeo: Limited free tier, less discoverable
- GitHub releases: Not designed for video streaming
- Documentation site: Large file sizes, slow loading

**Video Series Plan:**
1. Quick Start (3 minutes): Installation to first dictation
2. Voice Commands (5 minutes): Common commands and editing
3. Smart Editing (4 minutes): LLM cleanup and customization
4. Context Profiles (3 minutes): Per-app settings
5. Troubleshooting (4 minutes): Common issues and solutions

### Decision 5: README Restructuring

**Choice:** Keep README as landing page with links to detailed docs

**Rationale:**
- README is first thing users see on GitHub
- Should be concise and inviting
- Links to detailed docs for those who need more
- Maintains single source of truth (no duplication)

**New README Structure:**
1. Hero section (what is DictaPilot3)
2. Key features (bullet points)
3. Quick start (5 steps with link to full guide)
4. Links to documentation sections
5. Community and support links
6. License and credits

**Before/After:**
- Before: 500+ lines, overwhelming
- After: 150 lines, focused on getting started

## Risks / Trade-offs

### Risk 1: Documentation Maintenance Burden
**Risk:** Multiple documentation files could become outdated or inconsistent

**Mitigation:**
- Use documentation linting (markdownlint)
- Add CI checks for broken links
- Create documentation update checklist for PRs
- Use includes/snippets for shared content
- Regular documentation review schedule

### Risk 2: Onboarding Wizard Complexity
**Risk:** Wizard could become complex and hard to maintain

**Mitigation:**
- Keep wizard simple (5 pages max)
- Reuse existing config infrastructure
- Make wizard optional (can skip and configure manually)
- Add "Skip Setup" button on every page
- Provide "Re-run Setup" option in settings

### Risk 3: Video Tutorial Obsolescence
**Risk:** Videos become outdated as UI changes

**Mitigation:**
- Focus videos on concepts, not specific UI elements
- Add text overlays noting version
- Plan for periodic video updates (every 6 months)
- Supplement with screenshots that are easier to update
- Use voiceover that can be re-recorded separately

### Risk 4: Documentation Website Hosting
**Risk:** GitHub Pages could have downtime or limitations

**Mitigation:**
- Keep all docs in repo (accessible offline)
- Documentation works without website (Markdown readable)
- Can migrate to alternative hosting if needed
- Static site can be hosted anywhere

### Risk 5: Platform-Specific Documentation Drift
**Risk:** Platform guides could diverge and become inconsistent

**Mitigation:**
- Use shared templates for common sections
- Cross-reference between platform guides
- Test setup on all platforms before documentation updates
- Community contributions for platform-specific issues

## Migration Plan

### Phase 1: Documentation Structure (Week 1)
1. Create docs/ directory structure
2. Split README into separate files
3. Restructure README as landing page
4. Add cross-references between documents
5. Test all links

### Phase 2: Visual Assets (Week 1-2)
1. Take screenshots of key features
2. Create animated GIFs for common workflows
3. Record video tutorials
4. Upload videos to YouTube
5. Add visual assets to documentation

### Phase 3: Documentation Website (Week 2)
1. Set up MkDocs configuration
2. Configure Material theme
3. Test local build
4. Deploy to GitHub Pages
5. Configure custom domain (optional)

### Phase 4: Onboarding Wizard (Week 2-3)
1. Implement wizard UI (5 pages)
2. Integrate with config system
3. Add first-run detection
4. Test on all platforms
5. Add "Re-run Setup" option

### Phase 5: Testing & Refinement (Week 3)
1. User testing with 10+ new users
2. Collect feedback on setup experience
3. Measure setup time and success rate
4. Refine documentation based on feedback
5. Update troubleshooting guide with common issues

### Rollback Strategy
- Keep original README in git history
- Documentation changes are non-breaking
- Onboarding wizard is optional (can be disabled)
- Can revert to single-file documentation if needed

### Success Metrics
- Setup time: <5 minutes (target)
- Setup success rate: >95% (target)
- Support questions: 50% reduction (target)
- Documentation website traffic: 1000+ visits/month
- Video views: 500+ views per video

## Open Questions

1. **Should we create a Discord/Slack community for support?**
   - Pro: Real-time help, community building
   - Con: Maintenance burden, moderation required
   - Decision: Defer to Phase 2, start with GitHub Discussions

2. **Should we add interactive code examples?**
   - Pro: Users can try features without installing
   - Con: Complex to implement, requires hosting
   - Decision: Not for initial release, consider for future

3. **Should we translate documentation to other languages?**
   - Pro: Broader audience reach
   - Con: Maintenance burden, translation quality
   - Decision: English only for now, accept community translations

4. **Should we add telemetry to track setup success?**
   - Pro: Data-driven improvements
   - Con: Privacy concerns, implementation complexity
   - Decision: Optional anonymous telemetry with explicit opt-in

5. **Should we create a separate "Getting Started" repository?**
   - Pro: Simpler for new users, focused examples
   - Con: Maintenance burden, potential confusion
   - Decision: No, keep everything in main repository
