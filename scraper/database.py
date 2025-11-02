"""Database module for storing video links and episode information."""
import logging
import os
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Configuration for database connection."""
    host: str = "localhost"
    port: int = 3306
    database: str = "scrapsama_db"
    user: str = "scrapsama_user"
    password: str = "scrapsama_password"

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load database configuration from environment variables.

        Raises:
            ValueError: If required environment variables are not set
        """
        host = os.getenv("DB_HOST")
        if not host:
            raise ValueError("DB_HOST environment variable is required but not set")

        port_str = os.getenv("DB_PORT")
        if not port_str:
            raise ValueError("DB_PORT environment variable is required but not set")

        database = os.getenv("DB_NAME")
        if not database:
            raise ValueError("DB_NAME environment variable is required but not set")

        user = os.getenv("DB_USER")
        if not user:
            raise ValueError("DB_USER environment variable is required but not set")

        password = os.getenv("DB_PASSWORD")
        if not password:
            raise ValueError("DB_PASSWORD environment variable is required but not set")

        return cls(
            host=host,
            port=int(port_str),
            database=database,
            user=user,
            password=password,
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
            # Create series table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS series (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    url TEXT NOT NULL,
                    alternative_names TEXT,
                    genres TEXT,
                    categories TEXT,
                    languages TEXT,
                    image_url TEXT,
                    advancement TEXT,
                    correspondence TEXT,
                    synopsis TEXT,
                    is_mature BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_serie (name)
                )
            """)
            
            # Create seasons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seasons (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    serie_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (serie_id) REFERENCES series(id) ON DELETE CASCADE,
                    INDEX idx_serie (serie_id),
                    UNIQUE KEY unique_season (serie_id, name)
                )
            """)
            
            # Create episodes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    season_id INT NOT NULL,
                    serie_name VARCHAR(255) NOT NULL,
                    season_name VARCHAR(255) NOT NULL,
                    episode_name VARCHAR(255) NOT NULL,
                    episode_index INT NOT NULL,
                    season_number INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE,
                    INDEX idx_season (season_id),
                    INDEX idx_serie (serie_name),
                    INDEX idx_episode (episode_name),
                    UNIQUE KEY unique_episode (season_id, episode_index)
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
            
            # Create logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    command VARCHAR(255) NOT NULL,
                    new_series INT DEFAULT 0,
                    new_seasons INT DEFAULT 0,
                    new_episodes INT DEFAULT 0,
                    error_count INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_command (command),
                    INDEX idx_created_at (created_at)
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
    
    def save_serie(self, serie_data: dict) -> tuple[Optional[int], bool]:
        """Save series information to database.
        
        Args:
            serie_data: Dictionary containing series information
            
        Returns:
            Tuple of (Series ID if successful, True if newly created) or (None, False) on error
        """
        if not self._connection:
            return None, False
            
        cursor = self._connection.cursor()
        try:
            # Convert lists/sets to JSON strings for storage
            import json
            alternative_names = json.dumps(serie_data.get("alternative_names", []))
            genres = json.dumps(serie_data.get("genres", []))
            categories = json.dumps(list(serie_data.get("categories", [])))
            languages = json.dumps(list(serie_data.get("languages", [])))
            
            # Check if series already exists
            cursor.execute("""
                SELECT id FROM series WHERE name = %s
            """, (serie_data["name"],))
            existing = cursor.fetchone()
            is_new = existing is None
            
            # Insert or update series
            cursor.execute("""
                INSERT INTO series 
                (name, url, alternative_names, genres, categories, languages, image_url, 
                 advancement, correspondence, synopsis, is_mature)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    url = VALUES(url),
                    alternative_names = VALUES(alternative_names),
                    genres = VALUES(genres),
                    categories = VALUES(categories),
                    languages = VALUES(languages),
                    image_url = VALUES(image_url),
                    advancement = VALUES(advancement),
                    correspondence = VALUES(correspondence),
                    synopsis = VALUES(synopsis),
                    is_mature = VALUES(is_mature),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                serie_data["name"],
                serie_data["url"],
                alternative_names,
                genres,
                categories,
                languages,
                serie_data.get("image_url", ""),
                serie_data.get("advancement", ""),
                serie_data.get("correspondence", ""),
                serie_data.get("synopsis", ""),
                serie_data.get("is_mature", False),
            ))
            
            # Get the series ID
            cursor.execute("""
                SELECT id FROM series WHERE name = %s
            """, (serie_data["name"],))
            
            result = cursor.fetchone()
            serie_id = result[0] if result else None
            
            self._connection.commit()
            logger.info(f"{'Created' if is_new else 'Updated'} series: {serie_data['name']} (ID: {serie_id})")
            return serie_id, is_new
            
        except Exception as e:
            logger.error(f"Failed to save series: {e}")
            self._connection.rollback()
            return None, False
        finally:
            cursor.close()
    
    def save_season(self, season_data: dict) -> tuple[Optional[int], bool]:
        """Save season information to database.
        
        Args:
            season_data: Dictionary containing season information
            
        Returns:
            Tuple of (Season ID if successful, True if newly created) or (None, False) on error
        """
        if not self._connection:
            return None, False
            
        cursor = self._connection.cursor()
        try:
            # Check if season already exists
            cursor.execute("""
                SELECT id FROM seasons 
                WHERE serie_id = %s AND name = %s
            """, (
                season_data["serie_id"],
                season_data["name"],
            ))
            existing = cursor.fetchone()
            is_new = existing is None
            
            # Insert or update season
            cursor.execute("""
                INSERT INTO seasons 
                (serie_id, name, url)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    url = VALUES(url),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                season_data["serie_id"],
                season_data["name"],
                season_data["url"],
            ))
            
            # Get the season ID
            cursor.execute("""
                SELECT id FROM seasons 
                WHERE serie_id = %s AND name = %s
            """, (
                season_data["serie_id"],
                season_data["name"],
            ))
            
            result = cursor.fetchone()
            season_id = result[0] if result else None
            
            self._connection.commit()
            logger.info(f"{'Created' if is_new else 'Updated'} season: {season_data['name']} (ID: {season_id})")
            return season_id, is_new
            
        except Exception as e:
            logger.error(f"Failed to save season: {e}")
            self._connection.rollback()
            return None, False
        finally:
            cursor.close()
    
    def save_episode(self, episode_data: dict) -> tuple[Optional[int], bool]:
        """Save episode information to database.
        
        Args:
            episode_data: Dictionary containing episode information
            
        Returns:
            Tuple of (Episode ID if successful, True if newly created) or (None, False) on error
        """
        if not self._connection:
            return None, False
            
        cursor = self._connection.cursor()
        try:
            # Check if episode already exists
            cursor.execute("""
                SELECT id FROM episodes 
                WHERE season_id = %s AND episode_index = %s
            """, (
                episode_data["season_id"],
                episode_data["episode_index"],
            ))
            existing = cursor.fetchone()
            is_new = existing is None
            
            # Insert or update episode
            cursor.execute("""
                INSERT INTO episodes 
                (season_id, serie_name, season_name, episode_name, episode_index, season_number)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    episode_name = VALUES(episode_name),
                    season_number = VALUES(season_number),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                episode_data["season_id"],
                episode_data["serie_name"],
                episode_data["season_name"],
                episode_data["episode_name"],
                episode_data["episode_index"],
                episode_data.get("season_number", 0),
            ))
            
            # Get the episode ID
            cursor.execute("""
                SELECT id FROM episodes 
                WHERE season_id = %s AND episode_index = %s
            """, (
                episode_data["season_id"],
                episode_data["episode_index"],
            ))
            
            result = cursor.fetchone()
            episode_id = result[0] if result else None
            
            self._connection.commit()
            logger.info(f"{'Created' if is_new else 'Updated'} episode: {episode_data['episode_name']} (ID: {episode_id})")
            return episode_id, is_new
            
        except Exception as e:
            logger.error(f"Failed to save episode: {e}")
            self._connection.rollback()
            return None, False
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
    
    def log_indexing(self, command: str, new_series: int = 0, new_seasons: int = 0, 
                     new_episodes: int = 0, error_count: int = 0) -> bool:
        """Log an indexing operation to the database.
        
        Args:
            command: Command executed (e.g., "index[series_name]", "index-all", "index-new")
            new_series: Number of new series indexed
            new_seasons: Number of new seasons indexed
            new_episodes: Number of new episodes indexed
            error_count: Number of errors encountered during indexing
            
        Returns:
            True if logged successfully, False otherwise
        """
        if not self._connection:
            return False
            
        cursor = self._connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO logs 
                (command, new_series, new_seasons, new_episodes, error_count)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                command,
                new_series,
                new_seasons,
                new_episodes,
                error_count,
            ))
            
            self._connection.commit()
            logger.info(f"Logged indexing operation: {command} - Series: {new_series}, Seasons: {new_seasons}, Episodes: {new_episodes}, Errors: {error_count}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log indexing operation: {e}")
            self._connection.rollback()
            return False
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            logger.info("Database connection closed")


def index_serie(catalogue, db: Optional[Database] = None) -> tuple[Optional[int], bool]:
    """Index a series (catalogue) in the database.
    
    Args:
        catalogue: Catalogue object to index
        db: Database instance. If None, creates a new one.
        
    Returns:
        Tuple of (Series ID if successful, True if newly created) or (None, False) on error
    """
    should_close = False
    if db is None:
        db = Database()
        if not db.connect():
            return None, False
        if not db.initialize_schema():
            db.close()
            return None, False
        should_close = True
    
    try:
        # Prepare series data
        serie_data = {
            "name": catalogue.name,
            "url": catalogue.url,
            "alternative_names": list(catalogue.alternative_names) if catalogue.alternative_names else [],
            "genres": list(catalogue.genres) if catalogue.genres else [],
            "categories": catalogue.categories if catalogue.categories else set(),
            "languages": catalogue.languages if catalogue.languages else set(),
            "image_url": catalogue.image_url,
        }
        
        # Save series
        serie_id, is_new = db.save_serie(serie_data)
        if serie_id:
            logger.info(f"Successfully indexed series: {catalogue.name}")
        
        return serie_id, is_new
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to index series {catalogue.name}: {error_msg}")
        return None, False
    finally:
        if should_close:
            db.close()


def index_season(season, serie_id: int, db: Optional[Database] = None) -> tuple[Optional[int], bool]:
    """Index a season in the database.
    
    Args:
        season: Season object to index
        serie_id: ID of the parent series
        db: Database instance. If None, creates a new one.
        
    Returns:
        Tuple of (Season ID if successful, True if newly created) or (None, False) on error
    """
    should_close = False
    if db is None:
        db = Database()
        if not db.connect():
            return None, False
        if not db.initialize_schema():
            db.close()
            return None, False
        should_close = True
    
    try:
        # Prepare season data
        season_data = {
            "serie_id": serie_id,
            "name": season.name,
            "url": season.url,
        }
        
        # Save season
        season_id, is_new = db.save_season(season_data)
        if season_id:
            logger.info(f"Successfully indexed season: {season.name}")
        
        return season_id, is_new
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to index season {season.name}: {error_msg}")
        return None, False
    finally:
        if should_close:
            db.close()


def index_episode(episode, season_id: Optional[int] = None, db: Optional[Database] = None) -> tuple[bool, bool]:
    """Index an episode and its players in the database.
    
    Args:
        episode: Episode object to index
        season_id: ID of the parent season (optional, will be looked up if not provided)
        db: Database instance. If None, creates a new one.
        
    Returns:
        Tuple of (True if successful, True if newly created) or (False, False) on error
    """
    should_close = False
    if db is None:
        db = Database()
        if not db.connect():
            return False, False
        if not db.initialize_schema():
            db.close()
            return False, False
        should_close = True
    
    try:
        # If season_id not provided, try to look it up (for backward compatibility)
        if season_id is None:
            cursor = db._connection.cursor()
            try:
                cursor.execute("""
                    SELECT s.id FROM seasons s
                    JOIN series sr ON s.serie_id = sr.id
                    WHERE sr.name = %s AND s.name = %s
                    LIMIT 1
                """, (episode.serie_name, episode.season_name))
                result = cursor.fetchone()
                season_id = result[0] if result else None
            finally:
                cursor.close()
            
            # If still not found, log error and return
            if season_id is None:
                error_msg = f"Season not found in database: {episode.serie_name} - {episode.season_name}"
                logger.error(error_msg)
                return False, False
        
        # Prepare episode data
        episode_data = {
            "season_id": season_id,
            "serie_name": episode.serie_name,
            "season_name": episode.season_name,
            "episode_name": episode.name,
            "episode_index": episode.index,
            "season_number": episode.season_number,
        }
        
        # Save episode
        episode_id, is_new = db.save_episode(episode_data)
        if not episode_id:
            logger.error(f"Failed to save episode: {episode.serie_name} - {episode.season_name} - {episode.name}")
            return False, False
        
        # Save players for each language
        for lang_id, players in episode.languages.items():
            if players:
                try:
                    success = db.save_players(episode_id, lang_id, list(players))
                    if not success:
                        logger.error(f"Failed to save players for {episode.serie_name} - {episode.name} - {lang_id}")
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error saving players for {episode.name} ({lang_id}): {error_msg}")
        
        logger.info(f"Successfully indexed episode: {episode.name}")
        return True, is_new
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to index episode {episode.name}: {error_msg}")
        return False, False
    finally:
        if should_close:
            db.close()
