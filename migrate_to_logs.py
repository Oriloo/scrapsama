#!/usr/bin/env python3
"""Migration script to convert from failures table to logs table.

This script should be run on existing installations to migrate from the old
failures table to the new logs table structure.
"""
import sys
from scraper.database import Database

def main():
    """Migrate from failures table to logs table."""
    print("Starting migration from failures table to logs table...")
    
    db = Database()
    if not db.connect():
        print("❌ Failed to connect to database")
        return 1
    
    cursor = db._connection.cursor()
    
    try:
        # Check if failures table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'failures'
        """)
        failures_exists = cursor.fetchone()[0] > 0
        
        # Check if logs table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'logs'
        """)
        logs_exists = cursor.fetchone()[0] > 0
        
        if not failures_exists and logs_exists:
            print("✅ Migration already completed - logs table exists and failures table is gone")
            return 0
        
        if not failures_exists:
            print("⚠️  Failures table doesn't exist - nothing to migrate")
            if not logs_exists:
                print("Creating logs table...")
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
                db._connection.commit()
                print("✅ Logs table created")
            return 0
        
        # Create logs table if it doesn't exist
        if not logs_exists:
            print("Creating logs table...")
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
            db._connection.commit()
            print("✅ Logs table created")
        
        # Count failures for summary
        cursor.execute("SELECT COUNT(*) FROM failures")
        failure_count = cursor.fetchone()[0]
        
        if failure_count > 0:
            print(f"Found {failure_count} entries in failures table")
            print("Note: These entries cannot be directly converted to logs format")
            print("      The failures table will be dropped, and new logging will start fresh")
        
        # Drop the failures table
        print("Dropping failures table...")
        cursor.execute("DROP TABLE IF EXISTS failures")
        db._connection.commit()
        print("✅ Failures table dropped")
        
        print("\n✅ Migration completed successfully!")
        print("\nThe new logs table will track:")
        print("  - Command executed (index[series_name], index-all, index-new)")
        print("  - Number of new series, seasons, and episodes indexed")
        print("  - Number of errors encountered")
        print("  - Timestamp of each indexing operation")
        
        return 0
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db._connection.rollback()
        return 1
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    sys.exit(main())
