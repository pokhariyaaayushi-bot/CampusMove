"""
Authentication Domain and API Tests
"""

import pytest
from backend.app.models.user import UserModel


def test_user_registration_and_login(client):
    """Verifies user registration and subsequent successful authentication."""
    reg_payload = {
        "name": "Test Student",
        "email": "test.student@geu.ac.in",
        "password": "SecretPassword123!",
        "role": "student",
        "department": "CSE"
    }

    # Register
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201
    user_data = res.get_json()["data"]
    assert user_data["email"] == "test.student@geu.ac.in"
    assert "password_hash" not in user_data

    # Login with correct password
    login_payload = {
        "email": "test.student@geu.ac.in",
        "password": "SecretPassword123!"
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    assert login_res.get_json()["message"] == "Login successful"
    assert login_res.get_json()["data"]["name"] == "Test Student"


def test_user_invalid_login(client):
    """Verifies that wrong passwords or non-existent accounts return 401."""
    # Register user
    client.post("/api/auth/register", json={
        "name": "Auth User",
        "email": "auth.user@geu.ac.in",
        "password": "ValidPassword123!"
    })

    # Wrong password
    bad_res = client.post("/api/auth/login", json={
        "email": "auth.user@geu.ac.in",
        "password": "WrongPassword!"
    })
    assert bad_res.status_code == 401
    assert bad_res.get_json()["error"]["code"] == "INVALID_CREDENTIALS"

    # Non-existent user
    not_found_res = client.post("/api/auth/login", json={
        "email": "nonexistent@geu.ac.in",
        "password": "SomePassword"
    })
    assert not_found_res.status_code == 401


def test_user_unique_email_constraint(client):
    """Verifies that duplicate registration with same email triggers 409 conflict."""
    payload = {
        "name": "Duplicate User",
        "email": "dup@geu.ac.in",
        "password": "Password123!"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 409
    assert res2.get_json()["error"]["code"] == "DUPLICATE_RESOURCE"


def test_user_validation_rules(client):
    """Verifies password length and role validation."""
    # Short password (< 6 chars)
    res = client.post("/api/auth/register", json={
        "name": "Short Pwd",
        "email": "short@geu.ac.in",
        "password": "123"
    })
    assert res.status_code == 400
    assert "at least 6 characters" in res.get_json()["error"]["message"]

    # Invalid role
    res2 = client.post("/api/auth/register", json={
        "name": "Bad Role",
        "email": "badrole@geu.ac.in",
        "password": "ValidPassword123!",
        "role": "superman"
    })
    assert res2.status_code == 400
    assert "Invalid user role" in res2.get_json()["error"]["message"]

