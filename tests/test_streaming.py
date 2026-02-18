"""
Tests for streaming transcription functionality
"""

import pytest
import numpy as np
import time
import threading

from audio_buffer import ChunkedAudioBuffer, AudioChunk, TextAssembler
from streaming_transcriber import StreamingTranscriber, StreamingHealth, StreamingResult


class TestChunkedAudioBuffer:
    """Tests for ChunkedAudioBuffer class"""
    
    def test_buffer_initialization(self):
        """Test buffer initializes with correct settings"""
        buffer = ChunkedAudioBuffer(
            sample_rate=16000,
            chunk_duration=1.0,
            chunk_overlap=0.2,
            min_chunks=2
        )
        
        assert buffer.sample_rate == 16000
        assert buffer.chunk_duration == 1.0
        assert buffer.chunk_overlap == 0.2
        assert buffer.min_chunks == 2
        assert buffer.chunk_samples == 16000
        assert buffer.overlap_samples == 3200
    
    def test_add_audio_accumulates(self):
        """Test that audio is accumulated in buffer"""
        buffer = ChunkedAudioBuffer(sample_rate=16000, chunk_duration=0.5, min_chunks=1)
        buffer.start_recording()
        
        # Add 0.5 seconds of audio
        audio = np.random.randn(8000, 1).astype(np.float32) * 0.1
        buffer.add_audio(audio)
        
        assert buffer.get_duration() == pytest.approx(0.5, rel=0.01)
    
    def test_chunk_creation(self):
        """Test that chunks are created when enough audio accumulates"""
        buffer = ChunkedAudioBuffer(
            sample_rate=16000,
            chunk_duration=0.5,
            chunk_overlap=0.1,
            min_chunks=1
        )
        
        chunks_created = []
        buffer.set_chunk_callback(lambda chunk: chunks_created.append(chunk))
        buffer.start_recording()
        
        # Add 1 second of audio (should create 2 chunks)
        for _ in range(2):
            audio = np.random.randn(8000, 1).astype(np.float32) * 0.1
            buffer.add_audio(audio)
        
        # Wait a bit for processing
        time.sleep(0.1)
        
        assert len(chunks_created) >= 1
        assert chunks_created[0].sample_count == 8000  # 0.5 seconds at 16kHz
    
    def test_get_full_audio(self):
        """Test that full audio can be retrieved"""
        buffer = ChunkedAudioBuffer(sample_rate=16000, chunk_duration=0.5)
        buffer.start_recording()
        
        # Add 1 second of audio
        audio1 = np.random.randn(8000, 1).astype(np.float32) * 0.1
        audio2 = np.random.randn(8000, 1).astype(np.float32) * 0.1
        buffer.add_audio(audio1)
        buffer.add_audio(audio2)
        
        full_audio = buffer.get_full_audio()
        assert full_audio is not None
        assert len(full_audio) == 16000  # 1 second at 16kHz
    
    def test_finalize_returns_remaining(self):
        """Test that finalize returns full audio and remaining chunks"""
        buffer = ChunkedAudioBuffer(sample_rate=16000, chunk_duration=0.5)
        buffer.start_recording()
        
        # Add audio
        audio = np.random.randn(8000, 1).astype(np.float32) * 0.1
        buffer.add_audio(audio)
        
        full_audio, remaining = buffer.finalize()
        assert full_audio is not None
        assert len(full_audio) == 8000
    
    def test_reset_clears_buffer(self):
        """Test that reset clears the buffer"""
        buffer = ChunkedAudioBuffer(sample_rate=16000)
        buffer.start_recording()
        
        audio = np.random.randn(8000, 1).astype(np.float32) * 0.1
        buffer.add_audio(audio)
        
        assert buffer.get_duration() > 0
        
        buffer.reset()
        assert buffer.get_duration() == 0


