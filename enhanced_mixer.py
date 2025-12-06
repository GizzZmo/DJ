#!/usr/bin/env python3
"""
Enhanced DJ Mixer with all advanced features
Integrates audio effects, beat detection, MIDI, recording, and more
"""

from typing import Dict, List, Optional
from pathlib import Path
import numpy as np

from dj_mixer import DJMixer, AudioTrack
from audio_effects import AudioEffects
from beat_detection import BeatDetector, AutoSync, BeatInfo
from playlist_manager import PlaylistManager, Playlist
from midi_controller import MIDIController, MockMIDIController
from recording import AudioRecorder, RecordingSettings
from waveform_display import WaveformCache


class EnhancedAudioTrack(AudioTrack):
    """Enhanced audio track with effects and beat detection"""

    def __init__(self, file_path: str, device_id: Optional[int] = None):
        super().__init__(file_path, device_id)
        self.effects = AudioEffects()
        self.beat_info: Optional[BeatInfo] = None
        self.effects_enabled = False

    def enable_effects(self, enabled: bool = True):
        """Enable or disable effects processing"""
        self.effects_enabled = enabled

    def set_eq(
        self,
        low: float = 1.0,
        mid_low: float = 1.0,
        mid: float = 1.0,
        mid_high: float = 1.0,
        high: float = 1.0,
    ):
        """Set EQ for this track"""
        self.effects.set_eq(low, mid_low, mid, mid_high, high)

    def set_filter(
        self, filter_type: str, cutoff_freq: float = 1000.0, resonance: float = 1.0
    ):
        """Set filter for this track"""
        self.effects.set_filter(filter_type, cutoff_freq, resonance)

    def set_reverb(
        self,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.3,
        dry_level: float = 0.7,
    ):
        """Set reverb for this track"""
        self.effects.set_reverb(room_size, damping, wet_level, dry_level)


