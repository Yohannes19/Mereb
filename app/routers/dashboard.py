from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app import models, services
from app.database import get_db
from app.dependencies import require_dashboard_profile

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("", response_class=HTMLResponse)
def dashboard(
    request: Request,
    profile: models.Profile = Depends(require_dashboard_profile),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    profile = db.query(models.Profile).filter_by(id=profile.id).first() or profile
    metrics = services.build_dashboard_metrics(profile)
    audit = services.build_profile_audit(profile)
    proof_items = sorted(profile.proof_items, key=lambda item: item.created_at, reverse=True)
    ratings = sorted(profile.ratings, key=lambda item: item.created_at, reverse=True)
    
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "profile": profile,
            "metrics": metrics,
            "audit": audit,
            "proof_items": proof_items,
            "ratings": ratings,
        },
    )


@router.post("/profile")
def update_dashboard_profile(
    display_name: str = Form(...),
    profile_type: str = Form("creator"),
    city: str = Form(""),
    country: str = Form("Ethiopia"),
    niche: str = Form(""),
    tagline: str = Form(""),
    bio: str = Form(""),
    instagram_handle: str = Form(""),
    tiktok_handle: str = Form(""),
    telegram_handle: str = Form(""),
    website_url: str = Form(""),
    profile_image_url: str = Form(""),
    profile: models.Profile = Depends(require_dashboard_profile),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    services.update_profile(
        db,
        profile=profile,
        display_name=display_name,
        profile_type=profile_type,
        city=city,
        country=country,
        niche=niche,
        tagline=tagline,
        bio=bio,
        instagram_handle=instagram_handle,
        tiktok_handle=tiktok_handle,
        telegram_handle=telegram_handle,
        website_url=website_url,
        profile_image_url=profile_image_url,
    )
    return RedirectResponse(url="/dashboard?profile=1", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/proof")
def create_proof_from_dashboard(
    title: str = Form(...),
    client_name: str = Form(""),
    category: str = Form("campaign"),
    summary: str = Form(...),
    result_metric: str = Form(""),
    proof_url: str = Form(""),
    image_url: str = Form(""),
    verification_note: str = Form(""),
    profile: models.Profile = Depends(require_dashboard_profile),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    services.add_proof_item(
        db,
        profile=profile,
        title=title,
        client_name=client_name,
        category=category,
        summary=summary,
        result_metric=result_metric,
        proof_url=proof_url,
        image_url=image_url,
        verification_note=verification_note,
    )
    return RedirectResponse(url="/dashboard?proof=1", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/proof/{item_id}/edit")
def edit_proof_from_dashboard(
    item_id: str,
    title: str = Form(...),
    client_name: str = Form(""),
    category: str = Form("campaign"),
    summary: str = Form(...),
    result_metric: str = Form(""),
    proof_url: str = Form(""),
    image_url: str = Form(""),
    verification_note: str = Form(""),
    profile: models.Profile = Depends(require_dashboard_profile),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    services.update_proof_item(
        db,
        proof_id=item_id,
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
    return RedirectResponse(url="/dashboard?proof=1", status_code=status.HTTP_303_SEE_OTHER)



@router.post("/ratings/{rating_id}/delete")
def delete_rating_from_dashboard(
    rating_id: str,
    profile: models.Profile = Depends(require_dashboard_profile),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    services.delete_rating(db, rating_id=rating_id, profile_id=profile.id)
    return RedirectResponse(url="/dashboard?rating=deleted", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/proof/{item_id}/delete")
def delete_proof_from_dashboard(
    item_id: str,
    profile: models.Profile = Depends(require_dashboard_profile),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    services.delete_proof_item(db, proof_id=item_id, profile_id=profile.id)
    return RedirectResponse(url="/dashboard?proof=deleted", status_code=status.HTTP_303_SEE_OTHER)
