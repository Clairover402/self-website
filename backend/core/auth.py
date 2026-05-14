"""
JWT authentication utilities for admin access.

Uses python-jose for JWT encode/decode.
The admin token is configured via ADMIN_TOKEN env var.
"""
import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Request, HTTPException

SECRET_KEY = os.getenv("ADMIN_SECRET", "self-website-admin-secret-key-change-me")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin123")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def create_admin_token() -> str:
    """Create a JWT token for admin access."""
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": "admin", "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_admin_token(token: str) -> bool:
    """Verify a JWT admin token. Returns True if valid."""
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except JWTError:
        return False


def login_admin(password: str) -> str | None:
    """Validate admin password and return JWT token if correct."""
    if password == ADMIN_TOKEN:
        return create_admin_token()
    return None


def check_admin_security():
    """Startup check: warn if default credentials are in use."""
    import logging
    logger = logging.getLogger("auth")
    if SECRET_KEY == "self-website-admin-secret-key-change-me":
        logger.warning("ADMIN_SECRET is using the default value! Set ADMIN_SECRET in .env for production.")
    if ADMIN_TOKEN == "admin123":
        logger.warning("ADMIN_TOKEN is using the default value! Set ADMIN_TOKEN in .env for production.")