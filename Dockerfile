# syntax=docker/dockerfile:1

# Build stage with UV
FROM ghcr.io/astral-sh/uv:python3.10-slim AS builder

# Set environment variables
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy UV configuration files first for better layer caching
COPY pyproject.toml ./

# Copy source code
COPY aide ./aide
COPY setup.py README.md ./

# Install dependencies and the package
RUN uv sync --frozen --no-dev && \
    uv pip install -e .

# Runtime stage
FROM python:3.10-slim

# Install runtime dependencies including UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        unzip \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 aide

# Copy UV environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Set working directory
WORKDIR /app

# Create and set permissions for logs and workspaces
RUN mkdir -p logs workspaces && \
    chown -R aide:aide /app

# Switch to non-root user
USER aide

# Set default command
ENTRYPOINT ["uv", "run", "aide"]
