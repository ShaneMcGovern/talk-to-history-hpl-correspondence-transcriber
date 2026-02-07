#FROM nvidia/cuda:12.9.0-base-ubuntu22.04
FROM ollama/ollama:0.15.2

ENV OLLAMA_FLASH_ATTENTION=1 \
    OLLAMA_MAX_LOADED_MODELS=1 \
    OLLAMA_KEEP_ALIVE=15m \
    CUDA_VISIBLE_DEVICES=0,1

COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# UV_LINK_MODE=copy: Required for cache mounts - hard links fail across filesystems
# UV_COMPILE_BYTECODE=1: Pre-compiles .pyc files for faster Python startup
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y curl git libatomic1 \
    && rm -rf /var/lib/apt/lists/*

# UID/GID 10000+ avoids conflicts with host UIDs (most systems use <10000)
RUN groupadd --gid 10001 shanemcgovern \
    && useradd --uid 10000 --gid 10001 --create-home --shell /bin/bash shanemcgovern

# Matches compose.yml working_dir and devcontainer.json workspaceFolder
WORKDIR /workspaces

# Pre-create for ownership; compose.yml named volume shadows this at runtime
# without pre-creation, volume would be root-owned
RUN mkdir -p /workspaces/.venv \
    && chown -R shanemcgovern:shanemcgovern /workspaces/.venv

USER shanemcgovern

# safe.directory: Bind mount causes UID mismatch - Git sees "dubious ownership"
# User config: Matches devcontainer.json remoteUser for commit attribution
RUN git config --global --add safe.directory /workspaces \
    && git config --global user.email "shanemcgovern@protonmail.com" \
    && git config --global user.name "shanemcgovern"

# Build context is parent (..) per compose.yml, so .devcontainer/ prefix needed
COPY --chown=shanemcgovern:shanemcgovern .devcontainer/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]