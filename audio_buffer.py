"""
DictaPilot Audio Buffer Module
Chunked audio buffer with overlap for streaming transcription

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

import threading
import queue
import time
from typing import Optional, Callable, List, Tuple
import numpy as np


class AudioChunk:
    """Represents a single audio chunk for streaming transcription"""
    
    def __init__(self, audio_data: np.ndarray, chunk_id: int, 
                 start_time: float, duration: float, overlap: float = 0.0):
        self.audio_data = audio_data
        self.chunk_id = chunk_id
        self.start_time = start_time
        self.duration = duration
        self.overlap = overlap
        self.transcription: Optional[str] = None
        self.error: Optional[str] = None
        self.timestamp = time.time()
    
    @property
    def sample_count(self) -> int:
        return len(self.audio_data)
    
    def get_audio_with_overlap(self, previous_chunk: Optional['AudioChunk'] = None) -> np.ndarray:
        """Get audio data including overlap from previous chunk"""
        if previous_chunk is None or self.overlap <= 0:
            return self.audio_data
        
        overlap_samples = int(self.overlap * len(self.audio_data) / self.duration)
        if overlap_samples <= 0:
            return self.audio_data
        
        # Take the end of the previous chunk
        prev_overlap = previous_chunk.audio_data[-overlap_samples:]
        return np.concatenate([prev_overlap, self.audio_data])


class ChunkedAudioBuffer:
    """
    Audio buffer that accumulates audio and creates chunks for streaming transcription.
    
    Features:
    - Fixed-size chunks with configurable overlap
    - Queue management for streaming processing
    - Full audio accumulation for final pass
    """
    
    def __init__(self,
                 sample_rate: int = 16000,
                 channels: int = 1,
                 chunk_duration: float = 1.5,
                 chunk_overlap: float = 0.3,
                 min_chunks: int = 2):
        """
        Initialize the chunked audio buffer.
        
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels
            chunk_duration: Duration of each chunk in seconds
            chunk_overlap: Overlap between consecutive chunks in seconds
            min_chunks: Minimum chunks before emitting first result
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration = chunk_duration
        self.chunk_overlap = chunk_overlap
        self.min_chunks = min_chunks
        
        # Chunk size in samples
        self.chunk_samples = int(sample_rate * chunk_duration)
        self.overlap_samples = int(sample_rate * chunk_overlap)
        
        # Audio buffers
        self._full_buffer: List[np.ndarray] = []
        self._chunk_buffer: List[np.ndarray] = []
        self._buffer_lock = threading.RLock()
        
        # Chunk queue for streaming
        self._chunk_queue: queue.Queue = queue.Queue()
        
        # Chunk tracking
        self._chunk_counter = 0
        self._chunks_created = 0
        self._recording_start_time = 0.0
        
        # Callbacks
        self._chunk_callback: Optional[Callable[[AudioChunk], None]] = None
    
    def set_chunk_callback(self, callback: Callable[[AudioChunk], None]):
        """Set callback to be invoked when a new chunk is ready"""
        self._chunk_callback = callback
    
    def start_recording(self):
        """Reset buffer state for a new recording session"""
        with self._buffer_lock:
            self._full_buffer = []
            self._chunk_buffer = []
            self._chunk_counter = 0
            self._chunks_created = 0
            self._recording_start_time = time.time()
            
            # Clear the queue
            while not self._chunk_queue.empty():
                try:
                    self._chunk_queue.get_nowait()
                except queue.Empty:
                    break
    
    def add_audio(self, audio_data: np.ndarray):
        """
        Add audio data to the buffer.
        
        Args:
            audio_data: Audio samples as numpy array (shape: [samples, channels] or [samples])
        """
        with self._buffer_lock:
            # Add to full buffer for final pass
            self._full_buffer.append(audio_data.copy())
            
            # Add to chunk buffer
            self._chunk_buffer.append(audio_data.copy())
            
            # Check if we have enough for a new chunk
            self._try_create_chunk()
    
    def _try_create_chunk(self):
        """Create a new chunk if enough audio has accumulated"""
        if not self._chunk_buffer:
            return
        
        # Concatenate all audio in chunk buffer
        all_audio = np.concatenate(self._chunk_buffer, axis=0)
        total_samples = len(all_audio)
        
        # Need at least chunk_samples for a new chunk
        if total_samples < self.chunk_samples:
            return
        
        # Create chunk from the beginning
        chunk_audio = all_audio[:self.chunk_samples]
        
        # Calculate timing
        start_time = self._recording_start_time + (self._chunk_counter * 
                    (self.chunk_duration - self.chunk_overlap))
        
        # Create chunk object
        chunk = AudioChunk(
            audio_data=chunk_audio,
            chunk_id=self._chunk_counter,
            start_time=start_time,
            duration=self.chunk_duration,
            overlap=self.chunk_overlap
        )
        
        self._chunk_counter += 1
        self._chunks_created += 1
        
        # Add to queue
        self._chunk_queue.put(chunk)
        
        # Call callback if set
        if self._chunk_callback:
            try:
                self._chunk_callback(chunk)
            except Exception as e:
                print(f"Chunk callback error: {e}", file=__import__('sys').stderr)
        
        # Keep overlap amount of audio for next chunk
        keep_samples = self.overlap_samples
        if total_samples > self.chunk_samples:
            remaining = all_audio[self.chunk_samples - keep_samples:]
            self._chunk_buffer = [remaining]
        else:
            # Reset with just the overlap portion
            overlap_audio = all_audio[-keep_samples:] if keep_samples > 0 else np.array([])
            self._chunk_buffer = [overlap_audio] if len(overlap_audio) > 0 else []
    
    def get_pending_chunk(self, timeout: float = 0.1) -> Optional[AudioChunk]:
        """
        Get the next pending chunk from the queue.
        
        Args:
            timeout: Maximum time to wait for a chunk
            
        Returns:
            AudioChunk if available, None otherwise
        """
        try:
            return self._chunk_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def has_pending_chunks(self) -> bool:
        """Check if there are pending chunks in the queue"""
        return not self._chunk_queue.empty()
    
    def get_chunks_created(self) -> int:
        """Get the number of chunks created so far"""
        return self._chunks_created
    
    def has_minimum_chunks(self) -> bool:
        """Check if minimum number of chunks have been created for first result"""
        return self._chunks_created >= self.min_chunks
    
    def get_full_audio(self) -> Optional[np.ndarray]:
        """
        Get the complete audio buffer for final transcription.
        
        Returns:
            Concatenated audio as numpy array, or None if no audio
        """
        with self._buffer_lock:
            if not self._full_buffer:
                return None
            return np.concatenate(self._full_buffer, axis=0)
    
    def get_duration(self) -> float:
        """Get the total duration of recorded audio in seconds"""
        with self._buffer_lock:
            if not self._full_buffer:
                return 0.0
            total_samples = sum(len(chunk) for chunk in self._full_buffer)
            return total_samples / self.sample_rate
    
    def finalize(self) -> Tuple[Optional[np.ndarray], List[AudioChunk]]:
        """
        Finalize the recording and get all remaining data.
        
        Returns:
            Tuple of (full_audio, remaining_chunks)
        """
        # Create a final chunk with remaining audio if significant
        remaining_chunks = []
        
        with self._buffer_lock:
            if self._chunk_buffer:
                remaining_audio = np.concatenate(self._chunk_buffer, axis=0)
                # Only create chunk if at least 0.5 seconds of audio
                if len(remaining_audio) >= self.sample_rate * 0.5:
                    start_time = self._recording_start_time + (self._chunk_counter * 
                                (self.chunk_duration - self.chunk_overlap))
                    
                    final_chunk = AudioChunk(
                        audio_data=remaining_audio,
                        chunk_id=self._chunk_counter,
                        start_time=start_time,
                        duration=len(remaining_audio) / self.sample_rate,
                        overlap=0.0  # No overlap for final chunk
                    )
                    remaining_chunks.append(final_chunk)
        
        # Get any remaining queued chunks
        while not self._chunk_queue.empty():
            try:
                chunk = self._chunk_queue.get_nowait()
                remaining_chunks.append(chunk)
            except queue.Empty:
                break
        
        return self.get_full_audio(), remaining_chunks
    
    def reset(self):
        """Reset the buffer completely"""
        self.start_recording()


