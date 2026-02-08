from app.db.migrations.session import engine
from app.models.user import User

def main():
    print("🚀 Creating user-service tables...")
    User.metadata.create_all(bind=engine)
    print("✅ User tables created")

if __name__ == "__main__":
    main()
