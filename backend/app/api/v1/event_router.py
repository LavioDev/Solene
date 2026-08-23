from datetime import date, datetime, time, timezone
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.api.deps import get_current_user
from app.modules.auth.models import User
from app.modules.events.schemas import SpecialEventCreate, SpecialEventUpdate, SpecialEventOut, EventOccurrenceOut
from app.modules.events.service import EventService
from app.modules.couples.models import Couple
from app.modules.memories.models import Memory
from app.modules.tasks.models import Task

router = APIRouter(prefix="/events", tags=["Special Events & Calendar"])



@router.post("", response_model=SpecialEventOut, status_code=status.HTTP_201_CREATED)
async def create_special_event(
    payload: SpecialEventCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """Create a new recurring special event rule."""
    return await EventService.create_event(session, current_user.id, payload)


@router.get("", response_model=List[SpecialEventOut])
async def list_special_events(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """List all recurring event rules for the current user."""
    return await EventService.get_user_events(session, current_user.id)


@router.put("/{event_id}", response_model=SpecialEventOut)
async def update_special_event(
    event_id: UUID,
    payload: SpecialEventUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """Update an existing recurring special event rule."""
    updated = await EventService.update_event(session, current_user.id, event_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return updated


@router.get("/occurrences", response_model=List[EventOccurrenceOut])
async def get_event_occurrences(
    start_date: date = Query(..., description="Start of date range (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End of date range (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """
    Dynamically calculate and return event occurrences and date-bound memories falling within the specified date window.
    Unifies recurring milestone rules and memories.
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date",
        )

    all_occurrences: List[EventOccurrenceOut] = []

    # 1. Recurring Milestone Rules from special_events
    events = await EventService.get_user_events(session, current_user.id)
    for event in events:
        occs = EventService.generate_occurrences_for_window(event, start_date, end_date)
        all_occurrences.extend(occs)

    # 2. Date-bound Memories from memories
    couple_stmt = (
        select(Couple)
        .where(
            or_(Couple.user1_id == current_user.id, Couple.user2_id == current_user.id),
            Couple.status == "active",
        )
        .order_by(Couple.created_at.desc())
    )
    couple_res = await session.execute(couple_stmt)
    couple = couple_res.scalars().first()
    partner_id = None
    if couple:
        partner_id = couple.user2_id if couple.user1_id == current_user.id else couple.user1_id

    if partner_id:
        memory_user_filter = or_(
            Memory.user_id == current_user.id,
            and_(Memory.user_id == partner_id, Memory.is_shared == True),
        )
    else:
        memory_user_filter = (Memory.user_id == current_user.id)

    memory_stmt = select(Memory).where(
        memory_user_filter,
        Memory.display_type == "DATE",
        Memory.target_date >= start_date,
        Memory.target_date <= end_date,
    )
    memory_res = await session.execute(memory_stmt)
    date_memories = memory_res.scalars().all()

    for mem in date_memories:
        if mem.target_date:
            all_occurrences.append(
                EventOccurrenceOut(
                    event_id=mem.id,
                    title=mem.title,
                    date=mem.target_date,
                    category="memory",
                    milestone_info=mem.content,
                    image_url=mem.image_url,
                    is_shared=mem.is_shared,
                )
            )

    # Sort occurrences chronologically
    all_occurrences.sort(key=lambda x: x.date)
    return all_occurrences




@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_special_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """Delete an event rule."""
    deleted = await EventService.delete_event(session, current_user.id, event_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return None
