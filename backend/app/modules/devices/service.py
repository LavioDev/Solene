from typing import Sequence
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, NotFoundException
from app.modules.devices.models import Device, TelemetryLog
from app.modules.devices.repository import DeviceRepository
from app.modules.devices.schemas import DeviceCreate, DeviceUpdate, TelemetryIn


class DeviceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.device_repo = DeviceRepository(session=session)

    async def list_devices(self, skip: int = 0, limit: int = 100) -> Sequence[Device]:
        return await self.device_repo.get_multi(skip=skip, limit=limit)

    async def get_device(self, device_id: uuid.UUID) -> Device:
        device = await self.device_repo.get_by_id(device_id)
        if not device:
            raise NotFoundException("Device not found.")
        return device

    async def register_device(self, payload: DeviceCreate) -> Device:
        existing = await self.device_repo.get_by_code(payload.device_code)
        if existing:
            raise BadRequestException("Device code is already registered.")
        return await self.device_repo.create(schema_in=payload)

    async def update_device(self, device_id: uuid.UUID, payload: DeviceUpdate) -> Device:
        device = await self.get_device(device_id)
        return await self.device_repo.update(db_obj=device, schema_in=payload)

    async def delete_device(self, device_id: uuid.UUID) -> None:
        device = await self.get_device(device_id)
        await self.device_repo.remove(id=device.id)

    async def ingest_telemetry(self, device_id: uuid.UUID, payload: TelemetryIn) -> TelemetryLog:
        device = await self.get_device(device_id)
        return await self.device_repo.record_telemetry(device_id=device.id, telemetry_in=payload)

    async def get_telemetry_history(self, device_id: uuid.UUID, limit: int = 50) -> Sequence[TelemetryLog]:
        await self.get_device(device_id)
        return await self.device_repo.get_latest_telemetry(device_id=device_id, limit=limit)
