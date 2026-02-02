from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "auth-service"
    app_port: int = 8001

    class Config:
        env_file = ".env"


settings = Settings()
