from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.database import get_db
from app.dependencies import require_api_profile_by_key

router = APIRouter(prefix="/v1", tags=["api"])


def proof_response(item: models.ProofItem) -> schemas.ProofItemResponse:
    return schemas.ProofItemResponse(
        id=item.id,
        title=item.title,
        client_name=item.client_name,
        category=item.category,
        summary=item.summary,
        result_metric=item.result_metric,
        proof_url=item.proof_url,
        image_url=item.image_url,
        verification_note=item.verification_note,
        created_at=item.created_at,
    )


def rating_response(item: models.Rating) -> schemas.RatingResponse:
    return schemas.RatingResponse(
        id=item.id,
        reviewer_name=item.reviewer_name,
        reviewer_role=item.reviewer_role,
        stars=item.stars,
        testimonial=item.testimonial,
        created_at=item.created_at,
    )


@router.post("/proof", response_model=schemas.ProofItemResponse, status_code=status.HTTP_201_CREATED)
def create_proof_api(
    payload: schemas.ProofItemCreate,
    profile: models.Profile = Depends(require_api_profile_by_key),
    db: Session = Depends(get_db),
) -> schemas.ProofItemResponse:
    item = services.add_proof_item(
        db,
        profile=profile,
        title=payload.title,
        client_name=payload.client_name,
        category=payload.category,
        summary=payload.summary,
        result_metric=payload.result_metric,
        proof_url=payload.proof_url,
        image_url=payload.image_url,
        verification_note=payload.verification_note,
    )
    return proof_response(item)


@router.post("/ratings", response_model=schemas.RatingResponse, status_code=status.HTTP_201_CREATED)
def create_rating_api(
    payload: schemas.RatingCreate,
    profile: models.Profile = Depends(require_api_profile_by_key),
    db: Session = Depends(get_db),
) -> schemas.RatingResponse:
    item = services.add_rating(
        db,
        profile=profile,
        reviewer_name=payload.reviewer_name,
        reviewer_role=payload.reviewer_role,
        stars=payload.stars,
        testimonial=payload.testimonial,
    )
    return rating_response(item)


@router.get("/proof", response_model=list[schemas.ProofItemResponse])
def list_proof_api(
    profile: models.Profile = Depends(require_api_profile_by_key),
    db: Session = Depends(get_db),
) -> list[schemas.ProofItemResponse]:
    items = (
        db.query(models.ProofItem)
        .filter(models.ProofItem.profile_id == profile.id)
        .order_by(models.ProofItem.created_at.desc())
        .all()
    )
    return [proof_response(item) for item in items]


@router.get("/ratings", response_model=list[schemas.RatingResponse])
def list_ratings_api(
    profile: models.Profile = Depends(require_api_profile_by_key),
    db: Session = Depends(get_db),
) -> list[schemas.RatingResponse]:
    items = (
        db.query(models.Rating)
        .filter(models.Rating.profile_id == profile.id)
        .order_by(models.Rating.created_at.desc())
        .all()
    )
    return [rating_response(item) for item in items]


@router.get("/profile", response_model=schemas.ProfileResponse)
def get_profile_api(profile: models.Profile = Depends(require_api_profile_by_key)) -> schemas.ProfileResponse:
    return schemas.ProfileResponse(
        id=profile.id,
        display_name=profile.display_name,
        email=profile.email,
        slug=profile.slug,
        profile_type=profile.profile_type,
        city=profile.city,
        country=profile.country,
        niche=profile.niche,
        tagline=profile.tagline,
        bio=profile.bio,
        instagram_handle=profile.instagram_handle,
        tiktok_handle=profile.tiktok_handle,
        telegram_handle=profile.telegram_handle,
        website_url=profile.website_url,
        created_at=profile.created_at,
    )
