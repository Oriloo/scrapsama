# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variable to avoid pip SSL verification issues in some environments
# Remove this if you have SSL issues
# ENV PIP_TRUSTED_HOST=pypi.org pypi.python.org files.pythonhosted.org

# Copy requirements first for better caching
COPY requirements.txt .
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir python-dotenv

# Copy the application code
COPY scraper/ ./scraper/
COPY README.md .
COPY LICENSE .

# Install the package
RUN pip install --no-cache-dir -e .

# Create a directory for .env file (will be mounted or provided via env vars)
RUN mkdir -p /app/config

# Set default command (can be overridden)
CMD ["scrapsama-index-new"]
