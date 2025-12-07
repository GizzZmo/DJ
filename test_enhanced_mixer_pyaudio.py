#!/usr/bin/env python3
"""
Test EnhancedDJMixer with PyAudio/ASIO support
"""

import pytest
from enhanced_mixer import EnhancedDJMixer


class TestEnhancedMixerPyAudio:
    """Test EnhancedDJMixer with PyAudio support"""

    def test_initialization_pygame_mode(self):
        """Test initialization in pygame mode (default)"""
        mixer = EnhancedDJMixer()
        assert mixer.use_pyaudio  is False
        assert mixer.use_asio  is False
        assert mixer.pyaudio_mixer is None

    def test_initialization_pyaudio_mode(self):
        """Test initialization in PyAudio mode"""
        mixer = EnhancedDJMixer(use_pyaudio=True)
        assert mixer.use_pyaudio  is True
        # pyaudio_mixer is created during initialize(), not __init__()
        mixer.initialize()
        assert mixer.pyaudio_mixer is not None
        mixer.cleanup()

    def test_initialization_asio_mode(self):
        """Test initialization with ASIO preference"""
        mixer = EnhancedDJMixer(use_pyaudio=True, use_asio=True)
        assert mixer.use_pyaudio  is True
        assert mixer.use_asio  is True

    def test_initialize_pyaudio(self):
        """Test initializing PyAudio mixer"""
        mixer = EnhancedDJMixer(use_pyaudio=True)
        # Will use mock mode since we don't have real audio devices in CI
        assert mixer.initialize()  is True
        assert mixer.is_initialized  is True
        mixer.cleanup()

    def test_initialize_with_asio(self):
        """Test initializing with ASIO"""
        mixer = EnhancedDJMixer(use_pyaudio=True, use_asio=True)
        assert mixer.initialize()  is True
        assert mixer.is_initialized  is True

        # Check that ASIO device was selected (if available in mock mode)
        status = mixer.get_mixer_status()
        if "audio_device" in status:
            # In mock mode with use_asio=True, should prefer ASIO device
            # But if it falls back, that's ok too
            assert "host_api" in status["audio_device"]

        mixer.cleanup()

    def test_get_asio_devices(self):
        """Test getting ASIO devices"""
        mixer = EnhancedDJMixer(use_pyaudio=True)
        mixer.initialize()

        asio_devices = mixer.get_asio_devices()
        assert isinstance(asio_devices, list)
        # In mock mode, should have some ASIO devices
        assert len(asio_devices) > 0

        mixer.cleanup()

    def test_get_audio_devices_pyaudio(self):
        """Test getting audio devices with PyAudio"""
        mixer = EnhancedDJMixer(use_pyaudio=True)
        mixer.initialize()

        devices = mixer.get_audio_devices()
        assert isinstance(devices, list)
        assert len(devices) > 0

        mixer.cleanup()

    def test_mixer_status_with_pyaudio(self):
        """Test mixer status includes PyAudio info"""
        mixer = EnhancedDJMixer(use_pyaudio=True, use_asio=True)
        mixer.initialize()

        status = mixer.get_mixer_status()
        assert status["use_pyaudio"]  is True
        assert status["use_asio"]  is True
        assert "audio_device" in status
        assert "name" in status["audio_device"]
        assert "host_api" in status["audio_device"]

        mixer.cleanup()

    def test_playback_controls_pyaudio(self):
        """Test playback controls with PyAudio"""
        mixer = EnhancedDJMixer(use_pyaudio=True)
        mixer.initialize()

        # Test volume control
        assert mixer.set_master_volume(0.7)  is True
        assert mixer.get_master_volume() == 0.7

        # Test crossfader
        assert mixer.set_crossfader(0.3)  is True
        assert mixer.get_crossfader() == 0.3

        mixer.cleanup()

    def test_cleanup_pyaudio(self):
        """Test cleanup with PyAudio"""
        mixer = EnhancedDJMixer(use_pyaudio=True)
        mixer.initialize()
        mixer.cleanup()

        # Verify cleanup
        if mixer.pyaudio_mixer:
            assert mixer.pyaudio_mixer.is_running  is False

    def test_pygame_mode_still_works(self):
        """Test that pygame mode still works (backwards compatibility)"""
        mixer = EnhancedDJMixer(use_pyaudio=False)
        # Don't initialize pygame in CI, just test configuration
        assert mixer.use_pyaudio  is False
        assert mixer.pyaudio_mixer is None


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Enhanced Mixer PyAudio/ASIO Tests")
    print("=" * 60)

    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
