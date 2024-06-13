from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

class Settings(BaseSettings):
    """
    Configuration settings for the FastAPI application.

    Attributes:
        SECRET_KEY (str): Secret key for cryptographic operations.
        ALGORITHM (str): Algorithm used for cryptographic operations.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Expiry time for access tokens in minutes.
        DATABASE_URL (str): URL of the database.
        CORS_ORIGINS (str): Comma-separated list of allowed CORS origins.
        RABBITMQ_URL (str): URL for the message queue.
        MAIL_USERNAME (str): Username for the mail server.
        MAIL_PASSWORD (str): Password for the mail server.
        MAIL_FROM (str): Email address from which emails are sent.
        MAIL_PORT (int): Port number for the mail server.
        MAIL_SERVER (str): Mail server address.
        MAIL_STARTTLS (bool): Whether to use STARTTLS for the mail server.
        MAIL_SSL_TLS (bool): Whether to use SSL/TLS for the mail server.
        USE_CREDENTIALS (bool): Whether to use credentials for the mail server.
        MAIN_ADMIN (str): Main administrator's email.
    """
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL")
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_FROM")
    MAIL_PORT: int = os.getenv("MAIL_PORT")
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS") == 'true'
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS") == 'true'
    USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS") == 'true'
    MAIN_ADMIN: str = os.getenv("MAIN_ADMIN")

# Create an instance of the Settings class
settings = Settings()
