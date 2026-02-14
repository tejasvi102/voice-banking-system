from app.db.migrations.session import Base, engine
from app.models import voice_profile  # noqa: F401 - ensure model metadata is imported


def main() -> None:
    print("Creating voice-service tables...")
    Base.metadata.create_all(bind=engine)
    print("voice-service tables created.")


if __name__ == "__main__":
    main()
