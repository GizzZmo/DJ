#!/usr/bin/env python3
"""
Pytest-compatible tests for DJ Mixer core functionality
"""

import pytest
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from test_mixer import MockDJMixer


class TestDJMixer:
    """Test suite for DJ Mixer functionality using pytest"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mixer = MockDJMixer()

    def teardown_method(self):
        """Clean up after tests"""
        if hasattr(self.mixer, "cleanup"):
            self.mixer.cleanup()

    def test_mixer_initialization(self):
        """Test mixer initialization"""
        assert self.mixer.initialize() == True
        assert self.mixer.is_initialized == True
        assert self.mixer.sample_rate == 44100
        assert self.mixer.channels == 2

    def test_track_loading(self):
        """Test loading tracks to decks"""
        self.mixer.initialize()

        # Test loading valid tracks
        assert self.mixer.load_track("deck1", "house_track.mp3") == True
        assert self.mixer.load_track("deck2", "techno_beat.wav") == True
        assert self.mixer.load_track("vocal", "vocal_sample.ogg") == True

        # Test that tracks are in the loaded tracks list
        loaded_tracks = self.mixer.get_loaded_tracks()
        assert "deck1" in loaded_tracks
        assert "deck2" in loaded_tracks
        assert "vocal" in loaded_tracks

    def test_playback_control(self):
        """Test play, pause, stop functionality"""
        self.mixer.initialize()
        self.mixer.load_track("deck1", "test_track.mp3")

        # Test play
        assert self.mixer.play_track("deck1") == True
        status = self.mixer.get_track_status("deck1")
        assert status["is_playing"] == True

        # Test pause
        assert self.mixer.pause_track("deck1") == True
        status = self.mixer.get_track_status("deck1")
        assert status["is_playing"] == False

        # Test stop
        assert self.mixer.stop_track("deck1") == True
        status = self.mixer.get_track_status("deck1")
        assert status["is_playing"] == False

    def test_volume_control(self):
        """Test volume controls"""
        self.mixer.initialize()
        self.mixer.load_track("deck1", "test_track.mp3")

        # Test track volume
        assert self.mixer.set_track_volume("deck1", 0.8) == True
        status = self.mixer.get_track_status("deck1")
        assert status["volume"] == 0.8

        # Test master volume
        assert self.mixer.set_master_volume(0.5) == True
        assert self.mixer.get_master_volume() == 0.5

        # Test volume bounds
        assert self.mixer.set_track_volume("deck1", 1.5) == False  # Above max
        assert self.mixer.set_track_volume("deck1", -0.1) == False  # Below min

    def test_crossfader(self):
        """Test crossfader functionality"""
        self.mixer.initialize()
        self.mixer.load_track("deck1", "track1.mp3")
        self.mixer.load_track("deck2", "track2.mp3")

        # Test crossfader position setting
        assert self.mixer.set_crossfader(0.0) == True  # Full left
        assert self.mixer.get_crossfader() == 0.0

        assert self.mixer.set_crossfader(0.5) == True  # Center
        assert self.mixer.get_crossfader() == 0.5

        assert self.mixer.set_crossfader(1.0) == True  # Full right
        assert self.mixer.get_crossfader() == 1.0

        # Test crossfader bounds
        assert self.mixer.set_crossfader(-0.1) == False  # Below min
        assert self.mixer.set_crossfader(1.1) == False  # Above max

        # Test crossfader application
        assert self.mixer.apply_crossfader("deck1", "deck2") == True

    def test_device_management(self):
        """Test audio device management"""
        self.mixer.initialize()

        # Test getting available devices
        devices = self.mixer.get_available_devices()
        assert len(devices) > 0

        # In mock mode, we should have some default devices
        device_names = [device["name"] for device in devices]
        assert "Default Audio Device" in device_names

    def test_mixer_status(self):
        """Test mixer status reporting"""
        self.mixer.initialize()
        self.mixer.load_track("deck1", "test_track.mp3")
        self.mixer.play_track("deck1")
        self.mixer.set_master_volume(0.8)
        self.mixer.set_crossfader(0.3)

        status = self.mixer.get_status()

        # Check that status contains expected keys
        expected_keys = [
            "loaded_tracks",
            "master_volume",
            "crossfader_position",
            "is_initialized",
        ]
        for key in expected_keys:
            assert key in status

        assert status["master_volume"] == 0.8
        assert status["crossfader_position"] == 0.3
        assert status["is_initialized"] == True

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Test operations before initialization
        assert self.mixer.load_track("deck1", "test.mp3") == False
        assert self.mixer.play_track("deck1") == False

        # Test operations on non-existent tracks
        self.mixer.initialize()
        assert self.mixer.play_track("nonexistent") == False
        assert self.mixer.set_track_volume("nonexistent", 0.5) == False


class TestMockAudioTrack:
    """Test suite for MockAudioTrack class"""

    def test_track_creation(self):
        """Test creating mock audio tracks"""
        from test_mixer import MockAudioTrack

        track = MockAudioTrack("test_track.mp3")
        assert track.file_path.name == "test_track.mp3"
        assert track.volume == 1.0
        assert track.is_loaded == False
        assert track.is_playing == False

    def test_track_loading(self):
        """Test track loading"""
        from test_mixer import MockAudioTrack

        track = MockAudioTrack("test_track.mp3")
        assert track.load() == True
        assert track.is_loaded == True

    def test_track_playback(self):
        """Test track playback controls"""
        from test_mixer import MockAudioTrack

        track = MockAudioTrack("test_track.mp3")
        track.load()

        # Test play
        assert track.play() == True
        assert track.is_playing == True

        # Test pause
        assert track.pause() == True
        assert track.is_playing == False

        # Test stop
        assert track.stop() == True
        assert track.is_playing == False


def test_main_functionality():
    """Integration test for main mixer functionality"""
    mixer = MockDJMixer()

    # Initialize mixer
    assert mixer.initialize() == True

    # Load multiple tracks
    tracks = ["house_track.mp3", "techno_beat.wav", "vocal_sample.ogg"]
    deck_names = ["deck1", "deck2", "vocal"]

    for deck, track in zip(deck_names, tracks):
        assert mixer.load_track(deck, track) == True

    # Start playback on some tracks
    assert mixer.play_track("deck1") == True
    assert mixer.play_track("deck2") == True

    # Set volumes
    assert mixer.set_track_volume("deck1", 0.7) == True
    assert mixer.set_track_volume("deck2", 0.6) == True
    assert mixer.set_master_volume(0.8) == True

    # Test crossfader
    crossfader_positions = [0.0, 0.3, 0.5, 0.7, 1.0]
    for pos in crossfader_positions:
        assert mixer.set_crossfader(pos) == True
        assert mixer.apply_crossfader("deck1", "deck2") == True

    # Cleanup
    mixer.cleanup()


if __name__ == "__main__":
    # Run pytest when executed directly
    pytest.main([__file__, "-v"])
