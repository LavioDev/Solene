from typing import AsyncGenerator
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_async_db),
) -> User:
    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authentication token is missing.")

    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type.")
        user_id = payload.get("sub")
    except Exception:
        raise UnauthorizedException("Token is invalid or expired.")

    user_repo = UserRepository(session=session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedException("User does not exist.")
    if not user.is_active:
        raise UnauthorizedException("User account is inactive.")

    return user
