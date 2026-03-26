import pytest
from fastapi import status

def login_user(client):
    client.post(
        "/auth/register",
        data={
            "display_name": "Dashboard User",
            "email": "dash@example.com",
            "password": "password",
            "profile_type": "creator",
            "city": "Addis Ababa",
            "niche": "Software"
        }
    )
    client.post(
        "/auth/login",
        data={"email": "dash@example.com", "password": "password"}
    )

def test_dashboard_access_unauthenticated(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert "/auth/login" in response.headers["location"]

def test_dashboard_access_authenticated(client):
    login_user(client)
    response = client.get("/dashboard")
    assert response.status_code == status.HTTP_200_OK
    assert "Dashboard" in response.text or "Mereb" in response.text

def test_update_profile(client):
    login_user(client)
    response = client.post(
        "/dashboard/profile",
        data={
            "display_name": "Updated Name",
            "profile_type": "business",
            "tagline": "New Tagline",
            "bio": "New Bio",
            "city": "Gondar",
            "country": "Ethiopia",
            "niche": "Tourism",
            "website_url": "https://example.com"
        },
        follow_redirects=False
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert "/dashboard?profile=1" in response.headers["location"]

def test_add_proof_item(client):
    login_user(client)
    response = client.post(
        "/dashboard/proof",
        data={
            "title": "New Project",
            "client_name": "ABC Corp",
            "category": "design",
            "summary": "Project summary",
            "result_metric": "100% success",
            "proof_url": "https://proof.com",
            "image_url": "https://image.com",
            "verification_note": "Verified"
        },
        follow_redirects=False
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert "/dashboard?proof=1" in response.headers["location"]

def test_add_rating(client):
    login_user(client)
    response = client.post(
        "/dashboard/ratings",
        data={
            "reviewer_name": "John Doe",
            "reviewer_role": "Manager",
            "stars": 4,
            "testimonial": "Great work!"
        },
        follow_redirects=False
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert "/dashboard?rating=1" in response.headers["location"]
