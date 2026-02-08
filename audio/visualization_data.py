"""
DictaPilot Audio Visualization Data Structures
Ring buffers and data structures for audio visualization

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
from collections import deque
import time
from typing import List, Optional, Tuple, Union


class RingBuffer:
    """
    Circular buffer for storing audio visualization data
    Efficient for continuous audio streaming with fixed-size storage
    """

    def __init__(self, size: int):
        """
        Initialize ring buffer
        size: maximum number of elements to store
        """
        self.size = size
        self.buffer = deque(maxlen=size)
        self.fill_count = 0

    def add(self, value: float):
        """
        Add a value to the buffer
        """
        if len(self.buffer) >= self.size:
            self.buffer.popleft()  # Remove oldest element
        self.buffer.append(value)
        self.fill_count = min(self.fill_count + 1, self.size)

    def get_values(self) -> List[float]:
        """
        Get all values in the buffer (oldest to newest)
        """
        return list(self.buffer)

    def get_recent(self, count: int) -> List[float]:
        """
        Get the most recent values (up to count)
        """
        return list(self.buffer)[-min(count, len(self.buffer)):]

    def clear(self):
        """
        Clear the buffer
        """
        self.buffer.clear()
        self.fill_count = 0

    def is_full(self) -> bool:
        """
        Check if buffer is full
        """
        return len(self.buffer) >= self.size

    def get_averages(self, num_sections: int) -> List[float]:
        """
        Divide the buffer into sections and return average of each section
        Useful for waveform visualization with fewer bars than buffer size
        """
        if len(self.buffer) == 0:
            return [0.0] * num_sections

        values = list(self.buffer)
        section_size = max(1, len(values) // num_sections)
        averages = []

        for i in range(num_sections):
            start_idx = i * section_size
            end_idx = min(start_idx + section_size, len(values))

            if start_idx < len(values):
                section_values = values[start_idx:end_idx]
                avg = sum(section_values) / len(section_values)
                averages.append(avg)
            else:
                averages.append(0.0)

        return averages


class AudioSampleBuffer:
    """
    Buffer specifically designed for audio samples
    Stores raw audio data for visualization processing
    """

    def __init__(self, max_duration: float = 1.0, sample_rate: int = 16000):
        """
        Initialize audio sample buffer
        max_duration: maximum duration in seconds to keep
        sample_rate: sample rate of audio
        """
        self.sample_rate = sample_rate
        self.max_samples = int(max_duration * sample_rate)
        self.buffer = np.zeros(self.max_samples, dtype=np.float32)
        self.write_pos = 0
        self.valid_samples = 0

    def add_samples(self, samples: Union[np.ndarray, list]):
        """
        Add audio samples to the buffer
        """
        if isinstance(samples, list):
            samples = np.array(samples, dtype=np.float32)

        num_new = len(samples)

        # If adding more samples than our capacity, only keep the most recent
        if num_new >= self.max_samples:
            # Take only the last max_samples from the input
            samples = samples[-self.max_samples:]
            num_new = len(samples)
            self.buffer[:num_new] = samples
            self.write_pos = num_new
            self.valid_samples = num_new
            return

        # Check if we need to wrap around
        if self.write_pos + num_new <= self.max_samples:
            # No wrap-around needed
            self.buffer[self.write_pos:self.write_pos + num_new] = samples
        else:
            # Wrap-around needed
            first_part = self.max_samples - self.write_pos
            self.buffer[self.write_pos:] = samples[:first_part]
            self.buffer[:num_new - first_part] = samples[first_part:]

        self.write_pos = (self.write_pos + num_new) % self.max_samples
        self.valid_samples = min(self.valid_samples + num_new, self.max_samples)

    def get_recent_samples(self, num_samples: int) -> np.ndarray:
        """
        Get the most recent audio samples
        """
        num_samples = min(num_samples, self.valid_samples, self.max_samples)
        if num_samples <= 0:
            return np.array([], dtype=np.float32)

        # Calculate the starting position
        start_pos = (self.write_pos - num_samples) % self.max_samples

        if start_pos + num_samples <= self.max_samples:
            # No wrap-around in the requested range
            return np.copy(self.buffer[start_pos:start_pos + num_samples])
        else:
            # Wrap-around in the requested range
            first_part = self.buffer[start_pos:]
            second_part = self.buffer[:num_samples - len(first_part)]
            return np.concatenate([first_part, second_part])

    def get_rms_values(self, window_size: int = 100, hop_size: int = 50) -> List[float]:
        """
        Calculate RMS values for visualization windows
        window_size: number of samples per window
        hop_size: number of samples between windows
        """
        if self.valid_samples < window_size:
            return []

        samples = self.get_recent_samples(self.valid_samples)
        rms_values = []

        for i in range(0, len(samples) - window_size, hop_size):
            window = samples[i:i + window_size]
            rms = np.sqrt(np.mean(window ** 2))
            rms_values.append(float(rms))

        return rms_values

    def clear(self):
        """
        Clear the buffer
        """
        self.buffer.fill(0.0)
        self.write_pos = 0
        self.valid_samples = 0


class TimeStampedDataBuffer:
    """
    Buffer that stores data with timestamps
    Useful for synchronized visualization of audio levels
    """

    def __init__(self, max_age: float = 5.0):
        """
        Initialize time-stamped buffer
        max_age: maximum age of data to keep in seconds
        """
        self.data = deque()  # Each entry: (timestamp, value)
        self.max_age = max_age

    def add(self, value: float, timestamp: Optional[float] = None):
        """
        Add a value with timestamp
        """
        if timestamp is None:
            timestamp = time.time()

        self.data.append((timestamp, value))
        self._prune_old_data()

    def get_recent(self, max_age: float = 2.0) -> List[Tuple[float, float]]:
        """
        Get recent data within max_age seconds
        Returns list of (timestamp, value) tuples
        """
        current_time = time.time()
        recent_data = []

        for ts, val in reversed(self.data):  # Iterate backwards for efficiency
            if current_time - ts <= max_age:
                recent_data.append((ts, val))
            else:
                break

        return list(reversed(recent_data))  # Reverse back to chronological order

    def get_latest_value(self) -> Optional[float]:
        """
        Get the most recent value
        """
        if self.data:
            return self.data[-1][1]
        return None

    def get_average_in_range(self, time_range: float = 1.0) -> float:
        """
        Get average of values in the specified time range
        """
        recent_data = self.get_recent(time_range)
        if not recent_data:
            return 0.0

        values = [val for _, val in recent_data]
        return sum(values) / len(values)

    def _prune_old_data(self):
        """
        Remove data older than max_age
        """
        current_time = time.time()
        while self.data and current_time - self.data[0][0] > self.max_age:
            self.data.popleft()

    def clear(self):
        """
        Clear the buffer
        """
        self.data.clear()


class LevelHistory:
    """
    Track historical audio levels for visualization
    Maintains min/max/average over time periods
    """

    def __init__(self, max_duration: float = 10.0, resolution: float = 0.1):
        """
        Initialize level history
        max_duration: maximum history duration in seconds
        resolution: time resolution in seconds
        """
        self.max_duration = max_duration
        self.resolution = resolution
        self.max_points = int(max_duration / resolution)

        self.timestamps = deque(maxlen=self.max_points)
        self.levels = deque(maxlen=self.max_points)
        self.peak_levels = deque(maxlen=self.max_points)
        self.rms_levels = deque(maxlen=self.max_points)

    def add_level(self, level: float, peak: float, rms: float, timestamp: Optional[float] = None):
        """
        Add a new level reading
        """
        if timestamp is None:
            timestamp = time.time()

        self.timestamps.append(timestamp)
        self.levels.append(level)
        self.peak_levels.append(peak)
        self.rms_levels.append(rms)

    def get_levels_in_range(self, duration: float = 5.0) -> Tuple[List[float], List[float], List[float]]:
        """
        Get level history for the specified duration
        Returns (levels, peaks, rms) lists
        """
        if not self.timestamps:
            return [], [], []

        current_time = time.time()
        start_time = current_time - duration

        levels = []
        peaks = []
        rms_values = []

        for i, ts in enumerate(self.timestamps):
            if ts >= start_time:
                levels.append(self.levels[i])
                peaks.append(self.peak_levels[i])
                rms_values.append(self.rms_levels[i])

        return levels, peaks, rms_values

    def get_average_level(self, duration: float = 1.0) -> Tuple[float, float, float]:
        """
        Get average levels over the specified duration
        Returns (avg_level, avg_peak, avg_rms)
        """
        levels, peaks, rms_values = self.get_levels_in_range(duration)

        if not levels:
            return 0.0, 0.0, 0.0

        avg_level = sum(levels) / len(levels)
        avg_peak = sum(peaks) / len(peaks)
        avg_rms = sum(rms_values) / len(rms_values)

        return avg_level, avg_peak, avg_rms

    def clear(self):
        """
        Clear all history
        """
        self.timestamps.clear()
        self.levels.clear()
        self.peak_levels.clear()
        self.rms_levels.clear()


# Example usage and testing:
if __name__ == "__main__":
    import time as time_module

    # Test RingBuffer
    print("Testing RingBuffer...")
    rb = RingBuffer(size=10)
    for i in range(15):  # Add more than capacity
        rb.add(i * 0.1)

    print(f"Values: {rb.get_values()}")
    print(f"Recent 5: {rb.get_recent(5)}")
    print(f"Averages (5 sections): {rb.get_averages(5)}")

    # Test AudioSampleBuffer
    print("\nTesting AudioSampleBuffer...")
    asb = AudioSampleBuffer(max_duration=0.5, sample_rate=16000)  # 0.5 seconds buffer

    # Add some test samples
    test_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, int(16000 * 0.1)))
    asb.add_samples(test_signal)

    recent = asb.get_recent_samples(1000)
    print(f"Recent samples shape: {recent.shape}")
    print(f"RMS values: {asb.get_rms_values(window_size=100, hop_size=50)[:5]}")  # First 5 values

    # Test TimeStampedDataBuffer
    print("\nTesting TimeStampedDataBuffer...")
    tsdb = TimeStampedDataBuffer(max_age=2.0)

    for i in range(5):
        tsdb.add(i * 0.2)
        time_module.sleep(0.1)  # Small delay between additions

    recent_data = tsdb.get_recent(1.0)
    print(f"Recent data: {[(t, round(v, 2)) for t, v in recent_data]}")
    print(f"Latest value: {tsdb.get_latest_value()}")
    print(f"Average in 1s: {tsdb.get_average_in_range(1.0):.2f}")

    # Test LevelHistory
    print("\nTesting LevelHistory...")
    lh = LevelHistory(max_duration=5.0, resolution=0.5)

    for i in range(10):
        lh.add_level(i * 0.1, i * 0.12, i * 0.08)
        time_module.sleep(0.1)

    levels, peaks, rms = lh.get_levels_in_range(3.0)
    print(f"Levels in 3s: {len(levels)} points")
    print(f"Average (1s): {lh.get_average_level(1.0)}")