class EnhancedDJMixer(DJMixer):
    """Enhanced DJ Mixer with all advanced features"""

    def __init__(
        self,
        frequency: int = 44100,
        size: int = -16,
        channels: int = 2,
        buffer: int = 512,
    ):
        super().__init__(frequency, size, channels, buffer)

        # Advanced features
        self.beat_detector = BeatDetector(sample_rate=frequency)
        self.auto_sync = AutoSync()
        self.playlist_manager = PlaylistManager()
        self.waveform_cache = WaveformCache()
        self.recorder = AudioRecorder()

        # MIDI controller (use mock by default)
        self.midi_controller = MockMIDIController()
        self.midi_enabled = False

        # Beat info for each track
        self.beat_info: Dict[str, BeatInfo] = {}

        # Effects enabled flag
        self.effects_enabled = False

    def load_track(
        self,
        name: str,
        file_path: str,
        device_id: Optional[int] = None,
        analyze_beats: bool = True,
    ) -> bool:
        """Load track with enhanced features"""
        if not self.is_initialized:
            print("Mixer not initialized")
            return False

        # Load track using enhanced track class
        track = EnhancedAudioTrack(file_path, device_id)
        if track.load():
            self.tracks[name] = track

            # Analyze beats if requested
            if analyze_beats:
                self.analyze_track_beats(name)

            # Generate waveform (cache it)
            self.waveform_cache.get_waveform(file_path, width=1000)

            return True
        return False

    def analyze_track_beats(self, name: str) -> Optional[BeatInfo]:
        """Analyze beats for a track"""
        if name not in self.tracks:
            return None

        track = self.tracks[name]
        # For now, use mock beat detection (would need actual audio data)
        # In a real implementation, we'd read the audio file and analyze it

        # Mock beat info - example 128 BPM track
        MOCK_BPM = 128.0
        BEAT_INTERVAL = 60.0 / MOCK_BPM  # 0.46875 seconds per beat

        # Generate mock beat positions
        mock_beat_positions = [i * BEAT_INTERVAL for i in range(8)]

        beat_info = BeatInfo(
            bpm=MOCK_BPM,
            beat_positions=mock_beat_positions[:4],
            beat_grid=mock_beat_positions[:5],
            confidence=0.85,
            first_beat=0.0,
        )

        self.beat_info[name] = beat_info

        if isinstance(track, EnhancedAudioTrack):
            track.beat_info = beat_info

        return beat_info

    def get_beat_info(self, name: str) -> Optional[BeatInfo]:
        """Get beat information for a track"""
        return self.beat_info.get(name)

    def sync_tracks(self, track1: str, track2: str) -> dict:
        """Calculate sync information between two tracks"""
        beat1 = self.beat_info.get(track1)
        beat2 = self.beat_info.get(track2)

        if not beat1 or not beat2:
            return {"error": "Beat info not available for both tracks"}

        return self.auto_sync.calculate_sync_adjustment(beat1.bpm, beat2.bpm)

    def enable_track_effects(self, name: str, enabled: bool = True) -> bool:
        """Enable effects for a specific track"""
        if name not in self.tracks:
            return False

        track = self.tracks[name]
        if isinstance(track, EnhancedAudioTrack):
            track.enable_effects(enabled)
            return True
        return False

    def set_track_eq(
        self,
        name: str,
        low: float = 1.0,
        mid_low: float = 1.0,
        mid: float = 1.0,
        mid_high: float = 1.0,
        high: float = 1.0,
    ) -> bool:
        """Set EQ for a track"""
        if name not in self.tracks:
            return False

        track = self.tracks[name]
        if isinstance(track, EnhancedAudioTrack):
            track.set_eq(low, mid_low, mid, mid_high, high)
            return True
        return False

    def set_track_filter(
        self,
        name: str,
        filter_type: str,
        cutoff_freq: float = 1000.0,
        resonance: float = 1.0,
    ) -> bool:
        """Set filter for a track"""
        if name not in self.tracks:
            return False

        track = self.tracks[name]
        if isinstance(track, EnhancedAudioTrack):
            track.set_filter(filter_type, cutoff_freq, resonance)
            return True
        return False

    def set_track_reverb(
        self,
        name: str,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.3,
        dry_level: float = 0.7,
    ) -> bool:
        """Set reverb for a track"""
        if name not in self.tracks:
            return False

        track = self.tracks[name]
        if isinstance(track, EnhancedAudioTrack):
            track.set_reverb(room_size, damping, wet_level, dry_level)
            return True
        return False

    def start_recording(self, output_file: Optional[str] = None) -> bool:
        """Start recording mixer output"""
        return self.recorder.start_recording(output_file)

    def stop_recording(self) -> bool:
        """Stop recording and save"""
        return self.recorder.stop_recording()

    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.recorder.is_recording

    def get_recording_info(self) -> dict:
        """Get recording information"""
        return self.recorder.get_recording_info()

    def connect_midi(
        self, device_name: Optional[str] = None, use_mock: bool = True
    ) -> bool:
        """Connect MIDI controller"""
        if use_mock:
            self.midi_controller = MockMIDIController()
        else:
            self.midi_controller = MIDIController()

        success = self.midi_controller.connect(device_name)
        if success:
            self.midi_enabled = True
            self._setup_midi_mappings()
        return success

    def _setup_midi_mappings(self):
        """Setup default MIDI mappings"""
        # Load generic DJ preset
        self.midi_controller.load_mapping_preset("generic_dj")

        # Register callbacks
        self.midi_controller.register_callback(
            "crossfader", lambda v: self.set_crossfader(v)
        )
        self.midi_controller.register_callback(
            "deck1_volume", lambda v: self.set_track_volume("deck1", v)
        )
        self.midi_controller.register_callback(
            "deck2_volume", lambda v: self.set_track_volume("deck2", v)
        )
        self.midi_controller.register_callback(
            "master_volume", lambda v: self.set_master_volume(v)
        )
        self.midi_controller.register_callback(
            "deck1_play", lambda v: self.play_track("deck1") if v else None
        )
        self.midi_controller.register_callback(
            "deck2_play", lambda v: self.play_track("deck2") if v else None
        )

    def poll_midi(self):
        """Poll for MIDI events (call regularly in main loop)"""
        if self.midi_enabled:
            self.midi_controller.poll_messages()

    def get_current_playlist(self) -> Optional[Playlist]:
        """Get current playlist"""
        return self.playlist_manager.get_current_playlist()

    def create_playlist(self, name: str) -> Playlist:
        """Create a new playlist"""
        return self.playlist_manager.create_playlist(name)

    def load_playlist_track(self, deck: str, track_index: Optional[int] = None) -> bool:
        """Load a track from current playlist to a deck"""
        playlist = self.get_current_playlist()
        if not playlist:
            return False

        if track_index is not None:
            track = playlist.get_track(track_index)
        else:
            track = playlist.get_current_track()

        if not track:
            return False

        return self.load_track(deck, track.path)

    def next_playlist_track(self) -> bool:
        """Move to next track in playlist"""
        playlist = self.get_current_playlist()
        if playlist:
            playlist.next_track()
            return True
        return False

    def previous_playlist_track(self) -> bool:
        """Move to previous track in playlist"""
        playlist = self.get_current_playlist()
        if playlist:
            playlist.previous_track()
            return True
        return False

    def get_mixer_status(self) -> dict:
        """Get comprehensive mixer status"""
        status = {
            "initialized": self.is_initialized,
            "master_volume": self.get_master_volume(),
            "crossfader": self.get_crossfader(),
            "loaded_tracks": self.get_loaded_tracks(),
            "recording": self.is_recording(),
            "midi_enabled": self.midi_enabled,
            "effects_enabled": self.effects_enabled,
            "tracks": {},
            "beat_info": {},
        }

        for track_name in self.get_loaded_tracks():
            status["tracks"][track_name] = {
                "volume": self.get_track_volume(track_name),
                "playing": self.is_track_playing(track_name),
                "effects_enabled": False,
            }

            track = self.tracks.get(track_name)
            if isinstance(track, EnhancedAudioTrack):
                status["tracks"][track_name]["effects_enabled"] = track.effects_enabled

            # Add beat info
            beat_info = self.beat_info.get(track_name)
            if beat_info:
                status["beat_info"][track_name] = {
                    "bpm": beat_info.bpm,
                    "confidence": beat_info.confidence,
                }

        # Add playlist info
        playlist = self.get_current_playlist()
        if playlist:
            status["playlist"] = {
                "name": playlist.name,
                "track_count": playlist.get_track_count(),
                "current_index": playlist.current_index,
            }

        return status


