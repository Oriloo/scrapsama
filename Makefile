# Makefile for Anime-Sama Docker Setup

.PHONY: help build up down logs restart clean validate shell db phpmyadmin

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

validate: ## Validate Docker configuration
	@./validate-docker-setup.sh

build: ## Build Docker images
	docker compose build

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## Show logs from all services
	docker compose logs -f

restart: ## Restart all services
	docker compose restart

clean: ## Stop and remove all containers, volumes, and images
	docker compose down -v --rmi all

shell: ## Open a shell in the app container
	docker compose exec app bash

run: ## Run the anime-sama CLI interactively
	docker compose run --rm app anime-sama

db: ## Connect to MySQL database
	docker compose exec mysql mysql -u animesama_user -panimesama_password animesama_db

phpmyadmin: ## Show phpMyAdmin URL
	@echo "phpMyAdmin is available at: http://localhost:8080"
	@echo "Username: root"
	@echo "Password: rootpassword"

status: ## Show status of all services
	docker compose ps
