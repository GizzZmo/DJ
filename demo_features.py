#!/usr/bin/env python3
"""
Comprehensive demo of all advanced DJ Mixer features
Demonstrates audio effects, beat detection, MIDI, recording, playlists, and waveforms
"""

import time
import numpy as np
from enhanced_mixer import EnhancedDJMixer
from test_mixer import MockDJMixer
from audio_effects import EffectsPresets
from playlist_manager import PlaylistTrack


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_audio_effects():
    """Demo audio effects features"""
    print_section("1. AUDIO EFFECTS DEMO")
    
    mixer = EnhancedDJMixer()
    mixer.initialize()
    
    # Load a mock track
    print("\nLoading track to deck1...")
    mixer.load_track("deck1", "mock_track.mp3", analyze_beats=False)
    
    # Enable effects
    print("Enabling effects on deck1...")
    mixer.enable_track_effects("deck1", True)
    
    # Test EQ
    print("\n--- EQ Controls ---")
    print("Setting bass boost...")
    mixer.set_track_eq("deck1", low=1.8, mid_low=1.2, mid=1.0, mid_high=0.9, high=0.9)
    print("  Low: 1.8, Mid-Low: 1.2, Mid: 1.0, Mid-High: 0.9, High: 0.9")
    
    # Test filters
    print("\n--- Filter Controls ---")
    print("Setting low-pass filter at 800 Hz...")
    mixer.set_track_filter("deck1", "lowpass", cutoff_freq=800.0, resonance=1.5)
    print("  Type: lowpass, Cutoff: 800 Hz, Resonance: 1.5")
    
    # Test reverb
    print("\n--- Reverb Effect ---")
    print("Setting club reverb...")
    mixer.set_track_reverb("deck1", room_size=0.6, damping=0.4, wet_level=0.25, dry_level=0.75)
    print("  Room Size: 0.6, Damping: 0.4, Wet: 0.25, Dry: 0.75")
    
    # Show presets
    print("\n--- Effect Presets ---")
    presets = ["bass_boost", "treble_boost", "vocal_enhance", "club_sound", "telephone_effect"]
    for preset_name in presets:
        preset_method = getattr(EffectsPresets, preset_name)
        preset = preset_method()
        print(f"  {preset_name.replace('_', ' ').title()}: Available")
    
    mixer.cleanup()
    print("\n✓ Audio effects demo complete")


def demo_beat_detection():
    """Demo beat detection and auto-sync"""
    print_section("2. BEAT DETECTION & AUTO-SYNC DEMO")
    
    mixer = EnhancedDJMixer()
    mixer.initialize()
    
    # Load two tracks
    print("\nLoading tracks...")
    mixer.load_track("deck1", "track1.mp3", analyze_beats=True)
    mixer.load_track("deck2", "track2.mp3", analyze_beats=True)
    
    # Get beat info
    print("\n--- Beat Analysis Results ---")
    for deck in ["deck1", "deck2"]:
        beat_info = mixer.get_beat_info(deck)
        if beat_info:
            print(f"{deck.upper()}:")
            print(f"  BPM: {beat_info.bpm}")
            print(f"  Confidence: {beat_info.confidence * 100:.1f}%")
            print(f"  First Beat: {beat_info.first_beat:.2f}s")
            print(f"  Beats Detected: {len(beat_info.beat_positions)}")
    
    # Test auto-sync
    print("\n--- Auto-Sync Analysis ---")
    sync_info = mixer.sync_tracks("deck1", "deck2")
    if "error" not in sync_info:
        print(f"Track 1 BPM: {sync_info['track1_bpm']}")
        print(f"Track 2 BPM: {sync_info['track2_bpm']}")
        print(f"Tempo Ratio: {sync_info['tempo_ratio']}")
        print(f"Pitch Adjustment: {sync_info['pitch_adjustment']:.2f} semitones")
        print(f"Sync Possible: {'Yes' if sync_info['sync_possible'] else 'No'}")
        print(f"Message: {sync_info['message']}")
    
    mixer.cleanup()
    print("\n✓ Beat detection demo complete")


