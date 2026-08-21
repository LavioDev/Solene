from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_async_db
from app.core.exceptions import UnauthorizedException
from app.modules.auth.models import User
from app.modules.auth.schemas import TokenOut, UserLoginIn, UserOut, UserRegisterIn
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production HTTPS
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/",
    )


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterIn,
    response: Response,
    session: AsyncSession = Depends(get_async_db),
) -> TokenOut:
    auth_service = AuthService(session=session)
    user, access_token, refresh_token = await auth_service.register(payload)
    _set_refresh_cookie(response, refresh_token)
    return TokenOut(access_token=access_token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
async def login(
    payload: UserLoginIn,
    response: Response,
    session: AsyncSession = Depends(get_async_db),
) -> TokenOut:
    auth_service = AuthService(session=session)
    user, access_token, refresh_token = await auth_service.authenticate(payload)
    _set_refresh_cookie(response, refresh_token)
    return TokenOut(access_token=access_token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/refresh", response_model=TokenOut)
async def refresh_token(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_async_db),
) -> TokenOut:
    cookie_token = request.cookies.get("refresh_token")
    if not cookie_token:
        raise UnauthorizedException("Refresh token cookie is missing.")

    auth_service = AuthService(session=session)
    user, access_token, new_refresh_token = await auth_service.refresh_session(cookie_token)
    _set_refresh_cookie(response, new_refresh_token)
    return TokenOut(access_token=access_token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        samesite="lax",
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
