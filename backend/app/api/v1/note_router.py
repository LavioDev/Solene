from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.api.deps import get_current_user
from app.modules.auth.models import User
from app.modules.notes.schemas import NoteCreate, NoteUpdate, NoteOut
from app.modules.notes.service import NoteService

router = APIRouter(prefix="/notes", tags=["User Notes & Memories"])


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """Create a new note or memory card."""
    return await NoteService.create_note(session, current_user.id, payload)


@router.get("", response_model=List[NoteOut])
async def list_notes(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """List all notes and memory cards for current user."""
    return await NoteService.list_user_notes(session, current_user.id)


@router.put("/{note_id}", response_model=NoteOut)
async def update_note(
    note_id: UUID,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """Update an existing note or memory card."""
    updated = await NoteService.update_note(session, current_user.id, note_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return updated


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """Delete a note or memory card."""
    deleted = await NoteService.delete_note(session, current_user.id, note_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return None
