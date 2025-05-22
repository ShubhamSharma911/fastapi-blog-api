import pytest
from starlette import status
from jose import jwt
from app import schemas
from tests.database import  client, session
from app.config import settings
from fastapi import status


def test_create_user(client):
    response = client.post("/users/", json={"email": "123@gmail.com", "password": "Hello123"})
    new_user = schemas.CreateUserResponse(**response.json())
    assert new_user.email == "123@gmail.com"
    assert response.status_code == status.HTTP_201_CREATED


def test_login_user(client, test_user):
    response = client.post("/login", data = {"username": test_user['email'], "password": test_user['password']})
    response_data = response.json()
    payload = jwt.decode(response_data["access_token"], settings.secret_key, algorithms=[settings.algorithm])
    payload_id = payload.get("user_id")
    assert payload_id == test_user['id']
    assert response_data["token_type"] == "Bearer"
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.parametrize("email, password, status_code", [
    ("wrongemail@gmail.com", 'Hello123', 403),
    ("123@gmail.com", 'wrongpassword', 403),
    ("wrongemail@gmail.com", 'wrongpassword', 403),
    (None, 'Hello123', 422),
    ("123@gmail.com", None , 422),
])
def test_incorrect_login(test_user, client, email, password, status_code):
    login_data = {}
    if email is not None:
        login_data["username"] = email
    if password is not None:
        login_data["password"] = password

    response = client.post("/login", data=login_data)
    assert response.status_code == status_code