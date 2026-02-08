from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    app_name: str
    app_env: str
    app_port: int

    # Database
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    class Config:
        env_file = ".env"

settings = Settings()
