import secrets
import jwt
from datetime import datetime, timedelta
from hashlib import pbkdf2_hmac
from typing import Any, Union
from app.core.config import settings

def generate_api_key() -> str:
    return secrets.token_hex(24)

def hash_password(password: str, salt: str | None = None) -> str:
    salt_value = salt or secrets.token_hex(16)
    digest = pbkdf2_hmac("sha256", password.encode("utf-8"), salt_value.encode("utf-8"), settings.PBKDF2_ITERATIONS)
    return f"{salt_value}${digest.hex()}"

def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash or "$" not in password_hash:
        return False
    salt, expected = password_hash.split("$", 1)
    return hash_password(password, salt) == f"{salt}${expected}"

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> str | None:
    try:
        decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_data.get("sub")
    except jwt.PyJWTError:
        return None
