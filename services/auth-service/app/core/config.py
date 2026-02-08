from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ======================
    # App
    # ======================
    app_name: str
    app_env: str = "development"
    app_port: int

    # ======================
    # Database (raw parts)
    # ======================
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # ======================
    # Auth / JWT
    # ======================
    jwt_secret_key: str
    jwt_expire_minutes: int = 60
    jwt_refresh_expire_days: int = 7

    # ======================
    # Derived / Computed
    # ======================
    @property
    def DATABASE_URL(self) -> str:
        # Use a property to avoid Pydantic version quirks with post-init fields.
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"
        extra = "forbid"


# ✅ SINGLE SOURCE OF TRUTH
settings = Settings()

# Backwards-compatible module constants
JWT_SECRET = settings.jwt_secret_key
