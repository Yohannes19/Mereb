import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    display_name: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    api_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    slug: Mapped[Optional[str]] = mapped_column(String(120), unique=True, index=True, nullable=True)
    profile_type: Mapped[str] = mapped_column(String(30), default="creator")
    city: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    country: Mapped[str] = mapped_column(String(64), default="Ethiopia")
    niche: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    tagline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instagram_handle: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    tiktok_handle: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    telegram_handle: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    profile_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    proof_items: Mapped[list["ProofItem"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    ratings: Mapped[list["Rating"]] = relationship(back_populates="profile", cascade="all, delete-orphan")


class ProofItem(Base):
    __tablename__ = "proof_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    client_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(80), default="campaign")
    summary: Mapped[str] = mapped_column(Text)
    result_metric: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    proof_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    verification_note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    profile: Mapped["Profile"] = relationship(back_populates="proof_items")


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id"), index=True)
    reviewer_name: Mapped[str] = mapped_column(String(255))
    reviewer_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stars: Mapped[int] = mapped_column(Integer, default=5)
    testimonial: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    profile: Mapped["Profile"] = relationship(back_populates="ratings")
