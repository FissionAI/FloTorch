"""
Database initialization script for FloTorch PostgreSQL setup.
"""
import os
import logging
from app.database.connection import db_manager
from app.database.models import Base

logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with tables."""
    try:
        logger.info("Initializing database...")
        db_manager.create_tables()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def drop_database():
    """Drop all database tables (use with caution!)."""
    try:
        logger.warning("Dropping all database tables...")
        db_manager.drop_tables()
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_database()
    else:
        init_database()

