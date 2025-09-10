#!/usr/bin/env python3
"""
Graphical User Interface for the DJ Mixer
Provides visual controls for all mixer functionality
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from pathlib import Path
from dj_mixer import DJMixer
from ai_dj_assistant import AIDJAssistant


class DJMixerGUI:
    """Main GUI application for the DJ Mixer"""
    
    def __init__(self):
        self.mixer = DJMixer()
        self.ai_assistant = AIDJAssistant()
        self.initialized = False
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("DJ Mixer - AI-Powered Multi-Device Audio Mixing System")
        self.root.geometry("1100x700")
        self.root.resizable(True, True)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Track information
        self.deck1_file = tk.StringVar(value="No file loaded")
        self.deck2_file = tk.StringVar(value="No file loaded")
        self.deck1_status = tk.StringVar(value="STOPPED")
        self.deck2_status = tk.StringVar(value="STOPPED")
        self.master_vol_var = tk.DoubleVar(value=1.0)
        self.crossfader_var = tk.DoubleVar(value=0.5)
        self.deck1_vol_var = tk.DoubleVar(value=1.0)
        self.deck2_vol_var = tk.DoubleVar(value=1.0)
        
        # AI variables
        self.gemini_api_key = tk.StringVar()
        self.ai_status_var = tk.StringVar(value="AI: Not configured")
        self.auto_mix_active = tk.BooleanVar(value=False)
        
        self.setup_ui()
        self.setup_ai_callbacks()
        self.start_status_updater()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Updated for AI section
        
        # Title
        title_label = ttk.Label(main_frame, text="AI-POWERED DJ MIXER", 
                               font=('Arial', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Initialize button and AI status
        init_frame = ttk.Frame(main_frame)
        init_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        self.init_button = ttk.Button(init_frame, text="Initialize Mixer", 
                                     command=self.initialize_mixer)
        self.init_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_label = ttk.Label(init_frame, text="Mixer not initialized", 
                                     foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # AI status label
        self.ai_status_label = ttk.Label(init_frame, textvariable=self.ai_status_var,
                                        foreground="blue")
        self.ai_status_label.pack(side=tk.LEFT)
        
        # Create AI configuration section
        self.create_ai_section(main_frame, 2, 0)
        
        # Create deck sections (moved down)
        self.create_deck_section(main_frame, "DECK 1", 3, 0, 
                               self.deck1_file, self.deck1_status, self.deck1_vol_var, "deck1")
        self.create_deck_section(main_frame, "DECK 2", 3, 2, 
                               self.deck2_file, self.deck2_status, self.deck2_vol_var, "deck2")
        
        # Create crossfader section (moved down)
        self.create_crossfader_section(main_frame, 3, 1)
        
        # Create master controls (moved down)
        self.create_master_section(main_frame, 4, 0)
        
        # Create status display (moved down)
        self.create_status_section(main_frame, 5, 0)
    
    def create_deck_section(self, parent, title, row, col, file_var, status_var, vol_var, deck_name):
        """Create a deck control section"""
        # Main deck frame
        deck_frame = ttk.LabelFrame(parent, text=title, padding="10")
        deck_frame.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File display
        file_frame = ttk.Frame(deck_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="Track:").pack(anchor=tk.W)
        file_label = ttk.Label(file_frame, textvariable=file_var, 
                              background="white", relief="sunken", padding="5")
        file_label.pack(fill=tk.X, pady=(2, 0))
        
        # Load button
        load_button = ttk.Button(deck_frame, text="Load Track", 
                               command=lambda: self.load_track(deck_name, file_var))
        load_button.pack(fill=tk.X, pady=(0, 10))
        
        # Playback controls
        control_frame = ttk.Frame(deck_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        play_button = ttk.Button(control_frame, text="Play", 
                               command=lambda: self.play_track(deck_name))
        play_button.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        pause_button = ttk.Button(control_frame, text="Pause", 
                                command=lambda: self.pause_track(deck_name))
        pause_button.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        stop_button = ttk.Button(control_frame, text="Stop", 
                               command=lambda: self.stop_track(deck_name))
        stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Volume control
        vol_frame = ttk.Frame(deck_frame)
        vol_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(vol_frame, text="Volume:").pack(anchor=tk.W)
        vol_scale = ttk.Scale(vol_frame, from_=0.0, to=1.0, variable=vol_var,
                            command=lambda v: self.set_track_volume(deck_name, float(v)))
        vol_scale.pack(fill=tk.X, pady=(2, 0))
        
        vol_label = ttk.Label(vol_frame, text="1.00")
        vol_label.pack(anchor=tk.W)
        
        # Update volume label when scale changes
        def update_vol_label(var, label):
            label.config(text=f"{var.get():.2f}")
        
        vol_var.trace('w', lambda *args: update_vol_label(vol_var, vol_label))
        
        # Status display
        status_frame = ttk.Frame(deck_frame)
        status_frame.pack(fill=tk.X)
        
        ttk.Label(status_frame, text="Status:").pack(anchor=tk.W)
        status_label = ttk.Label(status_frame, textvariable=status_var, 
                               font=('Arial', 10, 'bold'))
        status_label.pack(anchor=tk.W)
    
    def create_crossfader_section(self, parent, row, col):
        """Create crossfader control section"""
        cross_frame = ttk.LabelFrame(parent, text="CROSSFADER", padding="10")
        cross_frame.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Crossfader scale
        ttk.Label(cross_frame, text="Position:").pack(anchor=tk.W)
        
        position_frame = ttk.Frame(cross_frame)
        position_frame.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(position_frame, text="L").pack(side=tk.LEFT)
        
        cross_scale = ttk.Scale(position_frame, from_=0.0, to=1.0, 
                              variable=self.crossfader_var, orient=tk.HORIZONTAL,
                              command=self.update_crossfader)
        cross_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(position_frame, text="R").pack(side=tk.RIGHT)
        
        # Position display
        self.cross_pos_label = ttk.Label(cross_frame, text="0.50 (CENTER)")
        self.cross_pos_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Apply crossfader button
        apply_button = ttk.Button(cross_frame, text="Apply Crossfader", 
                                command=self.apply_crossfader)
        apply_button.pack(fill=tk.X)
        
        # Instructions
        instruction_text = "Crossfader controls the balance between Deck 1 (left) and Deck 2 (right)"
        instruction_label = ttk.Label(cross_frame, text=instruction_text, 
                                    wraplength=200, justify=tk.CENTER, 
                                    font=('Arial', 8))
        instruction_label.pack(pady=(10, 0))
    
    def create_master_section(self, parent, row, col):
        """Create master controls section"""
        master_frame = ttk.LabelFrame(parent, text="MASTER CONTROLS", padding="10")
        master_frame.grid(row=row, column=col, columnspan=3, padx=5, pady=5, 
                         sticky=(tk.W, tk.E))
        
        # Master volume
        vol_frame = ttk.Frame(master_frame)
        vol_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        
        ttk.Label(vol_frame, text="Master Volume:").pack(anchor=tk.W)
        master_scale = ttk.Scale(vol_frame, from_=0.0, to=1.0, 
                               variable=self.master_vol_var, orient=tk.HORIZONTAL,
                               command=self.set_master_volume)
        master_scale.pack(fill=tk.X, pady=(2, 0))
        
        self.master_vol_label = ttk.Label(vol_frame, text="1.00")
        self.master_vol_label.pack(anchor=tk.W)
        
        # Update master volume label
        self.master_vol_var.trace('w', lambda *args: 
                                self.master_vol_label.config(text=f"{self.master_vol_var.get():.2f}"))
        
    def create_ai_section(self, parent, row, col):
        """Create AI configuration and controls section"""
        ai_frame = ttk.LabelFrame(parent, text="🤖 AI DJ ASSISTANT", padding="10")
        ai_frame.grid(row=row, column=col, columnspan=3, padx=5, pady=5, 
                     sticky=(tk.W, tk.E))
        
        # API Key configuration
        key_frame = ttk.Frame(ai_frame)
        key_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(key_frame, text="Gemini API Key:").pack(side=tk.LEFT)
        key_entry = ttk.Entry(key_frame, textvariable=self.gemini_api_key, 
                             show="*", width=30)
        key_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        configure_button = ttk.Button(key_frame, text="Configure AI", 
                                    command=self.configure_ai)
        configure_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # AI Controls
        controls_frame = ttk.Frame(ai_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Auto mixing controls
        auto_mix_frame = ttk.LabelFrame(controls_frame, text="Auto Mixing", padding="5")
        auto_mix_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.auto_mix_button = ttk.Button(auto_mix_frame, text="Start Auto Mix", 
                                         command=self.start_auto_mix)
        self.auto_mix_button.pack(fill=tk.X, pady=(0, 2))
        
        self.stop_auto_mix_button = ttk.Button(auto_mix_frame, text="Stop Auto Mix", 
                                              command=self.stop_auto_mix, state=tk.DISABLED)
        self.stop_auto_mix_button.pack(fill=tk.X)
        
        # Key mixing controls
        key_mix_frame = ttk.LabelFrame(controls_frame, text="Key Mixing", padding="5")
        key_mix_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.analyze_keys_button = ttk.Button(key_mix_frame, text="Analyze Keys", 
                                            command=self.analyze_track_keys)
        self.analyze_keys_button.pack(fill=tk.X, pady=(0, 2))
        
        self.key_advice_button = ttk.Button(key_mix_frame, text="Get Key Advice", 
                                          command=self.get_key_mixing_advice)
        self.key_advice_button.pack(fill=tk.X)
        
        # Fader effects controls
        effects_frame = ttk.LabelFrame(controls_frame, text="Fader Effects", padding="5")
        effects_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.fader_effects_button = ttk.Button(effects_frame, text="Suggest Effects", 
                                             command=self.suggest_fader_effects)
        self.fader_effects_button.pack(fill=tk.X, pady=(0, 2))
        
        self.apply_effects_button = ttk.Button(effects_frame, text="Apply Effects", 
                                             command=self.apply_ai_effects)
        self.apply_effects_button.pack(fill=tk.X)
        
        # AI Info display
        self.ai_info_text = tk.Text(ai_frame, height=4, width=80, 
                                   state=tk.DISABLED, wrap=tk.WORD)
        self.ai_info_text.pack(fill=tk.X, pady=(10, 0))
        
        # Initialize AI info
        self.update_ai_info("Ready to configure AI assistant. Enter your Gemini API key above.")
    
    def setup_ai_callbacks(self):
        """Setup AI callbacks to control the mixer"""
        def ai_crossfader_callback(position):
            """AI callback to update crossfader"""
            self.crossfader_var.set(position)
            if self.initialized:
                self.mixer.set_crossfader(position)
                self.update_crossfader(str(position))
        
        def ai_volume_callback(deck, volume):
            """AI callback to update volume"""
            if deck == "deck1":
                self.deck1_vol_var.set(volume)
                if self.initialized:
                    self.mixer.set_track_volume("deck1", volume)
            elif deck == "deck2":
                self.deck2_vol_var.set(volume)
                if self.initialized:
                    self.mixer.set_track_volume("deck2", volume)
        
        # Register callbacks with AI assistant
        self.ai_assistant.register_callback('crossfader_change', ai_crossfader_callback)
        self.ai_assistant.register_callback('volume_change', ai_volume_callback)
    
    def configure_ai(self):
        """Configure the AI assistant with the API key"""
        api_key = self.gemini_api_key.get().strip()
        if not api_key:
            messagebox.showwarning("Warning", "Please enter a Gemini API key")
            return
        
        success = self.ai_assistant.configure_gemini(api_key)
        if success:
            self.ai_status_var.set("AI: Configured ✓")
            self.log_message("✓ AI Assistant configured with Gemini API")
            self.update_ai_info("🤖 AI Assistant configured successfully! Ready for intelligent mixing.")
        else:
            self.ai_status_var.set("AI: Configuration failed ✗")
            messagebox.showerror("Error", "Failed to configure AI. Check your API key.")
            self.log_message("✗ AI Assistant configuration failed")
    
    def start_auto_mix(self):
        """Start AI auto mixing"""
        if not self.initialized:
            messagebox.showwarning("Warning", "Please initialize the mixer first")
            return
        
        # Check if both decks have tracks
        loaded_tracks = self.mixer.get_loaded_tracks()
        if "deck1" not in loaded_tracks or "deck2" not in loaded_tracks:
            messagebox.showwarning("Warning", "Please load tracks on both decks first")
            return
        
        self.auto_mix_active.set(True)
        self.auto_mix_button.config(state=tk.DISABLED)
        self.stop_auto_mix_button.config(state=tk.NORMAL)
        
        self.log_message("🤖 Starting AI auto mixing...")
        self.update_ai_info("🎛️ AI Auto Mix active - analyzing tracks and optimizing transitions...")
        
        # Start AI auto mixing
        self.ai_assistant.start_auto_mixing("deck1", "deck2")
    
    def stop_auto_mix(self):
        """Stop AI auto mixing"""
        self.auto_mix_active.set(False)
        self.auto_mix_button.config(state=tk.NORMAL)
        self.stop_auto_mix_button.config(state=tk.DISABLED)
        
        self.log_message("⏹ AI auto mixing stopped")
        self.update_ai_info("🤖 AI Auto Mix stopped. Manual control restored.")
    
    def analyze_track_keys(self):
        """Analyze the keys of loaded tracks"""
        if not self.initialized:
            messagebox.showwarning("Warning", "Please initialize the mixer first")
            return
        
        loaded_tracks = self.mixer.get_loaded_tracks()
        if not loaded_tracks:
            messagebox.showwarning("Warning", "Please load some tracks first")
            return
        
        self.log_message("🎼 Analyzing track keys...")
        analysis_results = []
        
        for track in loaded_tracks:
            track_file = self.deck1_file.get() if track == "deck1" else self.deck2_file.get()
            if track_file != "No file loaded":
                analysis = self.ai_assistant.analyze_track(track, track_file)
                analysis_results.append(f"{track.upper()}: {analysis.key} ({analysis.genre}, {analysis.tempo} BPM)")
                self.log_message(f"📊 {track.upper()}: Key={analysis.key}, Tempo={analysis.tempo}, Energy={analysis.energy}")
        
        if analysis_results:
            info = "🎹 Track Analysis Complete:\n" + "\n".join(analysis_results)
            self.update_ai_info(info)
    
    def get_key_mixing_advice(self):
        """Get AI advice for key mixing"""
        if not self.initialized:
            messagebox.showwarning("Warning", "Please initialize the mixer first")
            return
        
        loaded_tracks = self.mixer.get_loaded_tracks()
        if "deck1" not in loaded_tracks or "deck2" not in loaded_tracks:
            messagebox.showwarning("Warning", "Please load tracks on both decks first")
            return
        
        advice = self.ai_assistant.get_key_mixing_advice("deck1", "deck2")
        
        info = f"""🎼 Key Mixing Analysis:
        
