from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app import models, services
from app.database import get_db
from app.dependencies import require_admin_profile

router = APIRouter(prefix="/admin", tags=["admin"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/dashboard", response_class=HTMLResponse)
@router.get("", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    admin_user: models.Profile = Depends(require_admin_profile), 
    db: Session = Depends(get_db)
):
    all_profiles = services.get_all_profiles(db)
    all_proofs = services.get_all_proof_items(db)
    all_ratings = services.get_all_ratings(db)
    
    return templates.TemplateResponse(
        request, 
        "admin_dashboard.html", 
        {
            "request": request, 
            "admin_user": admin_user,
            "all_profiles": all_profiles,
            "all_proofs": all_proofs,
            "all_ratings": all_ratings
        }
    )


@router.post("/users/{profile_id}/delete")
def admin_delete_user(
    profile_id: int,
    admin_user: models.Profile = Depends(require_admin_profile),
    db: Session = Depends(get_db)
):
    services.delete_profile(db, profile_id=profile_id)
    return RedirectResponse(url="/admin?user=deleted", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/proofs/{proof_id}/delete")
def admin_delete_proof(
    proof_id: int,
    admin_user: models.Profile = Depends(require_admin_profile),
    db: Session = Depends(get_db)
):
    # Retrieve the proof to get profile_id, wait, delete_proof_item requires profile_id for safety.
    # In admin mode, we can just delete it directly or fetch profile_id. Let's fetch it first.
    proof = db.query(models.ProofItem).filter_by(id=proof_id).first()
    if proof:
        services.delete_proof_item(db, proof_id=proof_id, profile_id=proof.profile_id)
    return RedirectResponse(url="/admin?proof=deleted", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/ratings/{rating_id}/delete")
def admin_delete_rating(
    rating_id: int,
    admin_user: models.Profile = Depends(require_admin_profile),
    db: Session = Depends(get_db)
):
    rating = db.query(models.Rating).filter_by(id=rating_id).first()
    if rating:
        services.delete_rating(db, rating_id=rating_id, profile_id=rating.profile_id)
    return RedirectResponse(url="/admin?rating=deleted", status_code=status.HTTP_303_SEE_OTHER)
