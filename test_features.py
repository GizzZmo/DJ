#!/usr/bin/env python3
"""
Test suite for new DJ Mixer features
Tests audio effects, beat detection, playlist management, MIDI, recording, and waveforms
"""

import pytest
import numpy as np
from pathlib import Path
import json

# Import modules to test
from audio_effects import AudioEffects, EQSettings, FilterSettings, ReverbSettings, EffectsPresets
from beat_detection import BeatDetector, AutoSync, BeatInfo
from playlist_manager import Playlist, PlaylistTrack, PlaylistManager
from midi_controller import MockMIDIController, MIDIControlType
from recording import AudioRecorder, RecordingSettings, ExportManager
from waveform_display import WaveformGenerator, WaveformDisplay, WaveformCache


class TestAudioEffects:
    """Test audio effects module"""
    
    def test_eq_initialization(self):
        """Test EQ initialization"""
        effects = AudioEffects(sample_rate=44100)
        assert effects.sample_rate == 44100
        assert effects.eq.low == 1.0
        assert effects.eq.mid == 1.0
        assert effects.eq.high == 1.0
    
    def test_set_eq(self):
        """Test setting EQ values"""
        effects = AudioEffects()
        effects.set_eq(low=1.5, mid=0.8, high=1.2)
        assert effects.eq.low == 1.5
        assert effects.eq.mid == 0.8
        assert effects.eq.high == 1.2
    
    def test_eq_clipping(self):
        """Test EQ values are clipped to valid range"""
        effects = AudioEffects()
        effects.set_eq(low=3.0, mid=-0.5, high=1.0)
        assert effects.eq.low == 2.0  # Clipped to max
        assert effects.eq.mid == 0.0  # Clipped to min
    
    def test_filter_settings(self):
        """Test filter configuration"""
        effects = AudioEffects()
        effects.set_filter("lowpass", cutoff_freq=500.0, resonance=2.0)
        assert effects.filter.filter_type == "lowpass"
        assert effects.filter.cutoff_freq == 500.0
        assert effects.filter.resonance == 2.0
    
    def test_invalid_filter_type(self):
        """Test invalid filter type raises error"""
        effects = AudioEffects()
        with pytest.raises(ValueError):
            effects.set_filter("invalid_filter")
    
    def test_reverb_settings(self):
        """Test reverb configuration"""
        effects = AudioEffects()
        effects.set_reverb(room_size=0.8, damping=0.6, wet_level=0.4)
        assert effects.reverb.room_size == 0.8
        assert effects.reverb.damping == 0.6
        assert effects.reverb.wet_level == 0.4
    
    def test_apply_eq_to_audio(self):
        """Test applying EQ to audio data"""
        effects = AudioEffects()
        audio_data = np.random.randint(-1000, 1000, 1024, dtype=np.int16)
        
        processed = effects.apply_eq(audio_data)
        assert len(processed) == len(audio_data)
        assert processed.dtype == audio_data.dtype
    
    def test_apply_filter_to_audio(self):
        """Test applying filter to audio data"""
        effects = AudioEffects()
        effects.set_filter("lowpass", cutoff_freq=1000.0)
        audio_data = np.random.randint(-1000, 1000, 1024, dtype=np.int16)
        
        processed = effects.apply_filter(audio_data)
        assert len(processed) == len(audio_data)
    
    def test_effects_presets(self):
        """Test effects presets"""
        bass_boost = EffectsPresets.bass_boost()
        assert 'eq' in bass_boost
        assert bass_boost['eq']['low'] > 1.0
        
        treble_boost = EffectsPresets.treble_boost()
        assert treble_boost['eq']['high'] > 1.0
    
    def test_reset_effects(self):
        """Test resetting effects to defaults"""
        effects = AudioEffects()
        effects.set_eq(low=1.5, mid=0.5, high=1.8)
        effects.reset()
        assert effects.eq.low == 1.0
        assert effects.eq.mid == 1.0


