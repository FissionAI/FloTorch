"""
PostgreSQL database connection and session management.
"""
import os
import logging
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages PostgreSQL database connections and sessions."""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection."""
        try:
            # Get database configuration
            db_host = os.getenv("POSTGRES_HOST", "localhost")
            db_port = os.getenv("POSTGRES_PORT", "5432")
            db_name = os.getenv("POSTGRES_DB", "flotorch")
            db_user = os.getenv("POSTGRES_USER", "flotorch")
            db_password = os.getenv("POSTGRES_PASSWORD", "flotorch")
            
            # Build connection URL
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
            # Create engine with connection pooling
            self.engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=int(os.getenv("POSTGRES_POOL_SIZE", "5")),
                max_overflow=int(os.getenv("POSTGRES_MAX_OVERFLOW", "10")),
                pool_pre_ping=True,
                pool_recycle=int(os.getenv("POSTGRES_POOL_RECYCLE", "3600")),
                echo=os.getenv("POSTGRES_ECHO", "false").lower() == "true"
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database connection initialized for {db_host}:{db_port}/{db_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session_dependency(self) -> Session:
        """Get database session for FastAPI dependency injection."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def create_tables(self):
        """Create all database tables."""
        try:
            from .models import Base
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables."""
        try:
            from .models import Base
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise

# Global database manager instance
db_manager = DatabaseManager()

# FastAPI dependency for database sessions
def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    with db_manager.get_session() as session:
        yield session

