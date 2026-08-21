from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import UserLoginIn, UserRegisterIn


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session=session)

    async def register(self, payload: UserRegisterIn) -> Tuple[User, str, str]:
        existing_user = await self.user_repo.get_by_email(payload.email)
        if existing_user:
            raise BadRequestException("An account with this email already exists.")

        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name or "User",
            role="admin",
            is_active=True,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        return user, access_token, refresh_token

    async def authenticate(self, payload: UserLoginIn) -> Tuple[User, str, str]:
        user = await self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive.")

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        return user, access_token, refresh_token

    async def refresh_session(self, refresh_token: str) -> Tuple[User, str, str]:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type.")
            user_id = payload.get("sub")
        except Exception:
            raise UnauthorizedException("Expired or invalid refresh token.")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive.")

        new_access_token = create_access_token(subject=str(user.id))
        new_refresh_token = create_refresh_token(subject=str(user.id))
        return user, new_access_token, new_refresh_token
