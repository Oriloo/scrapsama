# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variable to avoid pip SSL verification issues in some environments
# Uncomment the line below if you encounter SSL certificate verification errors
# ENV PIP_TRUSTED_HOST=pypi.org pypi.python.org files.pythonhosted.org

# Copy requirements first for better caching
COPY requirements.txt .
COPY pyproject.toml .

# Install dependencies
# Install all dependencies including optional ones for CLI and database
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY scraper/ ./scraper/
COPY README.md .
COPY LICENSE .

# Install the package with all optional dependencies
RUN pip install --no-cache-dir -e ".[cli,database]"

# Set default command (can be overridden)
CMD ["scrapsama-index-new"]
