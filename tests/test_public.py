import pytest
from fastapi import status
from app.models import Profile

from app import services
from app.models import Profile

def test_public_profile_view(client, db_session):
    # Use services to create profile correctly
    profile = services.create_profile(
        db_session,
        display_name="Public Tester",
        email="tester@example.com",
        password="password",
        profile_type="creator",
        city="Addis Ababa",
        niche="Software"
    )
    db_session.commit()
    db_session.refresh(profile)

    # Visit the profile using its real slug
    response = client.get(f"/p/{profile.slug}")
    assert response.status_code == status.HTTP_200_OK
    assert "Public Tester" in response.text


def test_public_profile_404(client):
    response = client.get("/p/non-existent-slug")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_submit_review_public(client, db_session):
    profile = Profile(
        display_name="Review User",
        email="review@example.com",
        slug="review-user",
        api_key="review-key"
    )
    db_session.add(profile)
    db_session.commit()

    response = client.post(
        "/p/review-user/review",
        data={
            "reviewer_name": "Public Critic",
            "reviewer_role": "Customer",
            "stars": 5,
            "testimonial": "Amazing experience!"
        },
        follow_redirects=False
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    # Based on main.py, it redirects back to the review page with success param
    assert "/p/review-user/review" in response.headers["location"]
    assert "success=1" in response.headers["location"]

