# Scrapsama Indexer

API for indexing anime series from anime-sama.org into a MySQL database with a web-based streaming interface.

## Features

- **Indexer**: CLI tools to index anime series, seasons, and episodes into MySQL database
- **Web Interface**: Browser-based streaming site to search, browse, and watch anime episodes
- **Database**: MySQL backend for storing series information and player URLs
- **Anti-Detection**: FlareSolverr integration for bypassing CloudFlare and other anti-bot protections

## Installation

### Option 1: Docker (Recommended)

Requirements:
- Docker & Docker Compose

```bash
# Build the Docker image (required after updates)
docker compose build app

# Start services (MySQL + phpMyAdmin + FlareSolverr + Web Interface)
docker compose up -d

# Initialize database schema
docker compose run --rm app python init_db.py

# For existing installations: migrate from old failures table to new logs table
docker compose run --rm app python migrate_to_logs.py

# Run indexer to populate database
docker compose run --rm app scrapsama-index
```

Access:
- **Web Interface**: http://localhost:5000 - Browse and watch anime
- **phpMyAdmin**: http://localhost:8080 (user: root, password: rootpassword)
- **FlareSolverr**: http://localhost:8191 - Anti-bot protection service

### Option 2: Local Installation

Requirements:
- Python 3.10+
- MySQL 8.0+
- FlareSolverr (optional, but recommended for better anti-detection)

```bash
pip install -e .
pip install mysql-connector-python rich
```

If using FlareSolverr locally:
```bash
# Using Docker
docker run -d \
  --name=flaresolverr \
  -p 8191:8191 \
  -e LOG_LEVEL=info \
  ghcr.io/flaresolverr/flaresolverr:latest
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

### FlareSolverr Configuration

FlareSolverr provides strong anti-detection capabilities to bypass CloudFlare and other bot protections. Configure it via environment variables:

```bash
# Enable/disable FlareSolverr (default: true)
export FLARESOLVERR_ENABLED=true

# FlareSolverr service URL (default: http://localhost:8191/v1)
export FLARESOLVERR_URL=http://localhost:8191/v1

# For Docker setup, these are already configured in docker-compose.yml
```

When enabled, all HTTP requests from the scraper will automatically route through FlareSolverr, which uses a real browser (Chrome) to:
- Bypass CloudFlare protection
- Solve CAPTCHAs (if configured)
- Execute JavaScript and handle dynamic content
- Mimic real user behavior with proper headers and fingerprints

To disable FlareSolverr and use direct HTTP requests:
```bash
export FLARESOLVERR_ENABLED=false
```

## Usage

### Web Interface

Start the web interface:
```bash
docker compose up web
```

Then navigate to http://localhost:5000 in your browser to:
- Search for anime series
- Browse series by category
- Select seasons and episodes
- Choose language and player for streaming

### CLI

```bash
# Index a specific series (prompts for series name)
scrapsama-index

# Index all available series from anime-sama.org
scrapsama-index-all

# Index new episodes from anime-sama.org homepage
# This command fetches the latest episodes and updates the database
# Perfect for running as a regular cron job to keep the index up-to-date
scrapsama-index-new
```

#### Scheduling Regular Updates

To keep your database up-to-date with new episodes, you can schedule `scrapsama-index-new` to run regularly:

**Using Docker with cron:**
```bash
# Add to your crontab (crontab -e)
# Run every 6 hours
0 */6 * * * docker compose -f /path/to/docker-compose.yml run --rm app scrapsama-index-new

# Run daily at 2 AM
0 2 * * * docker compose -f /path/to/docker-compose.yml run --rm app scrapsama-index-new
```

**Using systemd timer (Linux):**
```bash
# Create /etc/systemd/system/scrapsama-index-new.service
[Unit]
Description=Index new anime episodes
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/scrapsama-index-new
User=youruser

# Create /etc/systemd/system/scrapsama-index-new.timer
[Unit]
Description=Run scrapsama-index-new every 6 hours

[Timer]
OnBootSec=15min
OnUnitActiveSec=6h

[Install]
WantedBy=timers.target

# Enable and start the timer
sudo systemctl enable scrapsama-index-new.timer
sudo systemctl start scrapsama-index-new.timer
```

### Python API

**Index a specific series:**
```python
import asyncio
from scraper import AnimeSama, Database, index_serie, index_season, index_episode

async def index_series(name):
    # Search series
    anime_sama = AnimeSama("https://anime-sama.org/")
    catalogues = await anime_sama.search(name)
    catalogue = catalogues[0]
    
    # Initialize database
    db = Database()
    db.connect()
    db.initialize_schema()
    
    # Index the series
    serie_id = index_serie(catalogue, db)
    
    # Index all seasons and episodes
    seasons = await catalogue.seasons()
    for season in seasons:
        season_id = index_season(season, serie_id, db)
        episodes = await season.episodes()
        for episode in episodes:
            index_episode(episode, season_id, db)
    
    db.close()

asyncio.run(index_series("one piece"))
```

**Get new episodes from homepage:**
```python
import asyncio
from scraper import AnimeSama

