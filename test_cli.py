#!/usr/bin/env python3
"""
Mock CLI version for testing without audio hardware
Uses the mock mixer instead of pygame for testing purposes
"""

import cmd
import os
import sys
from pathlib import Path
from test_mixer import MockDJMixer


class MockDJMixerCLI(cmd.Cmd):
    """Interactive command-line interface for Mock DJ Mixer"""

    intro = """
    ╔═══════════════════════════════════════╗
    ║       MOCK DJ MIXER INTERFACE         ║
    ║   Multi-Device Audio Testing System   ║
    ║        (No Audio Hardware Required)   ║
    ╚═══════════════════════════════════════╝
    
    Type 'help' or '?' to list commands.
    This is a mock version for testing without audio hardware.
    """

    prompt = "MOCK-DJ> "

    def __init__(self):
        super().__init__()
        self.mixer = MockDJMixer()
        self.initialized = False

    def do_init(self, args):
        """Initialize the mock DJ mixer audio system"""
        if self.mixer.initialize():
            self.initialized = True
            print("✓ Mock DJ Mixer initialized successfully!")
            devices = self.mixer.get_audio_devices()
            print(f"Available mock audio devices:")
            for i, device in enumerate(devices, 1):
                print(f"  {i}. {device}")
        else:
            print("✗ Failed to initialize Mock DJ Mixer")

    def do_load(self, args):
        """Load an audio track: load <track_name> <file_path>"""
        if not self.initialized:
            print("Please initialize the mixer first with 'init'")
            return

        parts = args.split()
        if len(parts) < 2:
            print("Usage: load <track_name> <file_path>")
            return

        track_name = parts[0]
        file_path = " ".join(parts[1:])  # Handle paths with spaces

        if self.mixer.load_track(track_name, file_path):
            print(f"✓ Loaded track '{track_name}' from {file_path}")
        else:
            print(f"✗ Failed to load track '{track_name}'")

    def do_play(self, args):
        """Play a track: play <track_name> [loops] [fade_ms]"""
        if not self.initialized:
            print("Please initialize the mixer first with 'init'")
            return

        parts = args.split()
        if len(parts) < 1:
            print("Usage: play <track_name> [loops] [fade_ms]")
            return

        track_name = parts[0]
        loops = int(parts[1]) if len(parts) > 1 else 0
        fade_ms = int(parts[2]) if len(parts) > 2 else 0

        if self.mixer.play_track(track_name, loops, fade_ms):
            print(f"✓ Playing track '{track_name}'")
        else:
            print(f"✗ Failed to play track '{track_name}'")

    def do_stop(self, args):
        """Stop a track: stop <track_name> [fade_ms]"""
        if not self.initialized:
            print("Please initialize the mixer first with 'init'")
            return

        parts = args.split()
        if len(parts) < 1:
            print("Usage: stop <track_name> [fade_ms]")
            return

        track_name = parts[0]
        fade_ms = int(parts[1]) if len(parts) > 1 else 0

        self.mixer.stop_track(track_name, fade_ms)
        print(f"✓ Stopped track '{track_name}'")

    def do_volume(self, args):
        """Set track volume: volume <track_name> <level>"""
        if not self.initialized:
            print("Please initialize the mixer first with 'init'")
            return

        parts = args.split()
        if len(parts) < 2:
            print("Usage: volume <track_name> <level> (0.0 to 1.0)")
            return

        track_name = parts[0]
        try:
            volume = float(parts[1])
            self.mixer.set_track_volume(track_name, volume)
            print(f"✓ Set volume for '{track_name}' to {volume:.2f}")
        except ValueError:
            print("Volume must be a number between 0.0 and 1.0")

    def do_master(self, args):
        """Set master volume: master <level>"""
        if not self.initialized:
            print("Please initialize the mixer first with 'init'")
            return

        if not args:
            print(f"Current master volume: {self.mixer.get_master_volume():.2f}")
            return

        try:
            volume = float(args)
            self.mixer.set_master_volume(volume)
            print(f"✓ Set master volume to {volume:.2f}")
        except ValueError:
            print("Volume must be a number between 0.0 and 1.0")

    def do_crossfader(self, args):
        """Set crossfader position: crossfader <position>"""
        if not self.initialized:
            print("Please initialize the mixer first with 'init'")
            return

        if not args:
            pos = self.mixer.get_crossfader()
            print(
                f"Current crossfader position: {pos:.2f} ({'LEFT' if pos < 0.3 else 'RIGHT' if pos > 0.7 else 'CENTER'})"
            )
            return

        try:
            position = float(args)
            self.mixer.set_crossfader(position)
            pos_desc = (
                "LEFT" if position < 0.3 else "RIGHT" if position > 0.7 else "CENTER"
            )
            print(f"✓ Set crossfader to {position:.2f} ({pos_desc})")
        except ValueError:
            print(
                "Position must be a number between 0.0 (full left) and 1.0 (full right)"
            )

    def do_cross(self, args):
        """Apply crossfader between two tracks: cross <left_track> <right_track>"""
        if not self.initialized:
            print("Please initialize the mixer first with 'init'")
            return

        parts = args.split()
        if len(parts) < 2:
            print("Usage: cross <left_track> <right_track>")
            return

        left_track = parts[0]
        right_track = parts[1]
        self.mixer.apply_crossfader(left_track, right_track)
        pos = self.mixer.get_crossfader()
        print(
            f"✓ Applied crossfader ({pos:.2f}) between '{left_track}' and '{right_track}'"
        )

    def do_status(self, args):
        """Show mixer status and loaded tracks"""
        if not self.initialized:
            print("Mixer not initialized")
            return

        print("\n" + "═" * 50)
        print("MOCK DJ MIXER STATUS")
        print("═" * 50)
        print(f"Master Volume: {self.mixer.get_master_volume():.2f}")
        print(f"Crossfader: {self.mixer.get_crossfader():.2f}")

        tracks = self.mixer.get_loaded_tracks()
        if tracks:
            print(f"\nLoaded Tracks ({len(tracks)}):")
            print("-" * 30)
            for track_name in tracks:
                volume = self.mixer.get_track_volume(track_name)
                playing = (
                    "PLAYING" if self.mixer.is_track_playing(track_name) else "STOPPED"
                )
                print(f"  {track_name}: Vol={volume:.2f} [{playing}]")
        else:
            print("\nNo tracks loaded")
        print("═" * 50 + "\n")

    def do_demo(self, args):
        """Run a quick demo of the mixer functionality"""
        if not self.initialized:
            print("Please initialize the mixer first with 'init'")
            return

        print("\n🎧 Running Quick Demo...")
        print("-" * 30)

        # Load demo tracks
        demo_tracks = [("deck1", "demo_house.mp3"), ("deck2", "demo_techno.wav")]

        for name, file in demo_tracks:
            self.mixer.load_track(name, file)

        # Demo mixing sequence
        print("\n1. Playing both decks...")
        self.mixer.play_track("deck1")
        self.mixer.play_track("deck2")

        print("2. Setting initial volumes...")
        self.mixer.set_track_volume("deck1", 0.8)
        self.mixer.set_track_volume("deck2", 0.6)

        print("3. Crossfading demonstration...")
        positions = [0.0, 0.3, 0.5, 0.7, 1.0]
        for pos in positions:
            self.mixer.set_crossfader(pos)
            self.mixer.apply_crossfader("deck1", "deck2")

        print("4. Final status:")
        self.do_status("")

        print("✓ Demo completed!")

    def do_quit(self, args):
        """Quit the mock DJ mixer"""
        if self.initialized:
            self.mixer.cleanup()
        print("Goodbye! Thanks for testing the Mock DJ Mixer!")
        return True

    def do_exit(self, args):
        """Exit the mock DJ mixer (same as quit)"""
        return self.do_quit(args)

    def do_EOF(self, args):
        """Handle Ctrl+D"""
        print()
        return self.do_quit(args)


def main():
    """Main entry point for the mock CLI"""
    try:
        cli = MockDJMixerCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
