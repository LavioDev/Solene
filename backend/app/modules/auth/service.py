from typing import Any, Optional, Sequence, Tuple
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import UserCreate, UserLoginIn, UserRegisterIn, UserUpdate


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


class UserService:
    @staticmethod
    async def create_user(session: AsyncSession, payload: UserCreate) -> User:
        user_repo = UserRepository(session=session)
        existing_user = await user_repo.get_by_email(payload.email)
        if existing_user:
            raise BadRequestException("An account with this email already exists.")

        hashed_pw = hash_password(payload.password)
        return await user_repo.create_user(
            email=payload.email,
            hashed_password=hashed_pw,
            full_name=payload.full_name or "User",
            role=payload.role or "admin",
            avatar_url=payload.avatar_url,
            is_active=payload.is_active if payload.is_active is not None else True,
        )

    @staticmethod
    async def list_users(
        session: AsyncSession,
        *,
        page: int = 1,
        per_page: int = 15,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[Sequence[User], int]:
        user_repo = UserRepository(session=session)
        actual_skip = skip if skip is not None else max(0, (page - 1) * per_page)
        actual_limit = limit if limit is not None else per_page
        users = await user_repo.list_users(
            skip=actual_skip,
            limit=actual_limit,
            role=role,
            is_active=is_active,
            search=search,
        )
        total = await user_repo.count_users(
            role=role,
            is_active=is_active,
            search=search,
        )
        return users, total

    @staticmethod
    async def count_users(
        session: AsyncSession,
        *,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> int:
        user_repo = UserRepository(session=session)
        return await user_repo.count_users(
            role=role,
            is_active=is_active,
            search=search,
        )

    @staticmethod
    async def get_user(session: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        user_repo = UserRepository(session=session)
        return await user_repo.get_by_id(user_id)

    @staticmethod
    async def update_user(
        session: AsyncSession,
        user_id: uuid.UUID,
        payload: UserUpdate,
    ) -> Optional[User]:
        user_repo = UserRepository(session=session)
        user = await user_repo.get_by_id(user_id)
        if not user:
            return None

        if payload.email and payload.email != user.email:
            existing = await user_repo.get_by_email(payload.email)
            if existing and existing.id != user.id:
                raise BadRequestException("An account with this email already exists.")

        update_data: dict[str, Any] = {}
        if payload.email is not None:
            update_data["email"] = payload.email
        if payload.full_name is not None:
            update_data["full_name"] = payload.full_name
        if payload.role is not None:
            update_data["role"] = payload.role
        if payload.avatar_url is not None:
            update_data["avatar_url"] = payload.avatar_url
        if payload.is_active is not None:
            update_data["is_active"] = payload.is_active
        if payload.password is not None:
            update_data["hashed_password"] = hash_password(payload.password)

        return await user_repo.update_user(user=user, data=update_data)


    @staticmethod
    async def delete_user(
        session: AsyncSession,
        user_id: uuid.UUID,
        current_user_id: Optional[uuid.UUID] = None,
    ) -> bool:
        if current_user_id and user_id == current_user_id:
            raise BadRequestException("You cannot delete your own account.")

        user_repo = UserRepository(session=session)
        user = await user_repo.get_by_id(user_id)
        if not user:
            return False

        await user_repo.delete_user(user=user)
        return True

