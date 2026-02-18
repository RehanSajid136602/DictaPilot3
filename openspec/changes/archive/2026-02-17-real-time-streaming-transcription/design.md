## Context

DictaPilot3 currently uses batch transcription - users must release the hotkey before transcription begins. This creates a disconnected experience compared to competitors like WhisperFlow that provide real-time streaming transcription with immediate visual feedback.

**Current Architecture:**
- `recorder.py`: Captures audio via `sounddevice`, stores in memory buffer, saves to temp file on stop
- `transcriber.py`: `Transcriber` class with `transcribe()` method - takes audio file path, calls Groq API
- `app.py`: `Recorder` class handles recording, `transcribe_with_groq()` calls API after recording stops
- GUI: Shows audio bars during recording, switches to "processing" state after release

**Constraints:**
- Groq API doesn't support true streaming audio transcription (no WebSocket/streaming endpoint)
- Must work within existing PySide6 GUI framework
- Must maintain or improve transcription accuracy
- Should gracefully degrade if network issues occur

## Goals / Non-Goals

**Goals:**
- Provide partial transcription results during recording (perceived latency < 500ms)
- Implement chunked audio processing with overlap to prevent word cutoff
- Add live preview UI showing streaming results
- Implement dual-pass: streaming preview + final accuracy pass
- Make streaming configurable (can disable for privacy/bandwidth)
- Graceful fallback to batch mode if streaming fails

**Non-Goals:**
- True WebSocket-based streaming (Groq API doesn't support it)
- Real-time transcription latency < 100ms (API-bound)
- Changing the hotkey mechanism or core GUI architecture
- Supporting multiple simultaneous transcription sessions

## Decisions

### 1. Chunked Processing Approach

**Decision:** Use fixed-size audio chunks (default 1.5s) with overlap (0.3s) for streaming preview.

**Rationale:** 
- Groq API only accepts complete audio files - we simulate streaming by sending chunks
- Overlap prevents word cutoff at chunk boundaries
- 1.5s chunks balance perceived latency vs. API call overhead

**Alternatives Considered:**
- Smaller chunks (0.5s): More responsive but higher API costs, more boundary issues
- Larger chunks (3s+): Lower cost but less responsive feel
- VAD-triggered chunks: Better boundary detection but adds complexity and latency

### 2. Dual-Pass Transcription

**Decision:** Use streaming chunks for preview, full audio for final accuracy pass.

**Rationale:**
- Chunked transcription may have accuracy issues at boundaries
- Final pass on complete audio ensures quality matches current batch mode
- Users see preview while maintaining confidence in final result

**Alternatives Considered:**
- Single-pass streaming only: Simpler but accuracy concerns
- No final pass: Faster but quality degradation
- Use chunk results as final: No cost increase but accuracy concerns

### 3. Streaming Architecture

**Decision:** Create new `StreamingTranscriber` class with worker thread pattern, similar to existing `AsyncTranscriber`.

**Rationale:**
- Follows existing patterns in `transcriber.py`
- Worker thread handles API calls without blocking GUI
- Queue-based architecture for chunk processing
- Clean separation from batch transcription

**Architecture:**
```
[AudioRecorder] --> [ChunkBuffer] --> [StreamingWorker] --> [Preview UI]
       |                                       |
       v                                       v
  [Full Audio]                         [Partial Results]
       |                                       |
       v                                       v
[Transcriber] --> [Smart Editor] --> [Final Output]
```

### 4. UI Integration

**Decision:** Extend existing `GUIManager` to display streaming preview text in a floating overlay.

**Rationale:**
- Minimal changes to existing GUI code
- Preview appears above/below current floating window
- Uses same theming system
- Hides preview when final result is ready

**Alternatives Considered:**
- Inline preview in floating window: Limited space, visual clutter
- Separate preview window: More complex, positioning challenges
- Replace bars with text: Loses visual feedback

### 5. Configuration

**Decision:** Add streaming settings to existing `config.py` and `DictaPilotConfig` dataclass.

**New Settings:**
```python
streaming_enabled: bool = True
streaming_chunk_duration: float = 1.5  # seconds
streaming_chunk_overlap: float = 0.3  # seconds
streaming_min_chunks: int = 2  # minimum chunks before first result
streaming_final_pass: bool = True  # run final accuracy pass
```

**Rationale:**
- Follows existing configuration pattern
- Environment variable overrides supported
- Persisted to config.json

## Risks / Trade-offs

### Risk: Increased API Costs
**Impact:** Dual-pass transcription (streaming + final) roughly doubles API calls.
**Mitigation:** Make streaming configurable; users can disable if cost-sensitive. Default `streaming_final_pass=True` for accuracy.

### Risk: Chunk Boundary Accuracy
**Impact:** Words cut at chunk boundaries may be transcribed incorrectly.
**Mitigation:** 0.3s overlap helps; final pass corrects errors; display preview as "draft" state.

### Risk: Network Latency Spikes
**Impact:** Delayed partial results during poor connectivity.
**Mitigation:** Show "buffering..." indicator; queue results; fallback to batch mode on repeated failures.

### Risk: Visual Flicker
**Impact:** Rapid text updates may cause UI flicker.
**Mitigation:** Debounce UI updates (100ms); smooth text transitions; show stable prefix.

### Risk: Groq Rate Limiting
**Impact:** Too many chunk API calls may hit rate limits.
**Mitigation:** Track API call rate; back off if approaching limits; combine chunks if needed.

## Open Questions

1. **Preview Text Position:** Should preview appear above, below, or overlay the recording window?
   - Recommendation: Below the recording window, anchored to its position

2. **Preview Styling:** Should preview text have different styling than final output?
   - Recommendation: Italic + lighter color to indicate "draft" state

3. **Error Handling:** What to show if streaming fails but recording continues?
   - Recommendation: Show "Streaming paused..." indicator, continue recording, batch process on release

4. **Text Assembly:** How to merge overlapping chunk transcriptions?
   - Recommendation: Keep most recent complete sentence; discard partial prefixes from new chunks
