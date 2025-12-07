# DJ Mixer

[![Ubuntu](https://img.shields.io/badge/Ubuntu-latest-E95420?logo=ubuntu&logoColor=white)](https://github.com/GizzZmo/DJ/actions/workflows/ci.yml)
[![macOS](https://img.shields.io/badge/macOS-latest-000000?logo=apple&logoColor=white)](https://github.com/GizzZmo/DJ/actions/workflows/ci.yml)
[![Windows](https://img.shields.io/badge/Windows-latest-0078D6?logo=windows&logoColor=white)](https://github.com/GizzZmo/DJ/actions/workflows/ci.yml)

A Python-based DJ Mixer application for playback on multiple sound devices. This mixer supports loading audio files, controlling volume levels, crossfading between tracks, and managing playback across different audio outputs.

## Features

- **Multi-Device Audio Support**: Play audio on different sound devices simultaneously
- **Audio Format Support**: Compatible with MP3, WAV, OGG, FLAC, and other common formats
- **Crossfading**: Smooth transitions between tracks with adjustable crossfader
- **Volume Control**: Independent volume control per track plus master volume
- **Real-time Mixing**: Live control over playback and mixing parameters
- **Graphical User Interface**: Professional DJ mixer GUI with visual controls
- **Command-Line Interface**: Interactive CLI for easy mixer control
- **Mock Testing**: Test functionality without audio hardware
- **🤖 AI-Powered Features**: 
  - **Auto Mixing**: Intelligent track analysis and automated crossfader transitions
  - **Key Mixing**: Harmonic key analysis and compatibility recommendations
  - **Fader Effects**: Smart effect suggestions based on track energy and context
  - **Gemini API Integration**: Configure with your own API key for advanced AI features

## Installation

1. Clone the repository:
```bash
git clone https://github.com/GizzZmo/DJ.git
cd DJ
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

*Note: For the GUI interface, tkinter is required. On most systems it's included with Python. If not available:*
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Other systems may require different packages
```

## Quick Start

### Using the Graphical User Interface

Start the visual DJ mixer:
```bash
python dj_gui.py
```

The GUI provides:
- **Dual Deck Controls**: Load and control two audio tracks independently
- **Visual Crossfader**: Smooth transitions with real-time position display
- **Volume Sliders**: Individual track volumes and master volume control
- **Playback Controls**: Play, pause, stop buttons for each deck
- **File Browser**: Easy track loading with standard file dialogs
- **Status Monitor**: Real-time display of mixer status and track information
- **🤖 AI Assistant**: Configure Gemini API for intelligent mixing features
- **Auto Mixing**: Start AI-powered automatic transitions between tracks
- **Key Analysis**: Get harmonic compatibility advice for smooth mixing
- **Fader Effects**: AI-suggested effects based on track characteristics

### Using the Command-Line Interface

Start the interactive DJ mixer:
```bash
python dj_cli.py
```

Basic commands:
```
DJ> init                    # Initialize the mixer
DJ> list                    # Show audio files in current directory
DJ> load deck1 song1.mp3    # Load a track to deck1
DJ> load deck2 song2.wav    # Load a track to deck2
DJ> play deck1              # Play deck1
DJ> volume deck1 0.8        # Set deck1 volume to 80%
DJ> crossfader 0.3          # Set crossfader position
DJ> cross deck1 deck2       # Apply crossfader between decks
DJ> status                  # Show mixer status
DJ> help                    # Show all available commands
```

### Using the AI Features

The DJ Mixer now includes intelligent AI-powered mixing capabilities:

```python
from ai_dj_assistant import AIDJAssistant

# Initialize AI assistant
ai = AIDJAssistant()

# Configure with Gemini API key (optional - works in mock mode without)
ai.configure_gemini("your-gemini-api-key")

# Analyze tracks for intelligent mixing
analysis = ai.analyze_track("deck1", "house_track.mp3")
print(f"Track: {analysis.tempo} BPM, Key: {analysis.key}, Energy: {analysis.energy}")

# Get AI mixing advice
advice = ai.get_auto_mixing_advice("deck1", "deck2")
print(f"Suggested crossfader position: {advice.crossfader_position}")

# Check harmonic compatibility
key_advice = ai.get_key_mixing_advice("deck1", "deck2")
print(f"Key compatibility: {key_advice['compatibility']}")

# Start automated mixing
ai.start_auto_mixing("deck1", "deck2")
```

#### AI Features:
- **Auto Mixing**: Analyzes tempo, key, and energy to create smooth transitions
- **Key Mixing**: Provides harmonic compatibility analysis using music theory
- **Fader Effects**: Suggests optimal effects based on track characteristics
- **Mock Mode**: Full functionality without requiring API key for testing

### Testing Without Audio Hardware

Run the mock test to verify functionality:
```bash
python test_mixer.py
```

Test the GUI functionality:
```bash
python test_gui.py
```

## Examples

Run the example demo:
```bash
python example.py
```

For detailed examples and audio file information:
```bash
python example.py --info
```

## Project Structure

```
DJ/
├── dj_mixer.py        # Core DJ mixer functionality
├── dj_gui.py          # Graphical user interface with AI integration
├── dj_cli.py          # Interactive command-line interface
├── ai_dj_assistant.py # AI-powered mixing assistant with Gemini API
├── test_mixer.py      # Mock testing without audio hardware
├── test_gui.py        # GUI functionality tests
├── test_ai_assistant.py # AI assistant functionality tests
├── demo_ai_features.py # Demo of AI capabilities
├── example.py         # Example usage and demos
├── requirements.txt   # Python dependencies (includes google-generativeai)
└── README.md          # This file
```

## GUI Interface

The DJ Mixer includes a professional graphical interface built with tkinter that provides visual control over all mixer functions:

### GUI Features
- **Professional Layout**: Traditional DJ mixer design with dual decks and central crossfader
- **File Management**: Easy track loading through standard file dialogs
- **Visual Feedback**: Real-time status updates and visual indicators
- **Touch-Friendly Controls**: Large buttons and sliders for easy operation
- **Status Monitoring**: Comprehensive display of mixer state and track information

### GUI Controls
- **Initialize Button**: Start the audio mixer system
- **Load Track Buttons**: Browse and load audio files for each deck
- **Playback Controls**: Play, pause, and stop buttons for each deck
- **Volume Sliders**: Independent volume control for each track and master output
- **Crossfader Slider**: Smooth balance control between left and right decks
- **Apply Crossfader**: Apply the crossfader effect to the loaded tracks
- **Status Panel**: Real-time display of mixer status, track info, and system messages

## Audio Device Support

The mixer is designed to support multiple audio devices:

- **Main Output**: Primary speakers or PA system
- **Headphone Output**: DJ monitoring and cueing
- **Recording Output**: For recording or broadcasting
- **Additional Outputs**: Extra zones or devices

*Note: Current implementation uses pygame which abstracts device selection. For production use with specific device control, consider upgrading to PyAudio with ASIO drivers.*

## DJ Mixing Concepts

### Crossfading
- **Position 0.0**: Full left deck, right deck silent
- **Position 0.5**: Both decks at equal volume (center)
- **Position 1.0**: Full right deck, left deck silent

### Volume Control
- **Track Volume**: Individual volume for each loaded track
- **Master Volume**: Global volume affecting all outputs
- **Crossfader**: Relative volume control between two specific tracks

## Troubleshooting

### Audio Issues
If you encounter audio initialization errors:

1. Check audio system availability:
```bash
# On Linux, check ALSA/PulseAudio
pulseaudio --check -v

# Test pygame audio
python -c "import pygame; pygame.mixer.init(); print('Audio OK')"
```

2. Use mock testing mode:
```bash
python test_mixer.py
```

3. Install audio dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install python3-pygame libasound2-dev

# Other systems may require different audio libraries
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Requirements

- Python 3.9+ (Note: Python 3.8 is not supported due to google-generativeai dependency)
- pygame >= 2.5.0
- pydub >= 0.25.1
- google-generativeai >= 0.3.0 (for AI features)

## AI Configuration

To enable full AI features:
1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. In the GUI, enter your API key in the "AI DJ Assistant" section
3. Click "Configure AI" to enable intelligent mixing

The AI assistant works in mock mode without an API key for testing and development.

## Advanced Features (NEW!)

### 🎚️ Real-time Audio Effects
- **5-Band Equalizer**: Low, Mid-Low, Mid, Mid-High, High frequency control
- **Filters**: Low-pass, High-pass, Band-pass with adjustable cutoff and resonance
- **Reverb**: Room size, damping, wet/dry mix controls
- **Effect Presets**: Bass boost, Treble boost, Vocal enhance, Club sound, Telephone effect
- See `audio_effects.py` for full implementation

### 🎵 Beat Detection and Auto-Sync
- **BPM Detection**: Automatic tempo analysis
- **Beat Grid**: Quantized beat positions for precise mixing
- **Auto-Sync**: Calculate tempo adjustments needed to sync tracks
- **Beat Matching**: Find optimal mix points based on beat alignment
- See `beat_detection.py` for full implementation

### 🎹 MIDI Controller Support
- **Device Detection**: Automatic MIDI device enumeration
- **Flexible Mapping**: Map any MIDI control to mixer functions
- **Controller Presets**: Generic DJ, Pioneer DDJ, Traktor Kontrol
- **Real-time Control**: Live MIDI input processing
- **Mock Mode**: Test without hardware
- See `midi_controller.py` for full implementation

### 🔴 Recording and Export
- **Multi-Format Export**: WAV, MP3, OGG, FLAC support
- **Live Recording**: Capture mixer output in real-time
- **Audio Processing**: Normalization, splitting, concatenation
- **Configurable Quality**: Sample rate, bit depth, and format options
- See `recording.py` for full implementation

### 📋 Playlist Management
- **Create and Organize**: Multiple playlists with metadata
- **Import/Export**: M3U playlist support
- **Smart Filtering**: Filter by BPM, key, genre
- **Auto-Sorting**: Sort by title, artist, BPM
- **Navigation**: Next/previous track with looping
- See `playlist_manager.py` for full implementation

### 📊 Visual Waveform Display
- **Waveform Generation**: Create visual waveforms from audio
- **Frequency Spectrum**: Real-time spectrum analysis
- **Peak Detection**: Identify transients and beats
- **Zoom and Scroll**: Navigate through long tracks
- **Caching**: Efficient waveform storage and retrieval
- See `waveform_display.py` for full implementation

### 🌐 Web-Based Interface
- **REST API**: Full mixer control via HTTP endpoints
- **WebSocket**: Real-time status updates
- **Modern UI**: Responsive HTML/CSS/JavaScript interface
- **Remote Control**: Control mixer from any device on network
- **Live Monitoring**: Real-time track and mixer status
- See `web_interface.py` for full implementation

## Quick Start with New Features

### Using Enhanced Mixer
```python
from enhanced_mixer import EnhancedDJMixer

# Create enhanced mixer with all features
mixer = EnhancedDJMixer()
mixer.initialize()

# Load tracks with beat analysis
mixer.load_track("deck1", "track1.mp3", analyze_beats=True)
mixer.load_track("deck2", "track2.mp3", analyze_beats=True)

# Apply audio effects
mixer.enable_track_effects("deck1", True)
mixer.set_track_eq("deck1", low=1.5, mid=1.0, high=1.2)
mixer.set_track_filter("deck1", "lowpass", cutoff_freq=800.0)
mixer.set_track_reverb("deck1", room_size=0.6, wet_level=0.3)

# Check beat sync
sync_info = mixer.sync_tracks("deck1", "deck2")
print(f"BPM difference: {sync_info['tempo_ratio']}")

# Start recording
mixer.start_recording("my_mix.wav")

# Connect MIDI controller
mixer.connect_midi()

# Create and use playlist
playlist = mixer.create_playlist("My Set")
mixer.load_playlist_track("deck1", 0)

# Get comprehensive status
status = mixer.get_mixer_status()
```

### Starting Web Interface
```python
from web_interface import DJMixerWebServer, create_web_templates
from test_mixer import MockDJMixer

# Create web templates (only need to do once)
create_web_templates()

# Initialize mixer
mixer = MockDJMixer()
mixer.initialize()

# Start web server
server = DJMixerWebServer(mixer, port=5000)
server.start()

# Open http://localhost:5000 in your browser
```

### Running Feature Demos
```bash
# Run comprehensive demo of all features
python demo_features.py

# Run individual feature tests
python test_features.py

# Run enhanced mixer demo
python enhanced_mixer.py
```

## Advanced Usage Examples

### Audio Effects Chain
```python
from audio_effects import AudioEffects, EffectsPresets

effects = AudioEffects(sample_rate=44100)

# Apply preset
preset = EffectsPresets.club_sound()
effects.set_eq(**preset['eq'])
effects.set_reverb(**preset['reverb'])

# Process audio
processed_audio = effects.process(audio_data)
```

### Beat Detection
```python
from beat_detection import BeatDetector, AutoSync

detector = BeatDetector(sample_rate=44100)
beat_info = detector.detect_beats(audio_data, duration=180.0)

print(f"BPM: {beat_info.bpm}")
print(f"Confidence: {beat_info.confidence}")
print(f"Beats: {len(beat_info.beat_positions)}")

# Auto-sync two tracks
auto_sync = AutoSync()
timing = auto_sync.suggest_mix_timing(beat1, beat2, current_position=30.0)
```

### MIDI Control
```python
from midi_controller import MIDIController

midi = MIDIController()
midi.connect()  # Connect to first available device

# Map controls
midi.add_mapping(0, MIDIControlType.FADER, "crossfader", 0.0, 1.0)
midi.add_mapping(1, MIDIControlType.KNOB, "volume", 0.0, 1.0)

# Register callbacks
midi.register_callback("crossfader", lambda v: mixer.set_crossfader(v))
midi.register_callback("volume", lambda v: mixer.set_track_volume("deck1", v))

# Start listening
midi.start_listening()
```

## Testing

Run the comprehensive test suite:
```bash
# Test all new features
python -m pytest test_features.py -v

# Test original functionality
python test_mixer.py

# Run all tests
python -m pytest -v
```

## Project Structure (Updated)

```
DJ/
├── dj_mixer.py           # Core DJ mixer functionality
├── enhanced_mixer.py     # 🆕 Enhanced mixer with all features
├── dj_gui.py            # Graphical user interface
├── dj_cli.py            # Interactive command-line interface
├── ai_dj_assistant.py   # AI-powered mixing assistant
├── audio_effects.py     # 🆕 Real-time audio effects (EQ, filters, reverb)
├── beat_detection.py    # 🆕 Beat detection and auto-sync
├── midi_controller.py   # 🆕 MIDI controller support
├── recording.py         # 🆕 Recording and export functionality
├── playlist_manager.py  # 🆕 Playlist management
├── waveform_display.py  # 🆕 Waveform visualization
├── web_interface.py     # 🆕 Web-based interface (Flask + WebSocket)
├── demo_features.py     # 🆕 Comprehensive feature demonstrations
├── test_features.py     # 🆕 Test suite for new features
├── test_mixer.py        # Mock testing without audio hardware
├── test_gui.py          # GUI functionality tests
├── test_ai_assistant.py # AI assistant functionality tests
├── example.py           # Example usage and demos
└── requirements.txt     # Python dependencies (updated)
```

## Requirements (Updated)

- Python 3.9+ (Note: Python 3.8 is not supported due to google-generativeai dependency)
- pygame >= 2.5.0
- pydub >= 0.25.1
- numpy >= 1.24.0 🆕
- flask >= 2.3.0 🆕
- flask-socketio >= 5.3.0 🆕
- flask-cors >= 4.0.0 🆕
- mido >= 1.3.0 🆕
- python-rtmidi >= 1.5.0 🆕
- google-generativeai >= 0.3.0 (for AI features)

## Future Enhancements

- ~~Real-time audio effects (EQ, filters, reverb)~~ ✅ IMPLEMENTED
- ~~MIDI controller support~~ ✅ IMPLEMENTED
- ~~Recording and export functionality~~ ✅ IMPLEMENTED
- ~~Web-based interface~~ ✅ IMPLEMENTED
- Advanced device routing with PyAudio/ASIO (In Progress)
- ~~Beat detection and auto-sync~~ ✅ IMPLEMENTED
- ~~Playlist management~~ ✅ IMPLEMENTED
- ~~Visual waveform display~~ ✅ IMPLEMENTED
- Integration of all features into main GUI
- Hardware acceleration for real-time effects
- VST plugin support
