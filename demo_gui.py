#!/usr/bin/env python3
"""
Demo script showing the DJ GUI in action
This demonstrates the GUI functionality with mock audio
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
from dj_gui import DJMixerGUI

class DemoGUI(DJMixerGUI):
    """Demo version of the GUI with mock functionality"""
    
    def __init__(self):
        super().__init__()
        self.demo_mode = True
        self.root.title("DJ Mixer GUI - DEMO MODE (Mock Audio)")
        
        # Pre-populate with demo tracks
        self.deck1_file.set("demo_house_track.mp3")
        self.deck2_file.set("demo_techno_beat.wav")
        
        # Auto-initialize for demo
        self.root.after(1000, self.auto_demo_init)
    
    def auto_demo_init(self):
        """Auto-initialize the mixer for demo"""
        self.initialized = True
        self.status_label.config(text="Demo mixer initialized", foreground="green")
        self.init_button.config(text="Demo Mode Active", state=tk.DISABLED)
        self.log_message("🎵 Demo mode activated - all audio is simulated")
        self.log_message("✓ Mock mixer initialized successfully!")
        self.log_message("Available devices: Demo Device 1, Demo Device 2")
        
    def load_track(self, deck_name, file_var):
        """Mock track loading for demo"""
        demo_tracks = [
            "demo_house_track.mp3",
            "demo_techno_beat.wav", 
            "demo_vocal_sample.ogg",
            "demo_bass_drop.flac",
            "demo_ambient_pad.wav"
        ]
        
        # Simulate file selection
        import random
        selected_track = random.choice(demo_tracks)
        file_var.set(selected_track)
        self.log_message(f"✓ Demo track {selected_track} loaded into {deck_name.upper()}")
    
    def play_track(self, deck_name):
        """Mock track playing for demo"""
        self.log_message(f"▶️ Playing {deck_name.upper()} - {getattr(self, f'{deck_name}_file').get()}")
        
        # Simulate playing status
        if deck_name == "deck1":
            self.deck1_status.set("PLAYING")
        else:
            self.deck2_status.set("PLAYING")
    
    def stop_track(self, deck_name):
        """Mock track stopping for demo"""
        self.log_message(f"⏹ Stopped {deck_name.upper()}")
        
        if deck_name == "deck1":
            self.deck1_status.set("STOPPED")
        else:
            self.deck2_status.set("STOPPED")
    
    def pause_track(self, deck_name):
        """Mock track pausing for demo"""
        self.log_message(f"⏸ Paused {deck_name.upper()}")
        
        if deck_name == "deck1":
            self.deck1_status.set("PAUSED")
        else:
            self.deck2_status.set("PAUSED")

def run_demo():
    """Run the demo GUI"""
    print("Starting DJ Mixer GUI Demo...")
    print("This demo shows the GUI interface with mock audio functionality.")
    print("=" * 60)
    
    try:
        demo_app = DemoGUI()
        
        # Add demo instructions
        demo_app.log_message("Welcome to DJ Mixer GUI Demo!")
        demo_app.log_message("Try the following:")
        demo_app.log_message("1. Click 'Load Track' to load demo tracks")
        demo_app.log_message("2. Use Play/Pause/Stop buttons")
        demo_app.log_message("3. Adjust volume sliders")
        demo_app.log_message("4. Move the crossfader and click 'Apply Crossfader'")
        demo_app.log_message("5. Watch the real-time status updates")
        demo_app.log_message("All audio is simulated in this demo mode.")
        
        demo_app.run()
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo error: {e}")

if __name__ == "__main__":
    run_demo()