def demo_midi_controller():
    """Demo MIDI controller support"""
    print_section("3. MIDI CONTROLLER DEMO")
    
    mixer = EnhancedDJMixer()
    mixer.initialize()
    
    # Connect MIDI (using mock)
    print("\nConnecting MIDI controller...")
    if mixer.connect_midi(use_mock=True):
        print("✓ MIDI controller connected (Mock)")
    
    # Show available devices
    print("\n--- Available MIDI Devices ---")
    devices = mixer.midi_controller.get_available_devices()
    for i, device in enumerate(devices, 1):
        print(f"  {i}. {device}")
    
    # Show mappings
    print("\n--- MIDI Mappings ---")
    mappings = mixer.midi_controller.get_mappings()
    print(f"Total mappings: {len(mappings)}")
    for mapping in mappings[:5]:  # Show first 5
        print(f"  CC{mapping.control_number}: {mapping.function_name} "
              f"({mapping.control_type.value})")
    
    # Simulate MIDI input
    print("\n--- Simulating MIDI Input ---")
    print("Simulating crossfader movement (CC 0)...")
    mixer.midi_controller.simulate_control_change(0, 64)  # Middle position
    print(f"  Crossfader position: {mixer.get_crossfader():.2f}")
    
    print("\nSimulating volume change (CC 1)...")
    mixer.midi_controller.simulate_control_change(1, 96)  # ~75%
    print(f"  Deck1 volume: {mixer.get_track_volume('deck1'):.2f}")
    
    mixer.cleanup()
    print("\n✓ MIDI controller demo complete")


def demo_recording():
    """Demo recording and export functionality"""
    print_section("4. RECORDING & EXPORT DEMO")
    
    mixer = EnhancedDJMixer()
    mixer.initialize()
    
    # Start recording
    print("\nStarting recording...")
    mixer.start_recording("demo_recording.wav")
    print(f"  Recording: {mixer.is_recording()}")
    
    # Get recording info
    info = mixer.get_recording_info()
    print("\n--- Recording Info ---")
    print(f"  Format: {info['format']}")
    print(f"  Sample Rate: {info['sample_rate']} Hz")
    print(f"  Channels: {info['channels']}")
    print(f"  Output File: {info['output_file']}")
    
    # Simulate some recording time
    print("\nRecording for 2 seconds...")
    for i in range(2):
        time.sleep(1)
        duration = mixer.recorder.get_recording_duration()
        print(f"  Duration: {duration:.1f}s")
    
    # Stop recording
    print("\nStopping recording...")
    mixer.stop_recording()
    print(f"  Recording stopped: {not mixer.is_recording()}")
    
    # Show export formats
    print("\n--- Supported Export Formats ---")
    formats = ["WAV", "MP3", "OGG", "FLAC"]
    for fmt in formats:
        print(f"  ✓ {fmt}")
    
    mixer.cleanup()
    print("\n✓ Recording demo complete")


def demo_playlist_management():
    """Demo playlist management"""
    print_section("5. PLAYLIST MANAGEMENT DEMO")
    
    mixer = EnhancedDJMixer()
    mixer.initialize()
    
    # Create playlist
    print("\nCreating playlist...")
    playlist = mixer.create_playlist("My DJ Set")
    print(f"  Created: {playlist.name}")
    
    # Add tracks
    print("\n--- Adding Tracks ---")
    tracks_data = [
        {"title": "House Track", "artist": "DJ Mix", "bpm": 128.0, "key": "Am"},
        {"title": "Techno Beat", "artist": "Electronic", "bpm": 135.0, "key": "Dm"},
        {"title": "Deep Bass", "artist": "Bass Master", "bpm": 120.0, "key": "Cm"},
        {"title": "Trance Anthem", "artist": "Uplifter", "bpm": 140.0, "key": "F#m"},
    ]
    
    for i, track_data in enumerate(tracks_data, 1):
        track = PlaylistTrack(
            path=f"/path/to/track{i}.mp3",
            title=track_data["title"],
            artist=track_data["artist"],
            bpm=track_data["bpm"],
            key=track_data["key"],
            duration=240.0
        )
        playlist.add_track(track)
        print(f"  Added: {track.title} ({track.bpm} BPM, {track.key})")
    
    # Show playlist info
    print(f"\n--- Playlist Info ---")
    print(f"  Name: {playlist.name}")
    print(f"  Tracks: {playlist.get_track_count()}")
    print(f"  Total Duration: {playlist.get_total_duration() / 60:.1f} minutes")
    
    # Filter by BPM
    print("\n--- Filter by BPM (125-140) ---")
    filtered = playlist.filter_by_bpm(125.0, 140.0)
    for track in filtered:
        print(f"  {track.title}: {track.bpm} BPM")
    
    # Sort by BPM
    print("\n--- Sorted by BPM ---")
    playlist.sort_by_bpm()
    for track in playlist.tracks:
        print(f"  {track.bpm} BPM: {track.title}")
    
    # Navigation
    print("\n--- Playlist Navigation ---")
    current = playlist.get_current_track()
    print(f"  Current: {current.title}")
    
    next_track = playlist.next_track()
    print(f"  Next: {next_track.title}")
    
    prev_track = playlist.previous_track()
    print(f"  Previous: {prev_track.title}")
    
    mixer.cleanup()
    print("\n✓ Playlist management demo complete")


