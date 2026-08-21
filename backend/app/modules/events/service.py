import math
from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.events.models import SpecialEvent
from app.modules.events.schemas import SpecialEventCreate, SpecialEventUpdate, EventOccurrenceOut


class EventService:
    @staticmethod
    async def create_event(session: AsyncSession, user_id: UUID, payload: SpecialEventCreate) -> SpecialEvent:
        event = SpecialEvent(
            user_id=user_id,
            title=payload.title,
            anchor_date=payload.anchor_date,
            recurrence_type=payload.recurrence_type,
            interval_value=payload.interval_value,
            category=payload.category,
            description=payload.description,
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event

    @staticmethod
    async def get_user_events(session: AsyncSession, user_id: UUID) -> List[SpecialEvent]:
        stmt = select(SpecialEvent).where(SpecialEvent.user_id == user_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_event(session: AsyncSession, user_id: UUID, event_id: UUID, payload: SpecialEventUpdate) -> Optional[SpecialEvent]:
        stmt = select(SpecialEvent).where(SpecialEvent.id == event_id, SpecialEvent.user_id == user_id)
        result = await session.execute(stmt)
        event = result.scalars().first()
        if not event:
            return None
        if payload.title is not None:
            event.title = payload.title
        if payload.anchor_date is not None:
            event.anchor_date = payload.anchor_date
        if payload.recurrence_type is not None:
            event.recurrence_type = payload.recurrence_type
        if payload.interval_value is not None:
            event.interval_value = payload.interval_value
        if payload.category is not None:
            event.category = payload.category
        if payload.description is not None:
            event.description = payload.description
        await session.commit()
        await session.refresh(event)
        return event

    @staticmethod
    async def delete_event(session: AsyncSession, user_id: UUID, event_id: UUID) -> bool:
        stmt = select(SpecialEvent).where(SpecialEvent.id == event_id, SpecialEvent.user_id == user_id)
        result = await session.execute(stmt)
        event = result.scalars().first()
        if not event:
            return False
        await session.delete(event)
        await session.commit()
        return True

    @staticmethod
    def generate_occurrences_for_window(
        event: SpecialEvent, view_start: date, view_end: date
    ) -> List[EventOccurrenceOut]:
        occurrences: List[EventOccurrenceOut] = []

        if event.recurrence_type == "EVERY_N_DAYS":
            step = max(1, event.interval_value)
            anchor = event.anchor_date

            days_from_anchor_start = (view_start - anchor).days
            days_from_anchor_end = (view_end - anchor).days

            k_min = max(0, math.ceil(days_from_anchor_start / step))
            k_max = math.floor(days_from_anchor_end / step)

            for k in range(k_min, k_max + 1):
                occ_date = anchor + timedelta(days=k * step)
                if view_start <= occ_date <= view_end:
                    milestone_text = "Ngày bắt đầu" if k == 0 else f"Mốc {k * step} ngày"
                    occurrences.append(
                        EventOccurrenceOut(
                            event_id=event.id,
                            title=event.title,
                            date=occ_date,
                            category=event.category,
                            milestone_info=milestone_text,
                        )
                    )

        elif event.recurrence_type == "MONTHLY":
            anchor = event.anchor_date
            current = date(view_start.year, view_start.month, 1)
            end_month_date = date(view_end.year, view_end.month, 1)

            while current <= end_month_date:
                y = current.year
                m = current.month
                try:
                    occ_date = date(y, m, anchor.day)
                except ValueError:
                    next_m = date(y, m + 1, 1) if m < 12 else date(y + 1, 1, 1)
                    occ_date = next_m - timedelta(days=1)

                if view_start <= occ_date <= view_end:
                    months_count = (y - anchor.year) * 12 + (m - anchor.month)
                    milestone_text = f"Mốc {months_count} tháng" if months_count > 0 else "Ngày bắt đầu"
                    occurrences.append(
                        EventOccurrenceOut(
                            event_id=event.id,
                            title=event.title,
                            date=occ_date,
                            category=event.category,
                            milestone_info=milestone_text,
                        )
                    )

                if m == 12:
                    current = date(y + 1, 1, 1)
                else:
                    current = date(y, m + 1, 1)

        elif event.recurrence_type == "YEARLY":
            anchor = event.anchor_date
            for year in range(view_start.year, view_end.year + 1):
                try:
                    occ_date = date(year, anchor.month, anchor.day)
                except ValueError:
                    occ_date = date(year, 2, 28)

                if view_start <= occ_date <= view_end:
                    years_count = year - anchor.year
                    milestone_text = f"Kỷ niệm {years_count} năm" if years_count > 0 else "Ngày bắt đầu"
                    occurrences.append(
                        EventOccurrenceOut(
                            event_id=event.id,
                            title=event.title,
                            date=occ_date,
                            category=event.category,
                            milestone_info=milestone_text,
                        )
                    )

        elif event.recurrence_type == "SINGLE":
            if view_start <= event.anchor_date <= view_end:
                occurrences.append(
                    EventOccurrenceOut(
                        event_id=event.id,
                        title=event.title,
                        date=event.anchor_date,
                        category=event.category,
                        milestone_info="Ghi chú",
                    )
                )

        return occurrences
