# Contributing Guide

Thank you for your interest in contributing to DictaPilot3!

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Basic understanding of Python and async programming
- Familiarity with voice transcription concepts (helpful but not required)

### Development Setup

1. **Fork and clone the repository:**

```bash
git clone https://github.com/YOUR_USERNAME/DictaPilot.git
cd DictaPilot
```

2. **Create virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Set up environment:**

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

5. **Run tests:**

```bash
pytest tests/
```

6. **Run the application:**

```bash
python app.py
```

## Development Workflow

### Branch Strategy

- `main` - Stable release branch
- `develop` - Development branch (create PRs against this)
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches
- `docs/*` - Documentation branches

### Making Changes

1. **Create a feature branch:**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test your changes:**

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_smart_editor.py

# Run with coverage
pytest --cov=. tests/
```

4. **Commit your changes:**

```bash
git add .
git commit -m "feat: add new feature"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

5. **Push and create PR:**

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

**Formatting:**
- 4 spaces for indentation (no tabs)
- Max line length: 120 characters
- Use double quotes for strings
- Use f-strings for formatting

**Naming:**
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Private functions/methods: `_leading_underscore`

**Example:**

```python
# Good
def transcribe_audio(audio_data: np.ndarray, sample_rate: int = 16000) -> str:
    """Transcribe audio using Groq API."""
    if audio_data is None:
        raise ValueError("audio_data cannot be None")
    
    client = get_groq_client()
    result = client.audio.transcriptions.create(
        file=audio_file,
        model=GROQ_WHISPER_MODEL
    )
    return result.text

# Bad
def TranscribeAudio(audioData, sampleRate=16000):
    if audioData == None:
        raise ValueError("audioData cannot be None")
    client=get_groq_client()
    result=client.audio.transcriptions.create(file=audio_file,model=GROQ_WHISPER_MODEL)
    return result.text
```

### Type Hints

Use type hints for all public functions:

```python
from typing import Optional, List, Tuple

def process_text(
    text: str,
    cleanup_level: str = "balanced",
    context: Optional[DictationContext] = None
) -> Tuple[str, List[str]]:
    """Process text with cleanup."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def transcribe_audio(audio_data: np.ndarray, sample_rate: int = 16000) -> str:
    """
    Transcribe audio using Groq Whisper API.
    
    Args:
        audio_data: numpy array of audio samples
        sample_rate: Sample rate of audio (default: 16000)
    
    Returns:
        Transcribed text string
    
    Raises:
        APIError: If API call fails
        ValueError: If audio_data is invalid
    
    Example:
        >>> audio = record_audio(duration=5)
        >>> text = transcribe_audio(audio)
        >>> print(text)
        "Hello world"
    """
```

### Code Organization

**Module structure:**

```python
"""
Module docstring explaining purpose.
"""

# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import numpy as np
from groq import Groq

# Local imports
from .config import load_config
from .utils import helper_function

# Constants
DEFAULT_SAMPLE_RATE = 16000
MAX_RECORDING_DURATION = 300

# Classes
class MyClass:
    pass

# Functions
def my_function():
    pass

# Main execution
if __name__ == "__main__":
    main()
```

## Testing

### Writing Tests

Use `pytest` for all tests:

```python
# tests/test_smart_editor.py
import pytest
from smart_editor import TranscriptState, smart_update_state

def test_delete_command():
    """Test delete that command."""
    state = TranscriptState()
    state, _ = smart_update_state(state, "Hello world")
    assert state.output_text == "Hello world"
    
    state, action = smart_update_state(state, "delete that")
    assert state.output_text == ""
    assert action == "undo"

def test_replace_command():
    """Test replace command."""
    state = TranscriptState()
    state, _ = smart_update_state(state, "Hello world")
    state, _ = smart_update_state(state, "replace hello with goodbye")
    assert "goodbye" in state.output_text.lower()

@pytest.mark.parametrize("command,expected_action", [
    ("delete that", "undo"),
    ("clear all", "clear"),
    ("ignore", "ignore"),
])
def test_commands(command, expected_action):
    """Test various commands."""
    state = TranscriptState()
    state, _ = smart_update_state(state, "Some text")
    state, action = smart_update_state(state, command)
    assert action == expected_action
```

### Test Coverage

Aim for >80% test coverage:

```bash
# Run with coverage report
pytest --cov=. --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### Test Categories

**Unit tests:** Test individual functions
```python
def test_compute_delta():
    from paste_utils import compute_delta
    backspaces, text = compute_delta("Hello world", "Hello there world")
    assert backspaces == 5
    assert text == "there world"
