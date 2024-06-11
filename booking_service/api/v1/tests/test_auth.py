import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...main import app
from ..database import Base, get_db
from ..models import User as UserModel
from ..schemas import UserCreate
from ..utils.auth import get_password_hash

# Setup the test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


# Dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def setup_user():
    db = TestingSessionLocal()
    hashed_password = get_password_hash("testpassword")
    user = UserModel(email="testuser@example.com", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(UserModel).delete()
    db.commit()
    db.close()


@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/register", json={"email": "newuser@example.com", "password": "newpassword"})
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_register_existing_user(setup_user):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/register", json={"email": "testuser@example.com", "password": "newpassword"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_for_access_token(setup_user):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/token", data={"username": "testuser@example.com", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/token", data={"username": "invalid@example.com", "password": "wrongpassword"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"
