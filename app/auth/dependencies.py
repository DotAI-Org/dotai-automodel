"""JWT creation, decoding, and request authentication."""
from datetime import datetime, timedelta, timezone

from fastapi import Header, HTTPException
from jose import JWTError, jwt
from sqlalchemy import select

from app.auth.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_DAYS


def create_jwt(user_id: str, email: str, name: str) -> str:
    """Create a signed JWT token for a user."""
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    """Decode a JWT token and return user info dict."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "id": payload["sub"],
            "email": payload.get("email", ""),
            "name": payload.get("name", ""),
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_current_user(authorization: str = Header(default="")) -> dict:
    """Extract and decode JWT, verify user exists in DB."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization[7:]
    user = decode_jwt(token)

    from app.db.engine import AsyncSessionLocal
    from app.db.models import User

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user["id"]))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=401, detail="User not found, please login again")

    return user


def get_ws_user(token: str) -> dict:
    """Decode JWT from WebSocket query param."""
    return decode_jwt(token)