def demo_waveform_display():
    """Demo waveform display and visualization"""
    print_section("6. WAVEFORM DISPLAY DEMO")
    
    from waveform_display import WaveformGenerator, WaveformDisplay
    
    # Generate mock audio
    print("\nGenerating mock audio data...")
    sample_rate = 44100
    duration = 3.0  # 3 seconds
    samples = int(sample_rate * duration)
    
    # Create audio with varying amplitude
    t = np.linspace(0, duration, samples)
    audio = np.sin(2 * np.pi * 440 * t) * np.sin(2 * np.pi * 2 * t)
    audio = (audio * 10000).astype(np.int16)
    
    # Generate waveform
    print("\n--- Generating Waveform ---")
    generator = WaveformGenerator(sample_rate)
    min_vals, max_vals = generator.generate_waveform(audio, width=100)
    
    print(f"  Waveform points: {len(min_vals)}")
    print(f"  Duration: {duration}s")
    print(f"  Sample rate: {sample_rate} Hz")
    
    # Create display
    print("\n--- Waveform Display ---")
    display = WaveformDisplay(width=800, height=200)
    display.set_waveform(min_vals, max_vals, duration)
    
    print(f"  Display width: {display.width} pixels")
    print(f"  Display height: {display.height} pixels")
    
    # Test position conversion
    print("\n--- Position Conversion ---")
    test_positions = [0.0, 1.5, 3.0]
    for pos in test_positions:
        pixel = display.position_to_pixel(pos)
        if pixel >= 0:
            print(f"  {pos:.1f}s → pixel {pixel}")
    
    # Generate spectrum
    print("\n--- Frequency Spectrum ---")
    freqs, mags = generator.generate_spectrum(audio)
    print(f"  Frequency bins: {len(freqs)}")
    print(f"  Frequency range: 0 - {freqs[-1]:.0f} Hz")
    
    # Find peaks
    print("\n--- Peak Detection ---")
    peaks = generator.calculate_peaks(audio)
    print(f"  Peaks detected: {len(peaks)}")
    if peaks:
        print(f"  First peak at sample: {peaks[0]}")
    
    print("\n✓ Waveform display demo complete")


def demo_web_interface():
    """Demo web interface setup"""
    print_section("7. WEB INTERFACE DEMO")
    
    print("\nWeb interface features:")
    print("  ✓ Flask-based REST API")
    print("  ✓ WebSocket for real-time updates")
    print("  ✓ Modern, responsive HTML/CSS/JavaScript UI")
    print("  ✓ Remote control capabilities")
    
    print("\n--- API Endpoints ---")
    endpoints = [
        "GET  /api/status - Get mixer status",
        "POST /api/initialize - Initialize mixer",
        "POST /api/load - Load track",
        "POST /api/play/<deck> - Play track",
        "POST /api/pause/<deck> - Pause track",
        "POST /api/stop/<deck> - Stop track",
        "POST /api/volume/<deck> - Set volume",
        "POST /api/crossfader - Set crossfader",
        "POST /api/master-volume - Set master volume"
    ]
    
    for endpoint in endpoints:
        print(f"  {endpoint}")
    
    print("\n--- WebSocket Events ---")
    events = [
        "connect - Client connected",
        "disconnect - Client disconnected",
        "status_update - Real-time status broadcast",
        "request_status - Request current status"
    ]
    
    for event in events:
        print(f"  {event}")
    
    print("\nTo start web interface:")
    print("  from web_interface import DJMixerWebServer, create_web_templates")
    print("  from test_mixer import MockDJMixer")
    print("  ")
    print("  create_web_templates()")
    print("  mixer = MockDJMixer()")
    print("  mixer.initialize()")
    print("  server = DJMixerWebServer(mixer, port=5000)")
    print("  server.start()")
    print("  ")
    print("  Then open: http://localhost:5000")
    
    print("\n✓ Web interface demo complete")


