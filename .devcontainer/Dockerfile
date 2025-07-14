# Lightning-fast Python devcontainer for PPTX Shredder
# Based on official Python image with minimal additions for speed

FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Speed optimizations - run everything in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential tools only
    git \
    curl \
    # Required for python-pptx and lxml dependencies
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    # Cleanup in same layer for smaller image
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set up Python environment optimizations
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/workspace/src

# Pre-install common packages for faster container startup
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Create workspace directory
WORKDIR /workspace

# Default command
CMD ["bash"]