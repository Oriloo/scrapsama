# Scrapsama Indexer

API for indexing anime series from anime-sama.fr into a MySQL database.

## Installation

### Option 1: Docker (Recommended)

Requirements:
- Docker & Docker Compose

```bash
# Build the Docker image (required after updates)
docker compose build app

# Start services (MySQL + phpMyAdmin)
docker compose up -d

# Initialize database schema
docker compose run --rm app python init_db.py

# Run indexer
docker compose run --rm app scrapsama-index
```

Access phpMyAdmin at http://localhost:8080 (user: root, password: rootpassword)

### Option 2: Local Installation

Requirements:
- Python 3.10+
- MySQL 8.0+

```bash
pip install -e .
pip install mysql-connector-python rich
```

## Configuration

Set database connection via environment variables:

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=scrapsama_db
export DB_USER=scrapsama_user
export DB_PASSWORD=scrapsama_password
```

## Usage

### CLI

```bash
# Index a specific series (prompts for series name)
scrapsama-index

# Index all available series from anime-sama.fr
scrapsama-index-all
```

### Python API

```python
import asyncio
from scraper import AnimeSama, Database, index_episode

async def index_series(name):
    # Search series
    anime_sama = AnimeSama("https://anime-sama.fr/")
    catalogues = await anime_sama.search(name)
    
    # Initialize database
    db = Database()
    db.connect()
    db.initialize_schema()
    
    # Index all seasons and episodes
    seasons = await catalogues[0].seasons()
    for season in seasons:
        episodes = await season.episodes()
        for episode in episodes:
            index_episode(episode, db)
    
    db.close()

asyncio.run(index_series("one piece"))
```

## Troubleshooting

### Command not found in Docker

If you get an error like `executable file not found in $PATH` when running a command:

```bash
docker compose run --rm app scrapsama-index-all
# Error: executable file not found in $PATH
```

This means the Docker image needs to be rebuilt to include the new commands:

```bash
# Rebuild the Docker image
docker compose build app

# Then run the command
docker compose run --rm app scrapsama-index-all
```

## Database Schema

**episodes table:**
- serie_name, season_name, episode_name, episode_index, season_number

**players table:**
- episode_id, language, player_url, player_hostname

## License

GPL-3.0
