# Contributing

Thank you for your interest in contributing to the H.P. Lovecraft
Correspondence Transcriber! This guide will help you get started.

## Development Setup

### Prerequisites

- **Docker Desktop** (for Dev Container approach) or Docker Engine
- **Ollama** installed and running locally
- **Python 3.11** (for local setup without containers)
- **NVIDIA GPU** (optional, for faster transcription)

### Using Dev Container (Recommended)

Open in VS Code with Docker installed:

1. Install the Dev Containers extension
2. Command palette → "Reopen in Container"
3. Everything installs automatically (Python 3.11, uv, dependencies)
4. Install Ollama inside container or configure to use host Ollama

### Local Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the vision model
ollama pull qwen2.5vl:3b

# Start Ollama service
ollama serve
```

## Making Changes

1. Fork and clone the repository
2. Create a branch: `git checkout -b fix/description` or `feature/description`
3. Make your changes
4. Run checks: `uv run pre-commit run --all-files`
5. Run tests: `uv run pytest`
6. Push and open a PR

## Code Quality

Format and lint with ruff:

```bash
uv run ruff format .
uv run ruff check . --fix
```

Pre-commit hooks run automatically on commit and check:

- YAML/JSON formatting (prettier)
- Ruff formatting and linting
- Dockerfile formatting
- Tests

## Testing

### Running Tests

```bash
# Run all tests with coverage (80% minimum required)
uv run pytest

# Run specific test module
uv run pytest tests/test_transcriber_main.py

# Run with verbose output
uv run pytest -v

# Generate HTML coverage report
uv run pytest --cov-report=html
```

### Test Organization

Tests are organized by module in the `tests/` directory:

- `test_helper_*.py` - Helper module tests (batch processing)
- `test_main_*.py` - Main entry point tests
- `test_transcriber_*.py` - Transcriber module tests

Source code is in the root directory:

- `main.py` - CLI entry point for single images
- `helper.py` - Batch processing orchestration
- `transcriber.py` - Core OCR pipeline

### Coverage Requirements

- 80% minimum coverage (configured in `.pytest.toml`)
- Add tests for new features
- Add regression tests for bug fixes

### Testing with Ollama

Some tests mock Ollama responses. For integration testing:

```bash
# Ensure Ollama is running
ollama serve

# Run integration tests (if implemented)
uv run pytest -m integration
```

## Commit Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

`<type>: <description>`

Common types:

- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation
- `test`: tests
- `chore`: maintenance
- `refactor`: code restructuring

Breaking changes: add `!` after type or `BREAKING CHANGE:` in footer.

Examples:
feat: add user validation
fix: handle empty input
docs: update setup instructions

## Vision Model Development

### Model Configuration

The project uses `qwen2.5vl:3b` for OCR. Key configuration in
`transcriber.py`:

- **Temperature**: 0.0 (deterministic output)
- **Top P**: 0.05 (focused sampling)
- **Num Predict**: 1048 (max output tokens)
- **Stop Sequences**: Prevents model from adding analysis/corrections

### Prompt Engineering

The system prompt in `transcribe_image_text()` is specialized for:

- Early 20th-century American correspondence
- H.P. Lovecraft's archaic writing style
- Preserving original spelling and punctuation
- Avoiding modernization or "corrections"

When modifying the prompt:

1. Test with sample images from the corpus
2. Verify archaic spellings are preserved
3. Check that no metadata/analysis is added
4. Compare output with known transcriptions

### Testing OCR Changes

```bash
# Test single image transcription
uv run main.py --image-url <test-image-url>

# Compare with expected output
diff output/<pid>.txt expected/<pid>.txt
```

## Pull Requests

PR titles must follow semantic commit format (they become the squash
commit message).

CI runs on every PR:

- Tests and coverage (80% minimum)
- Ruff checks
- Pre-commit hooks
- Semantic PR title validation

PRs are squashed and merged to `main` after passing CI.

## Development Troubleshooting

### Ollama Not Found

```text
ConnectionError: Cannot connect to Ollama
```

**Solution**: Ensure Ollama is running with `ollama serve`

### Model Pull Issues

```text
Error: model 'qwen2.5vl:3b' not found
```

**Solution**: Pull the model with `ollama pull qwen2.5vl:3b`

### Cloudflare Blocking API Requests

When testing with Brown Digital Repository images:

```text
pydantic_core._pydantic_core.PydanticSerializationError
```

**Solution**: Visit `https://repository.library.brown.edu` in a browser
to complete human verification

### Test Coverage Below 80%

**Solution**: Add tests for untested code paths. Use coverage report:

```bash
uv run pytest --cov-report=html
# Open htmlcov/index.html to see uncovered lines
```

## Project-Specific Guidelines

### Code Organization

- **main.py**: Keep minimal, only argument parsing and orchestration
- **transcriber.py**: Pure functions where possible, dependency
  injection for testing
- **helper.py**: Batch processing logic, separate from single-image
  pipeline

### Error Handling

- Use retry logic with exponential backoff for network requests
- Log errors with context (URL, PID, error message)
- Continue batch processing on individual failures
- Exit codes: 0 (success), 1 (error), 130 (user interrupt)

### Adding New Features

1. Write tests first (TDD approach recommended)
2. Update relevant docstrings
3. Add configuration parameters to module constants
4. Document in README.md if user-facing
5. Add to CONTRIBUTING.md if developer-facing

## Questions or Issues?

- Open an issue on GitHub
- Check existing issues for similar problems
- Provide sample images (if public domain) when reporting OCR bugs
