# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY pyproject.toml ./
COPY anime_sama_api ./anime_sama_api
COPY README.md ./
COPY LICENSE ./

# Install the package in development mode
RUN pip install --no-cache-dir --no-deps -e .

# Create config directory
RUN mkdir -p /root/.config/anime-sama_cli

# Set default command
CMD ["anime-sama"]
