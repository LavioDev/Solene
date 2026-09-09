from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.modules.couples.repository import CoupleRepository
from app.modules.stickers.models import PinnedSticker
from app.modules.stickers.repository import StickerRepository
from app.modules.stickers.schemas import (
    PinnedStickerBatchSync,
    PinnedStickerCreate,
    PinnedStickerOut,
    PinnedStickerUpdate,
)


class StickerService:
    @staticmethod
    async def _get_user_couple(session: AsyncSession, user_id: UUID):
        couple_repo = CoupleRepository(session=session)
        couple = await couple_repo.get_by_user_id(user_id, status="active")
        if not couple:
            # Fallback to any couple if status is not strictly 'active'
            couple = await couple_repo.get_by_user_id(user_id)
        if not couple:
            raise NotFoundException("User is not linked to any couple.")
        return couple

    @staticmethod
    def _to_sticker_out(sticker: PinnedSticker) -> PinnedStickerOut:
        user_name = sticker.user.full_name if sticker.user else None
        return PinnedStickerOut(
            id=sticker.id,
            couple_id=sticker.couple_id,
            user_id=sticker.user_id,
            user_name=user_name,
            sticker_url=sticker.sticker_url,
            name=sticker.name,
            x_percent=sticker.x_percent,
            y_percent=sticker.y_percent,
            scale=sticker.scale,
            rotation=sticker.rotation,
            z_index=sticker.z_index,
            is_locked=getattr(sticker, 'is_locked', False),
            created_at=sticker.created_at,
            updated_at=sticker.updated_at,
        )

    @classmethod
    async def list_board_stickers(
        cls,
        session: AsyncSession,
        user_id: UUID,
    ) -> List[PinnedStickerOut]:
        couple = await cls._get_user_couple(session, user_id)
        stickers = await StickerRepository.list_by_couple(session, couple.id)
        return [cls._to_sticker_out(s) for s in stickers]

    @classmethod
    async def pin_sticker(
        cls,
        session: AsyncSession,
        user_id: UUID,
        payload: PinnedStickerCreate,
    ) -> PinnedStickerOut:
        couple = await cls._get_user_couple(session, user_id)
        sticker = await StickerRepository.create(
            session=session,
            couple_id=couple.id,
            user_id=user_id,
            payload=payload,
        )
        return cls._to_sticker_out(sticker)

    @classmethod
    async def update_sticker(
        cls,
        session: AsyncSession,
        user_id: UUID,
        sticker_id: UUID,
        payload: PinnedStickerUpdate,
    ) -> PinnedStickerOut:
        couple = await cls._get_user_couple(session, user_id)
        sticker = await StickerRepository.get_by_id(session, sticker_id)
        if not sticker:
            raise NotFoundException("Pinned sticker not found.")
        if sticker.couple_id != couple.id:
            raise ForbiddenException("You cannot modify stickers belonging to another couple.")

        updated = await StickerRepository.update(session, sticker, payload)
        return cls._to_sticker_out(updated)

    @classmethod
    async def batch_sync(
        cls,
        session: AsyncSession,
        user_id: UUID,
        payload: PinnedStickerBatchSync,
    ) -> List[PinnedStickerOut]:
        couple = await cls._get_user_couple(session, user_id)
        await StickerRepository.batch_update(session, couple.id, payload.stickers)
        stickers = await StickerRepository.list_by_couple(session, couple.id)
        return [cls._to_sticker_out(s) for s in stickers]

    @classmethod
    async def delete_sticker(
        cls,
        session: AsyncSession,
        user_id: UUID,
        sticker_id: UUID,
    ) -> None:
        couple = await cls._get_user_couple(session, user_id)
        sticker = await StickerRepository.get_by_id(session, sticker_id)
        if not sticker:
            raise NotFoundException("Pinned sticker not found.")
        if sticker.couple_id != couple.id:
            raise ForbiddenException("You cannot delete stickers belonging to another couple.")

        await StickerRepository.delete(session, sticker)

    @classmethod
    async def clear_board(
        cls,
        session: AsyncSession,
        user_id: UUID,
    ) -> int:
        couple = await cls._get_user_couple(session, user_id)
        return await StickerRepository.delete_all_by_couple(session, couple.id)
