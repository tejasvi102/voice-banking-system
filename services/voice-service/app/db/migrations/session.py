import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _build_database_url() -> str:
    """Build a PostgreSQL connection URL from env vars."""
    db_user = os.getenv("DB_USER", "voice_user")
    db_password = os.getenv("DB_PASSWORD", "voice_password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "voice_db")
    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


DATABASE_URL = os.getenv("DATABASE_URL", _build_database_url())

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