class TestBeatDetection:
    """Test beat detection module"""
    
    def test_beat_detector_initialization(self):
        """Test beat detector initialization"""
        detector = BeatDetector(sample_rate=44100)
        assert detector.sample_rate == 44100
        assert detector.min_bpm == 60
        assert detector.max_bpm == 200
    
    def test_detect_beats_empty_audio(self):
        """Test beat detection with empty audio"""
        detector = BeatDetector()
        result = detector.detect_beats(np.array([]), 0.0)
        assert result.bpm == 120.0  # Default BPM
        assert len(result.beat_positions) == 0
    
    def test_detect_beats_simple_audio(self):
        """Test beat detection with simple audio"""
        detector = BeatDetector()
        # Create simple audio with some peaks
        audio_data = np.zeros(44100)  # 1 second of audio
        # Add some peaks
        audio_data[0] = 1000
        audio_data[22050] = 1000  # Peak at 0.5s
        
        result = detector.detect_beats(audio_data, 1.0)
        assert result.bpm > 0
        assert isinstance(result.confidence, float)
    
    def test_auto_sync_initialization(self):
        """Test auto sync initialization"""
        auto_sync = AutoSync()
        assert auto_sync.beat_detector is not None
    
    def test_calculate_sync_adjustment(self):
        """Test sync adjustment calculation"""
        auto_sync = AutoSync()
        result = auto_sync.calculate_sync_adjustment(120.0, 125.0)
        
        assert 'sync_possible' in result
        assert 'pitch_adjustment' in result
        assert 'tempo_ratio' in result
        assert result['track1_bpm'] == 120.0
        assert result['track2_bpm'] == 125.0
    
    def test_sync_impossible_large_difference(self):
        """Test sync detection for tracks with large BPM difference"""
        auto_sync = AutoSync()
        result = auto_sync.calculate_sync_adjustment(80.0, 160.0)
        assert result['sync_possible'] == False


