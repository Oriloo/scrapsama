"""Tests for database functionality."""
import pytest
from anime_sama_api.database import Database, DatabaseConfig, index_episode
from anime_sama_api.episode import Episode, Languages, Players


def test_database_config_from_env(monkeypatch):
    """Test loading database configuration from environment variables."""
    monkeypatch.setenv("DB_HOST", "testhost")
    monkeypatch.setenv("DB_PORT", "3307")
    monkeypatch.setenv("DB_NAME", "testdb")
    monkeypatch.setenv("DB_USER", "testuser")
    monkeypatch.setenv("DB_PASSWORD", "testpass")
    
    config = DatabaseConfig.from_env()
    assert config.host == "testhost"
    assert config.port == 3307
    assert config.database == "testdb"
    assert config.user == "testuser"
    assert config.password == "testpass"


def test_database_initialization():
    """Test database initialization."""
    db = Database()
    assert db.config is not None
    assert db._connection is None


def test_index_episode_without_connection():
    """Test indexing episode without database connection."""
    episode = Episode(
        Languages(
            vostfr=Players(
                [
                    "https://vidmoly.net/embed-test.html",
                    "https://video.sibnet.ru/shell.php?videoid=12345",
                ]
            ),
        ),
        serie_name="test-serie",
        season_name="saison1",
        _name="Episode 1",
        index=1,
    )
    
    # Should not crash when database is not available
    # Returns False when connection fails
    result = index_episode(episode)
    assert isinstance(result, bool)


def test_database_config_defaults():
    """Test default database configuration."""
    config = DatabaseConfig()
    assert config.host == "localhost"
    assert config.port == 3306
    assert config.database == "animesama_db"
    assert config.user == "animesama_user"
    assert config.password == "animesama_password"
