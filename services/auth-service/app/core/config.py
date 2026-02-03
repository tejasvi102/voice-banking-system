from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str
    app_env: str
    app_port: int

    # Database (raw parts)
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # Auth / JWT
    jwt_secret_key: str
    jwt_expire_minutes: int
    jwt_refresh_expire_days: int

    # Derived / computed (MUST be Optional)
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: Optional[str] = None

    def model_post_init(self, __context):
        object.__setattr__(
            self,
            "DATABASE_URL",
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}",
        )
        object.__setattr__(self, "SECRET_KEY", self.jwt_secret_key)

    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()
