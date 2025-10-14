# Database Schema Changes - Summary

## Overview

This update adds three new tables to the database schema: `series`, `seasons`, and `failures`. The new schema provides better data organization and error tracking.

## New Tables

### 1. **series** table
Stores information about anime/manga series (catalogues).

**Columns:**
- `id` - Primary key
- `name` - Series name (unique)
- `url` - Series URL
- `alternative_names` - JSON array of alternative names
- `genres` - JSON array of genres
- `categories` - JSON array of categories (Anime, Scans, Film, Autres)
- `languages` - JSON array of available languages
- `image_url` - Series image URL
- `advancement` - Series advancement status
- `correspondence` - Episode-to-chapter correspondence
- `synopsis` - Series synopsis
- `is_mature` - Boolean flag for mature content
- `created_at`, `updated_at` - Timestamps

### 2. **seasons** table
Stores information about seasons of a series.

**Columns:**
- `id` - Primary key
- `serie_id` - Foreign key to series table
- `name` - Season name
- `url` - Season URL
- `created_at`, `updated_at` - Timestamps

**Constraints:**
- Foreign key: `serie_id` → `series.id` (CASCADE DELETE)
- Unique constraint: `(serie_id, name)`

### 3. **failures** table
Logs all indexing failures for troubleshooting.

**Columns:**
- `id` - Primary key
- `entity_type` - Type of entity (series, season, episode, player)
- `entity_name` - Name/identifier of the failed entity
- `entity_id` - Database ID of the entity (if available)
- `error_message` - Short error message
- `error_details` - Detailed error information
- `created_at` - When the error occurred

## Updated Tables

### **episodes** table
**Changes:**
- Added `season_id` - Foreign key to seasons table
- Changed unique constraint to `(season_id, episode_index)` instead of `(serie_name, season_name, episode_index)`

**Maintains backward compatibility:**
- Still stores `serie_name` and `season_name` for legacy compatibility

### **players** table
No structural changes, but error logging added when saving fails.

## Database Relationships

```
series (1) ---> (N) seasons
seasons (1) ---> (N) episodes  
episodes (1) ---> (N) players

failures - independent logging table
```

## New Functions

### `index_serie(catalogue, db)`
Indexes a series (Catalogue object) into the database.

**Returns:** Series ID or None

### `index_season(season, serie_id, db)`
Indexes a season into the database.

**Parameters:**
- `season` - Season object
- `serie_id` - ID of parent series

**Returns:** Season ID or None

### `index_episode(episode, season_id, db)` - Updated
Now requires `season_id` parameter (optional for backward compatibility).

**Parameters:**
- `episode` - Episode object
- `season_id` - ID of parent season (will be looked up if not provided)
- `db` - Database instance

**Returns:** True if successful, False otherwise

### `log_failure(entity_type, entity_name, error_message, error_details, entity_id)`
Logs an indexing failure to the database.

**Parameters:**
- `entity_type` - 'series', 'season', 'episode', or 'player'
- `entity_name` - Identifier for the entity
- `error_message` - Brief error description
- `error_details` - Detailed error information (optional)
- `entity_id` - Database ID if available (optional)

## Migration Notes

### For Existing Databases

If you have an existing database with episodes and players, you'll need to:

1. Back up your data
2. Run `init_db.py` to create new tables (existing tables won't be affected)
3. Optionally migrate existing data:
   - Extract unique series from episodes table
   - Extract unique seasons from episodes table
   - Create corresponding entries in series and seasons tables
   - Update episodes table with season_id

### Fresh Installation

Simply run `init_db.py` to create all tables.

## Usage Examples

### Indexing a Series Completely

```python
from scraper import AnimeSama, Database
from scraper.database import index_serie, index_season, index_episode

async def index_complete_series(series_name):
    anime_sama = AnimeSama("https://anime-sama.fr/")
    catalogues = await anime_sama.search(series_name)
    catalogue = catalogues[0]
    
    db = Database()
    db.connect()
    db.initialize_schema()
    
    # Index series
    serie_id = index_serie(catalogue, db)
    
    # Index seasons and episodes
    seasons = await catalogue.seasons()
    for season in seasons:
        season_id = index_season(season, serie_id, db)
        episodes = await season.episodes()
        for episode in episodes:
            index_episode(episode, season_id, db)
    
    db.close()
```

### Checking Failures

```sql
-- View all failures
SELECT * FROM failures ORDER BY created_at DESC;

-- View failures by type
SELECT entity_type, COUNT(*) as count 
FROM failures 
GROUP BY entity_type;

-- View recent episode failures
SELECT * FROM failures 
WHERE entity_type = 'episode' 
ORDER BY created_at DESC 
LIMIT 10;
```

## Benefits

1. **Better Data Organization**: Hierarchical structure (series → seasons → episodes → players)
2. **Metadata Storage**: Store series information (synopsis, genres, etc.)
3. **Error Tracking**: Comprehensive failure logging for debugging
4. **Data Integrity**: Foreign key constraints ensure data consistency
5. **Flexibility**: Can query at any level (series, season, episode)
