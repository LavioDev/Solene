"""
Solène Platform - Database Seed Script
Seeds the primary administrator accounts (khanhnd05@gmail.com & chud6222@gmail.com) and cleans up non-target accounts.
"""
import asyncio
import sys
from pathlib import Path

# Set up PYTHONPATH for script execution
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.modules.auth.models import User


async def seed_data() -> None:
    """Seed primary admin accounts and clean up non-target user accounts."""
    target_users = [
        {"email": "khanhnd05@gmail.com", "full_name": "Khanh ND", "role": "admin"},
        {"email": "chud6222@gmail.com", "full_name": "Chu D", "role": "admin"},
    ]
    target_password = "12345678"
    target_emails = [u["email"] for u in target_users]

    async with AsyncSessionLocal() as session:
        # 1. Clean up any non-target user accounts
        del_stmt = delete(User).where(User.email.notin_(target_emails))
        del_res = await session.execute(del_stmt)
        deleted_count = del_res.rowcount
        if deleted_count > 0:
            print(f"[SEED] Cleaned up {deleted_count} non-target user account(s).")

        # 2. Seed or Update Target Admin Users
        for user_data in target_users:
            email = user_data["email"]
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if not user:
                user = User(
                    email=email,
                    hashed_password=hash_password(target_password),
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    is_active=True,
                )
                session.add(user)
                await session.commit()
                print(f"[SEED] Created admin account: {email}")
            else:
                user.hashed_password = hash_password(target_password)
                user.full_name = user_data["full_name"]
                user.role = user_data["role"]
                user.is_active = True
                await session.commit()
                print(f"[SEED] Updated admin account: {email}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
