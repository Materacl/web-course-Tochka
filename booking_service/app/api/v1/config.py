from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv("api/.env")


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_FROM")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS") == 'true'
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS") == 'true'
    USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS") == 'true'


settings = Settings()
