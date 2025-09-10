# Contributing to DJ Mixer

Thank you for your interest in contributing to DJ Mixer! This document provides guidelines and information for contributors.

## 🎯 Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🚀 Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/DJ.git
   cd DJ
   ```

2. **Set up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

4. **Verify Setup**
   ```bash
   # Run tests
   python test_mixer.py
   pytest
   
   # Check code quality
   flake8 .
   black --check .
   ```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest -v

# Run specific test file
pytest test_pytest.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run original mock tests
python test_mixer.py
python test_cli.py
```

### Writing Tests

- Use `pytest` for new tests
- Place test files with `test_` prefix
- Mock audio hardware for CI compatibility
- Test both success and error cases
- Aim for good test coverage

### Mock Testing

The project includes mock audio systems for testing without hardware:

```python
from test_mixer import MockDJMixer

def test_feature():
    mixer = MockDJMixer()
    mixer.initialize()
    # Your test code here
```

## 📝 Code Style

### Python Code Standards

- **Black**: Code formatting (`black .`)
- **Flake8**: Linting (`flake8 .`)
- **Type Hints**: Use type hints where appropriate
- **Docstrings**: Document all public functions and classes
- **Line Length**: 88 characters (Black default)

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_CASE`

### Documentation

- Use clear, descriptive docstrings
- Include usage examples in docstrings
- Update README.md for user-facing changes
- Add inline comments for complex logic

## 🔧 Development Workflow

### Branch Naming

- **Features**: `feature/description`
- **Bug Fixes**: `fix/description`
- **Documentation**: `docs/description`
- **Refactoring**: `refactor/description`

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(mixer): add crossfading between multiple tracks
fix(gui): resolve volume slider not updating display
docs(api): add usage examples for DJMixer class
test(cli): add tests for command parsing
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Locally**
   ```bash
   # Run all tests
   pytest
   
   # Check code quality
   flake8 .
   black --check .
   
   # Test mock systems
   python test_mixer.py
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Use descriptive title and description
   - Reference related issues
   - Include testing instructions
   - Wait for CI to pass

## 📋 Types of Contributions

### 🐛 Bug Reports

When reporting bugs, include:
- DJ Mixer version
- Python version and OS
- Audio hardware details (if relevant)
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs

### 💡 Feature Requests

For new features, describe:
- Use case and motivation
- Proposed implementation approach
- Backwards compatibility considerations
- Testing strategy

### 🎵 Audio Features

For audio-related contributions:
- Consider multiple platforms (Windows/macOS/Linux)
- Test with mock audio system
- Document audio hardware requirements
- Consider performance implications

### 🖥️ GUI Improvements

For interface changes:
- Test on multiple screen sizes
- Consider accessibility guidelines
- Maintain consistent visual design
- Include screenshots in PR

## 🔬 Technical Areas

### Core Audio Engine (`dj_mixer.py`)

- Audio device management
- Track loading and playback
- Volume and crossfading logic
- Multi-device support

### Command Line Interface (`dj_cli.py`)

- Interactive command parsing
- User experience improvements
- Help system and documentation

### Graphical Interface (`dj_gui.py`)

- tkinter-based interface
- Real-time updates and feedback
- Professional DJ mixer layout

### Testing Infrastructure

- Mock audio systems
- Cross-platform testing
- Performance testing
- Integration tests

## 📊 Performance Guidelines

- Keep audio operations efficient
- Minimize GUI blocking operations
- Use appropriate data structures
- Profile performance-critical code

## 🔒 Security Considerations

- Validate all user inputs
- Handle file operations safely
- Avoid exposing sensitive information
- Use secure coding practices

## 📚 Documentation Standards

### Code Documentation

```python
def crossfade_tracks(self, track1: str, track2: str, position: float) -> bool:
    """
    Apply crossfader between two tracks.
    
    Args:
        track1: Name of first track (left side)
        track2: Name of second track (right side)
        position: Crossfader position (0.0-1.0)
    
    Returns:
        True if crossfading applied successfully, False otherwise
    
    Example:
        >>> mixer.crossfade_tracks("deck1", "deck2", 0.3)
        True
    """
```

### API Documentation

- Document all public methods
- Include parameter types and descriptions
- Provide usage examples
- Note any side effects or requirements

## 🎉 Recognition

Contributors are recognized in several ways:
- Listed in README.md contributors section
- Mentioned in release notes
- Attribution in commit messages

## ❓ Getting Help

- **Issues**: Use GitHub issues for bugs and features
- **Discussions**: GitHub discussions for questions
- **Documentation**: Check docs/ directory
- **Code Examples**: See examples/ directory

## 📋 Checklist for Contributors

Before submitting a PR:

- [ ] Code follows style guidelines (Black, Flake8)
- [ ] Tests pass locally (`pytest`)
- [ ] New features have tests
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] PR description is clear and complete
- [ ] No breaking changes (or clearly documented)

Thank you for contributing to DJ Mixer! 🎵