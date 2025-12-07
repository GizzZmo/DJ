#!/usr/bin/env python3
"""
PyAudio-based DJ Mixer with ASIO driver support
Provides professional audio interface control with low-latency ASIO support
"""

import numpy as np
from typing import Dict, List, Optional, Callable
from pathlib import Path
import threading
import time
from pydub import AudioSegment

from device_routing import AudioDeviceManager, AudioDevice


class PyAudioTrack:
    """Audio track for PyAudio playback"""

    def __init__(self, file_path: str, sample_rate: int = 44100):
        self.file_path = Path(file_path)
        self.sample_rate = sample_rate
        self.audio_data: Optional[np.ndarray] = None
        self.duration: float = 0.0
        self.is_loaded = False
        self.is_playing = False
        self.position = 0  # Current playback position in samples
        self.volume = 1.0
        self.loop = False

    def load(self) -> bool:
        """Load audio file into memory"""
        try:
            if not self.file_path.exists():
                print(f"Error: File {self.file_path} does not exist")
                return False

            # Load audio with pydub
            audio = AudioSegment.from_file(str(self.file_path))

            # Convert to target sample rate and stereo
            audio = audio.set_frame_rate(self.sample_rate)
            audio = audio.set_channels(2)

            # Convert to numpy array (int16)
            samples = np.array(audio.get_array_of_samples(), dtype=np.int16)

            # Reshape to stereo (2 channels)
            if audio.channels == 2:
                self.audio_data = samples.reshape((-1, 2))
            else:
                # Mono to stereo
                self.audio_data = np.column_stack((samples, samples))

            self.duration = len(self.audio_data) / self.sample_rate
            self.is_loaded = True
            self.position = 0
            print(f"Loaded: {self.file_path.name} ({self.duration:.2f}s)")
            return True

        except Exception as e:
            print(f"Error loading {self.file_path}: {e}")
            return False

    def get_audio_chunk(self, chunk_size: int) -> Optional[np.ndarray]:
        """Get next chunk of audio data"""
        if not self.is_loaded or self.audio_data is None or not self.is_playing:
            return None

        # Calculate remaining samples
        remaining = len(self.audio_data) - self.position

        if remaining <= 0:
            if self.loop:
                self.position = 0
                remaining = len(self.audio_data)
            else:
                self.is_playing = False
                return None

        # Get chunk
        actual_size = min(chunk_size, remaining)
        chunk = self.audio_data[self.position : self.position + actual_size]
        self.position += actual_size

        # Apply volume
        if self.volume != 1.0:
            chunk = (chunk * self.volume).astype(np.int16)

        # Pad with zeros if needed
        if actual_size < chunk_size:
            padding = np.zeros((chunk_size - actual_size, 2), dtype=np.int16)
            chunk = np.vstack((chunk, padding))

        return chunk

    def play(self, loops: int = 0) -> bool:
        """Start playback"""
        if not self.is_loaded:
            return False
        self.is_playing = True
        self.loop = loops != 0
        return True

    def stop(self) -> None:
        """Stop playback"""
        self.is_playing = False
        self.position = 0

    def pause(self) -> None:
        """Pause playback"""
        self.is_playing = False

    def unpause(self) -> None:
        """Resume playback"""
        if self.is_loaded:
            self.is_playing = True

    def set_volume(self, volume: float) -> None:
        """Set track volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))

    def seek(self, position: float) -> None:
        """Seek to position in seconds"""
        if self.is_loaded and self.audio_data is not None:
            sample_pos = int(position * self.sample_rate)
            self.position = max(0, min(sample_pos, len(self.audio_data)))


class PyAudioMixer:
    """
    DJ Mixer using PyAudio for professional audio interface support
    Supports ASIO drivers for low-latency audio output
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        buffer_size: int = 512,
        channels: int = 2,
        use_mock: bool = False,
    ):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.channels = channels
        self.use_mock = use_mock

        # Audio device manager
        self.device_manager = AudioDeviceManager()

        # PyAudio instance
        self.pyaudio_instance = None
        self.stream = None

        # Tracks
        self.tracks: Dict[str, PyAudioTrack] = {}

        # Mixer settings
        self.crossfader_position = 0.5  # 0.0 = full left, 1.0 = full right
        self.master_volume = 1.0
        self.is_initialized = False
        self.is_running = False

        # Current output device
        self.output_device: Optional[AudioDevice] = None

        # Audio callback lock
        self.lock = threading.Lock()

    def initialize(
        self, device_index: Optional[int] = None, use_asio: bool = False
    ) -> bool:
        """
        Initialize PyAudio mixer

        Args:
            device_index: Specific device index to use (None for default)
            use_asio: If True, try to use an ASIO device
        """
        try:
            # Initialize device manager
            if not self.device_manager.initialize(use_mock=self.use_mock):
                print("Failed to initialize device manager")
                return False

            # Select output device
            if use_asio:
                asio_devices = self.device_manager.get_asio_devices()
                if asio_devices:
                    self.output_device = asio_devices[0]
                    print(f"Using ASIO device: {self.output_device.name}")
                else:
                    print("No ASIO devices found, using default")
                    self.output_device = self.device_manager.get_default_output_device()
            elif device_index is not None:
                self.output_device = self.device_manager.get_device_by_index(
                    device_index
                )
            else:
                self.output_device = self.device_manager.get_default_output_device()

            if not self.output_device:
                print("No output device available")
                return False

            print(
                f"Output device: {self.output_device.name} "
                f"({self.output_device.host_api})"
            )

            # Initialize PyAudio (only if not in mock mode)
            if not self.use_mock:
                import pyaudio

                self.pyaudio_instance = pyaudio.PyAudio()

                # Open audio stream
                self.stream = self.pyaudio_instance.open(
                    format=pyaudio.paInt16,
                    channels=self.channels,
                    rate=self.sample_rate,
                    output=True,
                    output_device_index=self.output_device.index,
                    frames_per_buffer=self.buffer_size,
                    stream_callback=self._audio_callback,
                )

                self.stream.start_stream()
                self.is_running = True
            else:
                print("[MOCK] PyAudio stream opened")
                self.is_running = True

            self.is_initialized = True
            print(
                f"PyAudio Mixer initialized: {self.sample_rate}Hz, "
                f"{self.channels} channels, buffer: {self.buffer_size}"
            )
            return True

        except Exception as e:
            print(f"Failed to initialize PyAudio mixer: {e}")
            if not self.use_mock:
                print("Falling back to mock mode")
                self.use_mock = True
                return self.initialize(device_index=device_index, use_asio=use_asio)
            return False

    def _audio_callback(
        self, in_data, frame_count, time_info, status
    ) -> tuple:
        """PyAudio stream callback for real-time audio mixing"""
        with self.lock:
            # Initialize output buffer
            output = np.zeros((frame_count, self.channels), dtype=np.int16)

            # Mix all playing tracks
            for track in self.tracks.values():
                if track.is_playing:
                    chunk = track.get_audio_chunk(frame_count)
                    if chunk is not None:
                        # Add to mix (with clipping prevention)
                        output = np.clip(
                            output.astype(np.int32) + chunk.astype(np.int32),
                            -32768,
                            32767,
                        ).astype(np.int16)

            # Apply master volume
            if self.master_volume != 1.0:
                output = (output * self.master_volume).astype(np.int16)

            import pyaudio

            return (output.tobytes(), pyaudio.paContinue)

    def load_track(self, name: str, file_path: str) -> bool:
        """Load an audio track"""
        if not self.is_initialized:
            print("Mixer not initialized")
            return False

        track = PyAudioTrack(file_path, self.sample_rate)
        if track.load():
            with self.lock:
                self.tracks[name] = track
            return True
        return False

    def play_track(self, name: str, loops: int = 0) -> bool:
        """Play a loaded track"""
        if name not in self.tracks:
            print(f"Track '{name}' not found")
            return False

        with self.lock:
            return self.tracks[name].play(loops)

    def stop_track(self, name: str) -> bool:
        """Stop a track"""
        if name not in self.tracks:
            return False

        with self.lock:
            self.tracks[name].stop()
        return True

    def pause_track(self, name: str) -> bool:
        """Pause a track"""
        if name not in self.tracks:
            return False

        with self.lock:
            self.tracks[name].pause()
        return True

    def unpause_track(self, name: str) -> bool:
        """Unpause a track"""
        if name not in self.tracks:
            return False

        with self.lock:
            self.tracks[name].unpause()
        return True

    def set_track_volume(self, name: str, volume: float) -> bool:
        """Set volume for a specific track"""
        if name not in self.tracks:
            return False
        if volume < 0.0 or volume > 1.0:
            return False

        with self.lock:
            self.tracks[name].set_volume(volume)
        return True

    def get_track_volume(self, name: str) -> float:
        """Get volume for a specific track"""
        if name in self.tracks:
            return self.tracks[name].volume
        return 0.0

    def set_master_volume(self, volume: float) -> bool:
        """Set master volume (0.0 to 1.0)"""
        if volume < 0.0 or volume > 1.0:
            return False
        with self.lock:
            self.master_volume = max(0.0, min(1.0, volume))
        return True

    def get_master_volume(self) -> float:
        """Get master volume"""
        return self.master_volume

    def set_crossfader(self, position: float) -> bool:
        """Set crossfader position (0.0 = full left, 1.0 = full right)"""
        if position < 0.0 or position > 1.0:
            return False
        with self.lock:
            self.crossfader_position = max(0.0, min(1.0, position))
        return True

    def get_crossfader(self) -> float:
        """Get crossfader position"""
        return self.crossfader_position

    def apply_crossfader(self, left_track: str, right_track: str) -> bool:
        """Apply crossfader between two tracks"""
        if left_track not in self.tracks or right_track not in self.tracks:
            return False

        # Calculate volumes based on crossfader position
        left_volume = 1.0 - self.crossfader_position
        right_volume = self.crossfader_position

        with self.lock:
            self.tracks[left_track].set_volume(left_volume)
            self.tracks[right_track].set_volume(right_volume)

        return True

    def get_loaded_tracks(self) -> List[str]:
        """Get list of loaded track names"""
        return list(self.tracks.keys())

    def get_audio_devices(self) -> List[AudioDevice]:
        """Get available audio output devices"""
        return self.device_manager.get_devices(output_only=True)

    def get_asio_devices(self) -> List[AudioDevice]:
        """Get available ASIO devices"""
        return self.device_manager.get_asio_devices()

    def cleanup(self) -> None:
        """Cleanup PyAudio resources"""
        self.is_running = False

        if self.stream and not self.use_mock:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                print(f"Error closing stream: {e}")

        if self.pyaudio_instance and not self.use_mock:
            try:
                self.pyaudio_instance.terminate()
            except Exception as e:
                print(f"Error terminating PyAudio: {e}")

        self.device_manager.cleanup()

        if self.use_mock:
            print("[MOCK] PyAudio mixer cleaned up")


