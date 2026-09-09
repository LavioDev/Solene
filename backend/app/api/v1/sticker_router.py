from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_async_db
from app.modules.auth.models import User
from app.modules.stickers.schemas import (
    PinnedStickerBatchSync,
    PinnedStickerCreate,
    PinnedStickerOut,
    PinnedStickerUpdate,
)
from app.modules.stickers.service import StickerService

router = APIRouter(prefix="/stickers", tags=["Stickers & Dashboard Canvas"])


@router.get("/board", response_model=List[PinnedStickerOut])
async def get_board_stickers(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> List[PinnedStickerOut]:
    """Retrieve all pinned stickers for the current user's couple board."""
    return await StickerService.list_board_stickers(
        session=session,
        user_id=current_user.id,
    )


@router.post("/board", response_model=PinnedStickerOut, status_code=status.HTTP_201_CREATED)
async def pin_sticker(
    payload: PinnedStickerCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> PinnedStickerOut:
    """Pin a new sticker to the couple's dashboard board."""
    return await StickerService.pin_sticker(
        session=session,
        user_id=current_user.id,
        payload=payload,
    )


@router.put("/board/batch", response_model=List[PinnedStickerOut])
async def batch_sync_stickers(
    payload: PinnedStickerBatchSync,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> List[PinnedStickerOut]:
    """Batch update sticker positions/scales/rotations across the board."""
    return await StickerService.batch_sync(
        session=session,
        user_id=current_user.id,
        payload=payload,
    )


@router.put("/board/{sticker_id}", response_model=PinnedStickerOut)
async def update_pinned_sticker(
    sticker_id: UUID,
    payload: PinnedStickerUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> PinnedStickerOut:
    """Update a specific pinned sticker's position, scale, rotation, or z-index."""
    return await StickerService.update_sticker(
        session=session,
        user_id=current_user.id,
        sticker_id=sticker_id,
        payload=payload,
    )


@router.delete("/board/{sticker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pinned_sticker(
    sticker_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> None:
    """Remove a specific pinned sticker from the board."""
    await StickerService.delete_sticker(
        session=session,
        user_id=current_user.id,
        sticker_id=sticker_id,
    )


@router.delete("/board", status_code=status.HTTP_200_OK)
async def clear_board_stickers(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> dict:
    """Remove all pinned stickers from the couple's dashboard board."""
    count = await StickerService.clear_board(
        session=session,
        user_id=current_user.id,
    )
    return {"message": "All stickers cleared", "deleted_count": count}