def main():
    """Example usage of enhanced DJ mixer"""
    print("=" * 60)
    print("Enhanced DJ Mixer Demo (Mock Mode)")
    print("=" * 60)

    # Use mock mixer for demo - just show features
    from test_mixer import MockDJMixer
    from playlist_manager import PlaylistManager
    from midi_controller import MockMIDIController
    from recording import AudioRecorder

    mixer = MockDJMixer()

    if not mixer.initialize():
        print("Failed to initialize mixer")
        return

    print("\n✓ Mock mixer initialized")

    # Demo features separately
    print("\n--- Advanced Features Available ---")
    print("  ✓ Audio Effects (EQ, Filters, Reverb)")
    print("  ✓ Beat Detection and Auto-Sync")
    print("  ✓ MIDI Controller Support")
    print("  ✓ Recording and Export")
    print("  ✓ Playlist Management")
    print("  ✓ Waveform Display")
    print("  ✓ Web Interface")

    # Demo individual components
    print("\n--- Playlist Management ---")
    playlist_mgr = PlaylistManager()
    playlist = playlist_mgr.create_playlist("Demo Playlist")
    print(f"Created playlist: {playlist.name}")

    # Demo MIDI
    print("\n--- MIDI Controller ---")
    midi = MockMIDIController()
    if midi.connect():
        print("✓ MIDI controller connected (mock)")
        midi.disconnect()

    # Demo recording
    print("\n--- Recording ---")
    recorder = AudioRecorder()
    recorder.start_recording("demo_mix.wav")
    print(f"Recording started: {recorder.is_recording}")
    recorder.stop_recording()
    print("Recording stopped")

    print("\n--- Mixer Status ---")
    print(f"Initialized: {mixer.is_initialized}")
    print(f"Master Volume: {mixer.get_master_volume():.2f}")
    print(f"Crossfader: {mixer.get_crossfader():.2f}")

    # Cleanup
    mixer.cleanup()
    print("\n✓ Demo complete - see demo_features.py for full demonstration")


if __name__ == "__main__":
    main()
