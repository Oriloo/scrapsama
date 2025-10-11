# Quick Start Guide - Database Indexing with Docker

This guide shows how to use the database indexing feature with Docker to store video links instead of downloading.

## Prerequisites

- Docker and Docker Compose installed
- Repository cloned

## Steps

### 1. Start Services

```bash
docker compose up -d
```

This starts:
- MySQL database (port 3306)
- phpMyAdmin (http://localhost:8080)
- Anime-Sama app

### 2. Initialize Database

```bash
docker compose run --rm app python setup_database.py
```

This creates the required tables:
- `episodes` - stores episode metadata
- `players` - stores video player URLs

### 3. Enable Indexing

**Option A: Permanent (recommended)**

Edit `docker-compose.yml`, find the `app` service, and change:

```yaml
environment:
  - INDEX_TO_DATABASE=false
```

to:

```yaml
environment:
  - INDEX_TO_DATABASE=true
```

Then restart:

```bash
docker compose restart app
```

**Option B: Temporary (for testing)**

```bash
docker compose run --rm -e INDEX_TO_DATABASE=true app anime-sama
```

### 4. Use the Application

```bash
docker compose run --rm app anime-sama
```

Now when you search for and select episodes:
- ✅ Video links are indexed in the database
- ✅ Episode metadata is stored
- ❌ Videos are NOT downloaded

### 5. View Indexed Data

Open phpMyAdmin at http://localhost:8080

Login:
- **Server:** mysql
- **Username:** root
- **Password:** rootpassword

Select database `animesama_db` and browse the tables:
- `episodes` - episode information
- `players` - video player URLs

## Example Queries

Open phpMyAdmin SQL tab and run:

```sql
-- See all indexed series
SELECT DISTINCT serie_name FROM episodes;

-- Count episodes per series
SELECT serie_name, COUNT(*) as total 
FROM episodes 
GROUP BY serie_name;

-- Get all player URLs for a specific episode
SELECT e.serie_name, e.episode_name, p.language, p.player_url
FROM episodes e
JOIN players p ON e.id = p.episode_id
WHERE e.serie_name = 'one-piece' AND e.episode_index = 1;

-- List all available languages
SELECT DISTINCT language FROM players;
```

## Troubleshooting

### "setup_database.py not found"
- Make sure you pulled the latest changes
- Rebuild the Docker image: `docker compose build app`

### "Failed to index: Episode 1"

This error appears when the database connection or setup failed. Check the logs above the error for the specific cause:

**If you see "mysql-connector-python not installed":**
- Rebuild the Docker image: `docker compose build app`
- The latest code includes this dependency

**If you see "Failed to connect to database":**
- Check MySQL is running: `docker compose ps mysql`
- Check the logs: `docker compose logs mysql`
- Verify the connection settings in docker-compose.yml

**If you see "Failed to initialize database schema":**
- Run the setup script: `docker compose run --rm app python setup_database.py`
- Check for permission errors in MySQL logs

**Common fix - Rebuild and setup:**
```bash
# Rebuild with latest changes
docker compose build app

# Start services
docker compose up -d

# Initialize database
docker compose run --rm app python setup_database.py

# Enable indexing in docker-compose.yml
# Set: INDEX_TO_DATABASE=true

# Restart
docker compose restart app
```

## Switching Back to Download Mode

To go back to downloading videos instead of indexing:

1. Edit `docker-compose.yml` and set:
   ```yaml
   - INDEX_TO_DATABASE=false
   ```

2. Restart:
   ```bash
   docker compose restart app
   ```

## Complete Workflow Example

```bash
# 1. Start everything
docker compose up -d

# 2. Setup database (only needed once)
docker compose run --rm app python setup_database.py

# 3. Enable indexing in docker-compose.yml (edit the file)
# Change INDEX_TO_DATABASE=false to INDEX_TO_DATABASE=true

# 4. Restart to apply changes
docker compose restart app

# 5. Search and index anime
docker compose run --rm app anime-sama
# Search: one-piece
# Select: Saga 1 (East Blue)
# Choose: Episode 1
# → Video link is now indexed in database!

# 6. View results in phpMyAdmin
# Open: http://localhost:8080
# Login: root / rootpassword
# Browse: animesama_db → episodes / players tables
```

## Need Help?

- See [DATABASE.md](DATABASE.md) for detailed documentation
- See [DOCKER.md](DOCKER.md) for Docker-specific information
- Check the logs: `docker compose logs app`
