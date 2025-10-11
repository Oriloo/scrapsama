#!/usr/bin/env python3
"""Manual tests for database functionality without pytest."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anime_sama_api.database import Database, DatabaseConfig, index_episode
from anime_sama_api.episode import Episode, Languages, Players


def test_database_config_defaults():
    """Test default database configuration."""
    print("Testing database config defaults...")
    config = DatabaseConfig()
    assert config.host == "localhost"
    assert config.port == 3306
    assert config.database == "animesama_db"
    assert config.user == "animesama_user"
    assert config.password == "animesama_password"
    print("✓ Database config defaults work")


def test_database_config_from_env():
    """Test loading database configuration from environment variables."""
    print("\nTesting database config from environment...")
    os.environ["DB_HOST"] = "testhost"
    os.environ["DB_PORT"] = "3307"
    os.environ["DB_NAME"] = "testdb"
    os.environ["DB_USER"] = "testuser"
    os.environ["DB_PASSWORD"] = "testpass"
    
    config = DatabaseConfig.from_env()
    assert config.host == "testhost"
    assert config.port == 3307
    assert config.database == "testdb"
    assert config.user == "testuser"
    assert config.password == "testpass"
    
    # Clean up
    del os.environ["DB_HOST"]
    del os.environ["DB_PORT"]
    del os.environ["DB_NAME"]
    del os.environ["DB_USER"]
    del os.environ["DB_PASSWORD"]
    
    print("✓ Database config from environment works")


def test_database_initialization():
    """Test database initialization."""
    print("\nTesting database initialization...")
    db = Database()
    assert db.config is not None
    assert db._connection is None
    print("✓ Database initialization works")


def test_index_episode_without_connection():
    """Test indexing episode without database connection."""
    print("\nTesting index_episode without connection...")
    episode = Episode(
        Languages(
            vostfr=Players([
                "https://vidmoly.net/embed-test.html",
                "https://video.sibnet.ru/shell.php?videoid=12345",
            ])
        ),
        serie_name="test-serie",
        season_name="saison1",
        _name="Episode 1",
        index=1,
    )
    
    # Should not crash when database is not available
    result = index_episode(episode)
    assert isinstance(result, bool)
    assert result is False  # Should fail without connection
    print("✓ index_episode handles missing connection gracefully")


def test_episode_with_multiple_languages():
    """Test episode with multiple languages."""
    print("\nTesting episode with multiple languages...")
    episode = Episode(
        Languages(
            vostfr=Players([
                "https://vidmoly.net/embed-test1.html",
                "https://video.sibnet.ru/shell.php?videoid=12345",
            ]),
            vf=Players([
                "https://vidmoly.net/embed-test2.html",
            ])
        ),
        serie_name="test-serie",
        season_name="saison1",
        _name="Episode 1",
        index=1,
    )
    
    assert len(episode.languages) == 2
    assert "vostfr" in episode.languages
    assert "vf" in episode.languages
    print("✓ Episode with multiple languages works")


def main():
    """Run all tests."""
    print("=== Running Database Tests ===\n")
    
    try:
        test_database_config_defaults()
        test_database_config_from_env()
        test_database_initialization()
        test_index_episode_without_connection()
        test_episode_with_multiple_languages()
        
        print("\n=== All Tests Passed ===")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
