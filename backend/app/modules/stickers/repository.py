from typing import List, Optional
from uuid import UUID
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.stickers.models import PinnedSticker
from app.modules.stickers.schemas import PinnedStickerBatchItem, PinnedStickerCreate, PinnedStickerUpdate


class StickerRepository:
    @staticmethod
    async def list_by_couple(session: AsyncSession, couple_id: UUID) -> List[PinnedSticker]:
        stmt = (
            select(PinnedSticker)
            .where(PinnedSticker.couple_id == couple_id)
            .order_by(PinnedSticker.z_index.asc(), PinnedSticker.created_at.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(session: AsyncSession, sticker_id: UUID) -> Optional[PinnedSticker]:
        stmt = select(PinnedSticker).where(PinnedSticker.id == sticker_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        session: AsyncSession,
        couple_id: UUID,
        user_id: UUID,
        payload: PinnedStickerCreate,
    ) -> PinnedSticker:
        sticker = PinnedSticker(
            couple_id=couple_id,
            user_id=user_id,
            sticker_url=payload.sticker_url,
            name=payload.name,
            x_percent=payload.x_percent,
            y_percent=payload.y_percent,
            scale=payload.scale,
            rotation=payload.rotation,
            z_index=payload.z_index,
            is_locked=payload.is_locked,
        )
        session.add(sticker)
        await session.commit()
        await session.refresh(sticker)
        return sticker

    @staticmethod
    async def update(
        session: AsyncSession,
        sticker: PinnedSticker,
        payload: PinnedStickerUpdate,
    ) -> PinnedSticker:
        update_data = payload.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(sticker, field, val)

        await session.commit()
        await session.refresh(sticker)
        return sticker

    @staticmethod
    async def batch_update(
        session: AsyncSession,
        couple_id: UUID,
        items: List[PinnedStickerBatchItem],
    ) -> None:
        for item in items:
            stmt = select(PinnedSticker).where(
                PinnedSticker.id == item.id,
                PinnedSticker.couple_id == couple_id,
            )
            res = await session.execute(stmt)
            sticker = res.scalar_one_or_none()
            if sticker:
                sticker.x_percent = item.x_percent
                sticker.y_percent = item.y_percent
                sticker.scale = item.scale
                sticker.rotation = item.rotation
                sticker.z_index = item.z_index
                if item.is_locked is not None:
                    sticker.is_locked = item.is_locked

        await session.commit()

    @staticmethod
    async def delete(session: AsyncSession, sticker: PinnedSticker) -> None:
        await session.delete(sticker)
        await session.commit()

    @staticmethod
    async def delete_all_by_couple(session: AsyncSession, couple_id: UUID) -> int:
        stmt = delete(PinnedSticker).where(PinnedSticker.couple_id == couple_id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount or 0