class TestPlaylistManagement:
    """Test playlist management module"""
    
    def test_playlist_creation(self):
        """Test creating a new playlist"""
        playlist = Playlist("Test Playlist")
        assert playlist.name == "Test Playlist"
        assert len(playlist.tracks) == 0
        assert playlist.current_index == 0
    
    def test_add_track(self):
        """Test adding tracks to playlist"""
        playlist = Playlist()
        track = PlaylistTrack(
            path="/path/to/track.mp3",
            title="Test Track",
            artist="Test Artist",
            bpm=128.0
        )
        
        assert playlist.add_track(track) == True
        assert len(playlist.tracks) == 1
        assert playlist.tracks[0].title == "Test Track"
    
    def test_remove_track(self):
        """Test removing tracks from playlist"""
        playlist = Playlist()
        track1 = PlaylistTrack(path="/track1.mp3", title="Track 1")
        track2 = PlaylistTrack(path="/track2.mp3", title="Track 2")
        
        playlist.add_track(track1)
        playlist.add_track(track2)
        
        assert playlist.remove_track(0) == True
        assert len(playlist.tracks) == 1
        assert playlist.tracks[0].title == "Track 2"
    
    def test_move_track(self):
        """Test moving track position"""
        playlist = Playlist()
        track1 = PlaylistTrack(path="/track1.mp3", title="Track 1")
        track2 = PlaylistTrack(path="/track2.mp3", title="Track 2")
        
        playlist.add_track(track1)
        playlist.add_track(track2)
        
        assert playlist.move_track(0, 1) == True
        assert playlist.tracks[0].title == "Track 2"
        assert playlist.tracks[1].title == "Track 1"
    
    def test_next_previous_track(self):
        """Test navigation through playlist"""
        playlist = Playlist()
        playlist.add_track(PlaylistTrack(path="/track1.mp3", title="Track 1"))
        playlist.add_track(PlaylistTrack(path="/track2.mp3", title="Track 2"))
        
        # Initially at track 0
        assert playlist.current_index == 0
        
        # Move to next
        track = playlist.next_track()
        assert playlist.current_index == 1
        assert track.title == "Track 2"
        
        # Move to previous
        track = playlist.previous_track()
        assert playlist.current_index == 0
        assert track.title == "Track 1"
    
    def test_filter_by_bpm(self):
        """Test filtering tracks by BPM"""
        playlist = Playlist()
        playlist.add_track(PlaylistTrack(path="/track1.mp3", title="Track 1", bpm=120.0))
        playlist.add_track(PlaylistTrack(path="/track2.mp3", title="Track 2", bpm=140.0))
        playlist.add_track(PlaylistTrack(path="/track3.mp3", title="Track 3", bpm=128.0))
        
        filtered = playlist.filter_by_bpm(125.0, 145.0)
        assert len(filtered) == 2
        assert all(125.0 <= t.bpm <= 145.0 for t in filtered)
    
    def test_sort_by_bpm(self):
        """Test sorting playlist by BPM"""
        playlist = Playlist()
        playlist.add_track(PlaylistTrack(path="/track1.mp3", title="Track 1", bpm=140.0))
        playlist.add_track(PlaylistTrack(path="/track2.mp3", title="Track 2", bpm=120.0))
        playlist.add_track(PlaylistTrack(path="/track3.mp3", title="Track 3", bpm=128.0))
        
        playlist.sort_by_bpm()
        assert playlist.tracks[0].bpm == 120.0
        assert playlist.tracks[1].bpm == 128.0
        assert playlist.tracks[2].bpm == 140.0
    
    def test_playlist_serialization(self):
        """Test playlist to/from dict"""
        playlist = Playlist("Test")
        playlist.add_track(PlaylistTrack(path="/track.mp3", title="Track"))
        
        data = playlist.to_dict()
        assert data['name'] == "Test"
        assert len(data['tracks']) == 1
        
        loaded_playlist = Playlist.from_dict(data)
        assert loaded_playlist.name == "Test"
        assert len(loaded_playlist.tracks) == 1
    
    def test_playlist_manager(self):
        """Test playlist manager"""
        manager = PlaylistManager()
        
        # Create playlists
        playlist1 = manager.create_playlist("Playlist 1")
        playlist2 = manager.create_playlist("Playlist 2")
        
        assert len(manager.get_playlist_names()) == 2
        assert manager.get_current_playlist().name == "Playlist 1"
        
        # Switch playlist
        manager.set_current_playlist("Playlist 2")
        assert manager.get_current_playlist().name == "Playlist 2"
        
        # Delete playlist
        manager.delete_playlist("Playlist 1")
        assert len(manager.get_playlist_names()) == 1


class TestMIDIController:
    """Test MIDI controller module"""
    
    def test_mock_midi_initialization(self):
        """Test mock MIDI controller initialization"""
        controller = MockMIDIController()
        assert controller.connected == False
        assert len(controller.mappings) == 0
    
    def test_mock_midi_connect(self):
        """Test mock MIDI connection"""
        controller = MockMIDIController()
        assert controller.connect() == True
        assert controller.connected == True
    
    def test_add_mapping(self):
        """Test adding MIDI mappings"""
        controller = MockMIDIController()
        controller.add_mapping(
            control_number=1,
            control_type=MIDIControlType.FADER,
            function_name="volume",
            min_value=0.0,
            max_value=1.0
        )
        
        assert 1 in controller.mappings
        assert controller.mappings[1].function_name == "volume"
    
    def test_register_callback(self):
        """Test registering callback functions"""
        controller = MockMIDIController()
        
        called_values = []
        def test_callback(value):
            called_values.append(value)
        
        controller.register_callback("volume", test_callback)
        assert "volume" in controller.callbacks
    
    def test_simulate_control_change(self):
        """Test simulating MIDI control change"""
        controller = MockMIDIController()
        controller.connect()
        
        # Setup mapping and callback
        called_values = []
        def test_callback(value):
            called_values.append(value)
        
        controller.add_mapping(1, MIDIControlType.FADER, "volume")
        controller.register_callback("volume", test_callback)
        
        # Simulate MIDI input
        controller.simulate_control_change(1, 64)  # Half value
        
        assert len(called_values) > 0
        assert 0.0 <= called_values[0] <= 1.0
    
    def test_load_mapping_preset(self):
        """Test loading mapping presets"""
        controller = MockMIDIController()
        result = controller.load_mapping_preset("generic_dj")
        
        assert result == True
        assert len(controller.mappings) > 0


