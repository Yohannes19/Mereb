from pathlib import Path

from fastapi import Depends, FastAPI, Form, Header, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app import models, schemas, services
from app.database import Base, engine, get_db


BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title="Mereb",
    description="Public proof profiles for Ethiopian creators and small businesses.",
    version="0.1.0",
)
app.add_middleware(SessionMiddleware, secret_key="dev-session-secret-change-me")

static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.on_event("startup")
def on_startup():
    # Only create tables if we are not in a test (though TestClient usually respects overrides)
    # This is a safety measure for the production engine
    from app.database import engine
    Base.metadata.create_all(bind=engine)


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


def current_profile_from_session(request: Request, db: Session) -> models.Profile | None:
    profile_id = request.session.get("profile_id")
    if not profile_id:
        return None
    profile = db.query(models.Profile).filter_by(id=profile_id).first()
    if not profile:
        return None
    return services.ensure_profile_defaults(db, profile=profile)


def require_dashboard_profile(request: Request, db: Session = Depends(get_db)) -> models.Profile:
    profile = current_profile_from_session(request, db)
    if not profile:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/auth/login"})
    return profile


def require_api_profile(x_api_key: str | None = Header(default=None), db: Session = Depends(get_db)) -> models.Profile:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key header")
    profile = db.query(models.Profile).filter_by(api_key=x_api_key).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return profile


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    demo_profile = services.get_or_create_demo_profile(db)
    profile = current_profile_from_session(request, db)
    if profile:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request,
        "landing.html",
        {
            "request": request,
            "demo_profile": demo_profile,
        },
    )


@app.get("/dashboard", response_class=HTMLResponse)
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


@app.post("/dashboard/profile")
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
    )
    return RedirectResponse(url="/dashboard?profile=1", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/dashboard/proof")
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
        client_name=client_name or None,
        category=category,
        summary=summary,
        result_metric=result_metric or None,
        proof_url=proof_url or None,
        image_url=image_url or None,
        verification_note=verification_note or None,
    )
    return RedirectResponse(url="/dashboard?proof=1", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/dashboard/ratings")
def create_rating_from_dashboard(
    reviewer_name: str = Form(...),
    reviewer_role: str = Form(""),
    stars: int = Form(5),
    testimonial: str = Form(...),
    profile: models.Profile = Depends(require_dashboard_profile),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    services.add_rating(
        db,
        profile=profile,
        reviewer_name=reviewer_name,
        reviewer_role=reviewer_role or None,
        stars=stars,
        testimonial=testimonial,
    )
    return RedirectResponse(url="/dashboard?rating=1", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/auth/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {"request": request})


@app.post("/auth/login")
def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    profile = services.authenticate_profile(db, email=email, password=password)
    if not profile:
        return RedirectResponse(url="/auth/login?error=1", status_code=status.HTTP_303_SEE_OTHER)
    request.session["profile_id"] = profile.id
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/auth/register", response_class=HTMLResponse)
def register_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "register.html", {"request": request})


@app.post("/auth/register")
def register_action(
    request: Request,
    display_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_type: str = Form("creator"),
    city: str = Form("Addis Ababa"),
    niche: str = Form("Creative services"),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    existing = db.query(models.Profile).filter_by(email=email).first()
    if existing:
        return RedirectResponse(url="/auth/register?exists=1", status_code=status.HTTP_303_SEE_OTHER)
    profile = services.create_profile(
        db,
        display_name=display_name,
        email=email,
        password=password,
        profile_type=profile_type,
        city=city,
        niche=niche,
    )
    request.session["profile_id"] = profile.id
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/auth/logout")
def logout_action(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/p/{slug}", response_class=HTMLResponse)
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


@app.get("/p/{slug}/review", response_class=HTMLResponse)
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


@app.post("/p/{slug}/review")
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


@app.post("/v1/proof", response_model=schemas.ProofItemResponse, status_code=status.HTTP_201_CREATED)
def create_proof_api(
    payload: schemas.ProofItemCreate,
    profile: models.Profile = Depends(require_api_profile),
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


@app.post("/v1/ratings", response_model=schemas.RatingResponse, status_code=status.HTTP_201_CREATED)
def create_rating_api(
    payload: schemas.RatingCreate,
    profile: models.Profile = Depends(require_api_profile),
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


@app.get("/v1/proof", response_model=list[schemas.ProofItemResponse])
def list_proof_api(
    profile: models.Profile = Depends(require_api_profile),
    db: Session = Depends(get_db),
) -> list[schemas.ProofItemResponse]:
    items = (
        db.query(models.ProofItem)
        .filter(models.ProofItem.profile_id == profile.id)
        .order_by(models.ProofItem.created_at.desc())
        .all()
    )
    return [proof_response(item) for item in items]


@app.get("/v1/ratings", response_model=list[schemas.RatingResponse])
def list_ratings_api(
    profile: models.Profile = Depends(require_api_profile),
    db: Session = Depends(get_db),
) -> list[schemas.RatingResponse]:
    items = (
        db.query(models.Rating)
        .filter(models.Rating.profile_id == profile.id)
        .order_by(models.Rating.created_at.desc())
        .all()
    )
    return [rating_response(item) for item in items]


@app.get("/v1/profile", response_model=schemas.ProfileResponse)
def get_profile_api(profile: models.Profile = Depends(require_api_profile)) -> schemas.ProfileResponse:
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