Deck 1 Key: {advice['deck1_key']}
Deck 2 Key: {advice['deck2_key']}
Compatibility: {advice['compatibility']}

💡 Advice: {advice['advice']}
🎛️ Suggested Action: {advice['suggested_action']}"""
        
        self.update_ai_info(info)
        self.log_message(f"🎹 Key compatibility: {advice['compatibility']} ({advice['deck1_key']} + {advice['deck2_key']})")
    
    def suggest_fader_effects(self):
        """Get AI suggestions for fader effects"""
        if not self.initialized:
            messagebox.showwarning("Warning", "Please initialize the mixer first")
            return
        
        # Get current energy levels
        deck1_analysis = self.ai_assistant.track_analyses.get("deck1")
        deck2_analysis = self.ai_assistant.track_analyses.get("deck2")
        
        if not deck1_analysis or not deck2_analysis:
            messagebox.showinfo("Info", "Please analyze track keys first to get energy levels")
            return
        
        current_position = self.crossfader_var.get()
        effects_advice = self.ai_assistant.get_fader_effects_suggestion(
            current_position, deck1_analysis.energy, deck2_analysis.energy
        )
        
        info = f"""🎚️ Fader Effects Suggestion:
        
Effect: {effects_advice['suggested_effect']}
Technique: {effects_advice['technique']}
Optimal Speed: {effects_advice['optimal_speed']}

