from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_async_db
from app.modules.auth.models import User
from app.modules.moods.schemas import (
    HeatmapResponse,
    MoodCreate,
    MoodOut,
    MoodStatsResponse,
    MoodUpdate,
    TodayMoodResponse,
)
from app.modules.moods.service import MoodService

router = APIRouter(prefix="/moods", tags=["User Moods & Daily Emotions"])


@router.post("", response_model=MoodOut, status_code=status.HTTP_201_CREATED)
async def log_mood(
    payload: MoodCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> MoodOut:
    """Log or update (upsert) the current day's mood.

    Only current day entries are accepted.
    """
    return await MoodService.upsert_mood(
        session=session,
        user_id=current_user.id,
        payload=payload,
    )


@router.get("/today", response_model=TodayMoodResponse)
async def get_today_mood(
    timezone: str = Query("Asia/Ho_Chi_Minh", description="User IANA timezone"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> TodayMoodResponse:
    """Get today's logged mood for the current user and partner (if shared)."""
    return await MoodService.get_today_mood(
        session=session,
        user_id=current_user.id,
        timezone=timezone,
    )


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_mood_heatmap(
    year: Optional[int] = Query(None, description="Calendar year (e.g. 2026)"),
    timezone: str = Query("Asia/Ho_Chi_Minh", description="User IANA timezone"),
    include_partner: bool = Query(True, description="Include shared partner moods"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> HeatmapResponse:
    """Get full year 365-day grid data for GitHub-style contribution matrix."""
    return await MoodService.get_yearly_heatmap(
        session=session,
        user_id=current_user.id,
        year=year,
        timezone=timezone,
        include_partner=include_partner,
    )


@router.get("/stats", response_model=MoodStatsResponse)
async def get_mood_stats(
    from_date: Optional[date] = Query(None, description="Start date for stats (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date for stats (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> MoodStatsResponse:
    """Get mood analytics and score distributions."""
    return await MoodService.get_stats(
        session=session,
        user_id=current_user.id,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("", response_model=list[MoodOut])
async def list_moods(
    from_date: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    include_partner: bool = Query(True, description="Include shared partner moods"),
    timezone: str = Query("Asia/Ho_Chi_Minh", description="User IANA timezone"),
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(50, ge=1, le=100, description="Limit"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> list[MoodOut]:
    """List historical mood entries with dynamic locking status."""
    items, _ = await MoodService.list_moods(
        session=session,
        user_id=current_user.id,
        from_date=from_date,
        to_date=to_date,
        include_partner=include_partner,
        timezone=timezone,
        skip=skip,
        limit=limit,
    )
    return items


@router.put("/{mood_id}", response_model=MoodOut)
async def update_mood(
    mood_id: UUID,
    payload: MoodUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> MoodOut:
    """Update today's mood entry. Locked after midnight (403 Forbidden)."""
    return await MoodService.update_mood(
        session=session,
        user_id=current_user.id,
        mood_id=mood_id,
        payload=payload,
    )


@router.delete("/{mood_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mood(
    mood_id: UUID,
    timezone: str = Query("Asia/Ho_Chi_Minh", description="User IANA timezone"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> None:
    """Delete today's mood entry. Locked after midnight (403 Forbidden)."""
    await MoodService.delete_mood(
        session=session,
        user_id=current_user.id,
        mood_id=mood_id,
        timezone=timezone,
    )
    return None
