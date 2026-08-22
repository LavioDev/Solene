from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_async_db
from app.modules.auth.models import User
from app.modules.tasks.schemas import (
    PartnerActiveStatusOut,
    TaskCreate,
    TaskOut,
    TaskToggleStatus,
    TaskUpdate,
)
from app.modules.tasks.service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks & To-Do List"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> TaskOut:
    """Create a new task with schedule and status."""
    task = await TaskService.create_task(session=session, user_id=current_user.id, payload=payload)
    return task


@router.get("/partner-active", response_model=PartnerActiveStatusOut)
async def get_partner_active_task(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> PartnerActiveStatusOut:
    """Get active task and busy status for current user's partner in active couple."""
    return await TaskService.get_partner_active_status(session=session, user_id=current_user.id)


@router.get("", response_model=List[TaskOut])

async def list_tasks(
    is_completed: Optional[bool] = Query(None, description="Filter by completion status"),
    start_from: Optional[datetime] = Query(None, description="Filter tasks starting after or at this datetime"),
    end_to: Optional[datetime] = Query(None, description="Filter tasks ending before or at this datetime"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Limit for pagination"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> List[TaskOut]:
    """List all tasks for the current user with optional filters."""
    tasks = await TaskService.list_tasks(
        session=session,
        user_id=current_user.id,
        is_completed=is_completed,
        start_from=start_from,
        end_to=end_to,
        skip=skip,
        limit=limit,
    )
    return list(tasks)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> TaskOut:
    """Get details of a specific task."""
    task = await TaskService.get_task(session=session, user_id=current_user.id, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> TaskOut:
    """Update an existing task."""
    updated = await TaskService.update_task(
        session=session,
        user_id=current_user.id,
        task_id=task_id,
        payload=payload,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return updated


@router.patch("/{task_id}", response_model=TaskOut)
async def patch_task(
    task_id: UUID,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> TaskOut:
    """Partially update an existing task."""
    updated = await TaskService.update_task(
        session=session,
        user_id=current_user.id,
        task_id=task_id,
        payload=payload,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return updated


@router.patch("/{task_id}/toggle", response_model=TaskOut)
async def toggle_task_status(
    task_id: UUID,
    payload: Optional[TaskToggleStatus] = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> TaskOut:
    """Toggle or explicitly set completion status of a task."""
    target_status = payload.is_completed if payload else None
    updated = await TaskService.toggle_task_status(
        session=session,
        user_id=current_user.id,
        task_id=task_id,
        is_completed=target_status,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> None:
    """Delete a task."""
    deleted = await TaskService.delete_task(session=session, user_id=current_user.id, task_id=task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return None
