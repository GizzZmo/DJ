#!/usr/bin/env python3
"""
Waveform Display Module for DJ Mixer
Provides waveform visualization and analysis
"""

import numpy as np
from typing import Optional, Tuple, List
from pathlib import Path


class WaveformGenerator:
    """Generates waveform data for visualization"""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def generate_waveform(
        self, audio_data: np.ndarray, width: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate waveform data for visualization

        Args:
            audio_data: Audio samples
            width: Number of points in waveform (resolution)

        Returns:
            Tuple of (min_values, max_values) arrays
        """
        if len(audio_data) == 0:
            return np.array([]), np.array([])

        # Convert stereo to mono if needed
        if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
            audio_mono = np.mean(audio_data, axis=1)
        else:
            audio_mono = audio_data.flatten()

        # Calculate samples per pixel
        samples_per_pixel = len(audio_mono) // width

        if samples_per_pixel < 1:
            samples_per_pixel = 1
            width = len(audio_mono)

        # Generate min/max values for each pixel
        min_values = np.zeros(width)
        max_values = np.zeros(width)

        for i in range(width):
            start = i * samples_per_pixel
            end = min(start + samples_per_pixel, len(audio_mono))

            if start < len(audio_mono):
                segment = audio_mono[start:end]
                min_values[i] = np.min(segment)
                max_values[i] = np.max(segment)

        return min_values, max_values

    def generate_waveform_from_file(
        self, file_path: str, width: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate waveform from audio file

        Args:
            file_path: Path to audio file
            width: Number of points in waveform

        Returns:
            Tuple of (min_values, max_values) arrays
        """
        try:
            # Try to load with pydub
            from pydub import AudioSegment

            audio = AudioSegment.from_file(file_path)

            # Convert to numpy array
            samples = np.array(audio.get_array_of_samples())

            # Handle stereo
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))

            return self.generate_waveform(samples, width)

        except ImportError:
            print("Waveform generation from file requires pydub")
            print("Install with: pip install pydub")
            return np.array([]), np.array([])
        except Exception as e:
            print(f"Error generating waveform from file: {e}")
            return np.array([]), np.array([])

    def generate_spectrum(
        self, audio_data: np.ndarray, fft_size: int = 2048
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate frequency spectrum data

        Args:
            audio_data: Audio samples
            fft_size: FFT window size

        Returns:
            Tuple of (frequencies, magnitudes) arrays
        """
        if len(audio_data) == 0:
            return np.array([]), np.array([])

        # Convert stereo to mono if needed
        if len(audio_data.shape) > 1:
            audio_mono = np.mean(audio_data, axis=1)
        else:
            audio_mono = audio_data

        # Apply window
        window = np.hanning(fft_size)

        # Take middle section if audio is longer than fft_size
        if len(audio_mono) > fft_size:
            start = (len(audio_mono) - fft_size) // 2
            audio_segment = audio_mono[start : start + fft_size]
        else:
            # Pad with zeros if shorter
            audio_segment = np.pad(audio_mono, (0, fft_size - len(audio_mono)))

        # Apply window and compute FFT
        windowed = audio_segment * window
        spectrum = np.fft.rfft(windowed)

        # Calculate magnitude
        magnitude = np.abs(spectrum)

        # Calculate frequencies
        frequencies = np.fft.rfftfreq(fft_size, 1.0 / self.sample_rate)

        return frequencies, magnitude

    def calculate_peaks(
        self, audio_data: np.ndarray, threshold: Optional[float] = None
    ) -> List[int]:
        """
        Find peak positions in audio data

        Args:
            audio_data: Audio samples
            threshold: Peak threshold (None for auto)

        Returns:
            List of sample indices where peaks occur
        """
        if len(audio_data) == 0:
            return []

        # Convert to mono if needed
        if len(audio_data.shape) > 1:
            audio_mono = np.mean(audio_data, axis=1)
        else:
            audio_mono = audio_data

        # Calculate threshold if not provided
        if threshold is None:
            threshold = np.mean(np.abs(audio_mono)) + np.std(np.abs(audio_mono))

        # Find peaks
        peaks = []
        for i in range(1, len(audio_mono) - 1):
            if (
                abs(audio_mono[i]) > threshold
                and abs(audio_mono[i]) > abs(audio_mono[i - 1])
                and abs(audio_mono[i]) > abs(audio_mono[i + 1])
            ):
                peaks.append(i)

        return peaks


class WaveformDisplay:
    """Handles waveform display rendering"""

    def __init__(self, width: int = 800, height: int = 200):
        self.width = width
        self.height = height
        self.waveform_data: Optional[Tuple[np.ndarray, np.ndarray]] = None
        self.playback_position: float = 0.0  # Position in seconds
        self.duration: float = 0.0
        self.zoom_level: float = 1.0
        self.scroll_position: float = 0.0

    def set_waveform(
        self, min_values: np.ndarray, max_values: np.ndarray, duration: float
    ) -> None:
        """Set waveform data for display"""
        self.waveform_data = (min_values, max_values)
        self.duration = duration

    def set_playback_position(self, position: float) -> None:
        """Set current playback position in seconds"""
        self.playback_position = max(0.0, min(position, self.duration))

    def set_zoom(self, zoom_level: float) -> None:
        """Set zoom level (1.0 = normal, 2.0 = 2x zoom, etc.)"""
        self.zoom_level = max(0.1, min(zoom_level, 10.0))

    def set_scroll(self, scroll_position: float) -> None:
        """Set scroll position (0.0 to 1.0)"""
        self.scroll_position = max(0.0, min(scroll_position, 1.0))

    def get_visible_range(self) -> Tuple[float, float]:
        """Get the time range currently visible"""
        visible_duration = self.duration / self.zoom_level
        start_time = self.scroll_position * (self.duration - visible_duration)
        end_time = start_time + visible_duration
        return start_time, end_time

    def position_to_pixel(self, position: float) -> int:
        """Convert time position to pixel coordinate"""
        if self.duration == 0:
            return 0

        start_time, end_time = self.get_visible_range()
        visible_duration = end_time - start_time

        if position < start_time or position > end_time:
            return -1  # Not visible

        relative_position = (position - start_time) / visible_duration
        return int(relative_position * self.width)

    def pixel_to_position(self, pixel: int) -> float:
        """Convert pixel coordinate to time position"""
        start_time, end_time = self.get_visible_range()
        visible_duration = end_time - start_time

        relative_position = pixel / self.width
        return start_time + (relative_position * visible_duration)

    def get_waveform_points(self) -> List[Tuple[int, int, int, int]]:
        """
        Get waveform rendering points for current view

        Returns:
            List of (x, y_min, x, y_max) tuples for drawing lines
        """
        if self.waveform_data is None:
            return []

        min_values, max_values = self.waveform_data

        if len(min_values) == 0:
            return []

        # Calculate visible range
        start_time, end_time = self.get_visible_range()

        # Map to waveform data indices
        start_idx = int((start_time / self.duration) * len(min_values))
        end_idx = int((end_time / self.duration) * len(min_values))

        start_idx = max(0, start_idx)
        end_idx = min(len(min_values), end_idx)

        # Get visible portion
        visible_min = min_values[start_idx:end_idx]
        visible_max = max_values[start_idx:end_idx]

        if len(visible_min) == 0:
            return []

        # Normalize to display height
        center_y = self.height // 2
        scale = self.height / 2

        # Find global min/max for scaling
        global_min = np.min(visible_min)
        global_max = np.max(visible_max)
        max_amplitude = max(abs(global_min), abs(global_max))

        if max_amplitude == 0:
            max_amplitude = 1.0

        # Generate points
        points = []
        samples_per_pixel = max(1, len(visible_min) // self.width)

        for i in range(0, len(visible_min), samples_per_pixel):
            x = int((i / len(visible_min)) * self.width)

            # Get min/max for this pixel
            pixel_min = np.min(visible_min[i : i + samples_per_pixel])
            pixel_max = np.max(visible_max[i : i + samples_per_pixel])

            # Normalize and scale
            y_min = int(center_y - (pixel_min / max_amplitude) * scale)
            y_max = int(center_y - (pixel_max / max_amplitude) * scale)

            # Clamp to display bounds
            y_min = max(0, min(self.height - 1, y_min))
            y_max = max(0, min(self.height - 1, y_max))

            points.append((x, y_min, x, y_max))

        return points

    def get_playback_position_pixel(self) -> int:
        """Get pixel position of playback cursor"""
        return self.position_to_pixel(self.playback_position)


class WaveformCache:
    """Caches waveform data to avoid regenerating"""

    def __init__(self, max_cache_size: int = 10):
        self.cache: dict = {}
        self.max_cache_size = max_cache_size
        self.generator = WaveformGenerator()

    def get_waveform(
        self, file_path: str, width: int = 1000
    ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Get waveform from cache or generate if not cached"""
        cache_key = f"{file_path}_{width}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Generate waveform
        waveform = self.generator.generate_waveform_from_file(file_path, width)

        # Add to cache
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry
            self.cache.pop(next(iter(self.cache)))

        self.cache[cache_key] = waveform
        return waveform

    def clear_cache(self) -> None:
        """Clear waveform cache"""
        self.cache.clear()

    def remove_from_cache(self, file_path: str) -> None:
        """Remove specific file from cache"""
        keys_to_remove = [k for k in self.cache.keys() if k.startswith(file_path)]
        for key in keys_to_remove:
            del self.cache[key]
