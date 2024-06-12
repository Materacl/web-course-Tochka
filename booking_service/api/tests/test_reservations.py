import pytest
from datetime import datetime, timedelta

def test_create_reservation(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Register a user to create a booking and reservation
    user_response = client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "password"})
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

    # Create a reservation
    reservation_data = {
        "booking_id": booking_id,
        "seat_id": 1
    }
    response = client.post("/api/v1/reservations/", json=reservation_data, headers=headers)
    assert response.status_code == 201, response.text
    assert "id" in response.json()

def test_delete_reservation(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Register a user to create a booking and reservation
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

    # Create a reservation
    reservation_data = {
        "booking_id": booking_id,
        "seat_id": 1
    }
    reservation_response = client.post("/api/v1/reservations/", json=reservation_data, headers=headers)
    assert reservation_response.status_code == 201, reservation_response.text
    reservation_id = reservation_response.json()["id"]

    # Delete the reservation
    delete_response = client.delete(f"/api/v1/reservations/{reservation_id}/delete", headers=headers)
    assert delete_response.status_code == 200, delete_response.text
    assert "id" in delete_response.json()

def test_delete_nonexistent_reservation(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Attempt to delete a non-existent reservation
    delete_response = client.delete(f"/api/v1/reservations/9999/delete", headers=headers)
    assert delete_response.status_code == 404, delete_response.text
    assert delete_response.json()["detail"] == "Reservation not found"

def test_set_reservation_status(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Register a user to create a booking and reservation
    user_response = client.post("/api/v1/auth/register", json={"email": "user3@example.com", "password": "password"})
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

    # Create a reservation
    reservation_data = {
        "booking_id": booking_id,
        "seat_id": 1
    }
    reservation_response = client.post("/api/v1/reservations/", json=reservation_data, headers=headers)
    assert reservation_response.status_code == 201, reservation_response.text
    reservation_id = reservation_response.json()["id"]

    # Set reservation status
    new_status = "confirmed"  # Assuming 'confirmed' is a valid ReservationStatus
    status_response = client.post(f"/api/v1/reservations/{reservation_id}/status/{new_status}", headers=headers)
    assert status_response.status_code == 200, status_response.text
    assert status_response.json()["status"] == new_status

def test_cancel_reservation(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Register a user to create a booking and reservation
    user_response = client.post("/api/v1/auth/register", json={"email": "user4@example.com", "password": "password"})
    assert user_response.status_code == 201, user_response.text
    user_id = user_response.json()["id"]

    # Log in the user to get the user token
    login_response = client.post("/api/v1/auth/token", data={"username": "user4@example.com", "password": "password"})
    assert login_response.status_code == 200, login_response.text
    user_token = login_response.json()["access_token"]

    user_headers = {"Authorization": f"Bearer {user_token}"}

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

    # Create a booking with the logged-in user token
    booking_data = {
        "session_id": session_id,
        "booking_date": datetime.now().isoformat(),
        "status": "pending"
    }
    booking_response = client.post("/api/v1/bookings/", json=booking_data, headers=user_headers)
    assert booking_response.status_code == 201, booking_response.text
    booking_id = booking_response.json()["id"]

    # Create a reservation
    reservation_data = {
        "booking_id": booking_id,
        "seat_id": 1
    }
    reservation_response = client.post("/api/v1/reservations/", json=reservation_data, headers=user_headers)
    assert reservation_response.status_code == 201, reservation_response.text
    reservation_id = reservation_response.json()["id"]

    # Cancel the reservation
    cancel_response = client.delete(f"/api/v1/reservations/{reservation_id}/cancel", headers=user_headers)
    assert cancel_response.status_code == 200, cancel_response.text
    assert cancel_response.json()["status"] == "canceled"
