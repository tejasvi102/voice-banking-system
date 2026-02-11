from sqlalchemy import inspect, text
from app.db.migrations.session import engine


def ensure_refresh_token_columns() -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("users")}

    statements = []
    if "refresh_token_hash" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS refresh_token_hash VARCHAR"
        )
    if "refresh_token_expires_at" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS refresh_token_expires_at TIMESTAMP WITH TIME ZONE"
        )

    if not statements:
        return

    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
