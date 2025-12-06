#!/usr/bin/env python3
"""
Beat Detection and BPM Analysis for DJ Mixer
Provides beat detection, BPM calculation, and auto-sync functionality
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
import time


@dataclass
class BeatInfo:
    """Information about detected beats"""

    bpm: float
    beat_positions: List[float]  # Beat positions in seconds
    beat_grid: List[float]  # Quantized beat grid
    confidence: float  # Detection confidence (0.0 to 1.0)
    first_beat: float  # Position of first beat in seconds


class BeatDetector:
    """Beat detection and BPM analysis"""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.min_bpm = 60
        self.max_bpm = 200

    def detect_beats(self, audio_data: np.ndarray, duration: float) -> BeatInfo:
        """
        Detect beats in audio data and calculate BPM

        Args:
            audio_data: Audio samples
            duration: Duration of audio in seconds

        Returns:
            BeatInfo object with beat positions and BPM
        """
        if len(audio_data) == 0:
            return BeatInfo(
                bpm=120.0,
                beat_positions=[],
                beat_grid=[],
                confidence=0.0,
                first_beat=0.0,
            )

        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_mono = np.mean(audio_data, axis=1)
        else:
            audio_mono = audio_data

        # Calculate energy envelope
        energy = self._calculate_energy_envelope(audio_mono)

        # Find peaks in energy (potential beats)
        beat_positions = self._find_peaks(energy, duration)

        # Calculate BPM from beat positions
        bpm = self._calculate_bpm(beat_positions)

        # Generate beat grid
        beat_grid = self._generate_beat_grid(bpm, duration, beat_positions)

        # Calculate confidence based on regularity of beats
        confidence = self._calculate_confidence(beat_positions, bpm)

        # Find first beat
        first_beat = beat_positions[0] if beat_positions else 0.0

        return BeatInfo(
            bpm=bpm,
            beat_positions=beat_positions,
            beat_grid=beat_grid,
            confidence=confidence,
            first_beat=first_beat,
        )

    def _calculate_energy_envelope(self, audio_data: np.ndarray) -> np.ndarray:
        """Calculate energy envelope of audio signal"""
        # Use overlapping windows
        window_size = int(self.sample_rate * 0.05)  # 50ms windows
        hop_size = window_size // 4

        num_frames = (len(audio_data) - window_size) // hop_size + 1
        energy = np.zeros(num_frames)

        for i in range(num_frames):
            start = i * hop_size
            end = start + window_size
            frame = audio_data[start:end]
            energy[i] = np.sum(frame**2)

        # Smooth energy curve
        kernel_size = 5
        kernel = np.ones(kernel_size) / kernel_size
        energy = np.convolve(energy, kernel, mode="same")

        return energy

    def _find_peaks(self, energy: np.ndarray, duration: float) -> List[float]:
        """Find peaks in energy envelope (potential beats)"""
        if len(energy) == 0:
            return []

        # Calculate adaptive threshold
        threshold = np.mean(energy) + 0.5 * np.std(energy)

        # Find peaks above threshold
        peaks = []
        min_distance = int(len(energy) / duration * 0.3)  # Minimum 0.3s between beats

        for i in range(1, len(energy) - 1):
            if (
                energy[i] > threshold
                and energy[i] > energy[i - 1]
                and energy[i] > energy[i + 1]
            ):
                # Check minimum distance from last peak
                if not peaks or i - peaks[-1] >= min_distance:
                    peaks.append(i)

        # Convert peak indices to time positions
        hop_size = int(self.sample_rate * 0.05) // 4
        beat_positions = [p * hop_size / self.sample_rate for p in peaks]

        return beat_positions

    def _calculate_bpm(self, beat_positions: List[float]) -> float:
        """Calculate BPM from beat positions"""
        if len(beat_positions) < 2:
            return 120.0  # Default BPM

        # Calculate intervals between beats
        intervals = np.diff(beat_positions)

        # Remove outliers
        median_interval = np.median(intervals)
        valid_intervals = [
            i for i in intervals if 0.5 * median_interval < i < 1.5 * median_interval
        ]

        if not valid_intervals:
            return 120.0

        # Calculate BPM from average interval
        avg_interval = np.mean(valid_intervals)
        bpm = 60.0 / avg_interval

        # Clamp to reasonable range
        bpm = np.clip(bpm, self.min_bpm, self.max_bpm)

        return round(bpm, 2)

    def _generate_beat_grid(
        self, bpm: float, duration: float, beat_positions: List[float]
    ) -> List[float]:
        """Generate quantized beat grid based on BPM"""
        if bpm == 0:
            return []

        beat_interval = 60.0 / bpm
        first_beat = beat_positions[0] if beat_positions else 0.0

        # Generate grid
        grid = []
        t = first_beat
        while t < duration:
            grid.append(t)
            t += beat_interval

        return grid

    def _calculate_confidence(self, beat_positions: List[float], bpm: float) -> float:
        """Calculate confidence in beat detection"""
        if len(beat_positions) < 2:
            return 0.0

        # Calculate how regular the beats are
        intervals = np.diff(beat_positions)
        expected_interval = 60.0 / bpm

        # Calculate deviation from expected interval
        deviations = [abs(i - expected_interval) / expected_interval for i in intervals]
        avg_deviation = np.mean(deviations)

        # Convert to confidence (lower deviation = higher confidence)
        confidence = 1.0 - min(avg_deviation, 1.0)

        return round(confidence, 2)


class AutoSync:
    """Auto-sync functionality for matching track tempos"""

    def __init__(self):
        self.beat_detector = BeatDetector()

    def calculate_sync_adjustment(self, track1_bpm: float, track2_bpm: float) -> dict:
        """
        Calculate adjustment needed to sync two tracks

        Returns:
            dict with sync information
        """
        if track1_bpm == 0 or track2_bpm == 0:
            return {
                "sync_possible": False,
                "pitch_adjustment": 0.0,
                "tempo_ratio": 1.0,
                "message": "Invalid BPM values",
            }

        # Calculate tempo ratio
        tempo_ratio = track2_bpm / track1_bpm

        # Calculate pitch adjustment (in semitones)
        pitch_adjustment = 12 * np.log2(tempo_ratio)

        # Check if sync is reasonable (within ±12% tempo change)
        sync_possible = abs(tempo_ratio - 1.0) <= 0.12

        message = "Tracks can be synced"
        if not sync_possible:
            message = "BPM difference too large for sync"

        return {
            "sync_possible": sync_possible,
            "pitch_adjustment": round(pitch_adjustment, 2),
            "tempo_ratio": round(tempo_ratio, 4),
            "message": message,
            "track1_bpm": track1_bpm,
            "track2_bpm": track2_bpm,
        }

    def get_beat_match_point(
        self,
        track1_beat: BeatInfo,
        track2_beat: BeatInfo,
        current_position: float = 0.0,
    ) -> float:
        """
        Find the best point to mix in track2 based on track1's current position

        Returns:
            Position in track2 (seconds) where beats align
        """
        if not track1_beat.beat_grid or not track2_beat.beat_grid:
            return 0.0

        # Find nearest beat in track1 to current position
        track1_next_beat = min(
            [b for b in track1_beat.beat_grid if b >= current_position],
            default=track1_beat.beat_grid[-1],
        )

        # Find phase within measure (assuming 4/4 time)
        beats_per_measure = 4
        track1_beat_num = len(
            [b for b in track1_beat.beat_grid if b <= track1_next_beat]
        )
        phase_in_measure = track1_beat_num % beats_per_measure

        # Find corresponding beat in track2 with same phase
        if phase_in_measure < len(track2_beat.beat_grid):
            return track2_beat.beat_grid[phase_in_measure]
        else:
            return track2_beat.first_beat

    def suggest_mix_timing(
        self,
        track1_beat: BeatInfo,
        track2_beat: BeatInfo,
        current_position: float = 0.0,
    ) -> dict:
        """
        Suggest when and how to mix between tracks

        Returns:
            dict with mixing suggestions
        """
        # Calculate sync adjustment
        sync_info = self.calculate_sync_adjustment(track1_beat.bpm, track2_beat.bpm)

        # Find beat match point
        match_point = self.get_beat_match_point(
            track1_beat, track2_beat, current_position
        )

        # Suggest mixing points (on phrase boundaries - every 16 or 32 beats)
        beats_per_phrase = 16
        next_phrase_boundary = current_position

        if track1_beat.beat_grid:
            future_beats = [b for b in track1_beat.beat_grid if b > current_position]
            if future_beats:
                beats_ahead = len(future_beats)
                beats_to_phrase = beats_per_phrase - (beats_ahead % beats_per_phrase)
                if beats_to_phrase < len(future_beats):
                    next_phrase_boundary = future_beats[beats_to_phrase]

        return {
            "sync_info": sync_info,
            "match_point": round(match_point, 2),
            "next_phrase_boundary": round(next_phrase_boundary, 2),
            "recommended_action": (
                "Start crossfading at next phrase boundary"
                if sync_info["sync_possible"]
                else "Adjust tempo before mixing"
            ),
        }
