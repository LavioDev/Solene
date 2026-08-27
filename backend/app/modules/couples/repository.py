from typing import Optional, Sequence
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.core.repository import BaseRepository
from app.modules.couples.models import Couple, CoupleInvitation
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

    async def count_for_user(
        self,
        user_id: uuid.UUID,
        *,
        status: Optional[str] = None,
    ) -> int:
        stmt = select(func.count()).select_from(Couple).where(or_(Couple.user1_id == user_id, Couple.user2_id == user_id))
        if status:
            stmt = stmt.where(Couple.status == status)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

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

    async def count_all(
        self,
        *,
        status: Optional[str] = None,
    ) -> int:
        stmt = select(func.count()).select_from(Couple)
        if status:
            stmt = stmt.where(Couple.status == status)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

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

    # --- Invitation Repository Methods ---

    async def get_invitation_by_code(self, code: str) -> Optional[CoupleInvitation]:
        stmt = (
            select(CoupleInvitation)
            .options(joinedload(CoupleInvitation.inviter))
            .where(CoupleInvitation.code == code)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_active_invitation_by_inviter(self, inviter_id: uuid.UUID) -> Optional[CoupleInvitation]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(CoupleInvitation)
            .options(joinedload(CoupleInvitation.inviter))
            .where(
                CoupleInvitation.inviter_id == inviter_id,
                CoupleInvitation.status == "pending",
                CoupleInvitation.expires_at > now,
            )
            .order_by(desc(CoupleInvitation.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def revoke_active_invitations_for_user(self, inviter_id: uuid.UUID) -> None:
        stmt = (
            update(CoupleInvitation)
            .where(
                CoupleInvitation.inviter_id == inviter_id,
                CoupleInvitation.status == "pending",
            )
            .values(status="revoked")
        )
        await self.session.execute(stmt)

    async def create_invitation(
        self,
        inviter_id: uuid.UUID,
        code: str,
        expires_at: datetime,
    ) -> CoupleInvitation:
        # First revoke existing pending invitations for this user
        await self.revoke_active_invitations_for_user(inviter_id)
        invitation = CoupleInvitation(
            inviter_id=inviter_id,
            code=code,
            status="pending",
            expires_at=expires_at,
        )
        self.session.add(invitation)
        await self.session.commit()
        return await self.get_invitation_by_code(code)  # type: ignore[return-value]

    async def revoke_invitation(self, invitation: CoupleInvitation) -> None:
        invitation.status = "revoked"
        self.session.add(invitation)
        await self.session.commit()

    async def accept_invitation_and_create_couple(
        self,
        invitation: CoupleInvitation,
        partner_id: uuid.UUID,
        start_date: date,
        nickname: Optional[str] = None,
        cover_url: Optional[str] = None,
    ) -> Couple:
        # Mark invitation as accepted
        invitation.status = "accepted"
        self.session.add(invitation)

        # Create Couple record
        couple = Couple(
            user1_id=invitation.inviter_id,
            user2_id=partner_id,
            start_date=start_date,
            nickname=nickname,
            status="active",
            cover_url=cover_url,
        )
        self.session.add(couple)
        await self.session.commit()
        return await self.get_by_id_with_users(couple.id)  # type: ignore[return-value]

