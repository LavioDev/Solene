from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin_user, get_current_user, require_permission
from app.core.database import get_async_db
from app.core.exceptions import ForbiddenException
from app.core.pagination import PaginatedResponse, paginate_response
from app.modules.auth.models import User
from app.modules.couples.schemas import CoupleCreate, CoupleOut, CoupleUpdate
from app.modules.couples.service import CoupleService

router = APIRouter(prefix="/couples", tags=["Couples & Relationships"])


@router.post("", response_model=CoupleOut, status_code=status.HTTP_201_CREATED)
async def create_couple(
    payload: CoupleCreate,
    current_user: User = Depends(require_permission("couples:create")),
    session: AsyncSession = Depends(get_async_db),
) -> CoupleOut:
    """Create a new couple relationship profile (Admin or Manager with 'couples:create')."""
    couple = await CoupleService.create_couple(
        session=session,
        current_user_id=current_user.id,
        payload=payload,
        actor=current_user,
    )
    return couple


@router.get("/me", response_model=CoupleOut)
async def get_my_couple(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by couple status"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> CoupleOut:
    """Get the active couple relationship profile for the authenticated user."""
    couple = await CoupleService.get_my_couple(
        session=session,
        user_id=current_user.id,
        status=status_filter,
    )
    if not couple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No couple profile found for the current user.",
        )
    return couple


@router.get("", response_model=PaginatedResponse[CoupleOut])
async def list_couples(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g. active, paused)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(15, ge=1, le=100, description="Items per page (default: 15)"),
    skip: Optional[int] = Query(None, ge=0, description="Offset for pagination (backward compatibility)"),
    limit: Optional[int] = Query(None, ge=1, le=500, description="Limit for pagination (backward compatibility)"),
    current_user: User = Depends(require_permission("couples:read")),
    session: AsyncSession = Depends(get_async_db),
) -> PaginatedResponse[CoupleOut]:
    """List couples with pagination (Admin or Manager with 'couples:read')."""
    actual_page = page
    actual_per_page = limit if limit is not None else per_page
    if skip is not None and limit is not None:
        actual_page = (skip // limit) + 1

    couples, total = await CoupleService.list_couples(
        session=session,
        user_id=current_user.id,
        actor=current_user,
        status=status_filter,
        page=actual_page,
        per_page=actual_per_page,
        skip=skip,
        limit=limit,
    )
    return paginate_response(
        items=[CoupleOut.model_validate(c) for c in couples],
        total=total,
        page=actual_page,
        per_page=actual_per_page,
    )


@router.get("/{couple_id}", response_model=CoupleOut)
async def get_couple(
    couple_id: UUID,
    current_user: User = Depends(require_permission("couples:read")),
    session: AsyncSession = Depends(get_async_db),
) -> CoupleOut:
    """Get details of a specific couple by ID (Admin or Manager with 'couples:read')."""
    couple = await CoupleService.get_couple(
        session=session,
        couple_id=couple_id,
        user_id=current_user.id,
        actor=current_user,
    )
    if not couple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couple profile not found.",
        )
    return couple


@router.put("/{couple_id}", response_model=CoupleOut)
async def update_couple(
    couple_id: UUID,
    payload: CoupleUpdate,
    current_user: User = Depends(require_permission("couples:update")),
    session: AsyncSession = Depends(get_async_db),
) -> CoupleOut:
    """Update couple relationship details (Admin or Manager with 'couples:update')."""
    updated = await CoupleService.update_couple(
        session=session,
        couple_id=couple_id,
        user_id=current_user.id,
        payload=payload,
        actor=current_user,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couple profile not found.",
        )
    return updated


@router.patch("/{couple_id}", response_model=CoupleOut)
async def patch_couple(
    couple_id: UUID,
    payload: CoupleUpdate,
    current_user: User = Depends(require_permission("couples:update")),
    session: AsyncSession = Depends(get_async_db),
) -> CoupleOut:
    """Partially update couple relationship details (Admin or Manager with 'couples:update')."""
    return await update_couple(couple_id=couple_id, payload=payload, current_user=current_user, session=session)


@router.delete("/{couple_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_couple(
    couple_id: UUID,
    admin: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_async_db),
) -> None:
    """Delete a couple relationship profile (Strict Admin only)."""
    deleted = await CoupleService.delete_couple(
        session=session,
        couple_id=couple_id,
        user_id=admin.id,
        actor=admin,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couple profile not found.",
        )
    return None
