from typing import List, Sequence
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_admin_user, get_current_user
from app.core.database import get_async_db
from app.modules.auth.models import User
from app.modules.auth.schemas import AssignPermissionsPayload, PermissionOut
from app.modules.auth.service import PermissionService, UserService

router = APIRouter(prefix="/permissions", tags=["Permissions Management"])


@router.get("", response_model=List[PermissionOut])
async def list_permissions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> Sequence[PermissionOut]:
    """List all available system permissions."""
    service = PermissionService(session=session)
    perms = await service.list_permissions()
    return [PermissionOut.model_validate(p) for p in perms]


@router.get("/users/{user_id}", response_model=List[PermissionOut])
async def get_user_permissions(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> Sequence[PermissionOut]:
    """Get permissions assigned to a user (Admin or user themselves)."""
    perms = await UserService.get_user_permissions(
        session=session,
        user_id=user_id,
        actor=current_user,
    )
    return [PermissionOut.model_validate(p) for p in perms]


@router.put("/users/{user_id}", response_model=List[PermissionOut])
async def assign_user_permissions(
    user_id: UUID,
    payload: AssignPermissionsPayload,
    admin: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_async_db),
) -> Sequence[PermissionOut]:
    """Assign permissions dynamically to a manager/user (Admin only)."""
    assigned = await UserService.assign_manager_permissions(
        session=session,
        manager_id=user_id,
        permission_ids=payload.permission_ids,
        admin=admin,
    )
    return [PermissionOut.model_validate(p) for p in assigned]
