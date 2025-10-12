#!/usr/bin/env python3
"""
Demo script showing how to use the automatic series indexing feature.

This demonstrates both the programmatic API and the CLI usage.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("Anime-Sama Automatic Series Indexing - Usage Examples")
print("=" * 70)

print("\n1. Using the new CLI command:")
print("-" * 70)
print("""
# Index an entire series automatically
$ anime-sama-index-series

# You'll be prompted for a series name, then:
# - The system searches for the series
# - You select one from search results (if multiple)
# - ALL seasons are automatically processed
# - ALL episodes are automatically indexed
# - No manual season/episode selection required!
""")

print("\n2. Using the flag with the main CLI:")
print("-" * 70)
print("""
# Use the --index-full flag with anime-sama
$ anime-sama --index-full

# Same behavior as anime-sama-index-series
""")

print("\n3. Programmatic API usage:")
print("-" * 70)
print("""
import asyncio
from anime_sama_api import AnimeSama, Database, index_episode

async def index_series_programmatically(series_name):
    # Search for series
    anime_sama = AnimeSama("https://anime-sama.fr/")
    catalogues = await anime_sama.search(series_name)
    
    if not catalogues:
        print(f"No series found: {series_name}")
        return
    
    catalogue = catalogues[0]  # Take first result
    
    # Setup database
    db = Database()
    db.connect()
    db.initialize_schema()
    
    # Get all seasons
    seasons = await catalogue.seasons()
    
    # Index all episodes from all seasons
    for season in seasons:
        episodes = await season.episodes()
        for episode in episodes:
            success = index_episode(episode, db)
            if success:
                print(f"Indexed: {episode.name}")
    
    db.close()

# Run it
asyncio.run(index_series_programmatically("one piece"))
""")

print("\n4. Key Features:")
print("-" * 70)
print("""
✓ No manual season selection
✓ No manual episode selection  
✓ Processes ALL seasons automatically
✓ Indexes ALL episodes automatically
✓ Progress reporting for each season and episode
✓ Error handling for failed episodes
✓ Summary statistics at the end
✓ Database connection reuse for efficiency
""")

print("\n5. Requirements:")
print("-" * 70)
print("""
- MySQL 8.0 or higher running
- mysql-connector-python installed
- Database configured (see DATABASE.md)
- Database schema initialized (run setup_database.py)
""")

print("\n6. Example Session:")
print("-" * 70)
print("""
$ anime-sama-index-series
Series name: naruto

Searching for naruto...

Starting full series indexing for: Naruto

Getting all seasons for Naruto...
Found 3 season(s)

Processing season 1/3: Saison 1
Getting episodes for Saison 1...
Found 220 episode(s)

  ✓ [1/220] Episode 1
  ✓ [2/220] Episode 2
  ✓ [3/220] Episode 3
  ...

Processing season 2/3: Saison 2
Getting episodes for Saison 2...
Found 500 episode(s)
  ...

Indexing Complete!
Series: Naruto
Total episodes processed: 720
Successfully indexed: 720
""")

print("\n" + "=" * 70)
print("For more information, see DATABASE.md")
print("=" * 70)
print()
