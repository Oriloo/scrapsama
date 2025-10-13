# Anime-Sama Indexer

API for indexing anime series from anime-sama.fr into a MySQL database.

## Installation

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
export DB_NAME=animesama_db
export DB_USER=animesama_user
export DB_PASSWORD=animesama_password
```

## Usage

### CLI

```bash
# Index a full series
anime-sama-index-series
```

### Python API

```python
import asyncio
from anime_sama_api import AnimeSama, Database, index_episode

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

## Database Schema

**episodes table:**
- serie_name, season_name, episode_name, episode_index, season_number

**players table:**
- episode_id, language, player_url, player_hostname

## License

GPL-3.0