def demo_comprehensive_status():
    """Demo comprehensive mixer status"""
    print_section("8. COMPREHENSIVE MIXER STATUS")
    
    mixer = EnhancedDJMixer()
    mixer.initialize()
    
    # Setup mixer state
    print("\nSetting up mixer...")
    mixer.load_track("deck1", "track1.mp3")
    mixer.load_track("deck2", "track2.mp3")
    mixer.set_track_volume("deck1", 0.8)
    mixer.set_track_volume("deck2", 0.6)
    mixer.set_crossfader(0.3)
    mixer.enable_track_effects("deck1", True)
    mixer.connect_midi(use_mock=True)
    
    # Create playlist
    playlist = mixer.create_playlist("Demo Set")
    
    # Get comprehensive status
    print("\n--- Complete Mixer Status ---")
    status = mixer.get_mixer_status()
    
    print("\nSystem:")
    print(f"  Initialized: {status['initialized']}")
    print(f"  MIDI Enabled: {status['midi_enabled']}")
    print(f"  Recording: {status['recording']}")
    print(f"  Effects Enabled: {status['effects_enabled']}")
    
    print("\nMixer Controls:")
    print(f"  Master Volume: {status['master_volume']:.2f}")
    print(f"  Crossfader: {status['crossfader']:.2f}")
    
    print("\nTracks:")
    for track_name, track_info in status['tracks'].items():
        print(f"  {track_name.upper()}:")
        print(f"    Volume: {track_info['volume']:.2f}")
        print(f"    Playing: {track_info['playing']}")
        print(f"    Effects: {track_info['effects_enabled']}")
    
    print("\nBeat Info:")
    for track_name, beat_info in status['beat_info'].items():
        print(f"  {track_name.upper()}:")
        print(f"    BPM: {beat_info['bpm']}")
        print(f"    Confidence: {beat_info['confidence'] * 100:.1f}%")
    
    if 'playlist' in status:
        print("\nPlaylist:")
        print(f"  Name: {status['playlist']['name']}")
        print(f"  Tracks: {status['playlist']['track_count']}")
        print(f"  Current: #{status['playlist']['current_index'] + 1}")
    
    mixer.cleanup()
    print("\n✓ Comprehensive status demo complete")


def main():
    """Run all demos"""
    print("=" * 70)
    print("  DJ MIXER - COMPREHENSIVE FEATURES DEMONSTRATION")
    print("=" * 70)
    print("\nThis demo showcases all advanced features:")
    print("  1. Real-time Audio Effects (EQ, Filters, Reverb)")
    print("  2. Beat Detection and Auto-Sync")
    print("  3. MIDI Controller Support")
    print("  4. Recording and Export")
    print("  5. Playlist Management")
    print("  6. Visual Waveform Display")
    print("  7. Web-Based Interface")
    print("  8. Comprehensive Status Monitoring")
    
    input("\nPress Enter to start demos...")
    
    try:
        demo_audio_effects()
        input("\nPress Enter to continue to next demo...")
        
        demo_beat_detection()
        input("\nPress Enter to continue to next demo...")
        
        demo_midi_controller()
        input("\nPress Enter to continue to next demo...")
        
        demo_recording()
        input("\nPress Enter to continue to next demo...")
        
        demo_playlist_management()
        input("\nPress Enter to continue to next demo...")
        
        demo_waveform_display()
        input("\nPress Enter to continue to next demo...")
        
        demo_web_interface()
        input("\nPress Enter to continue to final demo...")
        
        demo_comprehensive_status()
        
        print("\n" + "=" * 70)
        print("  ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n✓ All advanced features demonstrated")
        print("\nNext steps:")
        print("  - Integrate these features into the GUI (dj_gui.py)")
        print("  - Test with real audio files")
        print("  - Connect real MIDI controller")
        print("  - Start web interface for remote control")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
