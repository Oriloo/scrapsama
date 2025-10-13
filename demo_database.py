#!/usr/bin/env python3
"""
Demonstration script for database indexing feature.

This script shows how to use the database indexing functionality
to store video links and episode information.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from anime_sama_api import Episode, Languages, Players, index_episode, DatabaseConfig


def demo_basic_indexing():
    """Demonstrate basic episode indexing."""
    print("=" * 60)
    print("Demo: Basic Episode Indexing")
    print("=" * 60)
    
    # Create an example episode
    episode = Episode(
        Languages(
            vostfr=Players([
                "https://vidmoly.net/embed-abc123.html",
                "https://video.sibnet.ru/shell.php?videoid=12345",
                "https://sendvid.com/embed/test123",
            ]),
            vf=Players([
                "https://vidmoly.net/embed-def456.html",
                "https://video.sibnet.ru/shell.php?videoid=67890",
            ])
        ),
        serie_name="one-piece",
        season_name="saison1",
        _name="Episode 1",
        index=1,
    )
    
    print(f"\nEpisode Information:")
    print(f"  Serie: {episode.serie_name}")
    print(f"  Season: {episode.season_name}")
    print(f"  Episode: {episode.name}")
    print(f"  Index: {episode.index}")
    print(f"\nAvailable Languages:")
    for lang_id, players in episode.languages.items():
        print(f"  {lang_id}: {len(players)} player(s)")
        for i, player in enumerate(players, 1):
            print(f"    {i}. {player}")
    
    print("\n" + "-" * 60)
    print("Attempting to index episode to database...")
    print("-" * 60)
    
    result = index_episode(episode)
    
    if result:
        print("\n✓ Episode successfully indexed to database!")
        print("\nYou can now query the database to retrieve:")
        print("  - Episode metadata (serie, season, episode name)")
        print("  - All player URLs for each language")
        print("  - Player ordering and hostname information")
    else:
        print("\n⚠ Database indexing failed.")
        print("\nThis is expected if:")
        print("  - MySQL is not running")
        print("  - Database credentials are incorrect")
        print("  - mysql-connector-python is not installed")
        print("\nTo enable database indexing:")
        print("  1. Install: pip install mysql-connector-python")
        print("  2. Setup MySQL database")
        print("  3. Run: python setup_database.py")


def demo_config():
    """Show database configuration options."""
    print("\n\n" + "=" * 60)
    print("Demo: Database Configuration")
    print("=" * 60)
    
    print("\nDatabase configuration can be set via:")
    print("\n1. Config file (~/.config/anime-sama_cli/config.toml):")
    print("""
    [database]
    host = "localhost"
    port = 3306
    database = "animesama_db"
    user = "animesama_user"
    password = "animesama_password"
    """)
    
    print("\n2. Environment variables (takes precedence):")
    print("    export DB_HOST=localhost")
    print("    export DB_PORT=3306")
    print("    export DB_NAME=animesama_db")
    print("    export DB_USER=animesama_user")
    print("    export DB_PASSWORD=animesama_password")
    
    print("\n3. Programmatically:")
    print("""
    from anime_sama_api import DatabaseConfig, Database
    
    config = DatabaseConfig(
        host="localhost",
        port=3306,
        database="animesama_db",
        user="animesama_user",
        password="animesama_password"
    )
    
    db = Database(config)
    db.connect()
    db.initialize_schema()
    """)
    
    # Show current config
    config = DatabaseConfig.from_env()
    print("\nCurrent Database Configuration:")
    print(f"  Host: {config.host}")
    print(f"  Port: {config.port}")
    print(f"  Database: {config.database}")
    print(f"  User: {config.user}")


def demo_usage():
    """Show usage examples."""
    print("\n\n" + "=" * 60)
    print("Demo: Usage Examples")
    print("=" * 60)
    
    print("\n1. Use the indexing CLI:")
    print("   $ anime-sama-index-series")
    print("\n2. Or use the main command:")
    print("   $ anime-sama")
    print("\n3. Videos will be indexed to the database")
    
    print("\n\nProgrammatic Usage:")
    print("""
    from anime_sama_api import (
        Episode, Languages, Players,
        index_episode, Database
    )
    
    # Create episode
    episode = Episode(
        Languages(
            vostfr=Players([
                "https://player1.com/video",
                "https://player2.com/video"
            ])
        ),
        serie_name="my-anime",
        season_name="saison1",
        _name="Episode 1",
        index=1
    )
    
    # Index to database
    success = index_episode(episode)
    
    # Or use Database directly for more control
    db = Database()
    if db.connect():
        db.initialize_schema()
        episode_id = db.save_episode({
            "serie_name": episode.serie_name,
            "season_name": episode.season_name,
            "episode_name": episode.name,
            "episode_index": episode.index,
            "season_number": episode.season_number,
        })
        db.close()
    """)


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Anime-Sama Database Indexing Feature Demo".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    
    try:
        demo_basic_indexing()
        demo_config()
        demo_usage()
        
        print("\n\n" + "=" * 60)
        print("Demo Complete!")
        print("=" * 60)
        print("\nFor more information, see DATABASE.md")
        print("\n")
        
        return 0
    except KeyboardInterrupt:
        print("\n\n[Interrupted]")
        return 1
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
