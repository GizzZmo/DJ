# DJ Mixer

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

### Using the Python API

```python
from dj_mixer import DJMixer

# Initialize mixer
mixer = DJMixer()
mixer.initialize()

# Load tracks
mixer.load_track("deck1", "track1.mp3")
mixer.load_track("deck2", "track2.wav")

# Control playback
mixer.play_track("deck1")
mixer.set_track_volume("deck1", 0.8)

# Crossfading
mixer.set_crossfader(0.3)  # 0.0 = full left, 1.0 = full right
mixer.apply_crossfader("deck1", "deck2")

# Cleanup
mixer.cleanup()
```

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
├── dj_mixer.py      # Core DJ mixer functionality
├── dj_gui.py        # Graphical user interface
├── dj_cli.py        # Interactive command-line interface
├── test_mixer.py    # Mock testing without audio hardware
├── test_gui.py      # GUI functionality tests
├── example.py       # Example usage and demos
├── requirements.txt # Python dependencies
└── README.md        # This file
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

- Python 3.7+
- pygame >= 2.5.0
- pydub >= 0.25.1

## Future Enhancements

- Real-time audio effects (EQ, filters, reverb)
- MIDI controller support
- Recording and export functionality
- Web-based interface
- Advanced device routing with PyAudio/ASIO
- Beat detection and auto-sync
- Playlist management
- Visual waveform display
