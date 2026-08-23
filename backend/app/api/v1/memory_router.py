from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.pagination import PaginatedResponse, paginate_response
from app.api.deps import get_current_user
from app.modules.auth.models import User
from app.modules.memories.schemas import MemoryCreate, MemoryUpdate, MemoryOut
from app.modules.memories.service import MemoryService

router = APIRouter(prefix="/memories", tags=["Memories & Moments"])


@router.post("", response_model=MemoryOut, status_code=status.HTTP_201_CREATED)
async def create_memory(
    payload: MemoryCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """Create a new memory card."""
    return await MemoryService.create_memory(session, current_user.id, payload)


@router.get("", response_model=PaginatedResponse[MemoryOut])
async def list_memories(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(15, ge=1, le=100, description="Items per page (default: 15)"),
    display_type: Optional[str] = Query(None, description="Filter by display type: DATE or RANDOM"),
    search: Optional[str] = Query(None, description="Search by title or content"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> PaginatedResponse[MemoryOut]:
    """List memory cards with pagination (per-page: 15)."""
    items, total = await MemoryService.list_user_memories(
        session=session,
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        display_type=display_type,
        search=search,
    )
    return paginate_response(
        items=[MemoryOut.model_validate(n) for n in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.put("/{memory_id}", response_model=MemoryOut)
async def update_memory(
    memory_id: UUID,
    payload: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """Update an existing memory card."""
    updated = await MemoryService.update_memory(session, current_user.id, memory_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
    return updated


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    """Delete a memory card."""
    deleted = await MemoryService.delete_memory(session, current_user.id, memory_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
    return None
