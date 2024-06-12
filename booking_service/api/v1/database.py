from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Retrieve the database URL from the settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create a database engine
# SQLite specific argument `check_same_thread` is required to allow multiple threads to use the same connection
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for our classes definitions
Base = declarative_base()

def get_db():
    """
    Dependency that provides a SQLAlchemy session (database connection).
    It ensures that the database session is properly managed by closing it after the request is completed.

    Yields:
        db (Session): SQLAlchemy session object
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        