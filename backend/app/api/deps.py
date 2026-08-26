from typing import AsyncGenerator, Callable
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.permission_cache import get_cached_user_permissions, set_cached_user_permissions
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


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise ForbiddenException("Admin privileges required.")
    return current_user


def require_permission(perm_code: str) -> Callable:
    """Dependency factory enforcing dynamic permissions for Managers, with Superuser Admin bypass."""
    async def _permission_checker(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
    ) -> User:
        # Admin has full unrestricted access
        if current_user.role == "admin":
            return current_user

        # Manager checks dynamic permission matrix
        if current_user.role == "manager":
            cached_perms = await get_cached_user_permissions(current_user.id)
            if cached_perms is not None:
                if perm_code in cached_perms or "*" in cached_perms:
                    return current_user
                raise ForbiddenException(f"Missing required permission: {perm_code}")

            user_repo = UserRepository(session=session)
            db_perms = await user_repo.get_user_permission_codes(current_user.id)
            await set_cached_user_permissions(current_user.id, db_perms)

            if perm_code in db_perms or "*" in db_perms:
                return current_user

            raise ForbiddenException(f"Missing required permission: {perm_code}")

        raise ForbiddenException("Administrative or Managerial privileges required.")

    return _permission_checker
