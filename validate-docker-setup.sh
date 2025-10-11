#!/bin/bash
# Docker Setup Validation Script

set -e

echo "==================================="
echo "Docker Setup Validation"
echo "==================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✓ Docker is installed"

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi
echo "✓ Docker Compose is installed"

# Validate docker-compose.yml syntax
if ! docker compose config --quiet; then
    echo "❌ docker-compose.yml has syntax errors"
    exit 1
fi
echo "✓ docker-compose.yml is valid"

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found"
    exit 1
fi
echo "✓ Dockerfile exists"

# Check if required files exist
required_files=(".dockerignore" ".env.example" "DOCKER.md" "requirements.txt")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ $file not found"
        exit 1
    fi
    echo "✓ $file exists"
done

echo ""
echo "==================================="
echo "All validation checks passed! ✓"
echo "==================================="
echo ""
echo "To start the Docker environment:"
echo "  docker compose up -d"
echo ""
echo "To access phpMyAdmin:"
echo "  http://localhost:8080"
echo ""
echo "To run the anime-sama CLI:"
echo "  docker compose run --rm app anime-sama"
echo ""