class TestRecording:
    """Test recording module"""
    
    def test_recorder_initialization(self):
        """Test recorder initialization"""
        recorder = AudioRecorder()
        assert recorder.is_recording == False
        assert len(recorder.recorded_data) == 0
    
    def test_start_recording(self):
        """Test starting recording"""
        recorder = AudioRecorder()
        assert recorder.start_recording("test.wav") == True
        assert recorder.is_recording == True
        assert recorder.output_file == "test.wav"
    
    def test_capture_audio(self):
        """Test capturing audio data"""
        recorder = AudioRecorder()
        recorder.start_recording()
        
        audio_data = np.random.randint(-1000, 1000, 1024, dtype=np.int16)
        recorder.capture_audio(audio_data)
        
        assert len(recorder.recorded_data) == 1
    
    def test_pause_resume_recording(self):
        """Test pausing and resuming recording"""
        recorder = AudioRecorder()
        recorder.start_recording()
        
        assert recorder.pause_recording() == True
        assert recorder.is_recording == False
        
        assert recorder.resume_recording() == True
        assert recorder.is_recording == True
    
    def test_get_recording_info(self):
        """Test getting recording information"""
        recorder = AudioRecorder()
        recorder.start_recording("test.wav")
        
        info = recorder.get_recording_info()
        assert 'is_recording' in info
        assert 'duration' in info
        assert 'output_file' in info
        assert info['output_file'] == "test.wav"


class TestWaveformDisplay:
    """Test waveform display module"""
    
    def test_waveform_generator_initialization(self):
        """Test waveform generator initialization"""
        generator = WaveformGenerator(sample_rate=44100)
        assert generator.sample_rate == 44100
    
    def test_generate_waveform(self):
        """Test waveform generation"""
        generator = WaveformGenerator()
        audio_data = np.random.randint(-1000, 1000, 44100, dtype=np.int16)
        
        min_vals, max_vals = generator.generate_waveform(audio_data, width=100)
        
        assert len(min_vals) == 100
        assert len(max_vals) == 100
        assert np.all(min_vals <= max_vals)
    
    def test_generate_waveform_empty_audio(self):
        """Test waveform generation with empty audio"""
        generator = WaveformGenerator()
        min_vals, max_vals = generator.generate_waveform(np.array([]), width=100)
        
        assert len(min_vals) == 0
        assert len(max_vals) == 0
    
    def test_generate_spectrum(self):
        """Test spectrum generation"""
        generator = WaveformGenerator()
        audio_data = np.random.randint(-1000, 1000, 2048, dtype=np.int16)
        
        freqs, mags = generator.generate_spectrum(audio_data)
        
        assert len(freqs) > 0
        assert len(mags) > 0
        assert len(freqs) == len(mags)
    
    def test_waveform_display_initialization(self):
        """Test waveform display initialization"""
        display = WaveformDisplay(width=800, height=200)
        assert display.width == 800
        assert display.height == 200
        assert display.playback_position == 0.0
    
    def test_set_waveform(self):
        """Test setting waveform data"""
        display = WaveformDisplay()
        min_vals = np.random.rand(100)
        max_vals = np.random.rand(100)
        
        display.set_waveform(min_vals, max_vals, duration=180.0)
        assert display.duration == 180.0
        assert display.waveform_data is not None
    
    def test_position_to_pixel(self):
        """Test converting position to pixel"""
        display = WaveformDisplay(width=800)
        display.set_waveform(np.zeros(100), np.zeros(100), duration=180.0)
        
        pixel = display.position_to_pixel(90.0)  # Middle of track
        assert 0 <= pixel <= 800
    
    def test_waveform_cache(self):
        """Test waveform caching"""
        cache = WaveformCache(max_cache_size=5)
        assert len(cache.cache) == 0
        
        cache.clear_cache()
        assert len(cache.cache) == 0


