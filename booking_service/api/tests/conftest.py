import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app 
from v1.utils.auth import get_password_hash
from v1.database import Base, get_db
from v1.models import User

# Alembic configuration
alembic_cfg = Config("alembic.ini")

# Use a test database URL (e.g., SQLite in-memory database for testing)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def apply_migrations():
    # Apply migrations at the beginning and end of the testing session
    command.upgrade(alembic_cfg, "head")

@pytest.fixture(scope="function")
def db_session(apply_migrations):
    """
    Create a new database session for a test.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a new FastAPI TestClient for a test.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def admin_token(client, db_session):
    """
    Create an admin user directly in the database and return the token.
    """
    # Create a user
    password_hash = get_password_hash("password")
    admin_user = User(email="admin@example.com", hashed_password=password_hash, is_admin=True)
    db_session.add(admin_user)
    db_session.commit()

    # Login to get the token
    response = client.post("/api/v1/auth/token", data={"username": "admin@example.com", "password": "password"})
    assert response.status_code == 200, response.text
    token = response.json().get("access_token")
    
    return token
