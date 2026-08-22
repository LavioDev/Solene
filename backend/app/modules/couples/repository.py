from typing import Optional, Sequence
import uuid
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.core.repository import BaseRepository
from app.modules.couples.models import Couple
from app.modules.couples.schemas import CoupleCreate, CoupleUpdate


class CoupleRepository(BaseRepository[Couple, CoupleCreate, CoupleUpdate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Couple, session=session)

    async def get_by_id_with_users(self, couple_id: uuid.UUID) -> Optional[Couple]:
        stmt = (
            select(Couple)
            .options(joinedload(Couple.user1), joinedload(Couple.user2))
            .where(Couple.id == couple_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        status: Optional[str] = None,
    ) -> Optional[Couple]:
        stmt = (
            select(Couple)
            .options(joinedload(Couple.user1), joinedload(Couple.user2))
            .where(or_(Couple.user1_id == user_id, Couple.user2_id == user_id))
        )
        if status:
            stmt = stmt.where(Couple.status == status)
        stmt = stmt.order_by(desc(Couple.created_at))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_couple_for_user(
        self,
        couple_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Couple]:
        stmt = (
            select(Couple)
            .options(joinedload(Couple.user1), joinedload(Couple.user2))
            .where(
                Couple.id == couple_id,
                or_(Couple.user1_id == user_id, Couple.user2_id == user_id),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Couple]:
        stmt = (
            select(Couple)
            .options(joinedload(Couple.user1), joinedload(Couple.user2))
            .where(or_(Couple.user1_id == user_id, Couple.user2_id == user_id))
        )
        if status:
            stmt = stmt.where(Couple.status == status)
        stmt = stmt.order_by(desc(Couple.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_all(
        self,
        *,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Couple]:
        stmt = (
            select(Couple)
            .options(joinedload(Couple.user1), joinedload(Couple.user2))
        )
        if status:
            stmt = stmt.where(Couple.status == status)
        stmt = stmt.order_by(desc(Couple.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_couple(
        self,
        user1_id: uuid.UUID,
        schema_in: CoupleCreate,
    ) -> Couple:
        data = schema_in.model_dump(exclude_unset=True)
        data.pop("user1_id", None)
        couple = Couple(user1_id=user1_id, **data)
        self.session.add(couple)
        await self.session.commit()
        # Fetch with relationships loaded
        return await self.get_by_id_with_users(couple.id)  # type: ignore[return-value]

    async def update_couple(
        self,
        couple: Couple,
        schema_in: CoupleUpdate | dict,
    ) -> Couple:
        await self.update(db_obj=couple, schema_in=schema_in)
        return await self.get_by_id_with_users(couple.id)  # type: ignore[return-value]

    async def delete_couple(self, couple: Couple) -> None:
        await self.session.delete(couple)
        await self.session.commit()
