from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_async_db
from app.modules.auth.models import User
from app.modules.couples.schemas import CoupleCreate, CoupleOut, CoupleUpdate
from app.modules.couples.service import CoupleService

router = APIRouter(prefix="/couples", tags=["Couples & Relationships"])


@router.post("", response_model=CoupleOut, status_code=status.HTTP_201_CREATED)
async def create_couple(
    payload: CoupleCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> CoupleOut:
    """Create a new couple relationship profile."""
    is_admin = current_user.role == "admin"
    couple = await CoupleService.create_couple(
        session=session,
        current_user_id=current_user.id,
        payload=payload,
        is_admin=is_admin,
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


@router.get("", response_model=List[CoupleOut])
async def list_couples(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g. active, paused)"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Limit for pagination"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> List[CoupleOut]:
    """List couples (all if admin, or belonging to the current user)."""
    is_admin = current_user.role == "admin"
    couples = await CoupleService.list_couples(
        session=session,
        user_id=current_user.id,
        is_admin=is_admin,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return list(couples)


@router.get("/{couple_id}", response_model=CoupleOut)
async def get_couple(
    couple_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> CoupleOut:
    """Get details of a specific couple by ID."""
    is_admin = current_user.role == "admin"
    couple = await CoupleService.get_couple(
        session=session,
        couple_id=couple_id,
        user_id=current_user.id,
        is_admin=is_admin,
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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> CoupleOut:
    """Update couple relationship details."""
    is_admin = current_user.role == "admin"
    updated = await CoupleService.update_couple(
        session=session,
        couple_id=couple_id,
        user_id=current_user.id,
        payload=payload,
        is_admin=is_admin,
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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> CoupleOut:
    """Partially update couple relationship details."""
    is_admin = current_user.role == "admin"
    updated = await CoupleService.update_couple(
        session=session,
        couple_id=couple_id,
        user_id=current_user.id,
        payload=payload,
        is_admin=is_admin,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couple profile not found.",
        )
    return updated


@router.delete("/{couple_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_couple(
    couple_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> None:
    """Delete a couple relationship profile."""
    is_admin = current_user.role == "admin"
    deleted = await CoupleService.delete_couple(
        session=session,
        couple_id=couple_id,
        user_id=current_user.id,
        is_admin=is_admin,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couple profile not found.",
        )
    return None
