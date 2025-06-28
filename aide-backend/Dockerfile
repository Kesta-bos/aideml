# Backend Dockerfile for AIDE FastAPI with UV
FROM python:3.10-slim AS base

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/uploads /app/experiments /app/static

# Copy application code first
COPY . .

# Install dependencies with UV  
RUN uv sync --no-dev

# Add the parent directory to Python path for AIDE imports
ENV PYTHONPATH=/app:/app/..

# Create a non-root user
RUN useradd --create-home --shell /bin/bash aide && \
    chown -R aide:aide /app
USER aide

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with UV
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]