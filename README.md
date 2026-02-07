# Talk to History: H.P. Lovecraft Correspondence Transcriber

<p align="center">
  <img src="docs/images/little_n'kai_transcribing_256x256.png"
  alt="Little N'Kai Transcribing">
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-package%20manager-green.svg)](https://github.com/astral-sh/uv)
[![Coverage Status](./reports/coverage/coverage-badge.svg?dummy=8484744)](./reports/coverage/index.html)

GPU-accelerated OCR tool that converts H.P. Lovecraft's handwritten
letters from Brown University's archives into searchable text. Runs in
Docker with Ollama vision models, preserving archaic spelling and
18th-century prose style.

## Features

- **Containerized Workflow** - Pre-configured Docker environment with
  Python 3.11, uv, and Ollama ready to run
- **GPU-Accelerated OCR** - 5-10x faster transcription with NVIDIA GPU
  passthrough
- **Specialized for Historical Text** - Preserves archaic spelling,
  punctuation, and Lovecraft's antiquated writing style
- **Batch Processing** - Process entire collections via IIIF manifest
  parsing
- **Production-Ready** - Retry logic, connection pooling, error
  handling for unreliable networks

## Installation

### Quick Start (VS Code Dev Container)

```bash
git clone <repository-url>
cd talk-to-history-hpl-correspondence-transcriber
code .
# Click "Reopen in Container" when prompted
```

### Docker Compose (Without VS Code)

```bash
git clone <repository-url>
cd talk-to-history-hpl-correspondence-transcriber
docker compose -f .devcontainer/compose.yml up -d
docker compose -f .devcontainer/compose.yml exec app bash
```

### Prerequisites

#### Required Software

- **Docker Desktop** 4.30+ (with WSL2 backend on Windows)
- **NVIDIA GPU** (Maxwell architecture or newer)
- **NVIDIA Drivers** 535.98+ (Windows: [WSL2-specific drivers](https://developer.nvidia.com/cuda/wsl))
- **System RAM:** 16GB RAM (32GB recommended for batch processing)
- **GPU VRAM:** 8GB RAM (16GB recommended for large images)
- **Storage:** 10GB free space (models + output)

## Quick Start

**Inside container** (VS Code terminal or `docker exec`):

```bash
# Transcribe single image
uv run main.py --image-url \
  https://repository.library.brown.edu/iiif/image/bdr:929604/full/full/0/default.jpg
```

**Output:**

```text
INFO:transcriber:Fetching image from https://repository.library.brown.edu/iiif/image/bdr:929604/full/full/0/default.jpg
INFO:transcriber:Encoding image to base64
INFO:transcriber:Transcribing image text using vision model
INFO:transcriber:Transcription saved to output/929604.txt
```

**Batch processing:**

```bash
uv run src/helper.py  # Process all images from metadata/
```

Files save to `./output` directory (accessible from host).

### Configuration

Key parameters in `transcriber.py`:

```python
MODEL = "qwen2.5vl:3b"                # Vision model
TEMPERATURE = 0.0                     # Deterministic output
TOP_P = 0.05                          # Focused sampling
NUM_PREDICT = 1048                    # Max tokens
```

### Troubleshooting

**GPU not detected:**

```bash
# Inside container
nvidia-smi  # Should show GPU
docker logs <container> 2>&1 | grep -i cuda  # Check Ollama GPU init
```

**Ollama not responding:**

```bash
curl http://localhost:11434  # Should return "Ollama is running"
ollama list  # Verify qwen2.5vl:3b is pulled
```

**Cloudflare blocking:** Visit
`https://repository.library.brown.edu` on host to pass human
verification.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed troubleshooting.

## Contributing

Contributions welcome! Please ensure:

1. Tests pass: `uv run pytest`
2. Code formatted: `uv run pre-commit run --all-files`
3. Coverage ≥80%

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, vision
model configuration, and coding guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Brown University Library** - Digital access to H.P. Lovecraft
  collection
- **Ollama** - Open-source vision model infrastructure
- **Qwen Team** - qwen2.5vl vision-language model
- **Brown Digital Repository** - IIIF API access