class TestTextAssembler:
    """Tests for TextAssembler class"""
    
    def test_first_chunk(self):
        """Test that first chunk is used as-is"""
        assembler = TextAssembler()
        chunk = AudioChunk(np.array([]), 0, 0.0, 1.0, 0.2)
        
        result = assembler.add_chunk_result(chunk, "Hello world")
        assert result == "Hello world"
    
    def test_merge_overlapping_text(self):
        """Test that overlapping text is merged correctly"""
        assembler = TextAssembler()
        
        chunk1 = AudioChunk(np.array([]), 0, 0.0, 1.0, 0.2)
        result1 = assembler.add_chunk_result(chunk1, "Hello world this")
        
        chunk2 = AudioChunk(np.array([]), 1, 1.0, 1.0, 0.2)
        result2 = assembler.add_chunk_result(chunk2, "this is a test")
        
        # Should merge at "this"
        assert "this is a test" in result2
        assert result2.startswith("Hello world")
    
    def test_separate_sentences(self):
        """Test that non-overlapping text is appended"""
        assembler = TextAssembler()
        
        chunk1 = AudioChunk(np.array([]), 0, 0.0, 1.0, 0.0)
        result1 = assembler.add_chunk_result(chunk1, "Hello world")
        
        chunk2 = AudioChunk(np.array([]), 1, 1.0, 1.0, 0.0)
        result2 = assembler.add_chunk_result(chunk2, "Goodbye world")
        
        # Should just append
        assert "Hello world" in result2
        assert "Goodbye world" in result2
    
    def test_reset_clears_state(self):
        """Test that reset clears assembler state"""
        assembler = TextAssembler()
        
        chunk = AudioChunk(np.array([]), 0, 0.0, 1.0, 0.2)
        assembler.add_chunk_result(chunk, "Hello world")
        
        assert assembler.get_assembled_text() == "Hello world"
        
        assembler.reset()
        assert assembler.get_assembled_text() == ""


class TestStreamingHealth:
    """Tests for StreamingHealth class"""
    
    def test_initial_state(self):
        """Test initial health state"""
        health = StreamingHealth()
        assert health.is_healthy
        assert not health.fallback_mode
        assert health.consecutive_failures == 0
    
    def test_record_success(self):
        """Test recording successful transcription"""
        health = StreamingHealth()
        health.record_success()
        
        assert health.successful_chunks == 1
        assert health.consecutive_failures == 0
        assert health.is_healthy
    
    def test_record_failure(self):
        """Test recording failed transcription"""
        health = StreamingHealth()
        health.record_failure("Test error")
        
        assert health.failed_chunks == 1
        assert health.consecutive_failures == 1
        assert health.last_error == "Test error"
        assert health.is_healthy  # Not yet in fallback
    
    def test_fallback_after_three_failures(self):
        """Test that fallback mode activates after 3 failures"""
        health = StreamingHealth()
        
        health.record_failure("Error 1")
        health.record_failure("Error 2")
        health.record_failure("Error 3")
        
        assert health.consecutive_failures == 3
        assert not health.is_healthy
        assert health.fallback_mode
    
    def test_success_resets_consecutive_failures(self):
        """Test that success resets consecutive failure count"""
        health = StreamingHealth()
        
        health.record_failure("Error 1")
        health.record_failure("Error 2")
        health.record_success()
        
        assert health.consecutive_failures == 0
        assert health.is_healthy
    
    def test_reset_clears_state(self):
        """Test that reset clears health state"""
        health = StreamingHealth()
        
        health.record_failure("Error")
        health.record_failure("Error")
        health.record_failure("Error")
        
        assert health.fallback_mode
        
        health.reset()
        
        assert health.is_healthy
        assert not health.fallback_mode
        assert health.consecutive_failures == 0


class TestAudioChunk:
    """Tests for AudioChunk class"""
    
    def test_chunk_properties(self):
        """Test chunk property values"""
        audio = np.random.randn(16000, 1).astype(np.float32)
        chunk = AudioChunk(
            audio_data=audio,
            chunk_id=0,
            start_time=0.0,
            duration=1.0,
            overlap=0.2
        )
        
        assert chunk.chunk_id == 0
        assert chunk.duration == 1.0
        assert chunk.overlap == 0.2
        assert chunk.sample_count == 16000
        assert chunk.transcription is None
        assert chunk.error is None
    
    def test_get_audio_with_overlap(self):
        """Test getting audio with overlap from previous chunk"""
        audio1 = np.ones((16000, 1), dtype=np.float32)
        chunk1 = AudioChunk(audio1, 0, 0.0, 1.0, 0.2)
        
        audio2 = np.ones((16000, 1), dtype=np.float32) * 2
        chunk2 = AudioChunk(audio2, 1, 1.0, 1.0, 0.2)
        
        result = chunk2.get_audio_with_overlap(chunk1)
        
        # Should have overlap samples + full chunk
        expected_overlap = int(0.2 * 16000)  # 3200 samples
        assert len(result) == 16000 + expected_overlap


class TestStreamingResult:
    """Tests for StreamingResult dataclass"""
    
    def test_partial_result(self):
        """Test creating partial result"""
        result = StreamingResult(
            text="Hello world",
            chunk_id=0,
            is_partial=True
        )
        
        assert result.text == "Hello world"
        assert result.chunk_id == 0
        assert result.is_partial
        assert result.error is None
    
    def test_error_result(self):
        """Test creating error result"""
        result = StreamingResult(
            text="",
            chunk_id=0,
            is_partial=True,
            error="Transcription failed"
        )
        
        assert result.error == "Transcription failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
