from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin_user, get_current_user, require_permission
from app.core.database import get_async_db
from app.core.exceptions import ForbiddenException
from app.core.pagination import PaginatedResponse, paginate_response
from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate, UserOut, UserUpdate
from app.modules.auth.service import UserService

router = APIRouter(prefix="/users", tags=["Users Management"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    caller: User = Depends(require_permission("users:create")),
    session: AsyncSession = Depends(get_async_db),
) -> UserOut:
    """Create a new user account (Admin or Manager with 'users:create' permission)."""
    user = await UserService.create_user(session=session, payload=payload, actor=caller)
    return UserOut.model_validate(user)


@router.get("", response_model=PaginatedResponse[UserOut])
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(15, ge=1, le=100, description="Items per page (default: 15)"),
    skip: Optional[int] = Query(None, ge=0, description="Offset for pagination (backward compatibility)"),
    limit: Optional[int] = Query(None, ge=1, le=500, description="Limit for pagination (backward compatibility)"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by email or full name"),
    caller: User = Depends(require_permission("users:read")),
    session: AsyncSession = Depends(get_async_db),
) -> PaginatedResponse[UserOut]:
    """List users with pagination, filters, and search (Admin or Manager with 'users:read')."""
    actual_page = page
    actual_per_page = limit if limit is not None else per_page
    if skip is not None and limit is not None:
        actual_page = (skip // limit) + 1

    users, total = await UserService.list_users(
        session=session,
        actor=caller,
        page=actual_page,
        per_page=actual_per_page,
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
        search=search,
    )
    return paginate_response(
        items=[UserOut.model_validate(u) for u in users],
        total=total,
        page=actual_page,
        per_page=actual_per_page,
    )


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> UserOut:
    """Get user details by ID (Admin, Manager with 'users:read', or self)."""
    if current_user.role == "manager":
        checker = require_permission("users:read")
        await checker(current_user=current_user, session=session)
    elif current_user.role != "admin" and current_user.id != user_id:
        raise ForbiddenException("Insufficient permissions to view this user profile.")

    user = await UserService.get_user(session=session, user_id=user_id, actor=current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserOut.model_validate(user)


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> UserOut:
    """Update user information (Admin, Manager with 'users:update', or self)."""
    if current_user.role == "manager":
        checker = require_permission("users:update")
        await checker(current_user=current_user, session=session)
    elif current_user.role != "admin" and current_user.id != user_id:
        raise ForbiddenException("Insufficient permissions to update this user.")

    updated_user = await UserService.update_user(
        session=session,
        user_id=user_id,
        payload=payload,
        actor=current_user,
    )
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserOut.model_validate(updated_user)


@router.patch("/{user_id}", response_model=UserOut)
async def patch_user(
    user_id: UUID,
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> UserOut:
    """Partially update user information."""
    return await update_user(user_id=user_id, payload=payload, current_user=current_user, session=session)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    admin: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_async_db),
) -> None:
    """Delete a user account (Strict Admin only). Cannot delete self."""
    deleted = await UserService.delete_user(session=session, user_id=user_id, actor=admin)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None
