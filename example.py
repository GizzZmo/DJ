#!/usr/bin/env python3
"""
Example usage of the DJ Mixer
Demonstrates basic functionality and multi-device audio concepts
"""

import time
import sys
from dj_mixer import DJMixer


def demo_basic_functionality():
    """Demonstrate basic DJ mixer functionality"""
    print("╔═══════════════════════════════════╗")
    print("║        DJ MIXER DEMO              ║")
    print("║   Basic Functionality Test       ║")
    print("╚═══════════════════════════════════╝\n")
    
    # Initialize mixer
    mixer = DJMixer()
    if not mixer.initialize():
        print("Failed to initialize mixer")
        return False
    
    print("✓ Mixer initialized successfully")
    
    # Show available devices
    devices = mixer.get_audio_devices()
    print(f"Available audio devices: {devices}")
    
    # Test basic controls
    print("\n--- Testing Basic Controls ---")
    
    # Master volume control
    mixer.set_master_volume(0.8)
    print(f"Master volume set to: {mixer.get_master_volume()}")
    
    # Crossfader control
    mixer.set_crossfader(0.3)
    print(f"Crossfader position: {mixer.get_crossfader()}")
    
    mixer.set_crossfader(0.7)
    print(f"Crossfader moved to: {mixer.get_crossfader()}")
    
    mixer.set_crossfader(0.5)  # Center
    print(f"Crossfader centered at: {mixer.get_crossfader()}")
    
    print("\n--- Audio Loading Test ---")
    
    # Try to load some example files (these won't exist, but we can test the interface)
    test_files = [
        ("deck1", "example_track1.mp3"),
        ("deck2", "example_track2.wav"),
        ("deck3", "background.ogg")
    ]
    
    for name, filename in test_files:
        result = mixer.load_track(name, filename)
        if result:
            print(f"✓ Loaded {name}: {filename}")
        else:
            print(f"✗ Could not load {name}: {filename} (file not found - this is expected for demo)")
    
    # Show loaded tracks
    loaded = mixer.get_loaded_tracks()
    print(f"\nLoaded tracks: {loaded}")
    
    print("\n--- Volume Control Test ---")
    
    # Test volume controls for theoretical tracks
    for name, _ in test_files:
        mixer.set_track_volume(name, 0.6)
        volume = mixer.get_track_volume(name)
        print(f"{name} volume: {volume}")
    
    print("\n--- Crossfader Demo ---")
    
    # Simulate crossfader between two decks
    if len(test_files) >= 2:
        left_deck = test_files[0][0]
        right_deck = test_files[1][0]
        
        print(f"Crossfading between {left_deck} and {right_deck}")
        
        positions = [0.0, 0.25, 0.5, 0.75, 1.0]
        for pos in positions:
            mixer.set_crossfader(pos)
            mixer.apply_crossfader(left_deck, right_deck)
            left_vol = mixer.get_track_volume(left_deck)
            right_vol = mixer.get_track_volume(right_deck)
            print(f"  Position {pos:.2f}: {left_deck}={left_vol:.2f}, {right_deck}={right_vol:.2f}")
    
    # Cleanup
    mixer.cleanup()
    print("\n✓ Demo completed successfully!")
    return True


def create_sample_audio_info():
    """Create information about sample audio files that could be used"""
    print("\n╔═══════════════════════════════════╗")
    print("║       SAMPLE AUDIO INFO           ║")
    print("╚═══════════════════════════════════╝")
    
    sample_files = [
        {
            "name": "Sample Beat 1",
            "file": "beat1.wav", 
            "description": "120 BPM house track",
            "format": "WAV"
        },
        {
            "name": "Sample Beat 2", 
            "file": "beat2.mp3",
            "description": "128 BPM techno track", 
            "format": "MP3"
        },
        {
            "name": "Vocal Sample",
            "file": "vocal.ogg",
            "description": "Vocal loop for mixing",
            "format": "OGG"
        }
    ]
    
    print("\nTo test with real audio files, place audio files in this directory:")
    print("Supported formats: MP3, WAV, OGG, FLAC")
    print("\nExample files you could use:")
    print("-" * 60)
    
    for sample in sample_files:
        print(f"  {sample['name']}")
        print(f"    File: {sample['file']}")
        print(f"    Description: {sample['description']}")
        print(f"    Format: {sample['format']}")
        print()
    
    print("Then use the CLI to load and mix them:")
    print("  python dj_cli.py")
    print("  DJ> init")
    print("  DJ> load deck1 beat1.wav")
    print("  DJ> load deck2 beat2.mp3")
    print("  DJ> play deck1")
    print("  DJ> volume deck1 0.8")
    print("  DJ> crossfader 0.3")


def test_device_concepts():
    """Demonstrate multi-device concepts"""
    print("\n╔═══════════════════════════════════╗")
    print("║     MULTI-DEVICE CONCEPTS         ║")
    print("╚═══════════════════════════════════╝")
    
    print("\nDJ Mixer Multi-Device Support:")
    print("-" * 40)
    print("• Each track can be assigned to different audio devices")
    print("• Crossfader controls mixing between devices")
    print("• Independent volume control per track/device")
    print("• Master volume affects all outputs")
    print("\nTypical DJ Setup:")
    print("• Device 1: Main speakers/PA system")
    print("• Device 2: DJ headphones for cueing")
    print("• Device 3: Secondary output (recording, broadcast)")
    print("\nNote: This implementation uses pygame which abstracts")
    print("device selection. For production use, consider:")
    print("• PyAudio for direct device control")
    print("• ASIO drivers for professional audio interfaces")
    print("• Real-time audio processing libraries")


def main():
    """Main demo function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        create_sample_audio_info()
        test_device_concepts()
        return
    
    print("DJ Mixer Example - Multi-Device Audio Playback")
    print("=" * 50)
    
    # Run basic functionality demo
    success = demo_basic_functionality()
    
    if success:
        create_sample_audio_info()
        test_device_concepts()
        
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("1. Add audio files to this directory")
        print("2. Run: python dj_cli.py")
        print("3. Use the interactive CLI to load and mix tracks")
        print("4. Try: python example.py --info for more details")
    else:
        print("Demo failed. Please check pygame installation:")
        print("pip install -r requirements.txt")


if __name__ == "__main__":
    main()