"""Database module for storing video links and episode information."""
import logging
import os
from dataclasses import dataclass
from typing import Optional
import json

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Configuration for database connection."""
    host: str = "localhost"
    port: int = 3306
    database: str = "animesama_db"
    user: str = "animesama_user"
    password: str = "animesama_password"

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load database configuration from environment variables."""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            database=os.getenv("DB_NAME", "animesama_db"),
            user=os.getenv("DB_USER", "animesama_user"),
            password=os.getenv("DB_PASSWORD", "animesama_password"),
        )


class Database:
    """Database interface for storing episode and player information."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """Initialize database connection.
        
        Args:
            config: Database configuration. If None, loads from environment.
        """
        self.config = config or DatabaseConfig.from_env()
        self._connection = None
        
    def connect(self):
        """Establish database connection."""
        try:
            import mysql.connector
            self._connection = mysql.connector.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
            )
            logger.info("Successfully connected to database")
            return True
        except ImportError:
            logger.error("mysql-connector-python not installed. Database features disabled.")
            logger.error("Install with: pip install mysql-connector-python")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            logger.error(f"Connection details: host={self.config.host}, port={self.config.port}, database={self.config.database}, user={self.config.user}")
            logger.error("Please check that MySQL is running and credentials are correct")
            return False
    
    def initialize_schema(self):
        """Create database tables if they don't exist."""
        if not self._connection:
            return False
            
        cursor = self._connection.cursor()
        try:
            # Create episodes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    serie_name VARCHAR(255) NOT NULL,
                    season_name VARCHAR(255) NOT NULL,
                    episode_name VARCHAR(255) NOT NULL,
                    episode_index INT NOT NULL,
                    season_number INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_serie (serie_name),
                    INDEX idx_season (season_name),
                    INDEX idx_episode (episode_name),
                    UNIQUE KEY unique_episode (serie_name, season_name, episode_index)
                )
            """)
            
            # Create players table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    episode_id INT NOT NULL,
                    language VARCHAR(50) NOT NULL,
                    player_url TEXT NOT NULL,
                    player_hostname VARCHAR(255),
                    player_order INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE,
                    INDEX idx_episode (episode_id),
                    INDEX idx_language (language)
                )
            """)
            
            self._connection.commit()
            logger.info("Database schema initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            self._connection.rollback()
            return False
        finally:
            cursor.close()
    
    def save_episode(self, episode_data: dict) -> Optional[int]:
        """Save episode information to database.
        
        Args:
            episode_data: Dictionary containing episode information
            
        Returns:
            Episode ID if successful, None otherwise
        """
        if not self._connection:
            return None
            
        cursor = self._connection.cursor()
        try:
            # Insert or update episode
            cursor.execute("""
                INSERT INTO episodes 
                (serie_name, season_name, episode_name, episode_index, season_number)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    episode_name = VALUES(episode_name),
                    season_number = VALUES(season_number),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                episode_data["serie_name"],
                episode_data["season_name"],
                episode_data["episode_name"],
                episode_data["episode_index"],
                episode_data.get("season_number", 0),
            ))
            
            # Get the episode ID
            cursor.execute("""
                SELECT id FROM episodes 
                WHERE serie_name = %s AND season_name = %s AND episode_index = %s
            """, (
                episode_data["serie_name"],
                episode_data["season_name"],
                episode_data["episode_index"],
            ))
            
            result = cursor.fetchone()
            episode_id = result[0] if result else None
            
            self._connection.commit()
            logger.info(f"Saved episode: {episode_data['episode_name']} (ID: {episode_id})")
            return episode_id
            
        except Exception as e:
            logger.error(f"Failed to save episode: {e}")
            self._connection.rollback()
            return None
        finally:
            cursor.close()
    
    def save_players(self, episode_id: int, language: str, players: list[str]):
        """Save player URLs for an episode.
        
        Args:
            episode_id: Episode ID
            language: Language code
            players: List of player URLs
        """
        if not self._connection or not episode_id:
            return False
            
        cursor = self._connection.cursor()
        try:
            # Delete existing players for this episode and language
            cursor.execute("""
                DELETE FROM players WHERE episode_id = %s AND language = %s
            """, (episode_id, language))
            
            # Insert new players
            from urllib.parse import urlparse
            for order, player_url in enumerate(players):
                hostname = urlparse(player_url).hostname or ""
                cursor.execute("""
                    INSERT INTO players 
                    (episode_id, language, player_url, player_hostname, player_order)
                    VALUES (%s, %s, %s, %s, %s)
                """, (episode_id, language, player_url, hostname, order))
            
            self._connection.commit()
            logger.info(f"Saved {len(players)} players for episode {episode_id} ({language})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save players: {e}")
            self._connection.rollback()
            return False
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            logger.info("Database connection closed")


def index_episode(episode, db: Optional[Database] = None) -> bool:
    """Index an episode and its players in the database.
    
    Args:
        episode: Episode object to index
        db: Database instance. If None, creates a new one.
        
    Returns:
        True if successful, False otherwise
    """
    should_close = False
    if db is None:
        db = Database()
        if not db.connect():
            return False
        if not db.initialize_schema():
            db.close()
            return False
        should_close = True
    
    try:
        # Prepare episode data
        episode_data = {
            "serie_name": episode.serie_name,
            "season_name": episode.season_name,
            "episode_name": episode.name,
            "episode_index": episode.index,
            "season_number": episode.season_number,
        }
        
        # Save episode
        episode_id = db.save_episode(episode_data)
        if not episode_id:
            return False
        
        # Save players for each language
        for lang_id, players in episode.languages.items():
            if players:
                db.save_players(episode_id, lang_id, list(players))
        
        logger.info(f"Successfully indexed episode: {episode.name}")
        return True
        
    finally:
        if should_close:
            db.close()
