import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import io

def test_create_film(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    film_data = {
        "title": "Test Film",
        "description": "A test film",
        "duration": 120,
        "status": "available"
    }
    
    response = client.post("/api/v1/films/", json=film_data, headers=headers)
    assert response.status_code == 201, response.text
    assert "id" in response.json()

def test_upload_film_image(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create a film first
    film_data = {
        "title": "Test Film",
        "description": "A test film",
        "duration": 120,
        "status": "available"
    }
    film_response = client.post("/api/v1/films/", json=film_data, headers=headers)
    assert film_response.status_code == 201, film_response.text
    film_id = film_response.json()["id"]

    # Create a mock image file
    image_content = io.BytesIO(b"fake image data")
    files = {"file": ("test_image.jpg", image_content, "image/jpeg")}
    
    # Upload the image for the film
    upload_response = client.post(f"/api/v1/films/{film_id}/upload_image", headers=headers, files=files)
    
    assert upload_response.status_code == 200, upload_response.text
    assert "image_url" in upload_response.json()

def test_upload_film_image_not_found(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a mock image file
    image_content = io.BytesIO(b"fake image data")
    files = {"file": ("test_image.jpg", image_content, "image/jpeg")}
    
    # Attempt to upload an image for a non-existent film
    upload_response = client.post(f"/api/v1/films/9999/upload_image", headers=headers, files=files)
    
    assert upload_response.status_code == 404, upload_response.text
    assert upload_response.json()["detail"] == "Film not found"

def test_delete_film(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create a film first
    film_data = {
        "title": "Test Film",
        "description": "A test film",
        "duration": 120,
        "status": "available"
    }
    film_response = client.post("/api/v1/films/", json=film_data, headers=headers)
    assert film_response.status_code == 201, film_response.text
    film_id = film_response.json()["id"]

    # Delete the film
    delete_response = client.delete(f"/api/v1/films/{film_id}/delete", headers=headers)
    assert delete_response.status_code == 200, delete_response.text
    assert "id" in delete_response.json()

def test_delete_film_not_found(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Attempt to delete a non-existent film
    delete_response = client.delete(f"/api/v1/films/9999/delete", headers=headers)
    assert delete_response.status_code == 404, delete_response.text
    assert delete_response.json()["detail"] == "Film not found"
