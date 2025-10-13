# Database Indexing Feature

## Overview

This project indexes anime video links and episode information in a MySQL database. This allows you to:
- Store video URLs for later use
- Keep track of all episodes and their available languages
- Query and manage your anime collection efficiently
- Easily access player URLs when needed
- **Automatically index entire series with all seasons and episodes**

## Requirements

1. MySQL 8.0 or higher
2. Python package: `mysql-connector-python`

```bash
pip install mysql-connector-python
```

Or install with database support:
```bash
pip install 'anime-sama-api[cli,database]'
```

## Automatic Series Indexing

### New Command: `anime-sama-index-series`

A new command-line tool has been added to automatically index all episodes of a series:

```bash
anime-sama-index-series
```

This command will:
1. Prompt for a series name
2. Search for the series
3. Let you select from search results (if multiple matches)
4. **Automatically process ALL seasons**
5. **Automatically index ALL episodes** without manual selection
6. Display progress for each season and episode
7. Provide a summary of indexed episodes

### Using the Main CLI

You can also use the main `anime-sama` command which now redirects to indexing:

```bash
anime-sama
```

This will start the series indexing process.

### Example Usage

```bash
$ anime-sama-index-series
Series name: one piece
Searching for one piece...

Starting full series indexing for: One Piece

Getting all seasons for One Piece...
Found 1 season(s)

Processing season 1/1: Saison 1
Getting episodes for Saison 1...
Found 1122 episode(s)

  ✓ [1/1122] Episode 1
  ✓ [2/1122] Episode 2
  ✓ [3/1122] Episode 3
  ...

Indexing Complete!
Series: One Piece
Total episodes processed: 1122
Successfully indexed: 1122
```

## Configuration

### 1. Database Setup

You can configure the database connection using environment variables or the config file.

#### Using Environment Variables (Recommended)

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=animesama_db
export DB_USER=animesama_user
export DB_PASSWORD=animesama_password
```

#### Using Config File

Edit `~/.config/anime-sama_cli/config.toml` (Linux/macOS) or `%APPDATA%/Local/anime-sama_cli/config.toml` (Windows):

```toml
[database]
host = "localhost"
port = 3306
database = "animesama_db"
user = "animesama_user"
password = "animesama_password"
```

### 2. Initialize Database Schema

Run the setup script to create the necessary tables:

```bash
python setup_database.py
```

Or from the repository:
```bash
python /path/to/anime-sama-api/setup_database.py
```

## Database Schema

The feature creates two tables:

### `episodes` table
- `id`: Primary key
- `serie_name`: Name of the series
- `season_name`: Name of the season
- `episode_name`: Name of the episode
- `episode_index`: Episode number
- `season_number`: Season number
- `created_at`: Timestamp when indexed
- `updated_at`: Timestamp of last update

### `players` table
- `id`: Primary key
- `episode_id`: Foreign key to episodes table
- `language`: Language code (vf, vostfr, etc.)
- `player_url`: Full URL to the video player
- `player_hostname`: Hostname of the player (for filtering)
- `player_order`: Order of the player in the list
- `created_at`: Timestamp when indexed

## Usage

Once configured, use the indexing commands:

```bash
anime-sama-index-series
# or
anime-sama
```

The application will:
1. Search for the anime
2. Select the series from search results
3. Automatically index all seasons and episodes
4. Store video links and episode information in the database
5. Display progress and summary

## Docker Setup

The project includes a Docker Compose configuration with MySQL and phpMyAdmin:

```bash
# Start all services
docker compose up -d

# Initialize database schema
docker compose run --rm app python setup_database.py

# Run the indexing tool
docker compose run --rm app anime-sama-index-series

# Or use the main command
docker compose run --rm app anime-sama
```

Access phpMyAdmin at http://localhost:8080 to view your indexed data.

## Querying the Database

### Get all episodes for a series
```sql
SELECT * FROM episodes 
WHERE serie_name = 'one-piece' 
ORDER BY season_number, episode_index;
```

### Get all player URLs for an episode
```sql
SELECT p.language, p.player_url, p.player_hostname
FROM players p
JOIN episodes e ON p.episode_id = e.id
WHERE e.serie_name = 'one-piece' 
  AND e.episode_name = 'Episode 1'
ORDER BY p.language, p.player_order;
```

### Count episodes per series
```sql
SELECT serie_name, COUNT(*) as episode_count
FROM episodes
GROUP BY serie_name
ORDER BY episode_count DESC;
```

## Troubleshooting

### Connection Issues

If you see "Failed to connect to database", check:
1. MySQL service is running
2. Database credentials are correct
3. `mysql-connector-python` is installed
4. Database exists and user has proper permissions

### Missing Tables

If you see errors about missing tables, run:
```bash
python setup_database.py
```

### Environment Variables Not Working

Environment variables take precedence over config file settings. If using Docker, make sure they're defined in `docker-compose.yml`.

## API Usage

You can also use the database indexing feature programmatically:

```python
from anime_sama_api import Episode, Languages, Players, index_episode

episode = Episode(
    Languages(
        vostfr=Players([
            "https://vidmoly.net/embed-example.html",
            "https://video.sibnet.ru/shell.php?videoid=12345",
        ])
    ),
    serie_name="my-anime",
    season_name="saison1",
    _name="Episode 1",
    index=1,
)

# Index the episode
success = index_episode(episode)
```
