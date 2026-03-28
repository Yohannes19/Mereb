from itsdangerous import URLSafeSerializer
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

serializer = URLSafeSerializer(settings.SECRET_KEY, salt="csrf-token")

def generate_csrf_token(session_id: str) -> str:
    """Generate a signed CSRF token for a given session/user identifier."""
    return serializer.dumps(session_id)

def verify_csrf_token(token: str, session_id: str) -> bool:
    """Verify a CSRF token matches the session/user identifier."""
    try:
        data = serializer.loads(token)
        return data == session_id
    except Exception:
        return False

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # We only care about state-changing methods
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            # Skip if it's an API request with an API Key or Bearer token (usually handled via CORS/Tokens)
            # For our app, we'll focus on Form submissions from the UI
            content_type = request.headers.get("Content-Type", "")
            if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                form_data = await request.form()
                csrf_token = form_data.get("csrf_token")
                
                # Use current profile ID or access_token as session identifier
                session_id = request.cookies.get("access_token", "anonymous")
                
                if not csrf_token or not verify_csrf_token(csrf_token, session_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="CSRF token validation failed. Please refresh the page and try again."
                    )
        
        response = await call_next(request)
        return response
