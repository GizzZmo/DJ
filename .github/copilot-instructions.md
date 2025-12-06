# DJ Mixer - GitHub Copilot Instructions

## Project Overview

DJ Mixer is a Python-based DJ mixing application designed for playback on multiple sound devices. It provides professional DJ functionality including dual-deck control, crossfading, real-time audio effects, beat detection, MIDI controller support, and AI-powered mixing features. The application targets both casual DJs and developers interested in audio processing.

### Key Features
- Multi-device audio playback with pygame
- Dual-deck mixing with crossfader control
- Real-time audio effects (EQ, filters, reverb)
- Beat detection and auto-sync capabilities
- MIDI controller integration
- AI-powered mixing assistant (using Google Gemini API)
- Web-based interface with REST API and WebSocket support
- Recording and export functionality
- Playlist management
- Visual waveform display

## Tech Stack

### Core Technologies
- **Language**: Python 3.8+
- **Audio Engine**: pygame (≥2.5.0), pydub (≥0.25.1)
- **Numerical Processing**: numpy (≥1.24.0)
- **Web Framework**: Flask (≥2.3.0), flask-socketio (≥5.3.0), flask-cors (≥4.0.0)
- **MIDI**: mido (≥1.3.0), python-rtmidi (≥1.5.0)
- **AI Features**: google-generativeai (≥0.3.0)
- **GUI**: tkinter (built-in with Python)

### Development Tools
- **Testing**: pytest, pytest-cov, pytest-mock
- **Code Quality**: Black (formatter), Flake8 (linter), mypy (type checking)
- **Security**: bandit, safety
- **Documentation**: Sphinx, sphinx-rtd-theme, myst-parser
- **Build**: setuptools, build, twine

## Coding Standards

### Code Formatting
- **Formatter**: Black with 88-character line length (default)
- **Linter**: Flake8 with Black-compatible settings
- **Type Hints**: Required for all public functions and class methods
- **Docstrings**: Required for all public classes, methods, and functions

### Naming Conventions
- **Files**: `snake_case.py` (e.g., `dj_mixer.py`, `audio_effects.py`)
- **Classes**: `PascalCase` (e.g., `DJMixer`, `AudioTrack`, `BeatDetector`)
- **Functions/Variables**: `snake_case` (e.g., `load_track`, `crossfader_position`)
- **Constants**: `UPPER_CASE` (e.g., `DEFAULT_SAMPLE_RATE`, `MAX_VOLUME`)
- **Private Members**: Prefix with single underscore `_private_method`

### Python Style Guidelines
- Use type hints from `typing` module for parameters and return types
- Prefer `pathlib.Path` over string paths for file operations
- Use `Optional[Type]` for nullable parameters
- Follow PEP 8 conventions (enforced by Black and Flake8)
- Use f-strings for string formatting
- Keep functions focused and single-purpose
- Maximum function length: ~50 lines (guideline, not strict rule)

### Documentation Standards

#### Docstring Format
Use descriptive docstrings with clear parameter and return type documentation:

```python
def crossfade_tracks(self, track1: str, track2: str, position: float) -> bool:
    """
    Apply crossfader between two tracks.
    
    Args:
        track1: Name of first track (left side)
        track2: Name of second track (right side)
        position: Crossfader position (0.0-1.0, where 0.0 is full left, 1.0 is full right)
    
    Returns:
        True if crossfading applied successfully, False otherwise
    
    Example:
        >>> mixer.crossfade_tracks("deck1", "deck2", 0.3)
        True
    """
```

#### Comments
- Use inline comments sparingly, only for complex logic that isn't obvious from code
- Prefer self-documenting code with clear variable and function names
- Document "why" not "what" when adding comments

## Testing Guidelines

### Test Framework
- Use `pytest` for all new tests
- Place test files with `test_` prefix (e.g., `test_mixer.py`, `test_features.py`)
- Test functions should start with `test_` prefix

### Mock Testing
- Always mock audio hardware for CI/CD compatibility
- Use `MockDJMixer` from `test_mixer.py` for testing without real audio devices
- Mock external dependencies (MIDI devices, Gemini API, file systems)

### Test Coverage
- Aim for high test coverage of core functionality
- Test both success and error cases
- Include edge cases and boundary conditions
- Test files are excluded from coverage reports (see `pyproject.toml`)

### Example Test Structure
```python
from test_mixer import MockDJMixer
import pytest

def test_feature():
    """Test description"""
    mixer = MockDJMixer()
    mixer.initialize()
    
    # Test implementation
    assert mixer.some_method() == expected_result
```

### Running Tests
```bash
# Run all tests
pytest -v

# Run specific test file
pytest test_features.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run original mock tests
python test_mixer.py
```

## Architecture Patterns

### Core Components
- **DJMixer** (`dj_mixer.py`): Core audio mixing engine
- **EnhancedDJMixer** (`enhanced_mixer.py`): Extended mixer with all advanced features
- **AudioTrack**: Individual track representation with playback controls
- **AudioEffects** (`audio_effects.py`): Real-time audio processing
- **BeatDetector** (`beat_detection.py`): Tempo and beat analysis
- **MIDIController** (`midi_controller.py`): MIDI device integration
- **AIDJAssistant** (`ai_dj_assistant.py`): AI-powered mixing features

