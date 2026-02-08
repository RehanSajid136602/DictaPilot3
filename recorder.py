"""
DictaPilot Audio Recorder
Handles audio recording with real-time level updates and chunking

Original by: Rohan Sharvesh
Fork maintained by: Rehan

MIT License
Copyright (c) 2026 Rohan Sharvesh
Copyright (c) 2026 Rehan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import threading
import time
import tempfile
import os
import queue
from typing import Optional, Callable
import numpy as np
import sounddevice as sd

from audio.vad import VoiceActivityDetector


class AudioRecorder:
    """
    Audio recorder with real-time level updates and optional VAD (Voice Activity Detection)
    Designed for real-time dictation with low-latency feedback
    """

    def __init__(self,
                 sample_rate: int = 16000,
                 channels: int = 1,
                 enable_vad: bool = False,
                 chunk_duration: float = 0.5):  # 500ms chunks

        self.sample_rate = sample_rate
        self.channels = channels
        self.enable_vad = enable_vad
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)

        # Audio state
        self.is_recording = False
        self._recording_thread = None
        self._should_stop = threading.Event()

        # Callbacks
        self.level_callback: Optional[Callable[[float], None]] = None
        self.chunk_callback: Optional[Callable[[np.ndarray], None]] = None

        # Audio buffer
        self._audio_buffer = []
        self._buffer_lock = threading.RLock()

        # VAD if enabled
        self.vad_detector = VoiceActivityDetector(sample_rate) if enable_vad else None

        # Statistics
        self.total_samples = 0
        self.rms_history = []

    def set_level_callback(self, callback: Callable[[float], None]):
        """Set callback for real-time audio level updates"""
        self.level_callback = callback

    def set_chunk_callback(self, callback: Callable[[np.ndarray], None]):
        """Set callback for audio chunk processing"""
        self.chunk_callback = callback

    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            return False

        self.is_recording = True
        self._should_stop.clear()
        self._audio_buffer = []
        self.total_samples = 0
        self.rms_history = []

        # Start recording thread
        self._recording_thread = threading.Thread(target=self._record_worker, daemon=True)
        self._recording_thread.start()

        return True

    def stop_recording(self) -> Optional[str]:
        """Stop recording and save to temporary file"""
        if not self.is_recording:
            return None

        self.is_recording = False
        self._should_stop.set()

        # Wait for recording thread to finish
        if self._recording_thread and self._recording_thread.is_alive():
            self._recording_thread.join(timeout=2.0)

        # Save accumulated audio to file
        if self._audio_buffer:
            audio_data = np.concatenate(self._audio_buffer, axis=0)
            fd, path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)

            import soundfile as sf
            sf.write(path, audio_data, self.sample_rate)
            return path

        return None

    def _record_worker(self):
        """Background worker for audio recording"""
        try:
            # Find a suitable samplerate
            candidates = [self.sample_rate, 16000, 44100, 48000]
            active_samplerate = None

            for sr in candidates:
                try:
                    with sd.InputStream(samplerate=sr, channels=self.channels,
                                      callback=self._audio_callback, blocksize=self.chunk_size):
                        active_samplerate = sr
                        break
                except Exception:
                    continue

            if active_samplerate is None:
                print("Could not open audio input stream", file=__import__('sys').stderr)
                return

            # Keep recording until stopped
            while self.is_recording and not self._should_stop.is_set():
                sd.sleep(100)

        except Exception as e:
            print(f"Recording error: {e}", file=__import__('sys').stderr)

    def _audio_callback(self, indata, frames, time_info, status):
        """Audio input callback - called continuously during recording"""
        if status:
            print(f"Recording status: {status}", file=__import__('sys').stderr)

        # Make a copy since sounddevice reuses the buffer
        audio_chunk = indata.copy()

        # Calculate RMS for level visualization
        rms = np.sqrt(np.mean(audio_chunk**2))
        if self.level_callback:
            self.level_callback(float(rms))

        # Store in buffer
        with self._buffer_lock:
            self._audio_buffer.append(audio_chunk)
            self.total_samples += len(audio_chunk)
            self.rms_history.append(rms)

        # Call chunk callback if set
        if self.chunk_callback:
            self.chunk_callback(audio_chunk)

        # Store recent RMS for VAD
        if self.vad_detector:
            self.vad_detector.process_chunk(audio_chunk)

    def get_current_level(self) -> float:
        """Get the most recent audio level"""
        if not self.rms_history:
            return 0.0
        return float(self.rms_history[-1])

    def is_speech_detected(self) -> bool:
        """Check if speech is currently detected (requires VAD)"""
        if self.vad_detector:
            return self.vad_detector.is_speech_active()
        # Fallback: detect based on audio level
        return self.get_current_level() > 0.01  # Threshold for "speech"

    def reset(self):
        """Reset the recorder state"""
        self.is_recording = False
        self._should_stop.set()

        if self._recording_thread and self._recording_thread.is_alive():
            self._recording_thread.join(timeout=1.0)

        self._audio_buffer = []
        self.total_samples = 0
        self.rms_history = []


class RollingBufferRecorder(AudioRecorder):
    """
    Extended recorder with rolling buffer for chunked processing
    Optimized for real-time transcription with configurable chunk size
    """

    def __init__(self,
                 sample_rate: int = 16000,
                 channels: int = 1,
                 enable_vad: bool = False,
                 chunk_duration: float = 0.5,  # 500ms chunks
                 rolling_window_duration: float = 2.0):  # 2-second rolling window

        super().__init__(sample_rate, channels, enable_vad, chunk_duration)
        self.rolling_window_duration = rolling_window_duration
        self.max_rolling_chunks = int(rolling_window_duration / chunk_duration)
        self.rolling_buffer = []

    def _audio_callback(self, indata, frames, time_info, status):
        """Enhanced audio callback with rolling buffer"""
        if status:
            print(f"Recording status: {status}", file=__import__('sys').stderr)

        # Make a copy since sounddevice reuses the buffer
        audio_chunk = indata.copy()

        # Calculate RMS for level visualization
        rms = np.sqrt(np.mean(audio_chunk**2))
        if self.level_callback:
            self.level_callback(float(rms))

        # Add to rolling buffer
        self.rolling_buffer.append(audio_chunk)
        if len(self.rolling_buffer) > self.max_rolling_chunks:
            self.rolling_buffer.pop(0)  # Remove oldest chunk

        # Store in main buffer
        with self._buffer_lock:
            self._audio_buffer.append(audio_chunk)
            self.total_samples += len(audio_chunk)
            self.rms_history.append(rms)

        # Call chunk callback if set
        if self.chunk_callback:
            self.chunk_callback(audio_chunk)

        # Store recent RMS for VAD
        if self.vad_detector:
            self.vad_detector.process_chunk(audio_chunk)


# Example usage:
if __name__ == "__main__":
    import time

    def on_level_update(level):
        print(f"\rAudio level: {level:.3f}", end="", flush=True)

    def on_chunk_received(chunk):
        print(f"Received chunk with {len(chunk)} samples")

    # Test the recorder
    recorder = AudioRecorder(enable_vad=True)
    recorder.set_level_callback(on_level_update)
    recorder.set_chunk_callback(on_chunk_received)

    print("Starting recording for 5 seconds...")
    recorder.start_recording()

    for i in range(5):
        time.sleep(1)
        print(f"\rRecording: {i+1}/5 seconds", end="", flush=True)

    print("\nStopping recording...")
    file_path = recorder.stop_recording()

    if file_path:
        print(f"Recording saved to: {file_path}")
        # Clean up temp file
        os.remove(file_path)
    else:
        print("No audio recorded")