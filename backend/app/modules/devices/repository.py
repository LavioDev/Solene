from datetime import datetime, timezone
from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.repository import BaseRepository
from app.modules.devices.models import Device, TelemetryLog
from app.modules.devices.schemas import DeviceCreate, DeviceUpdate, TelemetryIn


class DeviceRepository(BaseRepository[Device, DeviceCreate, DeviceUpdate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Device, session=session)

    async def get_by_code(self, device_code: str) -> Optional[Device]:
        stmt = select(Device).where(Device.device_code == device_code)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def record_telemetry(self, device_id: uuid.UUID, telemetry_in: TelemetryIn) -> TelemetryLog:
        log = TelemetryLog(
            device_id=device_id,
            cpu_temperature=telemetry_in.cpu_temperature,
            free_heap=telemetry_in.free_heap,
            wifi_rssi=telemetry_in.wifi_rssi,
            battery_voltage=telemetry_in.battery_voltage,
            custom_metrics=telemetry_in.custom_metrics or {},
        )
        self.session.add(log)
        
        # update device last seen
        device = await self.get_by_id(device_id)
        if device:
            device.last_seen_at = datetime.now(timezone.utc)
            device.status = "online"
            
        await self.session.commit()
        await self.session.refresh(log)
        return log

    async def get_latest_telemetry(self, device_id: uuid.UUID, limit: int = 50) -> Sequence[TelemetryLog]:
        stmt = (
            select(TelemetryLog)
            .where(TelemetryLog.device_id == device_id)
            .order_by(TelemetryLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
