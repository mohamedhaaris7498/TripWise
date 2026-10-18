from fastapi import Header, HTTPException, status
from typing import Optional, Dict, Any
from app.utils.security import decode_access_token
from app.database import get_db

async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Dependency to authenticate and return the current user profile from Bearer JWT token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required (Bearer <token>)."
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Must be 'Bearer <token>'."
        )

    token = parts[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token. Please sign in again."
        )

    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed user ID claim in authentication token."
        )

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, phone, age, location, age_bracket, created_at FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists."
        )

    return user

async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Optional dependency that returns user profile if token is valid, or None."""
    if not authorization:
        return None
    try:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            payload = decode_access_token(parts[1])
            if payload and "sub" in payload:
                user_id = int(payload["sub"])
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, name, email, phone, age, location, age_bracket, created_at FROM users WHERE id = ?", (user_id,))
                    return cursor.fetchone()
    except Exception:
        pass
    return None
