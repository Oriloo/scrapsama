#!/usr/bin/env python3
"""Initialize database schema for scrapsama indexing."""
import sys
from scraper.database import Database

def main():
    """Initialize the database schema."""
    print("Initializing database schema...")
    
    db = Database()
    if not db.connect():
        print("❌ Failed to connect to database")
        return 1
    
    if not db.initialize_schema():
        print("❌ Failed to initialize schema")
        db.close()
        return 1
    
    print("✅ Database schema initialized successfully")
    db.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
