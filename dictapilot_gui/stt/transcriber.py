"""
DictaPilot GUI Speech-to-Text Module
Handles transcription using faster-whisper
"""

import os
import threading
from typing import Optional, Callable, Iterator
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TranscriptionResult:
    """Transcription result"""
    text: str
    language: str
    duration: float
    confidence: float


class Transcriber:
    """
    Speech-to-text transcriber using faster-whisper
    Supports local models with CPU/CUDA inference
    """
    
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        download_root: Optional[str] = None
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.download_root = download_root or str(Path.home() / '.cache' / 'whisper')
        
        self._model = None
        self._lock = threading.Lock()
        self._is_loading = False
        
        # Ensure download directory exists
        Path(self.download_root).mkdir(parents=True, exist_ok=True)
    
    def _load_model(self):
        """Lazy load the whisper model"""
        if self._model is not None:
            return
        
        with self._lock:
            if self._model is not None:
                return
            
            self._is_loading = True
            try:
                from faster_whisper import WhisperModel
                
                # Map model sizes
                model_map = {
                    "tiny": "tiny",
                    "base": "base",
                    "small": "small",
                    "medium": "medium",
                }
                
                model_name = model_map.get(self.model_size, "base")
                
                self._model = WhisperModel(
                    model_name,
                    device=self.device,
                    compute_type=self.compute_type,
                    download_root=self.download_root,
                    cpu=True if self.device == "cpu" else False
                )
            except ImportError:
                raise ImportError(
                    "faster-whisper not installed. "
                    "Run: pip install faster-whisper"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to load model: {e}")
            finally:
                self._is_loading = False
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._model is not None
    
    def is_loading(self) -> bool:
        """Check if model is currently loading"""
        return self._is_loading
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        beam_size: int = 5,
        best_of: int = 5,
        temperature: float = 0.0,
        condition_on_previous_text: bool = True,
        on_progress: Optional[Callable[[str], None]] = None
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            language: Language code (e.g., 'en', 'es') or None for auto-detect
            task: 'transcribe' or 'translate'
            beam_size: Beam size for decoding
            best_of: Number of candidates when sampling
            temperature: Sampling temperature
            condition_on_previous_text: Condition on previous text
            on_progress: Callback for progress updates
            
        Returns:
            TranscriptionResult with text and metadata
        """
        # Load model if needed
        if not self.is_model_loaded():
            if on_progress:
                on_progress("Loading model...")
            self._load_model()
        
        if on_progress:
            on_progress("Transcribing...")
        
        try:
            # Run transcription
            segments, info = self._model.transcribe(
                audio_path,
                language=language if language != "auto" else None,
                task=task,
                beam_size=beam_size,
                best_of=best_of,
                temperature=temperature,
                condition_on_previous_text=condition_on_previous_text,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Collect all segments
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())
                if on_progress:
                    on_progress(f"Transcribing... ({segment.start:.1f}s)")
            
            full_text = " ".join(text_parts).strip()
            
            return TranscriptionResult(
                text=full_text,
                language=info.language or language or "unknown",
                duration=info.duration,
                confidence=getattr(info, 'confidence', 0.0) or 0.0
            )
            
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")
    
    def transcribe_streaming(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Iterator[str]:
        """
        Transcribe with streaming output (yields partial text)
        
        Args:
            audio_path: Path to audio file
            language: Language code or None for auto-detect
            task: 'transcribe' or 'translate'
            
        Yields:
            Partial transcription text as it becomes available
        """
        if not self.is_model_loaded():
            self._load_model()
        
        try:
            segments, info = self._model.transcribe(
                audio_path,
                language=language if language != "auto" else None,
                task=task,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            for segment in segments:
                yield segment.text.strip()
                
        except Exception as e:
            raise RuntimeError(f"Streaming transcription failed: {e}")
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "loaded": self.is_model_loaded(),
            "loading": self.is_loading(),
            "download_root": self.download_root
        }
    
    @staticmethod
    def check_cuda_available() -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    @staticmethod
    def get_compute_types(device: str) -> list:
        """Get available compute types for device"""
        if device == "cpu":
            return ["int8", "int8_float16"]
        else:
            return ["int8_float16", "float16", "int8"]


class TranscriptionWorker(threading.Thread):
    """
    Background worker for transcription
    Allows non-blocking transcription with progress callbacks
    """
    
    def __init__(
        self,
        transcriber: Transcriber,
        audio_path: str,
        language: Optional[str] = None,
        translate: bool = False,
        on_result: Optional[Callable[[TranscriptionResult], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_progress: Optional[Callable[[str], None]] = None
    ):
        super().__init__(daemon=True)
        self.transcriber = transcriber
        self.audio_path = audio_path
        self.language = language
        self.translate = translate
        self.on_result = on_result
        self.on_error = on_error
        self.on_progress = on_progress
        self.result: Optional[TranscriptionResult] = None
        self.error: Optional[str] = None
    
    def run(self):
        """Run transcription in background thread"""
        try:
            task = "translate" if self.translate else "transcribe"
            self.result = self.transcriber.transcribe(
                self.audio_path,
                language=self.language,
                task=task,
                on_progress=self.on_progress
            )
            if self.on_result:
                self.on_result(self.result)
        except Exception as e:
            self.error = str(e)
            if self.on_error:
                self.on_error(self.error)