```

**Integration tests:** Test component interactions
```python
def test_full_dictation_flow():
    # Record → Transcribe → Edit → Paste
    audio = record_audio(duration=2)
    text = transcribe_audio(audio)
    state = TranscriptState()
    state, _ = smart_update_state(state, text)
    success = paste_text(state.output_text)
    assert success
```

**Mocking external services:**
```python
from unittest.mock import patch, MagicMock

@patch('transcriber.Groq')
def test_transcribe_with_mock(mock_groq):
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create.return_value.text = "test"
    mock_groq.return_value = mock_client
    
    result = transcribe_audio(np.zeros(16000))
    assert result == "test"
```

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Use type hints
- Include examples in docstrings
- Keep comments concise and meaningful

### User Documentation

When adding features, update:
- `README.md` - If it affects setup or basic usage
- `docs/voice-commands.md` - If adding new commands
- `docs/troubleshooting.md` - If addressing common issues
- `docs/faq.md` - If answering common questions

### Developer Documentation

Update when changing architecture:
- `docs/developer/architecture.md` - System design changes
- `docs/developer/api-reference.md` - API changes

## Pull Request Guidelines

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass (`pytest tests/`)
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages follow Conventional Commits
- [ ] No merge conflicts with target branch
- [ ] PR description explains changes clearly

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guide
```

### Review Process

1. **Automated checks:** CI runs tests and linting
2. **Code review:** Maintainer reviews code
3. **Feedback:** Address review comments
4. **Approval:** Maintainer approves PR
5. **Merge:** PR merged to target branch

## Common Tasks

### Adding a New Voice Command

1. **Add regex pattern in `smart_editor.py`:**

```python
_MY_COMMAND_RE = re.compile(
    r"^my command pattern (.+)$",
    re.IGNORECASE
)
```

2. **Add handler function:**

```python
def handle_my_command(state: TranscriptState, match) -> str:
    arg = match.group(1)
    # Your logic here
    return updated_text
```

3. **Integrate in `smart_update_state`:**

```python
match = _MY_COMMAND_RE.match(utterance)
if match:
    result = handle_my_command(state, match)
    return state, "custom_action"
```

4. **Add tests:**

```python
def test_my_command():
    state = TranscriptState()
    state, _ = smart_update_state(state, "test input")
    state, action = smart_update_state(state, "my command pattern arg")
    assert action == "custom_action"
```

5. **Update documentation:**
   - Add to `docs/voice-commands.md`

### Adding a New Backend

1. **Implement backend in appropriate file:**

```python
# In paste_utils.py
def paste_my_backend(text: str) -> bool:
    """Custom paste backend."""
    try:
        # Your implementation
        return True
    except Exception as e:
        logger.error(f"Paste failed: {e}")
        return False
```

2. **Register backend:**

```python
PASTE_BACKENDS = {
    "keyboard": paste_keyboard,
    "pynput": paste_pynput,
    "my_backend": paste_my_backend,  # Add here
}
```

3. **Add tests:**

```python
def test_my_backend():
    success = paste_my_backend("test text")
    assert success
```

4. **Update documentation:**
   - Add to platform guides
   - Update backend selection logic

### Adding Configuration Option

1. **Add to `config.py`:**

```python
@dataclass
class DictaPilotConfig:
    # ... existing fields ...
    my_option: str = "default_value"
```

2. **Add environment variable handling:**

```python
def load_config() -> DictaPilotConfig:
    # ... existing code ...
    if "MY_OPTION" in env_overrides:
        config.my_option = env_overrides["MY_OPTION"]
```

3. **Use in code:**

```python
config = load_config()
if config.my_option == "special":
    # Do something
```

4. **Update documentation:**
   - Add to `README.md` environment variables section

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**Import errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Test failures:**
```bash
# Run specific test with verbose output
pytest -v tests/test_smart_editor.py::test_delete_command
```

**API errors:**
```bash
# Check API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GROQ_API_KEY'))"
```

## Release Process

(For maintainers)

1. Update version in `__version__.py`
2. Update `CHANGELOG.md`
3. Create release branch: `release/vX.Y.Z`
4. Run full test suite
5. Create GitHub release with tag
6. Merge to `main` and `develop`

## Getting Help

- **Questions:** Open a GitHub Discussion
- **Bugs:** Open a GitHub Issue
- **Chat:** Join Discord (coming soon)

## Code of Conduct

Be respectful and inclusive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to DictaPilot3!**

---

**Last Updated:** 2026-02-17