class TestDeviceRouting:
    """Test device routing module"""
    
    def test_device_manager_initialization(self):
        """Test device manager initialization"""
        from device_routing import AudioDeviceManager
        
        manager = AudioDeviceManager()
        assert manager.initialized == False
        assert len(manager.available_devices) == 0
    
    def test_mock_initialization(self):
        """Test mock device initialization"""
        from device_routing import AudioDeviceManager
        
        manager = AudioDeviceManager()
        assert manager.initialize(use_mock=True) == True
        assert manager.initialized == True
        assert len(manager.available_devices) > 0
    
    def test_get_devices(self):
        """Test getting device list"""
        from device_routing import AudioDeviceManager
        
        manager = AudioDeviceManager()
        manager.initialize(use_mock=True)
        
        devices = manager.get_devices(output_only=True)
        assert len(devices) > 0
        assert all(d.max_output_channels > 0 for d in devices)
    
    def test_get_default_output(self):
        """Test getting default output device"""
        from device_routing import AudioDeviceManager
        
        manager = AudioDeviceManager()
        manager.initialize(use_mock=True)
        
        default = manager.get_default_output_device()
        assert default is not None
        assert default.is_default_output == True
    
    def test_add_route(self):
        """Test adding audio route"""
        from device_routing import AudioDeviceManager
        
        manager = AudioDeviceManager()
        manager.initialize(use_mock=True)
        
        devices = manager.get_devices()
        success = manager.add_route("deck1", devices[0].index, [0, 1])
        
        assert success == True
        assert "deck1" in manager.routes
    
    def test_remove_route(self):
        """Test removing audio route"""
        from device_routing import AudioDeviceManager
        
        manager = AudioDeviceManager()
        manager.initialize(use_mock=True)
        
        devices = manager.get_devices()
        manager.add_route("deck1", devices[0].index)
        
        assert manager.remove_route("deck1") == True
        assert "deck1" not in manager.routes
    
    def test_enable_disable_route(self):
        """Test enabling/disabling routes"""
        from device_routing import AudioDeviceManager
        
        manager = AudioDeviceManager()
        manager.initialize(use_mock=True)
        
        devices = manager.get_devices()
        manager.add_route("deck1", devices[0].index)
        
        assert manager.enable_route("deck1", False) == True
        route = manager.get_route("deck1")
        assert route.enabled == False
        
        assert manager.enable_route("deck1", True) == True
        route = manager.get_route("deck1")
        assert route.enabled == True
    
    def test_setup_default_routing(self):
        """Test default routing setup"""
        from device_routing import AudioDeviceManager
        
        manager = AudioDeviceManager()
        manager.initialize(use_mock=True)
        
        assert manager.setup_default_routing() == True
        assert "master" in manager.routes
    
    def test_setup_dj_routing(self):
        """Test DJ routing setup"""
        from device_routing import AudioDeviceManager
        
        manager = AudioDeviceManager()
        manager.initialize(use_mock=True)
        
        assert manager.setup_dj_routing() == True
        assert "master" in manager.routes
        assert "headphone_cue" in manager.routes
    
    def test_get_asio_devices(self):
        """Test getting ASIO devices"""
        from device_routing import AudioDeviceManager
        
        manager = AudioDeviceManager()
        manager.initialize(use_mock=True)
        
        asio_devices = manager.get_asio_devices()
        assert len(asio_devices) > 0
        assert all('ASIO' in d.host_api.upper() for d in asio_devices)
    
    def test_routing_info(self):
        """Test getting routing information"""
        from device_routing import AudioDeviceManager
        
        manager = AudioDeviceManager()
        manager.initialize(use_mock=True)
        manager.setup_dj_routing()
        
        info = manager.get_routing_info()
        
        assert 'initialized' in info
        assert 'devices' in info
        assert 'routes' in info
        assert info['initialized'] == True
        assert len(info['devices']) > 0
        assert len(info['routes']) > 0


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running DJ Mixer Feature Tests")
    print("=" * 60)
    
    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
