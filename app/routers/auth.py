from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app import models, services
from app.database import get_db
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {"request": request})


@router.post("/login")
def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    profile = services.authenticate_profile(db, email=email, password=password)
    if not profile:
        return RedirectResponse(url="/auth/login?error=1", status_code=status.HTTP_303_SEE_OTHER)
    
    # Generate JWT token
    access_token = create_access_token(subject=profile.id)
    
    # Store in HTTPOnly cookie
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return response


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "register.html", {"request": request})


@router.post("/register")
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
    
    access_token = create_access_token(subject=profile.id)
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return response


@router.post("/logout")
def logout_action(request: Request) -> RedirectResponse:
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response
