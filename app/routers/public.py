from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app import models, services
from app.database import get_db

router = APIRouter(prefix="/p", tags=["public"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/{slug}", response_class=HTMLResponse)
def public_profile_page(slug: str, request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    profile = db.query(models.Profile).filter_by(slug=slug).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Increment view count
    profile.view_count += 1
    db.commit()

    profile = services.ensure_profile_defaults(db, profile=profile)
    metrics = services.build_dashboard_metrics(profile)
    proof_items = sorted(profile.proof_items, key=lambda item: item.created_at, reverse=True)
    ratings = sorted(profile.ratings, key=lambda item: item.created_at, reverse=True)
    return templates.TemplateResponse(
        request,
        "merchant_public.html",
        {
            "request": request,
            "profile": profile,
            "metrics": metrics,
            "proof_items": proof_items,
            "ratings": ratings,
        },
    )


@router.get("/{slug}/review", response_class=HTMLResponse)
def leave_review_page(slug: str, request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    profile = db.query(models.Profile).filter_by(slug=slug).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return templates.TemplateResponse(
        request,
        "leave_review.html",
        {
            "request": request,
            "profile": profile,
        },
    )


@router.post("/{slug}/review")
def submit_public_review(
    slug: str,
    reviewer_name: str = Form(...),
    reviewer_role: str = Form(""),
    stars: int = Form(5),
    testimonial: str = Form(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    profile = db.query(models.Profile).filter_by(slug=slug).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    services.add_rating(
        db,
        profile=profile,
        reviewer_name=reviewer_name,
        reviewer_role=reviewer_role or None,
        stars=stars,
        testimonial=testimonial,
    )
    return RedirectResponse(url=f"/p/{slug}/review?success=1", status_code=status.HTTP_303_SEE_OTHER)
