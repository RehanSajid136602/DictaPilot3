## Context

DictaPilot currently provides basic voice transcription with minimal personalization. This design addresses implementing 15 new features across 4 phases to match Wispr Flow's capabilities. The implementation will touch multiple modules: transcription handling, UI/dashboard, data storage, and potentially add new services for sync and mobile.

**Current State:**
- Basic real-time transcription using NVIDIA NIM API
- Simple app context detection for window titles
- Local SQLite storage for transcriptions
- Dashboard for viewing history and statistics
- No personalization features (dictionary, snippets, etc.)

**Constraints:**
- Must maintain backward compatibility with existing transcription flow
- Desktop application first; mobile is Phase 4
- Cloud sync is optional (offline-first approach)
- Must work on Linux (primary), with macOS and Windows support

## Goals / Non-Goals

**Goals:**
1. Implement Phase 1 features (Personal Dictionary, Snippet Library, Context Tone, Quick Edit Commands)
2. Create extensible architecture for Phase 2-4 features
3. Maintain 220+ WPM transcription speed
4. Achieve 95%+ transcription accuracy with personalization

**Non-Goals:**
- Mobile app development (Phase 4)
- Full enterprise/team features (Phase 4)
- HIPAA compliance implementation (Phase 4)
- Real-time collaborative editing

## Decisions

### 1. Personal Dictionary Storage: SQLite over JSON
**Decision:** Use SQLite database for personal dictionary storage.
**Rationale:** Better performance for frequent lookups, built-in frequency tracking, easier to query and manage than JSON files.
**Alternative Considered:** JSON file storage - simpler but slower for large dictionaries.

### 2. Snippet Library Format: JSON with Jinja2 Templates
**Decision:** Store snippets in JSON files with Jinja2 template support.
**Rationale:** Jinja2 provides powerful templating for dynamic content, widely used, easy to extend.
**Alternative Considered:** Custom template engine - unnecessary complexity.

### 3. Quick Edit Command Parser: Regex-based with State Machine
**Decision:** Implement command parser using regex patterns with undo/redo state machine.
**Rationale:** Fast, deterministic parsing for known commands; state machine handles complex edit sequences.
**Alternative Considered:** LLM-based parsing - too slow for real-time use.

### 4. Sync Strategy: Optional Cloud with Local-First
**Decision:** Implement offline-first with optional Firebase/Supabase sync.
**Rationale:** Most users work on single device; sync is optional enhancement. Local-first ensures functionality without cloud dependency.
**Alternative Considered:** Mandatory cloud sync - adds complexity and privacy concerns.

### 5. Multi-Language Detection: NVIDIA NIM API Language Parameter
**Decision:** Use NVIDIA NIM API's language detection parameter for transcription.
**Rationale:** Leverages existing API capabilities, no additional service needed.
**Alternative Considered:** Separate language detection service - added complexity for marginal benefit.

### 6. Code Dictation: IDE Integration via IPC
**Decision:** Connect to IDEs via language server protocol (LSP) for code-specific dictation.
**Rationale:** LSP provides rich context (syntax, imports, types) for accurate code transcription.
**Alternative Considered:** Pattern-based code detection - less accurate.

## Risks / Trade-offs

### Risk: Performance Impact from Personal Dictionary Lookup
**Risk:** Frequent dictionary lookups could slow down transcription.
**Mitigation:** Use in-memory caching with SQLite backing; only check against dictionary after full words are transcribed.

### Risk: Quick Edit Commands Interpreting Speech
**Risk:** User speech might trigger false-positive edit commands.
**Mitigation:** Require specific activation phrase; provide easy undo; allow customization of command phrases.

### Risk: Cross-Device Sync Conflicts
**Risk:** Concurrent edits on multiple devices could cause data conflicts.
**Mitigation:** Use last-write-wins with conflict logging; provide manual merge UI.

### Risk: Mobile App Resource Constraints
**Risk:** Mobile devices have limited resources for real-time transcription.
**Mitigation:** Use chunked audio processing; consider server-side transcription for mobile.

### Trade-off: Feature Scope vs. Implementation Time
**Trade-off:** 15 features across 4 phases is ambitious.
**Mitigation:** Strict phase gating; each phase must stabilize before starting next.

## Migration Plan

1. **Phase 1 (Weeks 1-6):**
   - Add SQLite schema for personal dictionary
   - Implement snippet library with JSON storage
   - Create command parser for quick edits
   - Add tone adjustment to transcription pipeline

2. **Phase 2 (Weeks 7-12):**
   - Add WPM calculation to transcription
   - Enhance filler word detection
   - Add app-specific formatting presets
   - Implement accessibility features

3. **Phase 3 (Weeks 13-20):**
   - Add multi-language support
   - Implement code dictation with IDE integration
   - Create demo mode web page

4. **Phase 4 (Weeks 21-32):**
   - Add sync service (optional Firebase/Supabase)
   - Create mobile apps
   - Add team features
   - Implement compliance features

**Rollback Strategy:** Each phase is independent; can rollback to previous phase by removing feature-specific code while maintaining core transcription.

## Open Questions

1. **Sync Service Provider:** Firebase or Supabase for cross-device sync? Need to evaluate pricing and privacy implications.

2. **Mobile Framework:** React Native or Flutter for mobile apps? Flutter offers better performance; React Native shares code with web dashboard.

3. **Team Features Scope:** What team features are most valuable? Need user research to prioritize.

4. **Demo Mode Hosting:** Where will demo mode be hosted? Could be embedded in website or separate subdomain.
