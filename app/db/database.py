# app/db/database.py
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import DATABASE_URL, BASE_DIR
from app.db.models import Base

logger = logging.getLogger(__name__)

# Ensure the data directory exists before creating the database
data_dir = BASE_DIR / "data"
data_dir.mkdir(exist_ok=True)

# Create engine
# check_same_thread=False is required for SQLite when used with FastAPI
# because FastAPI handles requests in multiple threads
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # set to True to see SQL queries in logs during debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Create all tables if they do not exist.
    Safe to call on every startup — SQLAlchemy skips existing tables.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified")


def get_db() -> Session:
    """
    Dependency that provides a database session.
    Automatically closes the session when done.
    Used as a FastAPI dependency in routes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()