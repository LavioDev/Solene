from typing import Any, Optional, Sequence, Tuple
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException, UnauthorizedException
from app.core.permission_cache import (
    get_cached_user_permissions,
    invalidate_cached_user_permissions,
    set_cached_user_permissions,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.models import Permission, User
from app.modules.auth.repository import PermissionRepository, UserRepository
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

        # Cache permissions in Redis for fast lookup
        if user.role == "manager":
            perm_codes = await self.user_repo.get_user_permission_codes(user.id)
            await set_cached_user_permissions(user.id, perm_codes)

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

        if user.role == "manager":
            perm_codes = await self.user_repo.get_user_permission_codes(user.id)
            await set_cached_user_permissions(user.id, perm_codes)

        new_access_token = create_access_token(subject=str(user.id))
        new_refresh_token = create_refresh_token(subject=str(user.id))
        return user, new_access_token, new_refresh_token


class PermissionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.perm_repo = PermissionRepository(session=session)

    async def list_permissions(self) -> Sequence[Permission]:
        return await self.perm_repo.list_all()


class UserService:
    @staticmethod
    async def create_user(
        session: AsyncSession,
        payload: UserCreate,
        actor: Optional[User] = None,
    ) -> User:
        user_repo = UserRepository(session=session)
        existing_user = await user_repo.get_by_email(payload.email)
        if existing_user:
            raise BadRequestException("An account with this email already exists.")

        target_role = payload.role or "user"
        permission_ids = payload.permission_ids

        # Invariant Guard: Manager can ONLY create regular users ('user' role)
        if actor and actor.role == "manager":
            if payload.role in ["admin", "manager"]:
                raise ForbiddenException("Managers are only allowed to create accounts with 'user' role.")
            target_role = "user"
            permission_ids = None  # Managers cannot grant permissions

        hashed_pw = hash_password(payload.password)
        created_user = await user_repo.create_user(
            email=payload.email,
            hashed_password=hashed_pw,
            full_name=payload.full_name or "User",
            role=target_role,
            avatar_url=payload.avatar_url,
            is_active=payload.is_active if payload.is_active is not None else True,
            permission_ids=permission_ids if (actor and actor.role == "admin") else None,
            assigned_by=actor.id if actor else None,
        )
        return created_user

    @staticmethod
    async def list_users(
        session: AsyncSession,
        *,
        actor: Optional[User] = None,
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

        target_role = role
        # Invariant Guard: Manager can only list users with role 'user'
        if actor and actor.role == "manager":
            target_role = "user"

        users = await user_repo.list_users(
            skip=actual_skip,
            limit=actual_limit,
            role=target_role,
            is_active=is_active,
            search=search,
        )
        total = await user_repo.count_users(
            role=target_role,
            is_active=is_active,
            search=search,
        )
        return users, total

    @staticmethod
    async def count_users(
        session: AsyncSession,
        *,
        actor: Optional[User] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> int:
        user_repo = UserRepository(session=session)
        target_role = role
        if actor and actor.role == "manager":
            target_role = "user"

        return await user_repo.count_users(
            role=target_role,
            is_active=is_active,
            search=search,
        )

    @staticmethod
    async def get_user(
        session: AsyncSession,
        user_id: uuid.UUID,
        actor: Optional[User] = None,
    ) -> Optional[User]:
        user_repo = UserRepository(session=session)
        user = await user_repo.get_by_id(user_id)
        if not user:
            return None

        # Invariant Guard: Manager can only view users with role 'user'
        if actor and actor.role == "manager" and user.role != "user" and user.id != actor.id:
            raise ForbiddenException("Managers are not permitted to view admin or manager profiles.")

        return user

    @staticmethod
    async def update_user(
        session: AsyncSession,
        user_id: uuid.UUID,
        payload: UserUpdate,
        actor: Optional[User] = None,
    ) -> Optional[User]:
        user_repo = UserRepository(session=session)
        user = await user_repo.get_by_id(user_id)
        if not user:
            return None

        # Invariant Guard: Permissions according to actor role
        if actor:
            if actor.role == "admin":
                pass
            elif actor.role == "manager":
                # Manager cannot modify admin or other managers
                if user.role != "user" and user.id != actor.id:
                    raise ForbiddenException("Managers can only manage users with 'user' role.")
                # Manager cannot elevate role or change role to admin/manager
                if payload.role is not None and payload.role != "user":
                    raise ForbiddenException("Managers cannot elevate or change user roles.")
                # Manager cannot assign permissions
                if payload.permission_ids is not None:
                    raise ForbiddenException("Managers cannot assign permissions.")
            else:
                if actor.id != user_id:
                    raise ForbiddenException("You can only modify your own profile.")
                if payload.role is not None and payload.role != user.role:
                    raise ForbiddenException("Cannot modify your own role.")
                if payload.is_active is not None and payload.is_active != user.is_active:
                    raise ForbiddenException("Cannot modify your own active status.")
                if payload.permission_ids is not None:
                    raise ForbiddenException("Cannot modify permissions.")

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
            # If actor is manager, keep role as user
            if actor and actor.role == "manager":
                update_data["role"] = "user"
            elif actor and actor.role == "admin":
                update_data["role"] = payload.role
        if payload.avatar_url is not None:
            update_data["avatar_url"] = payload.avatar_url
        if payload.is_active is not None:
            update_data["is_active"] = payload.is_active
        if payload.password is not None:
            update_data["hashed_password"] = hash_password(payload.password)

        updated_user = await user_repo.update_user(user=user, data=update_data)

        # Handle permissions assignment if admin provided permission_ids
        if actor and actor.role == "admin" and payload.permission_ids is not None:
            await user_repo.assign_permissions(
                user_id=user_id,
                permission_ids=payload.permission_ids,
                assigned_by=actor.id,
            )
            await invalidate_cached_user_permissions(user_id)
            await session.refresh(updated_user)

        return updated_user

    @staticmethod
    async def delete_user(
        session: AsyncSession,
        user_id: uuid.UUID,
        actor: User,
    ) -> bool:
        # Invariant Guard: Manager CANNOT delete any user
        if actor.role != "admin":
            raise ForbiddenException("Only administrators have permission to delete user accounts.")

        if user_id == actor.id:
            raise BadRequestException("You cannot delete your own account.")

        user_repo = UserRepository(session=session)
        user = await user_repo.get_by_id(user_id)
        if not user:
            return False

        await user_repo.delete_user(user=user)
        await invalidate_cached_user_permissions(user_id)
        return True

    @staticmethod
    async def assign_manager_permissions(
        session: AsyncSession,
        manager_id: uuid.UUID,
        permission_ids: Sequence[uuid.UUID],
        admin: User,
    ) -> Sequence[Permission]:
        if admin.role != "admin":
            raise ForbiddenException("Only administrators can assign permissions.")

        user_repo = UserRepository(session=session)
        manager = await user_repo.get_by_id(manager_id)
        if not manager:
            raise NotFoundException("User account not found.")

        assigned = await user_repo.assign_permissions(
            user_id=manager_id,
            permission_ids=permission_ids,
            assigned_by=admin.id,
        )
        await invalidate_cached_user_permissions(manager_id)
        return assigned

    @staticmethod
    async def get_user_permissions(
        session: AsyncSession,
        user_id: uuid.UUID,
        actor: User,
    ) -> Sequence[Permission]:
        if actor.role != "admin" and actor.id != user_id:
            raise ForbiddenException("Insufficient privileges to view permissions for this user.")

        user_repo = UserRepository(session=session)
        return await user_repo.get_user_permissions(user_id)
