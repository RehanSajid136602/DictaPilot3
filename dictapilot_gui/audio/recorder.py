"""
DictaPilot GUI Audio Recorder
Handles audio recording with WAV output for transcription
"""

import threading
import tempfile
import os
import wave
from typing import Optional, Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np


class RecorderError(Exception):
    """Custom exception for recorder errors"""
    pass


@dataclass
class AudioConfig:
    """Audio configuration"""
    sample_rate: int = 16000
    channels: int = 1
    dtype: str = 'int16'
    blocksize: int = 1024


class AudioRecorder:
    """
    Audio recorder for DictaPilot GUI
    Records audio from microphone and saves to WAV file
    """
    
    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        self.is_recording = False
        self._recording_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._audio_buffer: list = []
        self._buffer_lock = threading.Lock()
        self._temp_file: Optional[str] = None
        
        # Callbacks
        self.on_level_update: Optional[Callable[[float], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        # Try to import sounddevice
        try:
            import sounddevice as sd
            self._sd = sd
        except ImportError:
            raise RecorderError(
                "sounddevice not installed. Run: pip install sounddevice"
            )
    
    def get_audio_devices(self) -> list:
        """Get list of available audio input devices"""
        try:
            devices = self._sd.query_devices()
            input_devices = []
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    input_devices.append({
                        'index': i,
                        'name': dev['name'],
                        'channels': dev['max_input_channels'],
                        'default_samplerate': dev['default_samplerate']
                    })
            return input_devices
        except Exception as e:
            if self.on_error:
                self.on_error(f"Failed to query devices: {e}")
            return []
    
    def start_recording(self, device_index: Optional[int] = None) -> bool:
        """
        Start recording audio
        
        Args:
            device_index: Specific input device index, or None for default
            
        Returns:
            True if recording started successfully
        """
        if self.is_recording:
            return False
        
        try:
            # Check if any input devices are available
            devices = self.get_audio_devices()
            if not devices:
                raise RecorderError("No audio input devices found")
            
            self.is_recording = True
            self._stop_event.clear()
            self._audio_buffer = []
            
            # Start recording in background thread
            self._recording_thread = threading.Thread(
                target=self._record_worker,
                args=(device_index,),
                daemon=True
            )
            self._recording_thread.start()
            return True
            
        except Exception as e:
            self.is_recording = False
            error_msg = str(e)
            if self.on_error:
                self.on_error(error_msg)
            raise RecorderError(f"Failed to start recording: {error_msg}")
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and save to WAV file
        
        Returns:
            Path to saved WAV file, or None if no audio recorded
        """
        if not self.is_recording:
            return None
        
        self.is_recording = False
        self._stop_event.set()
        
        # Wait for recording thread to finish
        if self._recording_thread and self._recording_thread.is_alive():
            self._recording_thread.join(timeout=3.0)
        
        # Save audio buffer to WAV file
        with self._buffer_lock:
            if not self._audio_buffer:
                return None
            
            # Concatenate all audio chunks
            audio_data = np.concatenate(self._audio_buffer, axis=0)
            
            # Create temporary WAV file
            fd, wav_path = tempfile.mkstemp(suffix='.wav')
            os.close(fd)
            
            try:
                with wave.open(wav_path, 'wb') as wf:
                    wf.setnchannels(self.config.channels)
                    wf.setsampwidth(2)  # 16-bit = 2 bytes
                    wf.setframerate(self.config.sample_rate)
                    wf.writeframes(audio_data.tobytes())
                
                self._temp_file = wav_path
                return wav_path
                
            except Exception as e:
                if os.path.exists(wav_path):
                    os.remove(wav_path)
                raise RecorderError(f"Failed to save WAV file: {e}")
    
    def _record_worker(self, device_index: Optional[int]):
        """Background worker for audio recording"""
        try:
            def callback(indata, frames, time_info, status):
                """Called for each audio block"""
                if status:
                    print(f"Audio status: {status}")
                
                # Convert to int16 for WAV
                audio_chunk = (indata * 32767).astype(np.int16)
                
                # Calculate audio level for visualization
                if self.on_level_update:
                    rms = np.sqrt(np.mean(indata**2))
                    self.on_level_update(min(rms * 10, 1.0))  # Normalize to 0-1
                
                # Store in buffer
                with self._buffer_lock:
                    self._audio_buffer.append(audio_chunk.copy())
            
            # Open input stream
            with self._sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype='float32',
                blocksize=self.config.blocksize,
                device=device_index,
                callback=callback
            ):
                # Keep stream open until stopped
                while not self._stop_event.is_set():
                    self._stop_event.wait(0.1)
                    
        except Exception as e:
            self.is_recording = False
            error_msg = str(e)
            if self.on_error:
                self.on_error(f"Recording error: {error_msg}")
            print(f"Recording error: {error_msg}")
    
    def cleanup(self):
        """Clean up temporary files"""
        if self._temp_file and os.path.exists(self._temp_file):
            try:
                os.remove(self._temp_file)
            except OSError:
                pass
            self._temp_file = None
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()