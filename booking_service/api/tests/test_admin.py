import pytest

def test_set_user_admin(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Register a user
    user_response = client.post("/api/v1/auth/register", json={"email": "user2@example.com", "password": "password"})
    assert user_response.status_code == 201, user_response.text
    user_id = user_response.json()["id"]

    # Promote user to admin
    response = client.put(f"/api/v1/admin/users/{user_id}/set_admin", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["is_admin"] is True

def test_set_nonexistent_user_admin(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Attempt to promote a non-existent user to admin
    response = client.put("/api/v1/admin/users/9999/set_admin", headers=headers)
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "User not found"
