#!/usr/bin/env python3
"""
Audio Effects Module for DJ Mixer
Provides real-time audio effects including EQ, filters, and reverb
"""

import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class EQSettings:
    """Equalizer settings for frequency bands"""
    low: float = 1.0      # 20-250 Hz
    mid_low: float = 1.0  # 250-1000 Hz
    mid: float = 1.0      # 1000-4000 Hz
    mid_high: float = 1.0 # 4000-8000 Hz
    high: float = 1.0     # 8000-20000 Hz


@dataclass
class FilterSettings:
    """Filter settings"""
    filter_type: str = "none"  # none, lowpass, highpass, bandpass
    cutoff_freq: float = 1000.0  # Hz
    resonance: float = 1.0  # Q factor


@dataclass
class ReverbSettings:
    """Reverb effect settings"""
    room_size: float = 0.5  # 0.0 to 1.0
    damping: float = 0.5    # 0.0 to 1.0
    wet_level: float = 0.3  # 0.0 to 1.0
    dry_level: float = 0.7  # 0.0 to 1.0


class AudioEffects:
    """Audio effects processor for real-time audio manipulation"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.eq = EQSettings()
        self.filter = FilterSettings()
        self.reverb = ReverbSettings()
        
        # Reverb delay buffers
        self.reverb_buffer_size = int(sample_rate * 0.05)  # 50ms
        self.reverb_buffer = np.zeros(self.reverb_buffer_size)
        self.reverb_buffer_pos = 0
    
    def set_eq(self, low: float = 1.0, mid_low: float = 1.0, mid: float = 1.0, 
               mid_high: float = 1.0, high: float = 1.0) -> None:
        """Set equalizer levels (0.0 to 2.0, 1.0 is neutral)"""
        self.eq.low = np.clip(low, 0.0, 2.0)
        self.eq.mid_low = np.clip(mid_low, 0.0, 2.0)
        self.eq.mid = np.clip(mid, 0.0, 2.0)
        self.eq.mid_high = np.clip(mid_high, 0.0, 2.0)
        self.eq.high = np.clip(high, 0.0, 2.0)
    
    def set_filter(self, filter_type: str, cutoff_freq: float = 1000.0, 
                   resonance: float = 1.0) -> None:
        """Set filter type and parameters"""
        if filter_type not in ["none", "lowpass", "highpass", "bandpass"]:
            raise ValueError(f"Invalid filter type: {filter_type}")
        
        self.filter.filter_type = filter_type
        self.filter.cutoff_freq = cutoff_freq
        self.filter.resonance = resonance
    
    def set_reverb(self, room_size: float = 0.5, damping: float = 0.5,
                   wet_level: float = 0.3, dry_level: float = 0.7) -> None:
        """Set reverb parameters"""
        self.reverb.room_size = np.clip(room_size, 0.0, 1.0)
        self.reverb.damping = np.clip(damping, 0.0, 1.0)
        self.reverb.wet_level = np.clip(wet_level, 0.0, 1.0)
        self.reverb.dry_level = np.clip(dry_level, 0.0, 1.0)
    
    def apply_eq(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply equalizer to audio data
        This is a simplified EQ using spectral processing
        """
        if len(audio_data) == 0:
            return audio_data
        
        # Perform FFT
        fft_data = np.fft.rfft(audio_data)
        frequencies = np.fft.rfftfreq(len(audio_data), 1.0 / self.sample_rate)
        
        # Apply EQ gains to frequency bands
        for i, freq in enumerate(frequencies):
            if freq < 250:
                fft_data[i] *= self.eq.low
            elif freq < 1000:
                fft_data[i] *= self.eq.mid_low
            elif freq < 4000:
                fft_data[i] *= self.eq.mid
            elif freq < 8000:
                fft_data[i] *= self.eq.mid_high
            else:
                fft_data[i] *= self.eq.high
        
        # Inverse FFT
        result = np.fft.irfft(fft_data, len(audio_data))
        return result.astype(audio_data.dtype)
    
    def apply_filter(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply filter to audio data
        Simplified filter implementation using spectral processing
        """
        if self.filter.filter_type == "none" or len(audio_data) == 0:
            return audio_data
        
        # Perform FFT
        fft_data = np.fft.rfft(audio_data)
        frequencies = np.fft.rfftfreq(len(audio_data), 1.0 / self.sample_rate)
        
        # Apply filter
        cutoff = self.filter.cutoff_freq
        q = self.filter.resonance
        
        for i, freq in enumerate(frequencies):
            if self.filter.filter_type == "lowpass":
                # Low-pass: attenuate frequencies above cutoff
                if freq > cutoff:
                    attenuation = 1.0 / (1.0 + ((freq - cutoff) / (cutoff / q)) ** 2)
                    fft_data[i] *= attenuation
            elif self.filter.filter_type == "highpass":
                # High-pass: attenuate frequencies below cutoff
                if freq < cutoff:
                    attenuation = 1.0 / (1.0 + ((cutoff - freq) / (cutoff / q)) ** 2)
                    fft_data[i] *= attenuation
            elif self.filter.filter_type == "bandpass":
                # Band-pass: keep frequencies near cutoff
                distance = abs(freq - cutoff)
                bandwidth = cutoff / q
                if distance > bandwidth / 2:
                    attenuation = 1.0 / (1.0 + ((distance - bandwidth / 2) / bandwidth) ** 2)
                    fft_data[i] *= attenuation
        
        # Inverse FFT
        result = np.fft.irfft(fft_data, len(audio_data))
        return result.astype(audio_data.dtype)
    
    def apply_reverb(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply reverb effect to audio data
        Simplified reverb using delay and feedback
        """
        if len(audio_data) == 0:
            return audio_data
        
        result = np.zeros_like(audio_data, dtype=np.float32)
        audio_float = audio_data.astype(np.float32)
        
        # Calculate reverb parameters
        feedback = self.reverb.room_size * 0.7
        damping_factor = 1.0 - self.reverb.damping * 0.5
        
        for i in range(len(audio_data)):
            # Get delayed signal from buffer
            delayed = self.reverb_buffer[self.reverb_buffer_pos]
            
            # Mix dry and wet signals
            dry = audio_float[i] * self.reverb.dry_level
            wet = delayed * self.reverb.wet_level
            result[i] = dry + wet
            
            # Update delay buffer with feedback
            self.reverb_buffer[self.reverb_buffer_pos] = (
                audio_float[i] + delayed * feedback * damping_factor
            )
            
            # Advance buffer position
            self.reverb_buffer_pos = (self.reverb_buffer_pos + 1) % self.reverb_buffer_size
        
        return result.astype(audio_data.dtype)
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply all enabled effects to audio data in the correct order
        Order: EQ -> Filter -> Reverb
        """
        if len(audio_data) == 0:
            return audio_data
        
        # Convert to float for processing
        processed = audio_data.astype(np.float32)
        
        # Apply effects in order
        processed = self.apply_eq(processed)
        processed = self.apply_filter(processed)
        processed = self.apply_reverb(processed)
        
        # Clip to prevent overflow
        processed = np.clip(processed, -32768, 32767)
        
        return processed.astype(audio_data.dtype)
    
    def reset(self) -> None:
        """Reset all effects to default values"""
        self.eq = EQSettings()
        self.filter = FilterSettings()
        self.reverb = ReverbSettings()
        self.reverb_buffer = np.zeros(self.reverb_buffer_size)
        self.reverb_buffer_pos = 0
    
    def get_eq_settings(self) -> EQSettings:
        """Get current EQ settings"""
        return self.eq
    
    def get_filter_settings(self) -> FilterSettings:
        """Get current filter settings"""
        return self.filter
    
    def get_reverb_settings(self) -> ReverbSettings:
        """Get current reverb settings"""
        return self.reverb


class EffectsPresets:
    """Predefined effect presets for common DJ effects"""
    
    @staticmethod
    def bass_boost() -> dict:
        """Bass boost preset"""
        return {
            "eq": {"low": 1.8, "mid_low": 1.2, "mid": 1.0, "mid_high": 0.9, "high": 0.9}
        }
    
    @staticmethod
    def treble_boost() -> dict:
        """Treble boost preset"""
        return {
            "eq": {"low": 0.9, "mid_low": 0.9, "mid": 1.0, "mid_high": 1.3, "high": 1.6}
        }
    
    @staticmethod
    def vocal_enhance() -> dict:
        """Vocal enhancement preset"""
        return {
            "eq": {"low": 0.8, "mid_low": 1.0, "mid": 1.4, "mid_high": 1.3, "high": 1.0}
        }
    
    @staticmethod
    def club_sound() -> dict:
        """Club sound preset"""
        return {
            "eq": {"low": 1.5, "mid_low": 1.0, "mid": 0.9, "mid_high": 1.1, "high": 1.3},
            "reverb": {"room_size": 0.6, "damping": 0.4, "wet_level": 0.25, "dry_level": 0.75}
        }
    
    @staticmethod
    def telephone_effect() -> dict:
        """Telephone/radio effect preset"""
        return {
            "eq": {"low": 0.3, "mid_low": 0.8, "mid": 1.5, "mid_high": 1.2, "high": 0.4},
            "filter": {"filter_type": "bandpass", "cutoff_freq": 1500, "resonance": 2.0}
        }
    
    @staticmethod
    def echo_chamber() -> dict:
        """Echo chamber preset"""
        return {
            "reverb": {"room_size": 0.9, "damping": 0.3, "wet_level": 0.6, "dry_level": 0.5}
        }
