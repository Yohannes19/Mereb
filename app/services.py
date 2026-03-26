import re
import secrets
import string
from hashlib import pbkdf2_hmac

from sqlalchemy.orm import Session

from app import models


DEFAULT_PROFILE_EMAIL = "demo@proofpage.et"
DEFAULT_PROFILE_NAME = "Muna Studio"
DEFAULT_LOGIN_PASSWORD = "changeme123"
PBKDF2_ITERATIONS = 600000


def generate_api_key() -> str:
    return secrets.token_hex(24)


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


def hash_password(password: str, salt: str | None = None) -> str:
    salt_value = salt or secrets.token_hex(16)
    digest = pbkdf2_hmac("sha256", password.encode("utf-8"), salt_value.encode("utf-8"), PBKDF2_ITERATIONS)
    return f"{salt_value}${digest.hex()}"


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash or "$" not in password_hash:
        return False
    salt, expected = password_hash.split("$", 1)
    return hash_password(password, salt) == f"{salt}${expected}"


def get_or_create_demo_profile(db: Session) -> models.Profile:
    profile = db.query(models.Profile).filter_by(email=DEFAULT_PROFILE_EMAIL).first()
    if profile:
        return ensure_profile_defaults(db, profile=profile)

    profile = models.Profile(
        display_name=DEFAULT_PROFILE_NAME,
        email=DEFAULT_PROFILE_EMAIL,
        password_hash=hash_password(DEFAULT_LOGIN_PASSWORD),
        api_key=generate_api_key(),
        slug="muna-studio",
        profile_type="creator",
        city="Addis Ababa",
        country="Ethiopia",
        niche="Beauty content and brand promos",
        tagline="Your work, your proof, your reputation.",
        bio="A public proof profile for brand work, portfolio highlights, and client trust.",
        instagram_handle="@munastudio",
        tiktok_handle="@munastudio",
        telegram_handle="@munabusiness",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    add_proof_item(
        db,
        profile=profile,
        title="Glow Addis launch reel",
        client_name="Glow Addis",
        category="campaign",
        summary="Created a launch reel and short story sequence for a beauty drop campaign.",
        result_metric="12,400 views in 4 days",
        proof_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        image_url="https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80",
        verification_note="Client confirmed delivery and publish date.",
    )
    add_rating(
        db,
        profile=profile,
        reviewer_name="Sara Bekele",
        reviewer_role="Brand owner, Glow Addis",
        stars=5,
        testimonial="Fast delivery, strong communication, and the content looked much more premium than what we had before.",
    )
    return profile


def ensure_profile_defaults(db: Session, *, profile: models.Profile) -> models.Profile:
    updated = False
    if not profile.slug:
        profile.slug = ensure_unique_slug(db, display_name=profile.display_name, profile_id=profile.id)
        updated = True
    if not profile.country:
        profile.country = "Ethiopia"
        updated = True
    if not profile.profile_type:
        profile.profile_type = "creator"
        updated = True
    if updated:
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def authenticate_profile(db: Session, *, email: str, password: str) -> models.Profile | None:
    profile = db.query(models.Profile).filter_by(email=email).first()
    if not profile:
        return None
    if not verify_password(password, profile.password_hash):
        return None
    return ensure_profile_defaults(db, profile=profile)


def create_profile(
    db: Session,
    *,
    display_name: str,
    email: str,
    password: str,
    profile_type: str,
    city: str,
    niche: str,
) -> models.Profile:
    profile = models.Profile(
        display_name=display_name,
        email=email,
        password_hash=hash_password(password),
        api_key=generate_api_key(),
        slug=ensure_unique_slug(db, display_name=display_name),
        profile_type=profile_type or "creator",
        city=city or "Addis Ababa",
        country="Ethiopia",
        niche=niche or "Creative services",
        tagline="Built to show real proof, not just promises.",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(
    db: Session,
    *,
    profile: models.Profile,
    display_name: str,
    profile_type: str,
    city: str,
    country: str,
    niche: str,
    tagline: str,
    bio: str,
    instagram_handle: str,
    tiktok_handle: str,
    telegram_handle: str,
    website_url: str,
) -> models.Profile:
    profile.display_name = display_name
    profile.slug = ensure_unique_slug(db, display_name=display_name, profile_id=profile.id)
    profile.profile_type = profile_type or "creator"
    profile.city = city or None
    profile.country = country or "Ethiopia"
    profile.niche = niche or None
    profile.tagline = tagline or None
    profile.bio = bio or None
    profile.instagram_handle = format_handle(instagram_handle)
    profile.tiktok_handle = format_handle(tiktok_handle)
    profile.telegram_handle = format_handle(telegram_handle)
    profile.website_url = website_url or None
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def add_proof_item(
    db: Session,
    *,
    profile: models.Profile,
    title: str,
    client_name: str | None,
    category: str,
    summary: str,
    result_metric: str | None,
    proof_url: str | None,
    image_url: str | None,
    verification_note: str | None,
) -> models.ProofItem:
    item = models.ProofItem(
        profile_id=profile.id,
        title=title,
        client_name=client_name,
        category=category,
        summary=summary,
        result_metric=result_metric,
        proof_url=proof_url,
        image_url=image_url,
        verification_note=verification_note,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def add_rating(
    db: Session,
    *,
    profile: models.Profile,
    reviewer_name: str,
    reviewer_role: str | None,
    stars: int,
    testimonial: str,
) -> models.Rating:
    rating = models.Rating(
        profile_id=profile.id,
        reviewer_name=reviewer_name,
        reviewer_role=reviewer_role,
        stars=max(1, min(stars, 5)),
        testimonial=testimonial,
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


def build_dashboard_metrics(profile: models.Profile) -> dict[str, float]:
    proof_count = len(profile.proof_items)
    rating_count = len(profile.ratings)
    average_rating = (
        round(sum(rating.stars for rating in profile.ratings) / rating_count, 1)
        if rating_count
        else 0.0
    )
    return {
        "proof_count": proof_count,
        "rating_count": rating_count,
        "average_rating": average_rating,
    }


def build_profile_audit(profile: models.Profile) -> dict[str, object]:
    proof_items = list(profile.proof_items)
    ratings = list(profile.ratings)

    checks = [
        {
            "label": "Clear positioning",
            "done": bool(profile.tagline and profile.niche),
            "problem": "Add a sharper tagline and niche so visitors understand what you do quickly.",
            "improvement": "State who you help and the kind of work you are known for.",
        },
        {
            "label": "Trust-building bio",
            "done": bool(profile.bio and len(profile.bio.strip()) >= 80),
            "problem": "Your profile story is too thin to create confidence yet.",
            "improvement": "Add a short bio that explains your experience, process, and credibility.",
        },
        {
            "label": "Public proof depth",
            "done": len(proof_items) >= 3,
            "problem": "There are not enough proof items to make the page feel established.",
            "improvement": "Aim for at least 3 proof items covering different projects or outcomes.",
        },
        {
            "label": "Outcome-led evidence",
            "done": any(item.result_metric for item in proof_items),
            "problem": "Your work samples are missing visible result metrics.",
            "improvement": "Add at least one measurable outcome like revenue, reach, speed, or conversions.",
        },
        {
            "label": "Verifiable links",
            "done": any(item.proof_url for item in proof_items),
            "problem": "Visitors cannot click through to confirm the work.",
            "improvement": "Attach a live URL, post, case study, or external reference to a proof item.",
        },
        {
            "label": "Client validation",
            "done": len(ratings) >= 2,
            "problem": "There are not enough testimonials to reinforce trust.",
            "improvement": "Collect at least 2 testimonials with names and roles.",
        },
        {
            "label": "Contact readiness",
            "done": bool(profile.website_url or profile.instagram_handle or profile.tiktok_handle or profile.telegram_handle),
            "problem": "Your page does not offer an obvious next step for interested clients.",
            "improvement": "Add a website or social handle so people can continue the conversation.",
        },
    ]

    completed = sum(1 for check in checks if check["done"])
    score = round((completed / len(checks)) * 100)

    strengths = []
    if proof_items:
        strengths.append(f"{len(proof_items)} proof item{'s' if len(proof_items) != 1 else ''} published")
    if ratings:
        strengths.append(f"{len(ratings)} testimonial{'s' if len(ratings) != 1 else ''} on the page")
    if any(item.result_metric for item in proof_items):
        strengths.append("visible outcome metrics")
    if profile.website_url or profile.instagram_handle or profile.tiktok_handle or profile.telegram_handle:
        strengths.append("clear contact path")
    if not strengths:
        strengths.append("profile foundation created")

    problems = [check["problem"] for check in checks if not check["done"]][:4]
    improvements = [check["improvement"] for check in checks if not check["done"]][:4]

    if score >= 85:
        status = "Strong"
        summary = "Your page looks credible and close to client-ready."
    elif score >= 60:
        status = "Promising"
        summary = "The page is headed in the right direction but still needs a few trust signals."
    else:
        status = "Needs work"
        summary = "The structure is there, but key credibility details are still missing."

    return {
        "score": score,
        "status": status,
        "summary": summary,
        "checks": checks,
        "strengths": strengths,
        "problems": problems,
        "improvements": improvements,
    }


def format_handle(value: str) -> str | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    if cleaned.startswith("@"):
        return cleaned
    alphabet = string.ascii_letters + string.digits + "._"
    simplified = "".join(char for char in cleaned if char in alphabet)
    return f"@{simplified}" if simplified else None
