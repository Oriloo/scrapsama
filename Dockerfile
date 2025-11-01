# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and project metadata
COPY requirements.txt .
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Copy the application code BEFORE installing the package
# This is crucial for editable installation to work properly
COPY scraper/ ./scraper/

# Install Python dependencies with trusted host for environments with SSL issues
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt && \
    pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -e .[cli,database]

# Create a non-root user
RUN useradd -m -u 1000 scraper && chown -R scraper:scraper /app
USER scraper

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden)
CMD ["scrapsama-index"]
