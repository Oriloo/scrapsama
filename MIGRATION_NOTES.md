# Migration Summary: From Failures Table to Logs Table

## Overview
This document describes the changes made to replace the `failures` table with a new `logs` table that provides better tracking of indexing operations.

## What Changed

### Database Schema
- **Removed**: `failures` table (tracked individual failures with detailed error messages)
- **Added**: `logs` table (tracks complete indexing operations with statistics)

### New Logs Table Structure
```sql
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    command VARCHAR(255) NOT NULL,           -- e.g., "index[One Piece]", "index-all", "index-new"
    new_series INT DEFAULT 0,                -- Number of new series indexed
    new_seasons INT DEFAULT 0,               -- Number of new seasons indexed
    new_episodes INT DEFAULT 0,              -- Number of new episodes indexed
    error_count INT DEFAULT 0,               -- Total errors encountered
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_command (command),
    INDEX idx_created_at (created_at)
)
```

### API Changes
- **Removed**: `Database.log_failure(entity_type, entity_name, error_message, ...)`
- **Added**: `Database.log_indexing(command, new_series, new_seasons, new_episodes, error_count)`

### Command Tracking Format
Each indexing command now logs with a specific format:
- **index[series_name]**: When indexing a specific series (e.g., `index[One Piece]`)
- **index-all**: When indexing all available series
- **index-new**: When indexing new episodes from the homepage

## Benefits

1. **Better Statistics**: Track exactly how many series/seasons/episodes were indexed in each operation
2. **Simpler Schema**: One entry per indexing operation instead of one per failure
3. **Historical Data**: Easy to see indexing trends over time
4. **Error Tracking**: Still tracks error counts without cluttering the database

## Migration

### For New Installations
Simply run `init_db.py` - the logs table will be created automatically.

### For Existing Installations
Run the migration script:
```bash
# Docker
docker compose run --rm app python migrate_to_logs.py

# Local
python migrate_to_logs.py
```

The migration script will:
1. Create the new `logs` table
2. Drop the old `failures` table
3. Verify the migration was successful

**Note**: Historical failure data cannot be converted to the new format and will be lost. This is acceptable since the new logging approach provides different (and more useful) information.

## Usage Examples

### View Recent Indexing Operations
```sql
SELECT * FROM logs ORDER BY created_at DESC LIMIT 10;
```

### Statistics for a Specific Series
```sql
SELECT 
    command, 
    SUM(new_episodes) as total_episodes,
    SUM(error_count) as total_errors
FROM logs 
WHERE command LIKE 'index[%]'
GROUP BY command;
```

### Daily Indexing Summary
```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as operations,
    SUM(new_series) as series,
    SUM(new_seasons) as seasons,
    SUM(new_episodes) as episodes,
    SUM(error_count) as errors
FROM logs 
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

## Files Modified

1. `scraper/database.py`: Updated schema and replaced `log_failure` with `log_indexing`
2. `scraper/cli/index_series.py`: Added operation tracking and logging
3. `scraper/cli/index_all_series.py`: Added operation tracking and logging
4. `scraper/cli/index_new_episodes.py`: Added operation tracking and logging
5. `README.md`: Updated documentation
6. `migrate_to_logs.py`: New migration script for existing installations

## Testing

All changes have been:
- ✅ Syntax validated with Python AST parser
- ✅ Linted with ruff (all checks passing)
- ✅ Security scanned with CodeQL (no vulnerabilities found)
- ✅ Import tested successfully

## Security Summary

No security vulnerabilities were introduced by these changes. The CodeQL analysis found 0 alerts.
