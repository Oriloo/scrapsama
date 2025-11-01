.PHONY: help build run run-all run-new shell clean

# Default target
help:
	@echo "Scrapsama Docker Commands"
	@echo "========================="
	@echo ""
	@echo "make build      - Build the Docker image"
	@echo "make run        - Run scrapsama-index (interactive)"
	@echo "make run-all    - Run scrapsama-index-all"
	@echo "make run-new    - Run scrapsama-index-new (default command)"
	@echo "make shell      - Open a shell inside the container"
	@echo "make clean      - Remove the Docker image"
	@echo ""
	@echo "Docker Compose commands:"
	@echo "make up         - Start with docker-compose"
	@echo "make down       - Stop docker-compose"
	@echo "make logs       - Show docker-compose logs"

# Build the Docker image
build:
	docker build -t scrapsama:latest .

# Run scrapsama-index (interactive)
run:
	docker run --rm -it --env-file .env scrapsama scrapsama-index

# Run scrapsama-index-all
run-all:
	docker run --rm --env-file .env scrapsama scrapsama-index-all

# Run scrapsama-index-new (default)
run-new:
	docker run --rm --env-file .env scrapsama scrapsama-index-new

# Open a shell in the container
shell:
	docker run --rm -it --env-file .env scrapsama /bin/bash

# Clean up
clean:
	docker rmi scrapsama:latest

# Docker Compose commands
up:
	docker-compose up

down:
	docker-compose down

logs:
	docker-compose logs -f

# Check if .env exists
check-env:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found!"; \
		echo "Create it from .env.example: cp .env.example .env"; \
		exit 1; \
	fi