class TextAssembler:
    """
    Assembles coherent text from overlapping chunk transcriptions.
    """
    
    def __init__(self, overlap_duration: float = 0.3):
        self.overlap_duration = overlap_duration
        self._previous_text: Optional[str] = None
        self._assembled_text: str = ""
    
    def add_chunk_result(self, chunk: AudioChunk, transcription: str) -> str:
        """
        Add a chunk transcription and return the assembled text.
        
        Args:
            chunk: The audio chunk that was transcribed
            transcription: The transcription result
            
        Returns:
            The current assembled text
        """
        if not transcription or not transcription.strip():
            return self._assembled_text
        
        transcription = transcription.strip()
        
        if self._previous_text is None:
            # First chunk - use as-is
            self._assembled_text = transcription
        else:
            # Try to merge with overlap handling
            self._assembled_text = self._merge_texts(
                self._assembled_text, 
                transcription, 
                chunk.overlap
            )
        
        self._previous_text = transcription
        return self._assembled_text
    
    def _merge_texts(self, previous: str, new: str, overlap: float) -> str:
        """
        Merge two transcriptions handling overlap.
        
        Strategy: Find common suffix/prefix and merge at that point.
        """
        if not previous:
            return new
        if not new:
            return previous
        
        # Normalize whitespace
        prev_words = previous.split()
        new_words = new.split()
        
        if not prev_words:
            return new
        if not new_words:
            return previous
        
        # Look for common sequence at the boundary
        # Try to find the longest matching suffix/prefix
        best_overlap = 0
        
        # Check for word-level overlap
        for length in range(1, min(len(prev_words), len(new_words)) + 1):
            if prev_words[-length:] == new_words[:length]:
                best_overlap = length
        
        if best_overlap > 0:
            # Found overlap - merge at that point
            merged = prev_words + new_words[best_overlap:]
            return " ".join(merged)
        
        # No exact overlap found - try fuzzy matching on last/first words
        # Check if last word of previous is prefix of first word of new
        if prev_words and new_words:
            last_word = prev_words[-1].lower().strip(".,!?;:")
            first_word = new_words[0].lower().strip(".,!?;:")
            
            # If words share a significant prefix, the new word might be more complete
            if last_word and first_word and len(last_word) >= 3:
                if first_word.startswith(last_word) or last_word.startswith(first_word):
                    # Keep the longer word and merge
                    longer_word = prev_words[-1] if len(prev_words[-1]) >= len(new_words[0]) else new_words[0]
                    merged = prev_words[:-1] + [longer_word] + new_words[1:]
                    return " ".join(merged)
        
        # No overlap detected - append with space
        # This might indicate gap in transcription or new sentence
        return previous + " " + new
    
    def get_assembled_text(self) -> str:
        """Get the current assembled text"""
        return self._assembled_text
    
    def reset(self):
        """Reset the assembler state"""
        self._previous_text = None
        self._assembled_text = ""


