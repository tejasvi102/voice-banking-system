import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def _build_database_url() -> str:
    """Build a PostgreSQL connection URL from env vars."""
    db_user = os.getenv("DB_USER", "bank_user")
    db_password = os.getenv("DB_PASSWORD", "bank_password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "banking_db")
    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


DATABASE_URL = os.getenv("DATABASE_URL", _build_database_url())


def _ensure_database_exists(database_url: str) -> None:
    """Create the configured PostgreSQL database when it is missing."""
    url = make_url(database_url)

    if not url.drivername.startswith("postgresql") or not url.database:
        return

    admin_url = url.set(database="postgres")
    database_name = url.database

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                {"database_name": database_name},
            ).scalar()

            if not exists:
                quoted_name = admin_engine.dialect.identifier_preparer.quote(database_name)
                connection.execute(text(f"CREATE DATABASE {quoted_name}"))
    finally:
        admin_engine.dispose()


_ensure_database_exists(DATABASE_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
