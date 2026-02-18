"""
DictaPilot Streaming Transcriber
Handles real-time streaming transcription with chunked audio processing

MIT License
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

import os
import threading
import queue
import time
import tempfile
from typing import Optional, Callable, List, Tuple
from dataclasses import dataclass, field
import numpy as np

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

from audio_buffer import AudioChunk, TextAssembler


@dataclass
class StreamingResult:
    """Represents a streaming transcription result"""
    text: str
    chunk_id: int
    is_partial: bool = True
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class StreamingHealth:
    """Tracks streaming transcription health status"""
    total_chunks: int = 0
    successful_chunks: int = 0
    failed_chunks: int = 0
    consecutive_failures: int = 0
    last_error: Optional[str] = None
    last_success_time: Optional[float] = None
    is_healthy: bool = True
    fallback_mode: bool = False
    
    def record_success(self):
        self.total_chunks += 1
        self.successful_chunks += 1
        self.consecutive_failures = 0
        self.last_success_time = time.time()
        self.is_healthy = True
    
    def record_failure(self, error: str):
        self.total_chunks += 1
        self.failed_chunks += 1
        self.consecutive_failures += 1
        self.last_error = error
        # Enter fallback mode after 3 consecutive failures
        if self.consecutive_failures >= 3:
            self.is_healthy = False
            self.fallback_mode = True
    
    def reset(self):
        self.total_chunks = 0
        self.successful_chunks = 0
        self.failed_chunks = 0
        self.consecutive_failures = 0
        self.last_error = None
        self.last_success_time = None
        self.is_healthy = True
        self.fallback_mode = False


class StreamingTranscriber:
    """
    Real-time streaming transcription with chunked audio processing.
    
    Uses a worker thread to process audio chunks asynchronously,
    providing partial results via callback.
    """
    
    def __init__(self,
                 api_key: Optional[str] = None,
                 model: str = "whisper-large-v3-turbo",
                 max_retries: int = 2,
                 retry_delay: float = 0.5):
        """
        Initialize the streaming transcriber.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Whisper model to use
            max_retries: Maximum retry attempts for failed chunks
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self._groq_client = None
        self._task_queue: queue.Queue = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        
        # Text assembler for merging chunk results
        self._text_assembler = TextAssembler()
        
        # Health tracking
        self._health = StreamingHealth()
        
        # Callbacks
        self._partial_callback: Optional[Callable[[StreamingResult], None]] = None
        self._error_callback: Optional[Callable[[str], None]] = None
        
        # Previous chunk for overlap handling
        self._previous_chunk: Optional[AudioChunk] = None
    
    def set_partial_callback(self, callback: Callable[[StreamingResult], None]):
        """Set callback for partial transcription results"""
        self._partial_callback = callback
    
    def set_error_callback(self, callback: Callable[[str], None]):
        """Set callback for error notifications"""
        self._error_callback = callback
    
    def get_client(self):
        """Get or create Groq client"""
        if not self._groq_client and self.api_key:
            self._groq_client = Groq(api_key=self.api_key)
        return self._groq_client
    
    def start(self):
        """Start the streaming worker thread"""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._text_assembler.reset()
            self._health.reset()
            self._previous_chunk = None
            
            self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker_thread.start()
    
    def stop(self):
        """Stop the streaming worker thread"""
        with self._lock:
            self._running = False
            # Add poison pill
            self._task_queue.put((None, None))
        
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)
    
    def is_running(self) -> bool:
        """Check if the worker is running"""
        return self._running
    
    def get_health(self) -> StreamingHealth:
        """Get current health status"""
        return self._health
    
    def is_healthy(self) -> bool:
        """Check if streaming is healthy"""
        return self._health.is_healthy
    
    def in_fallback_mode(self) -> bool:
        """Check if in fallback mode"""
        return self._health.fallback_mode
    
    def queue_chunk(self, chunk: AudioChunk):
        """
        Queue an audio chunk for transcription.
        
        Args:
            chunk: AudioChunk to transcribe
        """
        if not self._running:
            self.start()
        
        self._task_queue.put((chunk, self._previous_chunk))
        self._previous_chunk = chunk
    
    def _worker_loop(self):
        """Background worker loop for processing chunks"""
        while self._running:
            try:
                chunk, prev_chunk = self._task_queue.get(timeout=1.0)
                
                if chunk is None:
                    break
                
                self._process_chunk(chunk, prev_chunk)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}", file=__import__('sys').stderr)
    
    def _process_chunk(self, chunk: AudioChunk, prev_chunk: Optional[AudioChunk]):
        """Process a single audio chunk with retry logic"""
        # Get audio with overlap from previous chunk
        audio_data = chunk.get_audio_with_overlap(prev_chunk)
        
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                result = self._transcribe_audio(audio_data)
                
                if result:
                    # Merge with previous text
                    assembled = self._text_assembler.add_chunk_result(chunk, result)
                    
                    # Record success
                    self._health.record_success()
                    
                    # Call callback
                    streaming_result = StreamingResult(
                        text=assembled,
                        chunk_id=chunk.chunk_id,
                        is_partial=True
                    )
                    
                    if self._partial_callback:
                        try:
                            self._partial_callback(streaming_result)
                        except Exception as e:
                            print(f"Partial callback error: {e}", file=__import__('sys').stderr)
                    
                    return
                else:
                    last_error = "Empty transcription result"
                    
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
        
        # All retries failed
        self._health.record_failure(last_error or "Unknown error")
        
        if self._error_callback:
            try:
                self._error_callback(last_error or "Transcription failed")
            except Exception as e:
                print(f"Error callback error: {e}", file=__import__('sys').stderr)
    
    def _transcribe_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Transcribe audio data using Groq API.
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            Transcription text or None on failure
        """
        if not GROQ_AVAILABLE:
            raise RuntimeError("Groq package not installed or failed to import")
        
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY not set")
        
        client = self.get_client()
        
        # Create temporary file for audio
        fd, temp_path = tempfile.mkstemp(suffix=".wav")
        try:
            os.close(fd)
            
            # Write audio to file
            import soundfile as sf
            sf.write(temp_path, audio_data, 16000)
            
            # Read and transcribe
            with open(temp_path, "rb") as f:
                audio_bytes = f.read()
            
            resp = client.audio.transcriptions.create(
                file=(os.path.basename(temp_path), audio_bytes),
                model=self.model,
                temperature=0,
                response_format="verbose_json",
            )
            
            # Extract text from response
            if hasattr(resp, "text"):
                return resp.text
            if isinstance(resp, dict):
                return resp.get("text") or resp.get("transcription") or str(resp)
            return str(resp)
            
        finally:
            # Clean up temp file
            try:
                os.remove(temp_path)
            except Exception:
                pass
    
    def get_assembled_text(self) -> str:
        """Get the current assembled text from all chunks"""
        return self._text_assembler.get_assembled_text()
    
    def reset(self):
        """Reset the transcriber state"""
        self._text_assembler.reset()
        self._health.reset()
        self._previous_chunk = None


class DualPassTranscriber:
    """
    Combines streaming preview with final accuracy pass.
    
    Provides:
    - Real-time partial results during recording
    - Final high-quality transcription on recording stop
    """
    
    def __init__(self,
                 streaming_transcriber: StreamingTranscriber,
                 final_pass_enabled: bool = True):
        """
        Initialize dual-pass transcriber.
        
        Args:
            streaming_transcriber: StreamingTranscriber instance
            final_pass_enabled: Whether to run final accuracy pass
        """
        self.streaming = streaming_transcriber
        self.final_pass_enabled = final_pass_enabled
        
        self._final_text: Optional[str] = None
        self._partial_text: str = ""
        self._final_callback: Optional[Callable[[str], None]] = None
    
    def set_partial_callback(self, callback: Callable[[StreamingResult], None]):
        """Set callback for partial results"""
        self.streaming.set_partial_callback(self._wrap_partial_callback(callback))
    
    def set_final_callback(self, callback: Callable[[str], None]):
        """Set callback for final transcription result"""
        self._final_callback = callback
    
    def _wrap_partial_callback(self, user_callback: Callable[[StreamingResult], None]):
        """Wrap partial callback to track partial text"""
        def wrapped(result: StreamingResult):
            self._partial_text = result.text
            user_callback(result)
        return wrapped
    
    def start(self):
        """Start streaming transcription"""
        self._final_text = None
        self._partial_text = ""
        self.streaming.start()
    
    def stop(self):
        """Stop streaming transcription"""
        self.streaming.stop()
    
    def queue_chunk(self, chunk: AudioChunk):
        """Queue a chunk for streaming transcription"""
        self.streaming.queue_chunk(chunk)
    
    def get_partial_text(self) -> str:
        """Get current partial transcription text"""
        return self._partial_text
    
    def finalize(self, full_audio: np.ndarray) -> str:
        """
        Perform final transcription pass on complete audio.
        
        Args:
            full_audio: Complete audio recording
            
        Returns:
            Final transcription text
        """
        if not self.final_pass_enabled:
            self._final_text = self._partial_text
            if self._final_callback and self._final_text:
                self._final_callback(self._final_text)
            return self._final_text or ""
        
        # Run final transcription pass
        try:
            final_result = self.streaming._transcribe_audio(full_audio)
            self._final_text = final_result or self._partial_text
        except Exception as e:
            print(f"Final pass error: {e}", file=__import__('sys').stderr)
            self._final_text = self._partial_text
        
        if self._final_callback and self._final_text:
            self._final_callback(self._final_text)
        
        return self._final_text or ""
    
    def get_final_text(self) -> Optional[str]:
        """Get the final transcription if available"""
        return self._final_text
    
    def reset(self):
        """Reset state for new recording"""
        self._final_text = None
        self._partial_text = ""
        self.streaming.reset()


# Example usage
if __name__ == "__main__":
    import time
    
    def on_partial(result: StreamingResult):
        print(f"[Partial] Chunk {result.chunk_id}: {result.text[:50]}...")
    
    def on_error(error: str):
        print(f"[Error] {error}")
    
    # Test streaming transcriber
    print("Testing StreamingTranscriber...")
    
    transcriber = StreamingTranscriber()
    transcriber.set_partial_callback(on_partial)
    transcriber.set_error_callback(on_error)
    
    # Check health
    health = transcriber.get_health()
    print(f"Initial health: healthy={health.is_healthy}, fallback={health.fallback_mode}")
    
    print("\nNote: To test with real audio, ensure GROQ_API_KEY is set.")
