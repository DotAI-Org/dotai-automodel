"""Google OAuth login and callback routes."""
import os

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from app.auth.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.auth.dependencies import create_jwt, get_current_user
from app.db.engine import AsyncSessionLocal
from app.db.models import User
from app.notifications import fire_and_forget as notify

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google")
async def login_google(request: Request):
    """Redirect user to Google OAuth consent screen."""
    redirect_uri = str(request.url_for("auth_google_callback"))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="auth_google_callback")
async def auth_google_callback(request: Request):
    """Handle Google OAuth callback, create or update user, issue JWT."""
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo", {})

    email = user_info.get("email", "")
    name = user_info.get("name", "")
    picture = user_info.get("picture", "")
    sub = user_info.get("sub", "")

    is_new_user = False
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user is None:
            is_new_user = True
            user = User(
                email=email,
                name=name,
                avatar_url=picture,
                provider="google",
                provider_id=sub,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            user.name = name
            user.avatar_url = picture
            user.provider_id = sub
            await db.commit()

        jwt_token = create_jwt(str(user.id), user.email, user.name or "")

    notify(
        "User login",
        f"{'New' if is_new_user else 'Returning'} user: {name} ({email})",
    )

    base_url = os.environ.get("APP_BASE_URL", str(request.base_url).rstrip("/"))
    return RedirectResponse(url=f"{base_url}/?token={jwt_token}")


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user["id"]))
        row = result.scalar_one_or_none()
        if row is None:
            return user
        return {
            "id": str(row.id),
            "email": row.email,
            "name": row.name,
            "avatar_url": row.avatar_url,
        }
