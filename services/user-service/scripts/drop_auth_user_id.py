from sqlalchemy import text
from app.db.migrations.session import engine


def main():
    # Drop deprecated column if it still exists.
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS auth_user_id;"))
        conn.commit()
    print("Dropped users.auth_user_id (if it existed).")


if __name__ == "__main__":
    main()
