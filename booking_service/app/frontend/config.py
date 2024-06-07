from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv("frontend/.env")


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    API_URL: str = os.getenv("API_URL")
    USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS") == 'true'


settings = Settings()
