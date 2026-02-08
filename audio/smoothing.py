"""
DictaPilot Audio Smoothing Algorithms
Various smoothing and averaging techniques for audio level processing

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


class ExponentialMovingAverage:
    """
    Exponential Moving Average (EMA) for smoothing audio levels
    Provides smooth transitions between values
    """

    def __init__(self, alpha=0.1):
        """
        Initialize EMA with smoothing factor
        alpha: smoothing factor (0.0 to 1.0), lower = smoother
        """
        self.alpha = max(0.01, min(0.99, alpha))  # Clamp to reasonable range
        self.value = 0.0
        self.initialized = False

    def update(self, new_value):
        """
        Update the EMA with a new value
        """
        if not self.initialized:
            self.value = new_value
            self.initialized = True
        else:
            # EMA formula: newValue = alpha * currentValue + (1 - alpha) * oldValue
            self.value = self.alpha * new_value + (1 - self.alpha) * self.value

        return self.value

    def get_value(self):
        """
        Get the current EMA value
        """
        return self.value

    def reset(self):
        """
        Reset the EMA to uninitialized state
        """
        self.value = 0.0
        self.initialized = False

    def set_alpha(self, alpha):
        """
        Set a new smoothing factor
        """
        self.alpha = max(0.01, min(0.99, alpha))


class PeakHoldBuffer:
    """
    Peak hold buffer with exponential decay
    Maintains the highest value seen over time with gradual decay
    """

    def __init__(self, size=100, decay_rate=0.02):
        """
        Initialize peak hold buffer
        size: size of the internal buffer
        decay_rate: how fast peaks decay (0.0 to 1.0)
        """
        self.buffer = deque([0.0] * size, maxlen=size)
        self.decay_rate = max(0.001, min(0.1, decay_rate))
        self.last_update_time = time.time()
        self.current_peak = 0.0

    def update(self, new_value):
        """
        Update the peak hold buffer with a new value
        """
        current_time = time.time()
        time_delta = current_time - self.last_update_time

        # Apply decay to current peak based on time passed
        decay_factor = (1.0 - self.decay_rate) ** time_delta
        self.current_peak *= decay_factor

        # Update with new value if it's higher than current peak
        if new_value > self.current_peak:
            self.current_peak = new_value

        # Add to buffer for historical tracking (optional)
        self.buffer.append(new_value)

        self.last_update_time = current_time
        return self.current_peak

    def get_peak(self):
        """
        Get the current peak value
        """
        # Apply decay since last update
        current_time = time.time()
        time_delta = current_time - self.last_update_time
        decay_factor = (1.0 - self.decay_rate) ** time_delta
        return self.current_peak * decay_factor

    def reset(self):
        """
        Reset the peak hold buffer
        """
        self.buffer.clear()
        self.current_peak = 0.0
        self.last_update_time = time.time()


class MovingAverage:
    """
    Simple moving average over a fixed window
    Good for smoothing out short-term fluctuations
    """

    def __init__(self, window_size=10):
        """
        Initialize moving average
        window_size: number of values to average over
        """
        self.window_size = max(1, window_size)
        self.values = deque(maxlen=window_size)
        self.sum = 0.0

    def update(self, new_value):
        """
        Update the moving average with a new value
        """
        if len(self.values) >= self.window_size:
            # Remove oldest value from sum
            self.sum -= self.values[0]

        # Add new value to sum
        self.values.append(new_value)
        self.sum += new_value

        # Calculate average
        return self.sum / len(self.values)

    def get_average(self):
        """
        Get the current moving average
        """
        if len(self.values) == 0:
            return 0.0
        return self.sum / len(self.values)

    def reset(self):
        """
        Reset the moving average
        """
        self.values.clear()
        self.sum = 0.0


class AdaptiveThreshold:
    """
    Adaptive threshold that adjusts based on recent audio levels
    Helps distinguish between noise and actual signal
    """

    def __init__(self, initial_threshold=0.02, adaptation_rate=0.01):
        """
        Initialize adaptive threshold
        initial_threshold: starting threshold value
        adaptation_rate: how quickly threshold adapts (0.0 to 1.0)
        """
        self.threshold = initial_threshold
        self.adaptation_rate = adaptation_rate
        self.long_term_avg = ExponentialMovingAverage(alpha=0.01)  # Very slow adaptation
        self.short_term_avg = ExponentialMovingAverage(alpha=0.1)  # Faster adaptation

    def update(self, new_value):
        """
        Update the adaptive threshold with a new value
        Returns True if the value exceeds the adaptive threshold
        """
        # Update both averages
        long_avg = self.long_term_avg.update(new_value)
        short_avg = self.short_term_avg.update(new_value)

        # Adjust threshold based on the difference between averages
        # If short-term average is much higher than long-term, lower the threshold
        # If short-term average is much lower, raise the threshold slightly
        diff = short_avg - long_avg
        adjustment = diff * self.adaptation_rate

        # Update threshold with bounds checking
        self.threshold = max(0.001, min(0.5, self.threshold + adjustment))

        # Return whether the value exceeds the adaptive threshold
        return new_value > self.threshold

    def get_threshold(self):
        """
        Get the current adaptive threshold
        """
        return self.threshold

    def reset(self):
        """
        Reset the adaptive threshold
        """
        self.long_term_avg.reset()
        self.short_term_avg.reset()
        self.long_term_avg.value = self.threshold
        self.short_term_avg.value = self.threshold


class LevelSmoothingPipeline:
    """
    Complete pipeline for audio level smoothing
    Combines multiple techniques for optimal smoothing
    """

    def __init__(self, ema_alpha=0.15, peak_decay=0.02, threshold_initial=0.02):
        self.ema = ExponentialMovingAverage(alpha=ema_alpha)
        self.peak_hold = PeakHoldBuffer(decay_rate=peak_decay)
        self.threshold = AdaptiveThreshold(initial_threshold=threshold_initial)

    def process(self, raw_level):
        """
        Process a raw audio level through the complete pipeline
        Returns (smoothed_level, peak_level, threshold_exceeded)
        """
        # Apply EMA smoothing
        smoothed = self.ema.update(raw_level)

        # Update peak hold
        peak = self.peak_hold.update(smoothed)

        # Check adaptive threshold
        threshold_exceeded = self.threshold.update(smoothed)

        return smoothed, peak, threshold_exceeded

    def reset(self):
        """
        Reset the entire pipeline
        """
        self.ema.reset()
        self.peak_hold.reset()
        self.threshold.reset()


# Example usage and testing:
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Generate some test data
    np.random.seed(42)
    time_vals = np.linspace(0, 5, 500)
    # Create a signal with varying amplitude and some noise
    signal = (np.sin(2 * np.pi * 2 * time_vals) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * time_vals)) +
              0.1 * np.random.randn(len(time_vals)))

    # Ensure all values are positive for level processing
    signal = np.abs(signal)

    # Test EMA
    ema = ExponentialMovingAverage(alpha=0.1)
    ema_results = [ema.update(val) for val in signal]

    # Test Peak Hold
    peak_hold = PeakHoldBuffer(decay_rate=0.02)
    peak_results = [peak_hold.update(val) for val in signal]

    # Test Moving Average
    mov_avg = MovingAverage(window_size=10)
    avg_results = [mov_avg.update(val) for val in signal]

    # Test Complete Pipeline
    pipeline = LevelSmoothingPipeline()
    pipeline_results = []
    for val in signal:
        smooth, peak, exceeded = pipeline.process(val)
        pipeline_results.append((smooth, peak, exceeded))

    # Plot results if matplotlib is available
    try:
        plt.figure(figsize=(12, 8))

        plt.subplot(2, 1, 1)
        plt.plot(time_vals, signal, label='Raw Signal', alpha=0.7)
        plt.plot(time_vals, ema_results, label='EMA Smoothed', linewidth=2)
        plt.plot(time_vals, avg_results, label='Moving Average', linewidth=2)
        plt.legend()
        plt.title('Audio Level Smoothing Comparison')
        plt.ylabel('Amplitude')

        plt.subplot(2, 1, 2)
        plt.plot(time_vals, signal, label='Raw Signal', alpha=0.5)
        plt.plot(time_vals, [x[0] for x in pipeline_results], label='Pipeline Smoothed', linewidth=2)
        plt.plot(time_vals, [x[1] for x in pipeline_results], label='Peak Hold', linestyle='--')
        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.title('Complete Smoothing Pipeline')

        plt.tight_layout()
        plt.show()
    except ImportError:
        print("Matplotlib not available, skipping plots")
        print(f"Signal range: {signal.min():.3f} to {signal.max():.3f}")
        print(f"EMA range: {min(ema_results):.3f} to {max(ema_results):.3f}")
        print(f"Peak hold range: {min(peak_results):.3f} to {max(peak_results):.3f}")