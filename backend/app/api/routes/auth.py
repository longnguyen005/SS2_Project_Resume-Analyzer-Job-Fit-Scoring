from __future__ import annotations

import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from authlib.integrations.base_client.errors import OAuthError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.oauth import get_oauth_client
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import User
from app.schemas.auth import TokenResponse, UserCreate, UserRead
from app.schemas.common import APIResponse

router = APIRouter()


@router.post("/register", response_model=APIResponse[UserRead], status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> APIResponse[UserRead]:
    existing_user = await db.execute(select(User).where(User.email == payload.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return APIResponse(message="Account created successfully.", data=UserRead.model_validate(user))


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TokenResponse]:
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(str(user.id))
    return APIResponse(message="Login successful.", data=TokenResponse(access_token=token))


@router.get("/me", response_model=APIResponse[UserRead])
async def read_current_user(current_user: User = Depends(get_current_user)) -> APIResponse[UserRead]:
    return APIResponse(message="Current user retrieved successfully.", data=UserRead.model_validate(current_user))


@router.get("/oauth/{provider}/login")
async def oauth_login(provider: str, request: Request) -> RedirectResponse:
    client = get_oauth_client(provider)
    if client is None:
        return RedirectResponse(_build_frontend_redirect(error=f"{provider.title()} login is not configured."))

    redirect_uri = f"{settings.backend_public_url}{settings.api_v1_prefix}/auth/oauth/{provider}/callback"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    client = get_oauth_client(provider)
    if client is None:
        return RedirectResponse(_build_frontend_redirect(error=f"{provider.title()} login is not configured."))

    try:
        token = await client.authorize_access_token(request)
        profile = await _load_oauth_profile(provider, client, token)
        user = await _get_or_create_oauth_user(db, profile)
        access_token = create_access_token(str(user.id))
    except OAuthError as exc:
        return RedirectResponse(_build_frontend_redirect(error=str(exc)))
    except HTTPException as exc:
        return RedirectResponse(_build_frontend_redirect(error=str(exc.detail)))
    except Exception:
        return RedirectResponse(_build_frontend_redirect(error="Social login failed. Please try again."))

    return RedirectResponse(
        _build_frontend_redirect(
            access_token=access_token,
            provider=provider,
        )
    )


def _build_frontend_redirect(**params: str) -> str:
    query = urlencode({key: value for key, value in params.items() if value})
    return f"{settings.frontend_public_url}/oauth/callback?{query}" if query else f"{settings.frontend_public_url}/oauth/callback"


async def _load_oauth_profile(provider: str, client, token: dict) -> dict[str, str]:
    if provider == "google":
        userinfo = token.get("userinfo")
        if not userinfo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not load Google profile.")

        email = userinfo.get("email")
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google account did not return an email.")

        return {
            "email": email,
            "full_name": userinfo.get("name") or email.split("@")[0],
        }

    if provider == "github":
        user_response = await client.get("user", token=token)
        user_data = user_response.json()
        email = user_data.get("email")

        if not email:
            emails_response = await client.get("user/emails", token=token)
            emails = emails_response.json()
            primary_email = next(
                (item["email"] for item in emails if item.get("primary") and item.get("verified")),
                None,
            )
            email = primary_email or next((item["email"] for item in emails if item.get("verified")), None)

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub account did not return a verified email.",
            )

        return {
            "email": email,
            "full_name": user_data.get("name") or user_data.get("login") or email.split("@")[0],
        }

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unsupported OAuth provider.")


async def _get_or_create_oauth_user(db: AsyncSession, profile: dict[str, str]) -> User:
    result = await db.execute(select(User).where(User.email == profile["email"]))
    user = result.scalar_one_or_none()

    if user is not None:
        if not user.full_name and profile.get("full_name"):
            user.full_name = profile["full_name"]
            await db.commit()
            await db.refresh(user)
        return user

    user = User(
        email=profile["email"],
        full_name=profile["full_name"],
        hashed_password=get_password_hash(secrets.token_urlsafe(32)),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
