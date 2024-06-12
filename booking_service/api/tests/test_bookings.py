import pytest
from datetime import datetime, timedelta

def test_create_booking(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Register a user to create a booking
    user_response = client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "password"})
    assert user_response.status_code == 201, user_response.text
    user_id = user_response.json()["id"]

    # Create a film
    film_data = {
        "title": "Test Film",
        "description": "A test film",
        "duration": 120,
        "status": "available"  # Assuming 'available' is a valid FilmStatus
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

    # Create a booking
    booking_data = {
        "session_id": session_id,
        "booking_date": datetime.now().isoformat(),
        "status": "pending"
    }
    response = client.post("/api/v1/bookings/", json=booking_data, headers=headers)
    assert response.status_code == 201, response.text
    assert "id" in response.json()

def test_create_booking_without_auth(client):
    # Attempt to create a booking without authentication
    booking_data = {
        "session_id": 1,
        "booking_date": datetime.now().isoformat(),
        "status": "pending"
    }
    response = client.post("/api/v1/bookings/", json=booking_data)
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Not authenticated"

def test_delete_booking(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Register a user to create a booking
    user_response = client.post("/api/v1/auth/register", json={"email": "user2@example.com", "password": "password"})
    assert user_response.status_code == 201, user_response.text
    user_id = user_response.json()["id"]

    # Create a film
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

    # Create a booking
    booking_data = {
        "session_id": session_id,
        "booking_date": datetime.now().isoformat(),
        "status": "pending"
    }
    booking_response = client.post("/api/v1/bookings/", json=booking_data, headers=headers)
    assert booking_response.status_code == 201, booking_response.text
    booking_id = booking_response.json()["id"]

    # Delete the booking
    delete_response = client.delete(f"/api/v1/bookings/{booking_id}/delete", headers=headers)
    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["id"] == booking_id

def test_delete_nonexistent_booking(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Attempt to delete a non-existent booking
    response = client.delete("/api/v1/bookings/9999/delete", headers=headers)
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Booking not found"
