import os
import logging
from sqlalchemy import inspect, text
from sqlalchemy.exc import ProgrammingError
from app.db.migrations.session import engine


def ensure_user_columns() -> None:
    if os.getenv("DB_BOOTSTRAP", "true").lower() not in {"1", "true", "yes"}:
        return

    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("users")}

    statements = []
    if "password_hash" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR"
        )
    if "is_active" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE"
        )
    if "full_name" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR"
        )
    if "phone" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR"
        )
    if "refresh_token_hash" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS refresh_token_hash VARCHAR"
        )
    if "refresh_token_expires_at" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS refresh_token_expires_at TIMESTAMP WITH TIME ZONE"
        )
    if "created_at" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()"
        )
    if "updated_at" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE"
        )

    if not statements:
        return

    try:
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))
    except ProgrammingError as exc:
        # If the DB user lacks ALTER privileges, don't crash the app.
        logging.warning("Skipping DB bootstrap due to insufficient privileges: %s", exc)
        return