💡 Reasoning: {effects_advice['reasoning']}"""
        
        self.update_ai_info(info)
        self.log_message(f"💫 Effect suggestion: {effects_advice['suggested_effect']}")
    
    def apply_ai_effects(self):
        """Apply AI-suggested effects"""
        if not self.initialized:
            messagebox.showwarning("Warning", "Please initialize the mixer first")
            return
        
        # Get AI mixing advice and apply it
        loaded_tracks = self.mixer.get_loaded_tracks()
        if "deck1" not in loaded_tracks or "deck2" not in loaded_tracks:
            messagebox.showwarning("Warning", "Please load tracks on both decks first")
            return
        
        advice = self.ai_assistant.get_auto_mixing_advice("deck1", "deck2")
        
        # Apply the advice
        self.crossfader_var.set(advice.crossfader_position)
        self.deck1_vol_var.set(advice.deck1_volume)
        self.deck2_vol_var.set(advice.deck2_volume)
        
        if self.initialized:
            self.mixer.set_crossfader(advice.crossfader_position)
            self.mixer.set_track_volume("deck1", advice.deck1_volume)
            self.mixer.set_track_volume("deck2", advice.deck2_volume)
            self.mixer.apply_crossfader("deck1", "deck2")
        
        self.update_crossfader(str(advice.crossfader_position))
        
        info = f"""✨ AI Effects Applied:
        
