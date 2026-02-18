## Why

DictaPilot3 currently uses batch processing that requires users to release the hotkey before transcription begins, creating a disconnected experience. WhisperFlow and other competitors provide real-time streaming transcription with immediate visual feedback during dictation. Implementing streaming transcription closes this major UX gap, making DictaPilot3 feel more responsive and modern while maintaining accuracy.

## What Changes

- Implement streaming transcription with chunked audio processing
- Add live preview UI component showing partial transcription results
- Implement dual-pass transcription (streaming for preview, final pass for accuracy)
- Add streaming worker thread for concurrent audio processing
- Implement audio buffer management with overlap to prevent word cutoff
- Add network latency handling and buffering strategies
- Add configuration options for streaming vs batch mode
- Implement fallback to batch mode if streaming fails or is disabled
- Add visual indicators for streaming vs finalizing states
- Test with various speech patterns and network conditions

## Capabilities

### New Capabilities
- `streaming-transcription`: Real-time audio transcription with partial results
- `chunked-audio-processing`: Process audio in chunks with overlap management
- `live-preview-ui`: Display partial transcription results during recording
- `dual-pass-transcription`: Streaming preview + final accuracy pass
- `streaming-fallback`: Graceful degradation to batch mode

### Modified Capabilities
<!-- No existing capabilities being modified - this is additive -->

## Impact

**Code Changes:**
- New: `streaming_transcriber.py` - Streaming transcription implementation
- New: `audio_buffer.py` - Chunked audio buffer with overlap management
- Modified: `transcriber.py` - Add streaming mode alongside batch mode
- Modified: `app.py` - Integrate streaming transcription and live preview
- Modified: `recorder.py` - Support chunked audio capture
- Modified: GUI components - Add live preview display

**Dependencies:**
- Groq API: Check if streaming API is available (or use alternative)
- Existing: `sounddevice`, `numpy` (already used)
- No new external dependencies required

**Configuration:**
- New: `STREAMING_ENABLED` - Enable/disable streaming (default: True)
- New: `CHUNK_SIZE` - Audio chunk size in seconds (default: 0.5)
- New: `CHUNK_OVERLAP` - Overlap between chunks (default: 0.1)
- New: `PREVIEW_MODE` - Show live preview (default: True)
- New: `STREAMING_MIN_CHUNKS` - Minimum chunks before first result (default: 2)
- New: `FINAL_PASS_ENABLED` - Run final accuracy pass (default: True)

**API Changes:**
- `transcribe_audio()` - Add `streaming=False` parameter
- `transcribe_streaming()` - New function for streaming mode
- New callback: `on_partial_result(text: str)` for live updates

**User Experience:**
- User holds F9 and sees words appearing in real-time (500ms latency)
- Visual indicator shows "Streaming..." during recording
- Visual indicator shows "Finalizing..." during final pass
- Option to disable streaming for privacy (batch mode)
- Graceful fallback if streaming unavailable

**Performance:**
- Partial results within 500ms of speech
- Final accuracy matches or exceeds batch mode
- <10% increase in API costs (streaming + final pass)
- Network latency handling with buffering

**Architecture:**
```
User speaks → Audio chunks → Streaming worker → Partial results → Live preview
                                                                         ↓
User releases → Final audio → Batch transcription → Final result → Paste
```

**Testing:**
- Test with fast speech
- Test with slow speech with pauses
- Test with various accents
- Test network latency scenarios
- Test fallback to batch mode
- Verify final accuracy matches batch
- Measure API cost increase

**Documentation:**
- Update README with streaming feature
- Add streaming configuration guide
- Document streaming vs batch trade-offs
- Add troubleshooting for streaming issues
- Update FAQ with streaming questions

**Risks:**
- Groq may not support streaming API (need alternative or workaround)
- Increased API costs from dual-pass transcription
- Network latency may affect user experience
- Partial results may be less accurate than final

**Mitigation:**
- Research Groq streaming capabilities first
- Make streaming optional (can disable)
- Implement smart buffering for latency
- Clear visual feedback about streaming vs final states
- Allow users to choose streaming vs batch based on needs
