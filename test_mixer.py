#!/usr/bin/env python3
"""
Test version of DJ Mixer that can run without audio hardware
Useful for testing the interface and logic without requiring actual audio devices
"""

import time
from typing import Dict, List, Optional
from pathlib import Path


class MockAudioTrack:
    """Mock audio track for testing without actual audio hardware"""

    def __init__(self, file_path: str, device_id: Optional[int] = None):
        self.file_path = Path(file_path)
        self.device_id = device_id
        self.volume = 1.0
        self.is_loaded = False
        self.is_playing = False
        self.position = 0.0  # Track position in seconds
        self.duration = 180.0  # Mock 3-minute track
        self.start_time = None

    def load(self) -> bool:
        """Mock load the audio file"""
        # In a real implementation, this would check if file exists and is valid
        self.is_loaded = True
        print(f"[MOCK] Loaded: {self.file_path.name}")
        return True

    def play(self, loops: int = 0, fade_ms: int = 0) -> bool:
        """Mock play the track"""
        if not self.is_loaded:
            print("[MOCK] Track not loaded")
            return False

        self.is_playing = True
        self.start_time = time.time()
        print(
            f"[MOCK] Playing: {self.file_path.name} (loops={loops}, fade={fade_ms}ms)"
        )
        return True

    def stop(self, fade_ms: int = 0) -> bool:
        """Mock stop the track"""
        self.is_playing = False
        self.start_time = None
        print(f"[MOCK] Stopped: {self.file_path.name} (fade={fade_ms}ms)")
        return True

    def pause(self) -> bool:
        """Mock pause the track"""
        if self.is_playing:
            self.is_playing = False
            print(f"[MOCK] Paused: {self.file_path.name}")
            return True
        return False

    def unpause(self) -> None:
        """Mock unpause the track"""
        if not self.is_playing:
            self.is_playing = True
            self.start_time = time.time()
            print(f"[MOCK] Unpaused: {self.file_path.name}")

    def set_volume(self, volume: float) -> None:
        """Set track volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        print(f"[MOCK] Volume for {self.file_path.name}: {self.volume:.2f}")

    def get_volume(self) -> float:
        """Get current volume"""
        return self.volume

    def is_track_playing(self) -> bool:
        """Check if track is currently playing"""
        return self.is_playing

    def get_position(self) -> float:
        """Get current playback position"""
        if self.is_playing and self.start_time:
            return time.time() - self.start_time
        return self.position


class MockDJMixer:
    """Mock DJ Mixer class for testing without audio hardware"""

    def __init__(
        self,
        frequency: int = 44100,
        size: int = -16,
        channels: int = 2,
        buffer: int = 512,
    ):
        """Initialize the mock DJ mixer"""
        self.frequency = frequency
        self.size = size
        self.channels = channels
        self.buffer = buffer
        self.sample_rate = frequency  # Add missing sample_rate attribute
        self.tracks: Dict[str, MockAudioTrack] = {}
        self.crossfader_position = 0.5  # 0.0 = full left, 1.0 = full right
        self.master_volume = 1.0
        self.is_initialized = False
        self.mock_devices = [
            "Default Audio Device",
            "Headphones (Realtek)",
            "Speakers (USB Audio)",
            "Line Out (Audio Interface)",
        ]

    def initialize(self) -> bool:
        """Initialize mock mixer"""
        self.is_initialized = True
        print(
            f"[MOCK] DJ Mixer initialized: {self.frequency}Hz, {self.channels} channels"
        )
        return True

    def get_audio_devices(self) -> List[str]:
        """Get mock list of available audio devices"""
        return self.mock_devices

    def load_track(
        self, name: str, file_path: str, device_id: Optional[int] = None
    ) -> bool:
        """Load a mock audio track"""
        if not self.is_initialized:
            print("[MOCK] Mixer not initialized")
            return False

        track = MockAudioTrack(file_path, device_id)
        if track.load():
            self.tracks[name] = track
            return True
        return False

    def play_track(self, name: str, loops: int = 0, fade_ms: int = 0) -> bool:
        """Play a mock track"""
        if name not in self.tracks:
            print(f"[MOCK] Track '{name}' not found")
            return False
        return self.tracks[name].play(loops, fade_ms)

    def stop_track(self, name: str, fade_ms: int = 0) -> bool:
        """Stop a mock track"""
        if name not in self.tracks:
            return False
        self.tracks[name].stop(fade_ms)
        return True

    def pause_track(self, name: str) -> bool:
        """Pause a mock track"""
        if name not in self.tracks:
            return False
        self.tracks[name].pause()
        return True

    def unpause_track(self, name: str) -> None:
        """Unpause a mock track"""
        if name in self.tracks:
            self.tracks[name].unpause()

    def set_track_volume(self, name: str, volume: float) -> bool:
        """Set volume for a specific track"""
        if name not in self.tracks:
            print(f"[MOCK] Track '{name}' not found")
            return False
        if volume < 0.0 or volume > 1.0:
            return False
        self.tracks[name].set_volume(volume)
        return True

    def get_track_volume(self, name: str) -> float:
        """Get volume for a specific track"""
        if name in self.tracks:
            return self.tracks[name].get_volume()
        return 0.0

    def set_crossfader(self, position: float) -> bool:
        """Set crossfader position (0.0 = full left, 1.0 = full right)"""
        if position < 0.0 or position > 1.0:
            return False
        self.crossfader_position = max(0.0, min(1.0, position))
        print(f"[MOCK] Crossfader position: {self.crossfader_position:.2f}")
        return True

    def get_crossfader(self) -> float:
        """Get crossfader position"""
        return self.crossfader_position

    def apply_crossfader(self, left_track: str, right_track: str) -> bool:
        """Apply crossfader effect between two tracks"""
        if left_track not in self.tracks or right_track not in self.tracks:
            return False
        left_volume = (1.0 - self.crossfader_position) * self.master_volume
        right_volume = self.crossfader_position * self.master_volume

        self.tracks[left_track].set_volume(left_volume)
        self.tracks[right_track].set_volume(right_volume)
        print(
            f"[MOCK] Crossfader applied: {left_track}={left_volume:.2f}, {right_track}={right_volume:.2f}"
        )
        return True

    def set_master_volume(self, volume: float) -> bool:
        """Set master volume"""
        if volume < 0.0 or volume > 1.0:
            return False
        self.master_volume = max(0.0, min(1.0, volume))
        print(f"[MOCK] Master volume: {self.master_volume:.2f}")
        return True

    def get_master_volume(self) -> float:
        """Get master volume"""
        return self.master_volume

    def is_track_playing(self, name: str) -> bool:
        """Check if a track is playing"""
        if name in self.tracks:
            return self.tracks[name].is_track_playing()
        return False

    def get_loaded_tracks(self) -> List[str]:
        """Get list of loaded track names"""
        return list(self.tracks.keys())

    def get_track_status(self, name: str) -> dict:
        """Get status information for a specific track"""
        if name not in self.tracks:
            return {"error": "Track not found"}
        track = self.tracks[name]
        return {
            "is_playing": track.is_track_playing(),
            "volume": track.get_volume(),
            "file_path": str(track.file_path),
            "is_loaded": track.is_loaded,
        }

    def get_available_devices(self) -> List[dict]:
        """Get list of available mock audio devices"""
        devices = []
        for i, device_name in enumerate(self.mock_devices):
            devices.append({"id": i, "name": device_name})
        return devices

    def get_status(self) -> dict:
        """Get comprehensive mixer status"""
        return {
            "loaded_tracks": self.get_loaded_tracks(),
            "master_volume": self.master_volume,
            "crossfader_position": self.crossfader_position,
            "is_initialized": self.is_initialized,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
        }

    def cleanup(self) -> None:
        """Clean up resources"""
        for track in self.tracks.values():
            track.stop()
        self.is_initialized = False
        print("[MOCK] DJ Mixer cleaned up")


def test_mock_mixer():
    """Test the mock DJ mixer functionality"""
    print("╔═══════════════════════════════════╗")
    print("║     MOCK DJ MIXER TEST            ║")
    print("║   Testing Without Audio Hardware  ║")
    print("╚═══════════════════════════════════╝\n")

    # Initialize mixer
    mixer = MockDJMixer()
    if not mixer.initialize():
        print("Failed to initialize mock mixer")
        return False

    print("✓ Mock mixer initialized successfully")

    # Show available devices
    devices = mixer.get_audio_devices()
    print("Available mock audio devices:")
    for i, device in enumerate(devices):
        print(f"  {i+1}. {device}")
    print()

    # Load some test tracks
    test_tracks = [
        ("deck1", "house_track.mp3"),
        ("deck2", "techno_beat.wav"),
        ("vocal", "vocal_sample.ogg"),
    ]

    print("--- Loading Test Tracks ---")
    for name, filename in test_tracks:
        mixer.load_track(name, filename)

    # Test playback
    print("\n--- Testing Playback ---")
    mixer.play_track("deck1")
    mixer.play_track("deck2")

    # Test volume controls
    print("\n--- Testing Volume Controls ---")
    mixer.set_master_volume(0.8)
    mixer.set_track_volume("deck1", 0.7)
    mixer.set_track_volume("deck2", 0.6)

    # Test crossfading
    print("\n--- Testing Crossfader ---")
    positions = [0.0, 0.3, 0.5, 0.7, 1.0]
    for pos in positions:
        mixer.set_crossfader(pos)
        mixer.apply_crossfader("deck1", "deck2")
        time.sleep(0.5)  # Brief pause to simulate real-time adjustment

    # Show status
    print("\n--- Final Status ---")
    tracks = mixer.get_loaded_tracks()
    print(f"Loaded tracks: {tracks}")
    for track_name in tracks:
        playing = mixer.is_track_playing(track_name)
        volume = mixer.get_track_volume(track_name)
        print(
            f"  {track_name}: {'PLAYING' if playing else 'STOPPED'}, Volume: {volume:.2f}"
        )

    print(f"Master volume: {mixer.get_master_volume():.2f}")
    print(f"Crossfader position: {mixer.get_crossfader():.2f}")

    # Cleanup
    mixer.cleanup()
    print("\n✓ Mock test completed successfully!")
    return True


if __name__ == "__main__":
    test_mock_mixer()