# Example usage and testing
if __name__ == "__main__":
    import time
    
    # Test the chunked buffer
    buffer = ChunkedAudioBuffer(
        sample_rate=16000,
        chunk_duration=1.0,
        chunk_overlap=0.2,
        min_chunks=1
    )
    
    def on_chunk(chunk: AudioChunk):
        print(f"Chunk {chunk.chunk_id}: {chunk.sample_count} samples, {chunk.duration:.2f}s")
    
    buffer.set_chunk_callback(on_chunk)
    buffer.start_recording()
    
    # Simulate adding audio in 0.5s chunks
    print("Simulating audio recording...")
    for i in range(10):
        # 0.5 seconds of audio at 16kHz = 8000 samples
        audio = np.random.randn(8000, 1).astype(np.float32) * 0.1
        buffer.add_audio(audio)
        time.sleep(0.1)
        print(f"  Added chunk {i+1}, total duration: {buffer.get_duration():.2f}s")
    
    print(f"\nTotal chunks created: {buffer.get_chunks_created()}")
    
    # Finalize
    full_audio, remaining = buffer.finalize()
    if full_audio is not None:
        print(f"Full audio: {len(full_audio)} samples, {len(full_audio)/16000:.2f}s")
    
    # Test text assembler
    print("\n--- Testing Text Assembler ---")
    assembler = TextAssembler()
    
    test_chunks = [
        "Hello world this is",
        "is a test of the",
        "the streaming transcription",
    ]
    
    for i, text in enumerate(test_chunks):
        chunk = AudioChunk(np.array([]), i, 0.0, 1.0, 0.2)
        result = assembler.add_chunk_result(chunk, text)
        print(f"  After chunk {i}: '{result}'")
    
    print(f"\nFinal assembled text: '{assembler.get_assembled_text()}'")
