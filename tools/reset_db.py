#!/usr/bin/env python
"""
Database Reset Tool for Debtonator

This script:
1. Deletes the existing SQLite database file
2. Runs the database initialization to recreate all tables
"""
import os
import sys
from pathlib import Path

# Add project root to Python path to allow imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.database.init_db import init_database


def reset_database():
    """Reset the database by deleting it and reinitializing"""
    db_path = project_root / "debtonator.db"

    # Delete existing database if it exists
    if db_path.exists():
        print(f"Deleting existing database at {db_path}")
        os.remove(db_path)
    else:
        print(f"No existing database found at {db_path}")

    # Reinitialize the database
    print("Initializing fresh database...")
    init_database()
    print("Database initialization complete!")


if __name__ == "__main__":
    reset_database()