Crossfader: {advice.crossfader_position:.2f}
Deck 1 Volume: {advice.deck1_volume:.2f}
Deck 2 Volume: {advice.deck2_volume:.2f}
Transition: {advice.transition_duration:.1f}s

💡 {advice.reasoning}"""
        
        self.update_ai_info(info)
        self.log_message(f"✨ Applied AI effects: {advice.effects_suggestion}")
    
    def update_ai_info(self, message):
        """Update the AI info display"""
        self.ai_info_text.config(state=tk.NORMAL)
        self.ai_info_text.delete(1.0, tk.END)
        self.ai_info_text.insert(tk.END, message)
        self.ai_info_text.config(state=tk.DISABLED)
    
    def create_status_section(self, parent, row, col):
        """Create status display section"""
        status_frame = ttk.LabelFrame(parent, text="STATUS", padding="10")
        status_frame.grid(row=row, column=col, columnspan=3, padx=5, pady=5, 
                         sticky=(tk.W, tk.E))
        
        # Create text widget for status display
        self.status_text = tk.Text(status_frame, height=8, width=80, 
                                  state=tk.DISABLED, wrap=tk.WORD)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, 
                                command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        self.update_status_display()
    
    def initialize_mixer(self):
        """Initialize the DJ mixer"""
        if self.mixer.initialize():
            self.initialized = True
            self.status_label.config(text="Mixer initialized successfully", 
                                   foreground="green")
            self.init_button.config(text="Mixer Initialized", state=tk.DISABLED)
            self.log_message("✓ DJ Mixer initialized successfully!")
            devices = self.mixer.get_audio_devices()
            self.log_message(f"Available devices: {', '.join(devices)}")
        else:
            messagebox.showerror("Error", "Failed to initialize DJ Mixer")
            self.log_message("✗ Failed to initialize DJ Mixer")
    
    def load_track(self, deck_name, file_var):
        """Load a track into a deck"""
        if not self.initialized:
            messagebox.showwarning("Warning", "Please initialize the mixer first")
            return
        
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.ogg *.flac *.aac *.m4a"),
            ("MP3 files", "*.mp3"),
            ("WAV files", "*.wav"),
            ("OGG files", "*.ogg"),
            ("FLAC files", "*.flac"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title=f"Load track for {deck_name.upper()}",
            filetypes=filetypes
        )
        
        if filename:
            if self.mixer.load_track(deck_name, filename):
                file_var.set(Path(filename).name)
                self.log_message(f"✓ Loaded {Path(filename).name} into {deck_name.upper()}")
                # Automatically analyze track with AI if configured
                if self.ai_assistant.is_configured:
                    self.ai_assistant.analyze_track(deck_name, filename)
                    self.log_message(f"🤖 AI analysis completed for {deck_name.upper()}")
            else:
                messagebox.showerror("Error", f"Failed to load track into {deck_name.upper()}")
                self.log_message(f"✗ Failed to load track into {deck_name.upper()}")
    
    def play_track(self, deck_name):
        """Play a track"""
        if not self.initialized:
            messagebox.showwarning("Warning", "Please initialize the mixer first")
            return
        
        if self.mixer.play_track(deck_name):
            self.log_message(f"✓ Playing {deck_name.upper()}")
        else:
            messagebox.showwarning("Warning", f"Cannot play {deck_name.upper()} - track not loaded")
    
    def pause_track(self, deck_name):
        """Pause a track"""
        if not self.initialized:
            return
        
        self.mixer.pause_track(deck_name)
        self.log_message(f"⏸ Paused {deck_name.upper()}")
    
    def stop_track(self, deck_name):
        """Stop a track"""
        if not self.initialized:
            return
        
        self.mixer.stop_track(deck_name)
        self.log_message(f"⏹ Stopped {deck_name.upper()}")
    
    def set_track_volume(self, deck_name, volume):
        """Set track volume"""
        if not self.initialized:
            return
        
        self.mixer.set_track_volume(deck_name, volume)
    
    def set_master_volume(self, volume):
        """Set master volume"""
        if not self.initialized:
            return
        
        self.mixer.set_master_volume(float(volume))
    
    def update_crossfader(self, value):
        """Update crossfader position display"""
        pos = float(value)
        if pos < 0.3:
            desc = "LEFT"
        elif pos > 0.7:
            desc = "RIGHT"
        else:
            desc = "CENTER"
        
        self.cross_pos_label.config(text=f"{pos:.2f} ({desc})")
        
        if self.initialized:
            self.mixer.set_crossfader(pos)
    
    def apply_crossfader(self):
        """Apply crossfader between deck1 and deck2"""
        if not self.initialized:
            messagebox.showwarning("Warning", "Please initialize the mixer first")
            return
        
        self.mixer.apply_crossfader("deck1", "deck2")
        pos = self.mixer.get_crossfader()
        self.log_message(f"Applied crossfader at position {pos:.2f}")
    
    def update_status_display(self):
        """Update the status display"""
        if not self.initialized:
            return
        
        # Clear current status
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        
        # Add current status
        status_lines = []
        status_lines.append("═" * 50)
        status_lines.append("DJ MIXER STATUS")
        status_lines.append("═" * 50)
        status_lines.append(f"Master Volume: {self.mixer.get_master_volume():.2f}")
        status_lines.append(f"Crossfader: {self.mixer.get_crossfader():.2f}")
        
        tracks = self.mixer.get_loaded_tracks()
        if tracks:
            status_lines.append(f"\nLoaded Tracks ({len(tracks)}):")
            status_lines.append("-" * 30)
            for track_name in tracks:
                volume = self.mixer.get_track_volume(track_name)
                playing = "PLAYING" if self.mixer.is_track_playing(track_name) else "STOPPED"
                status_lines.append(f"  {track_name}: Vol={volume:.2f} [{playing}]")
        else:
            status_lines.append("\nNo tracks loaded")
        
        status_lines.append("═" * 50)
        
        self.status_text.insert(tk.END, "\n".join(status_lines))
        self.status_text.config(state=tk.DISABLED)
    
    def start_status_updater(self):
        """Start background thread for status updates"""
        def update_loop():
            while True:
                if self.initialized:
                    # Update track status
                    try:
                        self.root.after(0, self.update_track_status)
                        self.root.after(0, self.update_status_display)
                    except (tk.TclError, RuntimeError):
                        # GUI has been destroyed, stop updating
                        break
                time.sleep(1)  # Update every second
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def update_track_status(self):
        """Update track playing status"""
        if self.initialized:
            if self.mixer.is_track_playing("deck1"):
                self.deck1_status.set("PLAYING")
            else:
                self.deck1_status.set("STOPPED")
            
            if self.mixer.is_track_playing("deck2"):
                self.deck2_status.set("PLAYING")
            else:
                self.deck2_status.set("STOPPED")
    
    def log_message(self, message):
        """Add a message to the status log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, log_entry)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def run(self):
        """Start the GUI application"""
        try:
            self.log_message("DJ Mixer GUI started")
            self.log_message("Click 'Initialize Mixer' to begin")
            self.root.mainloop()
        finally:
            if self.initialized:
                self.mixer.cleanup()


def main():
    """Main entry point for the GUI application"""
    try:
        app = DJMixerGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()