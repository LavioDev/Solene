from typing import Optional, Sequence
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, NotFoundException
from app.modules.auth.repository import UserRepository
from app.modules.couples.models import Couple
from app.modules.couples.repository import CoupleRepository
from app.modules.couples.schemas import CoupleCreate, CoupleUpdate


class CoupleService:
    @staticmethod
    async def create_couple(
        session: AsyncSession,
        current_user_id: uuid.UUID,
        payload: CoupleCreate,
        is_admin: bool = False,
    ) -> Couple:
        user_repo = UserRepository(session)
        user1_id = payload.user1_id if (payload.user1_id and is_admin) else (payload.user1_id or current_user_id)
        user2_id = payload.user2_id

        if user1_id == user2_id:
            raise BadRequestException("Cannot create a couple with yourself.")

        # Validate partner existence
        partner = await user_repo.get_by_id(user2_id)
        if not partner:
            raise NotFoundException("Partner user not found.")

        # Validate primary user existence
        user1 = await user_repo.get_by_id(user1_id)
        if not user1:
            raise NotFoundException("Primary user not found.")

        repo = CoupleRepository(session)
        return await repo.create_couple(user1_id=user1_id, schema_in=payload)

    @staticmethod
    async def get_my_couple(
        session: AsyncSession,
        user_id: uuid.UUID,
        status: Optional[str] = None,
    ) -> Optional[Couple]:
        repo = CoupleRepository(session)
        return await repo.get_by_user_id(user_id=user_id, status=status)

    @staticmethod
    async def get_couple(
        session: AsyncSession,
        couple_id: uuid.UUID,
        user_id: uuid.UUID,
        is_admin: bool = False,
    ) -> Optional[Couple]:
        repo = CoupleRepository(session)
        if is_admin:
            return await repo.get_by_id_with_users(couple_id)
        return await repo.get_couple_for_user(couple_id=couple_id, user_id=user_id)

    @staticmethod
    async def list_couples(
        session: AsyncSession,
        user_id: uuid.UUID,
        is_admin: bool = False,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Couple]:
        repo = CoupleRepository(session)
        if is_admin:
            return await repo.list_all(status=status, skip=skip, limit=limit)
        return await repo.list_for_user(user_id=user_id, status=status, skip=skip, limit=limit)

    @staticmethod
    async def update_couple(
        session: AsyncSession,
        couple_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: CoupleUpdate,
        is_admin: bool = False,
    ) -> Optional[Couple]:
        repo = CoupleRepository(session)
        couple = await repo.get_by_id_with_users(couple_id) if is_admin else await repo.get_couple_for_user(couple_id=couple_id, user_id=user_id)
        if not couple:
            return None

        return await repo.update_couple(couple=couple, schema_in=payload)

    @staticmethod
    async def delete_couple(
        session: AsyncSession,
        couple_id: uuid.UUID,
        user_id: uuid.UUID,
        is_admin: bool = False,
    ) -> bool:
        repo = CoupleRepository(session)
        couple = await repo.get_by_id_with_users(couple_id) if is_admin else await repo.get_couple_for_user(couple_id=couple_id, user_id=user_id)
        if not couple:
            return False

        await repo.delete_couple(couple)
        return True
