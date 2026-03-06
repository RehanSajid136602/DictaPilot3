## Context

This change defines a Windows-first DictaPilot desktop stack using Tauri (runtime), React (UI), TypeScript (frontend contracts), and Rust (backend command layer). The objective is to deliver modern UI responsiveness with lower memory/runtime overhead than Electron while maintaining secure boundaries and clear implementation paths.

**Constraints:**
- Windows-first scope
- Security-first command exposure (allowlist only)
- Maintain behavior parity for core dictation lifecycle
- Keep artifacts implementation-ready for `/opsx:apply`
- Existing Electron change remains separate and unchanged

## Goals / Non-Goals

**Goals:**
- Establish `tauri-desktop/` workspace and architecture baseline
- Define typed command contracts and structured error model
- Implement core dictation lifecycle end-to-end through Tauri commands
- Provide Windows `.exe` packaging and smoke-testable release flow
- Enable clean migration path from existing Python UI/runtime

**Non-Goals:**
- Full migration of every existing feature in first pass
- macOS/Linux bundle support in this change
- Cloud/team feature additions
- Rewriting existing Python stack in this artifact phase

## Decisions

### Decision 1: Tauri runtime with strict command allowlist
**Choice:** Use Tauri command invocations with explicit allowlisted commands and minimized frontend capability exposure.

**Rationale:**
- Reduces attack surface
- Keeps backend boundaries explicit
- Simplifies security review

### Decision 2: React renderer with typed API wrapper
**Choice:** Frontend uses a typed API wrapper generated from shared command contracts.

**Rationale:**
- Prevents loosely typed invoke calls
- Improves maintainability and refactoring safety
- Aligns UI behavior with backend guarantees

### Decision 3: Rust backend modules by domain
**Choice:** Split backend into `audio`, `transcription`, `editing`, `settings`, and `history` modules.

**Rationale:**
- Keeps codebase modular and testable
- Mirrors capability boundaries in specs
- Reduces implementation risk

### Decision 4: Migration via parallel workspace
**Choice:** Build under `tauri-desktop/` as a parallel track; do not alter existing implementation paths in this phase.

**Rationale:**
- Allows side-by-side validation
- Minimizes risk of regressions in current app
- Supports incremental rollout

### Decision 5: Packaging via Tauri bundle pipeline
**Choice:** Use Tauri bundling for Windows installer/executable outputs with CI artifact publishing.

**Rationale:**
- Native packaging path for Tauri
- Deterministic artifact generation
- Straightforward release automation

## Risks / Trade-offs

### Risk 1: Global hotkey/audio capture parity
**Mitigation:** Define and test latency/behavior acceptance scenarios early in command backend and UI state handling.

### Risk 2: Command contract drift
**Mitigation:** Add contract compatibility tests and versioning policy before broad feature expansion.

### Risk 3: Packaging environment complexity
**Mitigation:** Document prerequisites and pin toolchain versions in CI and local build docs.

### Risk 4: UI smoothness under high update frequency
**Mitigation:** Throttle streaming updates, use requestAnimationFrame patterns, and profile render updates.

## Migration Plan

1. Bootstrap `tauri-desktop/` workspace and toolchain config.
2. Implement Tauri shell + command allowlist + typed contracts.
3. Build React core views and dictation state machine UI.
4. Implement Rust backend command modules and local persistence.
5. Connect end-to-end dictation flow and error handling.
6. Add Windows package pipeline and smoke tests.
7. Validate against specs and proceed to implementation phase.
