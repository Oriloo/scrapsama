#!/bin/bash
# Quick start script for Docker deployment
# This script helps you quickly build and run the scraper with Docker

set -e

echo "==================================="
echo "Scrapsama Docker Quick Start"
echo "==================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "Please edit .env with your database credentials:"
    echo "  nano .env"
    echo "or"
    echo "  vim .env"
    echo ""
    read -p "Press Enter after editing .env to continue..."
fi

# Build the image
echo ""
echo "Building Docker image..."
docker build -t scrapsama:latest .

if [ $? -eq 0 ]; then
    echo "✓ Docker image built successfully!"
    echo ""
    echo "Available commands:"
    echo "  1. Index a specific series (interactive):"
    echo "     docker run --rm -it --env-file .env scrapsama scrapsama-index"
    echo ""
    echo "  2. Index all series:"
    echo "     docker run --rm --env-file .env scrapsama scrapsama-index-all"
    echo ""
    echo "  3. Index new episodes:"
    echo "     docker run --rm --env-file .env scrapsama scrapsama-index-new"
    echo ""
    echo "  Or use docker-compose:"
    echo "     docker-compose up    # Runs scrapsama-index-new by default"
    echo ""
else
    echo "❌ Failed to build Docker image"
    exit 1
fi
