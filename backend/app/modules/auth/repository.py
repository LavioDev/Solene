from typing import Any, List, Optional, Sequence
import uuid
from sqlalchemy import delete, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.repository import BaseRepository
from app.modules.auth.models import Permission, User, UserPermission
from app.modules.auth.schemas import PermissionCreate, UserCreate, UserUpdate


class PermissionRepository(BaseRepository[Permission, PermissionCreate, Any]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Permission, session=session)

    async def get_by_code(self, code: str) -> Optional[Permission]:
        stmt = select(Permission).where(Permission.code == code)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_ids(self, ids: Sequence[uuid.UUID]) -> Sequence[Permission]:
        if not ids:
            return []
        stmt = select(Permission).where(Permission.id.in_(ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_all(self) -> Sequence[Permission]:
        stmt = select(Permission).order_by(Permission.module, Permission.code)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=User, session=session)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    def _build_filter_stmt(
        self,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ):
        stmt = select(User)
        conditions = []
        if role is not None:
            conditions.append(User.role == role)
        if is_active is not None:
            conditions.append(User.is_active == is_active)
        if search:
            search_pattern = f"%{search.strip()}%"
            conditions.append(
                or_(
                    User.email.ilike(search_pattern),
                    User.full_name.ilike(search_pattern),
                )
            )
        if conditions:
            stmt = stmt.where(*conditions)
        return stmt

    async def list_users(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Sequence[User]:
        stmt = self._build_filter_stmt(role=role, is_active=is_active, search=search)
        stmt = stmt.order_by(desc(User.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_users(
        self,
        *,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> int:
        base_stmt = self._build_filter_stmt(role=role, is_active=is_active, search=search)
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        result = await self.session.execute(count_stmt)
        return result.scalar_one() or 0

    async def create_user(
        self,
        *,
        email: str,
        hashed_password: str,
        full_name: str = "User",
        role: str = "user",
        avatar_url: Optional[str] = None,
        is_active: bool = True,
        permission_ids: Optional[Sequence[uuid.UUID]] = None,
        assigned_by: Optional[uuid.UUID] = None,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            avatar_url=avatar_url,
            is_active=is_active,
        )
        self.session.add(user)
        await self.session.flush()

        if permission_ids:
            for pid in permission_ids:
                up = UserPermission(
                    user_id=user.id,
                    permission_id=pid,
                    assigned_by=assigned_by,
                )
                self.session.add(up)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user(self, *, user: User, data: dict[str, Any]) -> User:
        for field, value in data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, *, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def get_user_permission_codes(self, user_id: uuid.UUID) -> List[str]:
        stmt = (
            select(Permission.code)
            .join(UserPermission, UserPermission.permission_id == Permission.id)
            .where(UserPermission.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_permissions(self, user_id: uuid.UUID) -> Sequence[Permission]:
        stmt = (
            select(Permission)
            .join(UserPermission, UserPermission.permission_id == Permission.id)
            .where(UserPermission.user_id == user_id)
            .order_by(Permission.module, Permission.code)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def assign_permissions(
        self,
        *,
        user_id: uuid.UUID,
        permission_ids: Sequence[uuid.UUID],
        assigned_by: Optional[uuid.UUID] = None,
    ) -> Sequence[Permission]:
        # Delete existing permissions
        del_stmt = delete(UserPermission).where(UserPermission.user_id == user_id)
        await self.session.execute(del_stmt)

        # Insert new permissions
        for pid in permission_ids:
            up = UserPermission(
                user_id=user_id,
                permission_id=pid,
                assigned_by=assigned_by,
            )
            self.session.add(up)

        await self.session.commit()
        return await self.get_user_permissions(user_id)