async def get_new_episodes():
    anime_sama = AnimeSama("https://anime-sama.org/")
    episode_releases = await anime_sama.new_episodes()
    
    for release in episode_releases:
        print(f"{release.serie_name} - {release.descriptive} ({release.language})")
        print(f"  URL: {release.page_url}")

asyncio.run(get_new_episodes())
```

**Using custom FlareSolverr configuration:**
```python
import asyncio
from scraper import AnimeSama, create_client

async def custom_client_example():
    # Create a custom client with specific FlareSolverr settings
    custom_client = create_client(
        flaresolverr_url="http://localhost:8191/v1",
        flaresolverr_enabled=True
    )
    
    # Use the custom client
    anime_sama = AnimeSama("https://anime-sama.org/", client=custom_client)
    catalogues = await anime_sama.search("one piece")
    
    # Don't forget to close the client
    await custom_client.aclose()

asyncio.run(custom_client_example())
```

## Anti-Detection Features

Scrapsama includes a robust anti-detection system powered by FlareSolverr to bypass CloudFlare and other bot protection mechanisms.

### How it Works

1. **FlareSolverr Integration**: When enabled, all HTTP requests are routed through FlareSolverr, which uses a real Chrome browser to:
   - Execute JavaScript and handle dynamic content
   - Solve CloudFlare challenges automatically
   - Maintain browser fingerprints and sessions
   - Handle cookies and redirects naturally

2. **Enhanced HTTP Headers**: Even with FlareSolverr disabled, the scraper uses realistic browser headers:
   - Modern Chrome User-Agent
   - French locale preferences (fr-FR)
   - Proper Accept headers for HTML/CSS/JS
   - Security headers (Sec-Fetch-*)
   - DNT (Do Not Track) header

3. **Session Management**: FlareSolverr sessions are automatically created and reused across requests for better performance and consistency.

### Performance Considerations

- **FlareSolverr Enabled**: Slower (~3-5 seconds per request) but more reliable for protected sites
- **FlareSolverr Disabled**: Faster but may fail on CloudFlare-protected pages
- **Recommendation**: Keep FlareSolverr enabled for production use

### Debugging

To check if FlareSolverr is working:

```bash
# Check FlareSolverr status
curl http://localhost:8191/v1 -X POST -H "Content-Type: application/json" \
  -d '{"cmd": "sessions.list"}'

# View FlareSolverr logs
docker logs scrapsama_flaresolverr
```

## Troubleshooting

### FlareSolverr Issues

**FlareSolverr not accessible:**
```bash
# Check if FlareSolverr is running
docker ps | grep flaresolverr

# Start FlareSolverr if not running
docker compose up -d flaresolverr

# Check FlareSolverr logs
docker logs scrapsama_flaresolverr --tail 50

# Test FlareSolverr manually
curl http://localhost:8191/v1 -X POST -H "Content-Type: application/json" \
  -d '{"cmd": "sessions.list"}'
```

**Requests timing out:**
```bash
# FlareSolverr may need more time for complex pages
# Increase timeout in docker-compose.yml or via environment variable
export FLARESOLVERR_MAXWAIT=120000  # 2 minutes in milliseconds
```

**To disable FlareSolverr temporarily:**
```bash
# Set environment variable
export FLARESOLVERR_ENABLED=false

# Or in docker-compose.yml, set:
# FLARESOLVERR_ENABLED: false
```

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

The database consists of 5 main tables:

**series table:**
- id (PRIMARY KEY)
- name, url
- alternative_names, genres, categories, languages (JSON)
- image_url, advancement, correspondence, synopsis
- is_mature (boolean)
- created_at, updated_at

**seasons table:**
- id (PRIMARY KEY)
- serie_id (FOREIGN KEY → series.id)
- name, url
- created_at, updated_at

**episodes table:**
- id (PRIMARY KEY)
- season_id (FOREIGN KEY → seasons.id)
- serie_name, season_name, episode_name, episode_index, season_number
- created_at, updated_at

**players table:**
- id (PRIMARY KEY)
- episode_id (FOREIGN KEY → episodes.id)
- language, player_url, player_hostname, player_order
- created_at

**logs table:**
- id (PRIMARY KEY)
- command (e.g., "index[series_name]", "index-all", "index-new")
- new_series, new_seasons, new_episodes (count of newly indexed items)
- error_count (number of errors encountered)
- created_at

The logs table tracks all indexing operations, recording statistics about what was indexed and any errors encountered during the process.

## Web Interface

The web application provides a user-friendly interface to browse and watch anime episodes.

### Features

- **Search**: Real-time search for anime series by name
- **Browse**: View all available series with thumbnails and categories
- **Series Page**: Detailed information including synopsis, genres, and available seasons
- **Season Page**: List all episodes for a selected season with available languages
- **Episode Player**: Select language and player to watch episodes directly in the browser

### Pages

1. **Home Page** (`/`): Search bar and grid of available series
2. **Series Detail** (`/series/<id>`): Series information and list of seasons
3. **Season Detail** (`/season/<id>`): List of all episodes in the season
4. **Episode Player** (`/episode/<id>`): Video player with language and player selection

### API Endpoints

- `GET /search?q=<query>`: Search for series by name
- `GET /api/series`: List all series (limited to 100)

All player URLs stored in the database are accessible through the episode player interface.

## License

GPL-3.0
