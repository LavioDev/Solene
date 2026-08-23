from datetime import date, datetime
from typing import Optional, Sequence
import uuid
from sqlalchemy import desc, select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.repository import BaseRepository
from app.modules.couples.models import Couple
from app.modules.moods.models import UserMood
from app.modules.moods.schemas import MoodCreate, MoodUpdate


class MoodRepository(BaseRepository[UserMood, MoodCreate, MoodUpdate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=UserMood, session=session)

    async def get_by_user_and_date(self, user_id: uuid.UUID, entry_date: date) -> Optional[UserMood]:
        stmt = select(UserMood).where(
            UserMood.user_id == user_id,
            UserMood.entry_date == entry_date,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_partner_id(self, user_id: uuid.UUID) -> Optional[uuid.UUID]:
        couple_stmt = (
            select(Couple)
            .where(
                or_(Couple.user1_id == user_id, Couple.user2_id == user_id),
                Couple.status == "active",
            )
            .order_by(desc(Couple.created_at))
        )
        couple_res = await self.session.execute(couple_stmt)
        couple = couple_res.scalars().first()
        if not couple:
            return None
        return couple.user2_id if couple.user1_id == user_id else couple.user1_id

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        include_partner: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[UserMood]:
        partner_id = await self.get_partner_id(user_id) if include_partner else None

        if partner_id:
            user_filter = or_(
                UserMood.user_id == user_id,
                and_(UserMood.user_id == partner_id, UserMood.is_shared == True),
            )
        else:
            user_filter = (UserMood.user_id == user_id)

        stmt = select(UserMood).where(user_filter)

        if from_date is not None:
            stmt = stmt.where(UserMood.entry_date >= from_date)
        if to_date is not None:
            stmt = stmt.where(UserMood.entry_date <= to_date)

        stmt = stmt.order_by(desc(UserMood.entry_date), desc(UserMood.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_user(
        self,
        user_id: uuid.UUID,
        *,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        include_partner: bool = True,
    ) -> int:
        partner_id = await self.get_partner_id(user_id) if include_partner else None

        if partner_id:
            user_filter = or_(
                UserMood.user_id == user_id,
                and_(UserMood.user_id == partner_id, UserMood.is_shared == True),
            )
        else:
            user_filter = (UserMood.user_id == user_id)

        stmt = select(func.count(UserMood.id)).where(user_filter)

        if from_date is not None:
            stmt = stmt.where(UserMood.entry_date >= from_date)
        if to_date is not None:
            stmt = stmt.where(UserMood.entry_date <= to_date)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete_mood(self, mood: UserMood) -> None:
        await self.session.delete(mood)
        await self.session.commit()
