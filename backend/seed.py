import asyncio
import sys
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.modules.auth.models import User
from app.modules.events.models import SpecialEvent
from app.modules.notes.models import UserNote


async def seed_data() -> None:
    async with AsyncSessionLocal() as session:
        email = "khanhnd05@gmail.com"
        password = "12345678"

        # 1. Seed or Update User
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if not user:
            user = User(
                email=email,
                hashed_password=hash_password(password),
                full_name="Khanh ND",
                role="admin",
                is_active=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"Seeded user: {email}")
        else:
            user.hashed_password = hash_password(password)
            user.is_active = True
            await session.commit()
            print(f"Updated user password: {email}")

        # 2. Seed Default Special Event Rule (May 22, 2022 - 100 days milestone)
        event_stmt = select(SpecialEvent).where(
            SpecialEvent.user_id == user.id,
            SpecialEvent.anchor_date == date(2022, 5, 22),
            SpecialEvent.recurrence_type == "EVERY_N_DAYS",
            SpecialEvent.interval_value == 100,
        )
        event_res = await session.execute(event_stmt)
        event = event_res.scalars().first()

        if not event:
            event = SpecialEvent(
                user_id=user.id,
                title="Kỷ niệm ngày bên nhau ✨",
                anchor_date=date(2022, 5, 22),
                recurrence_type="EVERY_N_DAYS",
                interval_value=100,
                category="love",
                description="Tự động tính mốc 100, 200, 300... ngày yêu",
            )
            session.add(event)
            await session.commit()
            print(f"Seeded 100-day anniversary rule for user: {email}")
        else:
            print(f"Anniversary rule already exists for user: {email}")

        # 3. Seed Sample Memory Note
        note_stmt = select(UserNote).where(UserNote.user_id == user.id)
        note_res = await session.execute(note_stmt)
        note = note_res.scalars().first()

        if not note:
            sample_note = UserNote(
                user_id=user.id,
                title="Ngày đầu tiên gặp gỡ 💕",
                content="Khoảnh khắc dịu dàng nhất dưới bầu trời đêm. Cảm ơn em đã xuất hiện và cùng anh viết nên những kỷ niệm đẹp.",
                image_url="https://images.unsplash.com/photo-1518199266791-5375a83190b7?q=80&w=1000&auto=format&fit=crop",
                category="memory",
            )
            session.add(sample_note)
            await session.commit()
            print(f"Seeded sample memory note for user: {email}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
