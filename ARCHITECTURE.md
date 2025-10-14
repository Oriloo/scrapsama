# Scrapsama Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Docker Compose                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │              │  │              │  │                      │  │
│  │    MySQL     │  │     App      │  │      Web (NEW)      │  │
│  │  Container   │  │  Container   │  │     Container       │  │
│  │              │  │              │  │                      │  │
│  │  Port: 3306  │  │  CLI Tools   │  │   Flask Web App     │  │
│  │              │  │  - Indexer   │  │   Port: 5000        │  │
│  │  Database:   │  │  - Scraper   │  │                      │  │
│  │  scrapsama_db│  │              │  │   Routes:            │  │
│  │              │  │              │  │   - /                │  │
│  └──────┬───────┘  └──────┬───────┘  │   - /search         │  │
│         │                 │          │   - /series/<id>    │  │
│         │                 │          │   - /season/<id>    │  │
│         └─────────────────┴──────────┤   - /episode/<id>   │  │
│                   │                  │   - /api/series     │  │
│                   │                  │                      │  │
│  ┌──────────────┐ │                  └──────────┬───────────┘  │
│  │              │ │                             │               │
│  │ phpMyAdmin   │ │                             │               │
│  │  Container   │ │                             │               │
│  │              │ │                             │               │
│  │ Port: 8080   │ │                             │               │
│  │              │ │                             │               │
│  └──────────────┘ │                             │               │
│         │          │                             │               │
│         └──────────┴─────────────────────────────┘               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │
                    ┌────────▼────────┐
                    │                 │
                    │  anime-sama.fr  │
                    │   (scraping)    │
                    │                 │
                    └─────────────────┘
```

## Data Flow

### Indexing Flow (CLI)
```
1. User runs: docker compose run --rm app scrapsama-index
2. App scrapes anime-sama.fr for series information
3. App stores data in MySQL:
   - series table (name, genres, categories, etc.)
   - seasons table (linked to series)
   - episodes table (linked to seasons)
   - players table (video URLs, linked to episodes)
4. Data is now available for web interface
```

### Web Streaming Flow
```
1. User opens browser → http://localhost:5000
2. Flask app serves index.html
3. JavaScript loads series list via /api/series
4. User searches or clicks series
5. Flask queries MySQL for series/season/episode data
6. Flask renders template with data
7. User selects episode and player
8. JavaScript loads player URL in iframe
9. User watches video directly in browser
```

## Database Schema

```
┌─────────────────┐
│     series      │
├─────────────────┤
│ id (PK)         │
│ name            │
│ url             │
│ genres (JSON)   │
│ categories      │
│ languages       │
│ image_url       │
│ synopsis        │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐
│     seasons     │
├─────────────────┤
│ id (PK)         │
│ serie_id (FK)   │
│ name            │
│ url             │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐
│    episodes     │
├─────────────────┤
│ id (PK)         │
│ season_id (FK)  │
│ episode_name    │
│ episode_index   │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐
│     players     │
├─────────────────┤
│ id (PK)         │
│ episode_id (FK) │
│ language        │
│ player_url      │
│ player_hostname │
│ player_order    │
└─────────────────┘
```

## Technology Stack

### Backend
- Python 3.12
- Flask 3.0+ (Web framework)
- httpx (HTTP client for scraping)
- mysql-connector-python (Database driver)

### Frontend
- HTML5
- CSS3 (Custom styling)
- Vanilla JavaScript (No frameworks)

### Infrastructure
- Docker & Docker Compose
- MySQL 8.0
- phpMyAdmin (Database management)

### Deployment
- Multi-container Docker setup
- Shared network for container communication
- Volume mounts for code and data
- Environment variable configuration

## Port Mapping

- **5000**: Web interface (Flask app)
- **8080**: phpMyAdmin (Database admin)
- **3306**: MySQL (Internal only, not exposed by default)

## Environment Variables

```bash
DB_HOST=mysql          # MySQL container hostname
DB_PORT=3306           # MySQL port
DB_NAME=scrapsama_db   # Database name
DB_USER=scrapsama_user # Database user
DB_PASSWORD=scrapsama_password # Database password
```

## Key Components

### 1. Scraper Module (`scraper/`)
- Scrapes anime-sama.fr
- Parses HTML and JavaScript
- Extracts series, seasons, episodes, players
- Stores in database

### 2. Web Application (`webapp/`)
- Flask routes and views
- HTML templates (Jinja2)
- Static assets (CSS, JS)
- Database queries
- JSON API endpoints

### 3. Database (`database.py`)
- Connection management
- Schema initialization
- CRUD operations
- Error logging

## Security

- No authentication required (public site)
- Database credentials in environment variables
- Flask template auto-escaping (XSS protection)
- Database connection validation
- Error handling for missing data
