# Automatic Series Indexing - Quick Reference

## Problem Statement
Previously, the system required manual selection at each step:
1. User enters anime name
2. User selects catalogue
3. **User selects season** ← Manual
4. **User selects episode(s)** ← Manual

## Solution
New automated process that skips manual selection:
1. User provides series name
2. System automatically processes ALL seasons
3. System automatically indexes ALL episodes
4. Complete database indexing without any manual intervention

## Usage

### Option 1: Dedicated Command
```bash
anime-sama-index-series
```

### Option 2: Main CLI with Flag
```bash
anime-sama --index-full
```

## How It Works

```
User Input: Series Name
     ↓
Search & Select Catalogue
     ↓
Get ALL Seasons (automatic)
     ↓
For each season:
  ├─ Get ALL Episodes (automatic)
  └─ Index each episode to database
     ↓
Summary Report
```

## Key Features

✅ **Automated**: No manual season/episode selection  
✅ **Exhaustive**: Processes ALL seasons and episodes  
✅ **Progress Tracking**: Real-time feedback  
✅ **Error Handling**: Continues on failure  
✅ **Summary Statistics**: Total indexed count  
✅ **Database Optimized**: Single connection for all operations  

## Example Output

```
Starting full series indexing for: One Piece

Getting all seasons for One Piece...
Found 1 season(s)

Processing season 1/1: Saison 1
Getting episodes for Saison 1...
Found 1122 episode(s)

  ✓ [1/1122] Episode 1
  ✓ [2/1122] Episode 2
  ...

Indexing Complete!
Series: One Piece
Total episodes processed: 1122
Successfully indexed: 1122
```

## Requirements

- MySQL 8.0+ running
- `mysql-connector-python` installed
- Database configured (see DATABASE.md)
- Database schema initialized

## API Usage

```python
import asyncio
from anime_sama_api import AnimeSama, Database, index_episode

async def index_series(series_name: str):
    # Initialize
    anime_sama = AnimeSama("https://anime-sama.fr/")
    db = Database()
    db.connect()
    db.initialize_schema()
    
    # Search and select
    catalogues = await anime_sama.search(series_name)
    catalogue = catalogues[0]
    
    # Get all seasons
    seasons = await catalogue.seasons()
    
    # Index all episodes from all seasons
    for season in seasons:
        episodes = await season.episodes()
        for episode in episodes:
            index_episode(episode, db)
    
    db.close()

asyncio.run(index_series("one piece"))
```

## Comparison

### Before (Manual)
```
anime-sama
  → Enter name: "one piece"
  → Select catalogue: [1]
  → Select season: [1]     ← Manual
  → Select episodes: [1-5] ← Manual
```

### After (Automatic)
```
anime-sama-index-series
  → Enter name: "one piece"
  → Select catalogue: [1]
  → [Automatic: All seasons, all episodes]
```

## Benefits

1. **Time Saving**: No repetitive selections
2. **Complete Coverage**: Never miss episodes
3. **Consistent**: Same process for all series
4. **Reliable**: Database-backed indexing
5. **Scalable**: Handles series with many seasons/episodes

## Files Changed

- `anime_sama_api/cli/__main__.py` - Added `--index-full` flag support
- `anime_sama_api/cli/index_series.py` - New dedicated command
- `pyproject.toml` - New script entry point
- `DATABASE.md` - Updated documentation
- `README.md` - Updated feature list
- `tests/test_index_series.py` - Tests for new functionality
