from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ProofItemCreate(BaseModel):
    title: str = Field(max_length=255)
    client_name: str | None = Field(default=None, max_length=255)
    category: str = Field(default="campaign", max_length=80)
    summary: str = Field(min_length=10)
    result_metric: str | None = Field(default=None, max_length=255)
    proof_url: str | None = Field(default=None, max_length=500)
    image_url: str | None = Field(default=None, max_length=500)
    verification_note: str | None = Field(default=None, max_length=255)


class RatingCreate(BaseModel):
    reviewer_name: str = Field(max_length=255)
    reviewer_role: str | None = Field(default=None, max_length=255)
    stars: int = Field(default=5, ge=1, le=5)
    testimonial: str = Field(min_length=10)


class ProofItemResponse(BaseModel):
    id: str
    title: str
    client_name: str | None = None
    category: str
    summary: str
    result_metric: str | None = None
    proof_url: str | None = None
    image_url: str | None = None
    verification_note: str | None = None
    created_at: datetime


class RatingResponse(BaseModel):
    id: str
    reviewer_name: str
    reviewer_role: str | None = None
    stars: int
    testimonial: str
    created_at: datetime


class ProfileResponse(BaseModel):
    id: str
    display_name: str
    email: EmailStr
    slug: str | None = None
    profile_type: str
    city: str | None = None
    country: str
    niche: str | None = None
    tagline: str | None = None
    bio: str | None = None
    instagram_handle: str | None = None
    tiktok_handle: str | None = None
    telegram_handle: str | None = None
    website_url: str | None = None
    created_at: datetime
