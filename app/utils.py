import re
import secrets
import string
from sqlalchemy.orm import Session
from app import models

def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or f"profile-{secrets.token_hex(3)}"

def ensure_unique_slug(db: Session, *, display_name: str, profile_id: str | None = None) -> str:
    base_slug = slugify(display_name)
    candidate = base_slug
    counter = 2
    while True:
        query = db.query(models.Profile).filter_by(slug=candidate)
        if profile_id:
            query = query.filter(models.Profile.id != profile_id)
        if not query.first():
            return candidate
        candidate = f"{base_slug}-{counter}"
        counter += 1

def format_handle(value: str) -> str | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    if cleaned.startswith("@"):
        return cleaned
    alphabet = string.ascii_letters + string.digits + "._"
    simplified = "".join(char for char in cleaned if char in alphabet)
    return f"@{simplified}" if simplified else None
