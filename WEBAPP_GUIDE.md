# Scrapsama Web Interface Setup Guide

## Quick Start

### 1. Start the services

```bash
# Start all services (MySQL, phpMyAdmin, and Web Interface)
docker compose up -d

# Check that all services are running
docker compose ps
```

### 2. Initialize the database

```bash
# Create database schema
docker compose run --rm app python init_db.py
```

### 3. Index some anime series

```bash
# Index a specific series
docker compose run --rm app scrapsama-index

# Or index all available series (takes a long time!)
docker compose run --rm app scrapsama-index-all
```

### 4. Access the web interface

Open your browser and navigate to: **http://localhost:5000**

You can now:
- Search for anime series
- Browse by category
- Select seasons and episodes
- Choose language and player to watch

## Services

- **Web Interface**: http://localhost:5000 - Browse and watch anime
- **phpMyAdmin**: http://localhost:8080 - Database management (user: root, password: rootpassword)

## Troubleshooting

### Web interface shows no series

You need to index some series first:
```bash
docker compose run --rm app scrapsama-index
```

### Cannot connect to database

Make sure MySQL is running and healthy:
```bash
docker compose ps mysql
docker compose logs mysql
```

### Rebuild after code changes

```bash
docker compose build web
docker compose up -d web
```

## Development

To run the web interface in development mode with live reload:

```bash
# Set environment variables
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=scrapsama_db
export DB_USER=scrapsama_user
export DB_PASSWORD=scrapsama_password

# Run the Flask app
python -m webapp
```

Make sure MySQL is running and accessible at the configured host/port.
