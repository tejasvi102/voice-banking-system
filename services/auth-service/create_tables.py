from app.db.migrations.session import engine
from app.models.user import User

def main():
    print("🚀 Creating database tables...")
    User.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")

if __name__ == "__main__":
    main()
