import pytest
from datetime import datetime, timedelta

def test_create_session(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a film first (assuming there's an endpoint for this)
    film_data = {
        "title": "Test Film",
        "description": "A test film",
        "duration": 120,
        "status": "available"
    }
    film_response = client.post("/api/v1/films/", json=film_data, headers=headers)
    assert film_response.status_code == 201, film_response.text
    film_id = film_response.json()["id"]

    # Create a session
    session_data = {
        "film_id": film_id,
        "datetime": (datetime.now() + timedelta(days=1)).isoformat(),
        "price": 10.0,
        "capacity": 50,
        "auto_booking": True
    }
    response = client.post("/api/v1/sessions/", json=session_data, headers=headers)
    assert response.status_code == 201, response.text
    assert "id" in response.json()

def test_delete_session(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a film first (assuming there's an endpoint for this)
    film_data = {
        "title": "Test Film",
        "description": "A test film",
        "duration": 120,
        "status": "available"
    }
    film_response = client.post("/api/v1/films/", json=film_data, headers=headers)
    assert film_response.status_code == 201, film_response.text
    film_id = film_response.json()["id"]

    # Create a session
    session_data = {
        "film_id": film_id,
        "datetime": (datetime.now() + timedelta(days=1)).isoformat(),
        "price": 10.0,
        "capacity": 50,
        "auto_booking": True
    }
    session_response = client.post("/api/v1/sessions/", json=session_data, headers=headers)
    assert session_response.status_code == 201, session_response.text
    session_id = session_response.json()["id"]

    # Delete the session
    delete_response = client.delete(f"/api/v1/sessions/{session_id}/delete", headers=headers)
    assert delete_response.status_code == 200, delete_response.text
    assert "id" in delete_response.json()

def test_delete_nonexistent_session(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Attempt to delete a non-existent session
    delete_response = client.delete(f"/api/v1/sessions/9999/delete", headers=headers)
    assert delete_response.status_code == 404, delete_response.text
    assert delete_response.json()["detail"] == "Session not found"

def test_set_session_status(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a film first (assuming there's an endpoint for this)
    film_data = {
        "title": "Test Film",
        "description": "A test film",
        "duration": 120,
        "status": "available"
    }
    film_response = client.post("/api/v1/films/", json=film_data, headers=headers)
    assert film_response.status_code == 201, film_response.text
    film_id = film_response.json()["id"]

    # Create a session
    session_data = {
        "film_id": film_id,
        "datetime": (datetime.now() + timedelta(days=1)).isoformat(),
        "price": 10.0,
        "capacity": 50,
        "auto_booking": True
    }
    session_response = client.post("/api/v1/sessions/", json=session_data, headers=headers)
    assert session_response.status_code == 201, session_response.text
    session_id = session_response.json()["id"]

    # Set session status
    new_status = "now_playing"  # Using a valid SessionStatus
    status_response = client.post(f"/api/v1/sessions/{session_id}/status/{new_status}", headers=headers)
    assert status_response.status_code == 200, status_response.text
    assert status_response.json()["status"] == new_status

def test_set_session_price(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a film first (assuming there's an endpoint for this)
    film_data = {
        "title": "Test Film",
        "description": "A test film",
        "duration": 120,
        "status": "available"
    }
    film_response = client.post("/api/v1/films/", json=film_data, headers=headers)
    assert film_response.status_code == 201, film_response.text
    film_id = film_response.json()["id"]

    # Create a session
    session_data = {
        "film_id": film_id,
        "datetime": (datetime.now() + timedelta(days=1)).isoformat(),
        "price": 10.0,
        "capacity": 50,
        "auto_booking": True
    }
    session_response = client.post("/api/v1/sessions/", json=session_data, headers=headers)
    assert session_response.status_code == 201, session_response.text
    session_id = session_response.json()["id"]

    # Set session price
    new_price = 15.0
    price_response = client.post(f"/api/v1/sessions/{session_id}/price/{new_price}", headers=headers)
    assert price_response.status_code == 200, price_response.text
    assert price_response.json()["price"] == new_price
