import pytest

def test_create_reservation(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a film and a session first
    film_response = client.post("/api/v1/films/", json={"title": "Test Film", "description": "Description", "duration": 120, "status": "available"}, headers=headers)
    film_id = film_response.json()["id"]

    session_response = client.post("/api/v1/sessions/", json={"film_id": film_id, "datetime": "2024-06-10T10:00:00", "price": 10.0, "capacity": 100, "auto_booking": True}, headers=headers)
    session_id = session_response.json()["id"]

    # Create a booking
    booking_response = client.post("/api/v1/bookings/", json={"session_id": session_id}, headers=headers)
    booking_id = booking_response.json()["id"]

    # Create a reservation
    response = client.post("/api/v1/reservations/", json={"booking_id": booking_id, "seat_id": 1}, headers=headers)
    assert response.status_code == 201, response.text
    assert response.json()["booking_id"] == booking_id

    # Negative test case: Create reservation with invalid seat_id
    response = client.post("/api/v1/reservations/", json={"booking_id": booking_id, "seat_id": 9999}, headers=headers)
    assert response.status_code == 404, response.text
