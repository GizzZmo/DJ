#!/usr/bin/env python3
"""
Test suite for PyAudio mixer with ASIO support
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import wave

from pyaudio_mixer import PyAudioMixer, PyAudioTrack


class TestPyAudioTrack:
    """Test PyAudioTrack class"""

    def test_track_initialization(self):
        """Test track initialization"""
        track = PyAudioTrack("test.wav", sample_rate=44100)
        assert track.sample_rate == 44100
        assert track.is_loaded is False
        assert track.is_playing is False
        assert track.volume == 1.0

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file"""
        track = PyAudioTrack("nonexistent.wav")
        assert track.load() is False
        assert track.is_loaded is False

    def test_load_valid_file(self):
        """Test loading valid audio file"""
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            # Create a simple WAV file
            with wave.open(temp_path, "w") as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(44100)
                # Write 1 second of silence
                samples = np.zeros(44100 * 2, dtype=np.int16)
                wav_file.writeframes(samples.tobytes())

            track = PyAudioTrack(temp_path)
            assert track.load() is True
            assert track.is_loaded is True
            assert track.duration > 0

        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)

    def test_set_volume(self):
        """Test setting track volume"""
        track = PyAudioTrack("test.wav")
        track.set_volume(0.5)
        assert track.volume == 0.5

        # Test clamping
        track.set_volume(1.5)
        assert track.volume == 1.0

        track.set_volume(-0.5)
        assert track.volume == 0.0

    def test_play_without_loading(self):
        """Test playing without loading"""
        track = PyAudioTrack("test.wav")
        assert track.play() is False

    def test_get_audio_chunk_not_loaded(self):
        """Test getting chunk when not loaded"""
        track = PyAudioTrack("test.wav")
        chunk = track.get_audio_chunk(512)
        assert chunk is None

    def test_get_audio_chunk_not_playing(self):
        """Test getting chunk when not playing"""
        track = PyAudioTrack("test.wav")
        # Mock loading
        track.audio_data = np.zeros((1024, 2), dtype=np.int16)
        track.is_loaded = True
        chunk = track.get_audio_chunk(512)
        assert chunk is None


class TestPyAudioMixer:
    """Test PyAudioMixer class"""

    def test_mixer_initialization(self):
        """Test mixer initialization"""
        mixer = PyAudioMixer(use_mock=True)
        assert mixer.sample_rate == 44100
        assert mixer.buffer_size == 512
        assert mixer.is_initialized is False

    def test_initialize_mixer(self):
        """Test initializing the mixer"""
        mixer = PyAudioMixer(use_mock=True)
        assert mixer.initialize() is True
        assert mixer.is_initialized is True
        mixer.cleanup()

    def test_initialize_with_asio(self):
        """Test initializing with ASIO preference"""
        mixer = PyAudioMixer(use_mock=True)
        assert mixer.initialize(use_asio=True) is True
        assert mixer.is_initialized is True
        # Check that an ASIO device was selected
        assert "ASIO" in mixer.output_device.host_api
        mixer.cleanup()

    def test_load_track_not_initialized(self):
        """Test loading track without initialization"""
        mixer = PyAudioMixer(use_mock=True)
        assert mixer.load_track("deck1", "test.wav") is False

    def test_load_track_invalid_file(self):
        """Test loading nonexistent file"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()
        assert mixer.load_track("deck1", "nonexistent.wav") is False
        mixer.cleanup()

    def test_get_loaded_tracks(self):
        """Test getting loaded track list"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()
        assert len(mixer.get_loaded_tracks()) == 0
        mixer.cleanup()

    def test_play_track_not_found(self):
        """Test playing nonexistent track"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()
        assert mixer.play_track("nonexistent") is False
        mixer.cleanup()

    def test_stop_track(self):
        """Test stopping track"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()
        assert mixer.stop_track("nonexistent") is False
        mixer.cleanup()

    def test_pause_track(self):
        """Test pausing track"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()
        assert mixer.pause_track("nonexistent") is False
        mixer.cleanup()

    def test_unpause_track(self):
        """Test unpausing track"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()
        assert mixer.unpause_track("nonexistent") is False
        mixer.cleanup()

    def test_set_track_volume(self):
        """Test setting track volume"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()

        # Track doesn't exist
        assert mixer.set_track_volume("nonexistent", 0.5) is False

        # Invalid volume
        assert mixer.set_track_volume("deck1", 1.5) is False
        assert mixer.set_track_volume("deck1", -0.5) is False

        mixer.cleanup()

    def test_get_track_volume(self):
        """Test getting track volume"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()
        volume = mixer.get_track_volume("nonexistent")
        assert volume == 0.0
        mixer.cleanup()

    def test_master_volume(self):
        """Test master volume control"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()

        assert mixer.set_master_volume(0.8) is True
        assert mixer.get_master_volume() == 0.8

        # Test clamping
        assert mixer.set_master_volume(1.5) is False
        assert mixer.set_master_volume(-0.5) is False

        mixer.cleanup()

    def test_crossfader(self):
        """Test crossfader control"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()

        assert mixer.set_crossfader(0.3) is True
        assert mixer.get_crossfader() == 0.3

        assert mixer.set_crossfader(0.7) is True
        assert mixer.get_crossfader() == 0.7

        # Test clamping
        assert mixer.set_crossfader(1.5) is False
        assert mixer.set_crossfader(-0.5) is False

        mixer.cleanup()

    def test_apply_crossfader(self):
        """Test applying crossfader"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()

        # Tracks don't exist
        assert mixer.apply_crossfader("deck1", "deck2") is False

        mixer.cleanup()

    def test_get_audio_devices(self):
        """Test getting audio devices"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()

        devices = mixer.get_audio_devices()
        assert len(devices) > 0
        assert all(d.max_output_channels > 0 for d in devices)

        mixer.cleanup()

    def test_get_asio_devices(self):
        """Test getting ASIO devices"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()

        asio_devices = mixer.get_asio_devices()
        assert len(asio_devices) > 0
        assert all("ASIO" in d.host_api for d in asio_devices)

        mixer.cleanup()

    def test_cleanup(self):
        """Test cleanup"""
        mixer = PyAudioMixer(use_mock=True)
        mixer.initialize()
        mixer.cleanup()
        assert mixer.is_running is False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running PyAudio Mixer Tests")
    print("=" * 60)

    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
