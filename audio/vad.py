"""
DictaPilot Voice Activity Detection
Simple threshold-based voice activity detection

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

import numpy as np
from typing import List, Optional


class VoiceActivityDetector:
    """
    Simple threshold-based Voice Activity Detection
    Monitors audio chunks to detect speech vs silence
    """

    def __init__(self,
                 sample_rate: int = 16000,
                 silence_threshold: float = 0.02,  # Default threshold from original code
                 speech_frames_threshold: int = 3,  # Number of consecutive frames to confirm speech
                 silence_frames_threshold: int = 10):  # Number of consecutive frames to confirm silence):

        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.speech_frames_threshold = speech_frames_threshold
        self.silence_frames_threshold = silence_frames_threshold

        # State tracking
        self.is_speech_active = False
        self.silence_frame_count = 0
        self.speech_frame_count = 0
        self.current_rms = 0.0

        # Adaptive threshold variables
        self.adaptive_threshold = silence_threshold
        self.threshold_learning_rate = 0.01
        self.rms_history: List[float] = []

    def process_chunk(self, audio_chunk: np.ndarray):
        """
        Process an audio chunk and update VAD state
        """
        # Calculate RMS of the chunk
        rms = np.sqrt(np.mean(audio_chunk**2))
        self.current_rms = float(rms)

        # Update RMS history (last 100 samples)
        self.rms_history.append(self.current_rms)
        if len(self.rms_history) > 100:
            self.rms_history.pop(0)

        # Adaptive threshold adjustment
        if self.rms_history:
            # Use percentile to adjust threshold based on recent activity
            quiet_rms = np.percentile(self.rms_history, 20)  # 20th percentile as quiet baseline
            self.adaptive_threshold = max(
                self.silence_threshold,  # Don't go below configured threshold
                quiet_rms * 2.0  # Double the quiet baseline
            )

        # Update state based on current RMS
        is_speech_detected = self.current_rms > self.adaptive_threshold

        if is_speech_detected:
            self.speech_frame_count += 1
            self.silence_frame_count = max(0, self.silence_frame_count - 1)  # Hysteresis
        else:
            self.silence_frame_count += 1
            self.speech_frame_count = max(0, self.speech_frame_count - 1)  # Hysteresis

        # Update speech state with hysteresis
        if not self.is_speech_active and self.speech_frame_count >= self.speech_frames_threshold:
            self.is_speech_active = True
        elif self.is_speech_active and self.silence_frame_count >= self.silence_frames_threshold:
            self.is_speech_active = False

    def is_speech_active(self) -> bool:
        """Check if speech is currently detected"""
        return self.is_speech_active

    def get_current_rms(self) -> float:
        """Get the current RMS value"""
        return self.current_rms

    def get_adaptive_threshold(self) -> float:
        """Get the current adaptive threshold"""
        return self.adaptive_threshold

    def reset(self):
        """Reset the VAD state"""
        self.is_speech_active = False
        self.silence_frame_count = 0
        self.speech_frame_count = 0
        self.current_rms = 0.0
        self.adaptive_threshold = self.silence_threshold
        self.rms_history = []

    def update_threshold(self, new_threshold: float):
        """Manually update the silence threshold"""
        self.silence_threshold = new_threshold
        self.adaptive_threshold = new_threshold


class AdvancedVoiceActivityDetector(VoiceActivityDetector):
    """
    Enhanced VAD with multiple detection methods
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Additional detection parameters
        self.energy_ratio_threshold = 0.7  # Ratio of energy in high freq vs low freq
        self.spectral_features = []

    def process_chunk_advanced(self, audio_chunk: np.ndarray):
        """
        Process an audio chunk with advanced features
        """
        # Process with base method first
        self.process_chunk(audio_chunk)

        # Additional spectral features for advanced detection
        self._analyze_spectral_features(audio_chunk)

    def _analyze_spectral_features(self, audio_chunk: np.ndarray):
        """
        Analyze spectral characteristics for advanced VAD
        """
        # Simple spectral centroid calculation
        if len(audio_chunk) > 0:
            # Calculate FFT
            fft = np.fft.rfft(audio_chunk.flatten())
            magnitude = np.abs(fft)

            # Spectral centroid - center of mass of spectrum
            frequencies = np.fft.rfftfreq(len(audio_chunk), d=1/self.sample_rate)
            if len(frequencies) > 1:
                spectral_centroid = np.sum(frequencies * magnitude) / np.sum(magnitude)

                # Store for trend analysis
                self.spectral_features.append(spectral_centroid)
                if len(self.spectral_features) > 50:
                    self.spectral_features.pop(0)

    def get_voice_confidence(self) -> float:
        """
        Estimate confidence that current audio contains voice
        """
        # Base confidence on RMS level relative to threshold
        if self.adaptive_threshold > 0:
            confidence = min(1.0, self.current_rms / (self.adaptive_threshold * 2.0))
        else:
            confidence = 0.0

        # Adjust based on spectral characteristics if available
        if self.spectral_features and len(self.spectral_features) > 10:
            avg_centroid = np.mean(self.spectral_features[-10:])
            # Human voice typically has spectral centroid in certain range
            if 100 < avg_centroid < 3000:  # Typical human voice frequency range
                confidence = min(1.0, confidence * 1.2)  # Boost confidence

        return max(0.0, min(1.0, confidence))


# Example usage:
if __name__ == "__main__":
    import sounddevice as sd
    import time

    vad = VoiceActivityDetector(sample_rate=16000)

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"Status: {status}")

        vad.process_chunk(indata)
        print(f"\rRMS: {vad.get_current_rms():.3f}, Threshold: {vad.get_adaptive_threshold():.3f}, "
              f"Speech: {'YES' if vad.is_speech_active() else 'NO '}", end="", flush=True)

    print("Starting audio monitoring with VAD...")
    print("Speak to test voice detection")

    # Start recording to test VAD
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=16000, blocksize=1600):
        time.sleep(10)  # Monitor for 10 seconds

    print("\nMonitoring complete")