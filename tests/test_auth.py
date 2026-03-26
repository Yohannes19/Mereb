import pytest
from fastapi import status

def test_register_successful(client):
    response = client.post(
        "/auth/register",
        data={
            "display_name": "Test User",
            "email": "test@example.com",
            "password": "securepassword",
            "profile_type": "creator",
            "city": "Addis Ababa",
            "niche": "Software"
        },
        follow_redirects=False
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/dashboard"

def test_register_existing_email(client):
    # Register first
    client.post(
        "/auth/register",
        data={
            "display_name": "User 1",
            "email": "duplicate@example.com",
            "password": "password",
            "profile_type": "creator",
            "city": "Addis Ababa",
            "niche": "Software"
        }
    )
    # Try again with same email
    response = client.post(
        "/auth/register",
        data={
            "display_name": "User 2",
            "email": "duplicate@example.com",
            "password": "password",
            "profile_type": "creator",
            "city": "Addis Ababa",
            "niche": "Software"
        },
        follow_redirects=False
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert "/auth/register?exists=1" in response.headers["location"]

def test_login_successful(client):
    # Register first
    client.post(
        "/auth/register",
        data={
            "display_name": "Login User",
            "email": "login@example.com",
            "password": "correctpassword",
            "profile_type": "creator",
            "city": "Addis Ababa",
            "niche": "Software"
        }
    )
    # Login
    response = client.post(
        "/auth/login",
        data={
            "email": "login@example.com",
            "password": "correctpassword"
        },
        follow_redirects=False
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/dashboard"

def test_login_failed(client):
    response = client.post(
        "/auth/login",
        data={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        },
        follow_redirects=False
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert "/auth/login?error=1" in response.headers["location"]

def test_logout(client):
    response = client.post("/auth/logout", follow_redirects=False)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/auth/login"
