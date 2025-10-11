#!/usr/bin/env python3
"""Database setup script for anime-sama-api.

This script initializes the database schema for storing video links and episode information.
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the path to import anime_sama_api
sys.path.insert(0, str(Path(__file__).parent.parent))

from anime_sama_api.database import Database, DatabaseConfig


def main():
    """Initialize the database schema."""
    print("=== Anime-Sama Database Setup ===\n")
    
    # Load configuration from environment or use defaults
    config = DatabaseConfig.from_env()
    
    print(f"Database Configuration:")
    print(f"  Host: {config.host}")
    print(f"  Port: {config.port}")
    print(f"  Database: {config.database}")
    print(f"  User: {config.user}")
    print()
    
    # Create database instance
    db = Database(config)
    
    # Connect to database
    print("Connecting to database...")
    if not db.connect():
        print("❌ Failed to connect to database.")
        print("\nMake sure:")
        print("  1. MySQL is running")
        print("  2. Database credentials are correct")
        print("  3. mysql-connector-python is installed: pip install mysql-connector-python")
        return 1
    
    print("✓ Connected to database")
    
    # Initialize schema
    print("\nInitializing database schema...")
    if not db.initialize_schema():
        print("❌ Failed to initialize database schema.")
        db.close()
        return 1
    
    print("✓ Database schema initialized successfully")
    
    # Close connection
    db.close()
    
    print("\n=== Setup Complete ===")
    print("\nYou can now enable database indexing in your config:")
    print("  ~/.config/anime-sama_cli/config.toml")
    print("\nSet: index_to_database = true")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
