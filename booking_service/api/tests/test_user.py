import pytest

def test_change_nickname(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Register a user
    client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "password"})
    
    # Change nickname
    response = client.put("/api/v1/user/change_nickname/NewNickname", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["nickname"] == "NewNickname"

    # Negative test case: Change nickname for non-existent user
    response = client.put("/api/v1/user/change_nickname/NonExistentUser/NewNickname", headers=headers)
    assert response.status_code == 404, response.text
