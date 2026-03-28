from fastapi import Depends, HTTPException, Request, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, services
from app.core.security import verify_access_token
import logging

def get_current_profile_from_token(request: Request, db: Session = Depends(get_db)) -> models.Profile | None:
    # Check cookie for UI routes
    token = request.cookies.get("access_token")
    if not token:
        # Check header for API routes (Bearer token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        return None

    user_id = verify_access_token(token)
    if not user_id:
        return None

    profile = db.query(models.Profile).filter_by(id=user_id).first()
    if not profile:
        return None
    
    return services.ensure_profile_defaults(db, profile=profile)


def require_dashboard_profile(request: Request, db: Session = Depends(get_db)) -> models.Profile:
    profile = get_current_profile_from_token(request, db)
    if not profile:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/auth/login"})
    return profile


def require_api_profile_by_jwt(request: Request, db: Session = Depends(get_db)) -> models.Profile:
    profile = get_current_profile_from_token(request, db)
    if not profile:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing authentication token")
    return profile


def require_api_profile_by_key(x_api_key: str | None = Header(default=None), db: Session = Depends(get_db)) -> models.Profile:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key header")
    profile = db.query(models.Profile).filter_by(api_key=x_api_key).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return profile


def require_admin_profile(request: Request, db: Session = Depends(get_db)) -> models.Profile:
    profile = get_current_profile_from_token(request, db)
    if not profile:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/auth/login"})
        
    if not profile.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
    return profile
