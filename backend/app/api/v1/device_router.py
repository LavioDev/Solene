from typing import List
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.database import get_async_db
from app.modules.auth.models import User
from app.modules.devices.schemas import (
    DeviceCreate,
    DeviceOut,
    DeviceUpdate,
    TelemetryIn,
    TelemetryOut,
)
from app.modules.devices.service import DeviceService

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("", response_model=List[DeviceOut])
async def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> List[DeviceOut]:
    service = DeviceService(session=session)
    devices = await service.list_devices(skip=skip, limit=limit)
    return [DeviceOut.model_validate(d) for d in devices]


@router.post("", response_model=DeviceOut, status_code=status.HTTP_201_CREATED)
async def create_device(
    payload: DeviceCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> DeviceOut:
    service = DeviceService(session=session)
    device = await service.register_device(payload)
    return DeviceOut.model_validate(device)


@router.get("/{device_id}", response_model=DeviceOut)
async def get_device(
    device_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> DeviceOut:
    service = DeviceService(session=session)
    device = await service.get_device(device_id)
    return DeviceOut.model_validate(device)


@router.patch("/{device_id}", response_model=DeviceOut)
async def update_device(
    device_id: uuid.UUID,
    payload: DeviceUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> DeviceOut:
    service = DeviceService(session=session)
    device = await service.update_device(device_id, payload)
    return DeviceOut.model_validate(device)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> None:
    service = DeviceService(session=session)
    await service.delete_device(device_id)


@router.post("/{device_id}/telemetry", response_model=TelemetryOut, status_code=status.HTTP_201_CREATED)
async def record_telemetry(
    device_id: uuid.UUID,
    payload: TelemetryIn,
    session: AsyncSession = Depends(get_async_db),
) -> TelemetryOut:
    service = DeviceService(session=session)
    log = await service.ingest_telemetry(device_id, payload)
    return TelemetryOut.model_validate(log)


@router.get("/{device_id}/telemetry", response_model=List[TelemetryOut])
async def get_telemetry_history(
    device_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> List[TelemetryOut]:
    service = DeviceService(session=session)
    logs = await service.get_telemetry_history(device_id=device_id, limit=limit)
    return [TelemetryOut.model_validate(log) for log in logs]
