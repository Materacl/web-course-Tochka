import pytest

def test_register_user(client):
    response = client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "password"})
    assert response.status_code == 201, response.text
    assert "id" in response.json()

def test_register_user_with_existing_email(client):
    client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "password"})
    response = client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "password"})
    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Email already registered"

def test_login_user(client):
    client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "password"})
    response = client.post("/api/v1/auth/token", data={"username": "user@example.com", "password": "password"})
    assert response.status_code == 200, response.text
    assert "access_token" in response.json()

def test_login_user_with_wrong_password(client):
    client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "password"})
    response = client.post("/api/v1/auth/token", data={"username": "user@example.com", "password": "wrongpassword"})
    assert response.status_code == 400, response.text 
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_user_with_unregistered_email(client):
    response = client.post("/api/v1/auth/token", data={"username": "nonexistent@example.com", "password": "password"})
    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Incorrect email or password"