### Design Principles
- Separation of concerns: Keep audio, GUI, CLI, and web interfaces separate
- Mock-friendly: Design for testability without hardware dependencies
- Extensible: Support for adding new effects, features, and interfaces
- Type-safe: Use type hints and type checking with mypy

### Error Handling
- Use try-except blocks for external operations (file I/O, audio, network)
- Print informative error messages to console
- Return boolean success indicators or raise specific exceptions
- Validate inputs at public API boundaries

## Development Workflow

### Branch Naming
- **Features**: `feature/description` (e.g., `feature/add-reverb-effect`)
- **Bug Fixes**: `fix/description` (e.g., `fix/volume-slider-update`)
- **Documentation**: `docs/description` (e.g., `docs/update-api-guide`)
- **Refactoring**: `refactor/description` (e.g., `refactor/simplify-crossfader`)

### Commit Message Format
Follow conventional commit format:
```
type(scope): description

[optional body]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
- `feat(mixer): add 5-band equalizer support`
- `fix(gui): resolve volume slider not updating display`
- `docs(api): add usage examples for BeatDetector class`
- `test(cli): add tests for command parsing`

### Code Review Checklist
- [ ] Code follows Black formatting (`black --check .`)
- [ ] Passes Flake8 linting (`flake8 .`)
- [ ] Type hints added for public APIs
- [ ] Docstrings present for all public functions/classes
- [ ] Tests written and passing (`pytest`)
- [ ] No audio hardware dependencies in tests
- [ ] Documentation updated if needed
- [ ] No breaking changes (or clearly documented)

## Security Considerations

### Input Validation
- Validate all user inputs (file paths, volume levels, API keys)
- Use `pathlib.Path` for safe file path handling
- Sanitize file names and paths before file operations
- Validate numeric ranges (e.g., volume 0.0-1.0, crossfader 0.0-1.0)

### API Keys and Secrets
- Never commit API keys or secrets to repository
- Support environment variables for configuration
- Provide mock mode for testing without real credentials
- Document how to configure API keys securely

### Dependencies
- Keep dependencies up-to-date
- Use specific version constraints in requirements.txt
- Run `safety check` to identify vulnerable dependencies
- Use `bandit` for security issue detection

## Performance Guidelines

### Audio Processing
- Keep audio operations efficient and non-blocking
- Use appropriate buffer sizes (default: 512)
- Avoid synchronous operations in audio callbacks
- Profile performance-critical code paths

### GUI Responsiveness
- Don't block the GUI thread with long operations
- Use threading for background tasks (recording, analysis)
- Update UI periodically, not on every audio frame
- Keep event handlers lightweight

## Platform Compatibility

### Cross-Platform Considerations
- Test on Windows, macOS, and Linux when possible
- Use `pathlib.Path` for cross-platform path handling
- Handle platform-specific audio device differences
- Provide fallbacks for platform-specific features (MIDI, ASIO)

### Dependencies
- Use cross-platform dependencies where possible
- Document platform-specific requirements
- Provide installation instructions for each OS
- Test with mock systems when hardware unavailable

## AI Features

### Gemini API Integration
- Always provide mock mode for testing without API key
- Document API key configuration clearly
- Handle API errors gracefully
- Respect API rate limits and quotas
- Cache analysis results when appropriate

### AI Assistant Pattern
```python
# Initialize with optional API key
ai = AIDJAssistant()
ai.configure_gemini("api-key")  # Optional

# Works in mock mode without API key
analysis = ai.analyze_track("deck1", "track.mp3")
```

## Resources

### Documentation
- [README.md](../README.md): User-facing documentation and quick start
- [CONTRIBUTING.md](../CONTRIBUTING.md): Detailed contributor guidelines
- [FEATURES_SUMMARY.md](../FEATURES_SUMMARY.md): Overview of all features
- [IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md): Technical implementation details

### Project Links
- **Homepage**: https://github.com/GizzZmo/DJ
- **Issues**: https://github.com/GizzZmo/DJ/issues
- **Documentation**: https://github.com/GizzZmo/DJ/blob/main/README.md

### Build and Test Commands
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Format code
black .

# Lint code
flake8 .

# Type check
mypy .

# Run tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Security check
bandit -r .
safety check
```

## Common Patterns

### Loading and Playing Tracks
```python
mixer = DJMixer()
mixer.initialize()
mixer.load_track("deck1", "track1.mp3")
mixer.play_track("deck1")
mixer.set_track_volume("deck1", 0.8)
```

### Applying Effects
```python
from enhanced_mixer import EnhancedDJMixer

mixer = EnhancedDJMixer()
mixer.enable_track_effects("deck1", True)
mixer.set_track_eq("deck1", low=1.5, mid=1.0, high=1.2)
mixer.set_track_filter("deck1", "lowpass", cutoff_freq=800.0)
```

### Mock Testing Pattern
```python
from test_mixer import MockDJMixer

mixer = MockDJMixer()
mixer.initialize()
# Test without real audio hardware
```

## Key Implementation Notes

- All volume values are floats in range 0.0 to 1.0
- Crossfader position: 0.0 = full left, 0.5 = center, 1.0 = full right
- Default sample rate: 44100 Hz
- Audio files supported: MP3, WAV, OGG, FLAC
- GUI uses tkinter (included with most Python installations)
- Web interface runs on port 5000 by default
- MIDI CC values are normalized to 0.0-1.0 range