def demo_pyaudio_mixer():
    """Demo PyAudio mixer with ASIO support"""
    print("=" * 60)
    print("PyAudio Mixer with ASIO Driver Support Demo")
    print("=" * 60)

    # Initialize mixer in mock mode
    mixer = PyAudioMixer(use_mock=True)

    # Try to initialize with ASIO
    print("\n--- Initializing with ASIO support ---")
    if not mixer.initialize(use_asio=True):
        print("Failed to initialize mixer")
        return

    # Show available devices
    print("\n--- Available Audio Devices ---")
    devices = mixer.get_audio_devices()
    for device in devices:
        asio_marker = " [ASIO]" if "ASIO" in device.host_api else ""
        default_marker = " [DEFAULT]" if device.is_default_output else ""
        print(
            f"{device.index}: {device.name}{asio_marker}{default_marker}"
        )

    # Show ASIO devices specifically
    print("\n--- ASIO Devices ---")
    asio_devices = mixer.get_asio_devices()
    if asio_devices:
        for device in asio_devices:
            print(
                f"{device.index}: {device.name} "
                f"({device.max_output_channels} channels)"
            )
    else:
        print("No ASIO devices found")

    # Test basic controls
    print("\n--- Testing Mixer Controls ---")
    mixer.set_master_volume(0.8)
    print(f"Master volume: {mixer.get_master_volume()}")

    mixer.set_crossfader(0.3)
    print(f"Crossfader position: {mixer.get_crossfader()}")

    # Cleanup
    mixer.cleanup()
    print("\n✓ PyAudio mixer demo complete")


if __name__ == "__main__":
    demo_pyaudio_mixer()
