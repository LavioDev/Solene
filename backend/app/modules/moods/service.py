from datetime import date, datetime, timedelta, timezone
from typing import Optional, Sequence
import uuid
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.modules.auth.repository import UserRepository
from app.modules.moods.models import UserMood
from app.modules.moods.repository import MoodRepository
from app.modules.moods.schemas import (
    HeatmapDayItem,
    HeatmapResponse,
    MoodCreate,
    MoodUpdate,
    MoodOut,
    TodayMoodResponse,
    MoodStatsResponse,
)


class MoodService:
    @staticmethod
    def get_current_date_in_tz(tz_name: Optional[str] = None) -> date:
        target_tz = "Asia/Ho_Chi_Minh"
        if tz_name:
            try:
                target_tz = str(ZoneInfo(tz_name))
            except (ZoneInfoNotFoundError, Exception):
                target_tz = "Asia/Ho_Chi_Minh"

        try:
            return datetime.now(ZoneInfo(target_tz)).date()
        except Exception:
            return datetime.now(timezone.utc).date()

    @classmethod
    def is_locked(cls, entry_date: date, tz_name: Optional[str] = None) -> bool:
        """A mood entry is locked once the calendar date has passed (after midnight in the user's timezone)."""
        current_today = cls.get_current_date_in_tz(tz_name)
        return entry_date < current_today

    @classmethod
    def _to_mood_out(cls, mood: UserMood, tz_name: Optional[str] = None) -> MoodOut:
        is_locked_val = cls.is_locked(mood.entry_date, tz_name)
        mood_dict = {
            "id": mood.id,
            "user_id": mood.user_id,
            "entry_date": mood.entry_date,
            "mood_score": mood.mood_score,
            "mood_tag": mood.mood_tag,
            "note": mood.note,
            "activities": mood.activities,
            "is_shared": mood.is_shared,
            "is_locked": is_locked_val,
            "created_at": mood.created_at,
            "updated_at": mood.updated_at,
            "user_full_name": mood.user.full_name if mood.user else None,
            "user_avatar_url": mood.user.avatar_url if mood.user else None,
        }
        return MoodOut(**mood_dict)

    @classmethod
    async def upsert_mood(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        payload: MoodCreate,
    ) -> MoodOut:
        """Create or update mood for today (Option A: Upsert / In-place update within the day)."""
        repo = MoodRepository(session)
        today = cls.get_current_date_in_tz(payload.timezone)
        entry_date = payload.entry_date or today

        if entry_date < today:
            raise BadRequestException("Cannot log mood for past dates. Past dates are locked.")
        if entry_date > today:
            raise BadRequestException("Cannot log mood for future dates.")

        existing = await repo.get_by_user_and_date(user_id=user_id, entry_date=entry_date)

        if existing:
            if cls.is_locked(existing.entry_date, payload.timezone):
                raise ForbiddenException("Cannot edit mood from past days. Record is locked.")

            existing.mood_score = payload.mood_score
            existing.mood_tag = payload.mood_tag
            existing.note = payload.note
            existing.activities = payload.activities
            existing.is_shared = payload.is_shared
            existing.updated_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(existing)
            return cls._to_mood_out(existing, payload.timezone)

        # Create new record
        new_mood = UserMood(
            user_id=user_id,
            entry_date=entry_date,
            mood_score=payload.mood_score,
            mood_tag=payload.mood_tag,
            note=payload.note,
            activities=payload.activities,
            is_shared=payload.is_shared,
        )
        session.add(new_mood)
        await session.commit()
        await session.refresh(new_mood)
        return cls._to_mood_out(new_mood, payload.timezone)

    @classmethod
    async def update_mood(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        mood_id: uuid.UUID,
        payload: MoodUpdate,
    ) -> MoodOut:
        """Update an existing mood record within the same day. Locked after midnight."""
        repo = MoodRepository(session)
        mood = await repo.get_by_id(mood_id)

        if not mood or mood.user_id != user_id:
            raise NotFoundException("Mood entry not found.")

        if cls.is_locked(mood.entry_date, payload.timezone):
            raise ForbiddenException("Cannot edit mood from past days. Record is locked after midnight.")

        if payload.mood_score is not None:
            mood.mood_score = payload.mood_score
        if payload.mood_tag is not None:
            mood.mood_tag = payload.mood_tag
        if payload.note is not None:
            mood.note = payload.note
        if payload.activities is not None:
            mood.activities = payload.activities
        if payload.is_shared is not None:
            mood.is_shared = payload.is_shared

        mood.updated_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(mood)
        return cls._to_mood_out(mood, payload.timezone)

    @classmethod
    async def delete_mood(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        mood_id: uuid.UUID,
        timezone: Optional[str] = "Asia/Ho_Chi_Minh",
    ) -> bool:
        """Delete today's mood entry. Locked after midnight."""
        repo = MoodRepository(session)
        mood = await repo.get_by_id(mood_id)

        if not mood or mood.user_id != user_id:
            raise NotFoundException("Mood entry not found.")

        if cls.is_locked(mood.entry_date, timezone):
            raise ForbiddenException("Cannot delete mood from past days. Record is locked after midnight.")

        await repo.delete_mood(mood)
        return True

    @classmethod
    async def get_today_mood(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        timezone: Optional[str] = "Asia/Ho_Chi_Minh",
    ) -> TodayMoodResponse:
        repo = MoodRepository(session)
        today = cls.get_current_date_in_tz(timezone)

        my_mood_obj = await repo.get_by_user_and_date(user_id=user_id, entry_date=today)
        my_mood = cls._to_mood_out(my_mood_obj, timezone) if my_mood_obj else None

        partner_id = await repo.get_partner_id(user_id)
        partner_mood = None
        if partner_id:
            partner_mood_obj = await repo.get_by_user_and_date(user_id=partner_id, entry_date=today)
            if partner_mood_obj and partner_mood_obj.is_shared:
                partner_mood = cls._to_mood_out(partner_mood_obj, timezone)

        return TodayMoodResponse(my_mood=my_mood, partner_mood=partner_mood)

    @classmethod
    async def list_moods(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        *,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        include_partner: bool = True,
        timezone: Optional[str] = "Asia/Ho_Chi_Minh",
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[MoodOut], int]:
        repo = MoodRepository(session)
        items = await repo.list_by_user(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            include_partner=include_partner,
            skip=skip,
            limit=limit,
        )
        total = await repo.count_by_user(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            include_partner=include_partner,
        )
        mood_outs = [cls._to_mood_out(m, timezone) for m in items]
        return mood_outs, total

    @classmethod
    async def get_yearly_heatmap(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        year: Optional[int] = None,
        timezone: Optional[str] = "Asia/Ho_Chi_Minh",
        include_partner: bool = True,
    ) -> HeatmapResponse:
        today = cls.get_current_date_in_tz(timezone)
        target_year = year or today.year

        start_date = date(target_year, 1, 1)
        end_date = date(target_year, 12, 31)

        repo = MoodRepository(session)

        # Get my moods for the year
        my_moods = await repo.list_by_user(
            user_id=user_id,
            from_date=start_date,
            to_date=end_date,
            include_partner=False,
            skip=0,
            limit=400,
        )
        my_moods_map: dict[date, UserMood] = {m.entry_date: m for m in my_moods}

        # Get partner moods if available
        partner_moods_map: dict[date, UserMood] = {}
        partner_id = await repo.get_partner_id(user_id) if include_partner else None
        if partner_id:
            partner_moods = await repo.list_by_user(
                user_id=partner_id,
                from_date=start_date,
                to_date=end_date,
                include_partner=False,
                skip=0,
                limit=400,
            )
            partner_moods_map = {m.entry_date: m for m in partner_moods if m.is_shared}

        # Build day by day grid
        days: list[HeatmapDayItem] = []
        cur = start_date
        total_logged = 0
        score_sum = 0

        # Calculate streaks
        current_streak = 0
        longest_streak = 0
        temp_streak = 0

        while cur <= end_date:
            m = my_moods_map.get(cur)
            pm = partner_moods_map.get(cur)
            is_locked_val = cur < today
            is_today_val = cur == today

            if m:
                total_logged += 1
                score_sum += m.mood_score
                temp_streak += 1
                if temp_streak > longest_streak:
                    longest_streak = temp_streak
            else:
                if cur < today:
                    temp_streak = 0

            days.append(
                HeatmapDayItem(
                    date=cur,
                    mood_id=m.id if m else None,
                    score=m.mood_score if m else None,
                    tag=m.mood_tag if m else None,
                    note=m.note if m else None,
                    is_locked=is_locked_val,
                    is_today=is_today_val,
                    partner_mood_id=pm.id if pm else None,
                    partner_score=pm.mood_score if pm else None,
                    partner_tag=pm.mood_tag if pm else None,
                    partner_note=pm.note if pm else None,
                )
            )
            cur += timedelta(days=1)

        # Calculate active streak backwards from today
        check_date = today
        while True:
            if my_moods_map.get(check_date):
                current_streak += 1
                check_date -= timedelta(days=1)
            elif check_date == today:
                # If today hasn't been logged yet, check starting from yesterday
                check_date -= timedelta(days=1)
                if not my_moods_map.get(check_date):
                    break
            else:
                break

        avg_score = round(score_sum / total_logged, 2) if total_logged > 0 else 0.0

        return HeatmapResponse(
            year=target_year,
            total_logged_days=total_logged,
            current_streak=current_streak,
            longest_streak=longest_streak,
            average_score=avg_score,
            days=days,
        )

    @classmethod
    async def get_stats(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        *,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> MoodStatsResponse:
        repo = MoodRepository(session)
        items = await repo.list_by_user(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            include_partner=False,
            skip=0,
            limit=1000,
        )

        total = len(items)
        score_distribution: dict[int, int] = {i: 0 for i in range(1, 11)}

        if total == 0:
            return MoodStatsResponse(
                total_entries=0,
                average_score=0.0,
                mood_counts={},
                score_distribution=score_distribution,
            )

        avg_score = round(sum(m.mood_score for m in items) / total, 2)
        mood_counts: dict[str, int] = {}

        for m in items:
            mood_counts[m.mood_tag] = mood_counts.get(m.mood_tag, 0) + 1
            if 1 <= m.mood_score <= 10:
                score_distribution[m.mood_score] = score_distribution.get(m.mood_score, 0) + 1

        return MoodStatsResponse(
            total_entries=total,
            average_score=avg_score,
            mood_counts=mood_counts,
            score_distribution=score_distribution,
        )
