from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str
    app_env: str = "development"
    app_port: int

    # Database (raw parts)
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # Auth / JWT
    jwt_secret_key: str
    jwt_expire_minutes: int = 60
    jwt_refresh_expire_days: int = 7

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()

# Backwards-compatible module constant
JWT_SECRET = settings.jwt_secret_key
