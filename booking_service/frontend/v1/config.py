from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    API_URL: str = os.getenv("API_URL")
    USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS") == 'true'
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS").split(",")


settings = Settings()
