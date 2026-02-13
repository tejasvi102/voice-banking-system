from app.db.migrations.session import engine
from app.models.user import User

def main():
<<<<<<< Updated upstream:services/user-service/create_tables.py
    print("🚀 Creating user-service tables...")
    User.metadata.create_all(bind=engine)
    print("✅ User tables created")
=======
    print("🚀 Creating database tables...")
    User.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
>>>>>>> Stashed changes:services/auth-service/create_tables.py

if __name__ == "__main__":
    main()
