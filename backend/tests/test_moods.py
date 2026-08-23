import uuid
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.database import AsyncSessionLocal
from app.modules.moods.models import UserMood
from app.modules.couples.models import Couple


@pytest.mark.asyncio
async def test_mood_lifecycle_and_midnight_locking() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        rand_id = uuid.uuid4().hex[:8]
        user_a_email = f"user_mood_a_{rand_id}@example.com"
        user_b_email = f"user_mood_b_{rand_id}@example.com"
        password = "SecurePassword123!"

        # 1. Register and Login User A
        await ac.post(
            "/api/v1/auth/register",
            json={"email": user_a_email, "password": password, "full_name": "User Mood A"},
        )
        login_a = await ac.post("/api/v1/auth/login", json={"email": user_a_email, "password": password})
        assert login_a.status_code == 200
        token_a = login_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 2. Register and Login User B
        await ac.post(
            "/api/v1/auth/register",
            json={"email": user_b_email, "password": password, "full_name": "User Mood B"},
        )
        login_b = await ac.post("/api/v1/auth/login", json={"email": user_b_email, "password": password})
        assert login_b.status_code == 200
        token_b = login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 3. Validation: Cannot log mood for past date directly
        past_date = (date.today() - timedelta(days=2)).isoformat()
        res_past = await ac.post(
            "/api/v1/moods",
            json={
                "mood_score": 4,
                "mood_tag": "happy",
                "entry_date": past_date,
            },
            headers=headers_a,
        )
        assert res_past.status_code == 400

        # 4. Validation: Cannot log mood for future date
        future_date = (date.today() + timedelta(days=2)).isoformat()
        res_future = await ac.post(
            "/api/v1/moods",
            json={
                "mood_score": 5,
                "mood_tag": "excited",
                "entry_date": future_date,
            },
            headers=headers_a,
        )
        assert res_future.status_code == 400

        # 5. Log mood for TODAY (User A) - First entry of the day
        log_res_1 = await ac.post(
            "/api/v1/moods",
            json={
                "mood_score": 3,
                "mood_tag": "neutral",
                "note": "Morning start",
                "activities": "work,coffee",
                "is_shared": True,
            },
            headers=headers_a,
        )
        assert log_res_1.status_code == 201
        mood_1 = log_res_1.json()
        assert mood_1["mood_score"] == 3
        assert mood_1["mood_tag"] == "neutral"
        assert mood_1["is_locked"] is False
        mood_id = mood_1["id"]

        # 6. Option A Verification: Upsert in the same day (Updating mood in daytime)
        log_res_2 = await ac.post(
            "/api/v1/moods",
            json={
                "mood_score": 5,
                "mood_tag": "happy",
                "note": "Had a great meeting and finished project!",
                "activities": "work,celebration",
                "is_shared": True,
            },
            headers=headers_a,
        )
        assert log_res_2.status_code == 201
        mood_2 = log_res_2.json()
        assert mood_2["id"] == mood_id  # Same record updated in place!
        assert mood_2["mood_score"] == 5
        assert mood_2["mood_tag"] == "happy"
        assert mood_2["note"] == "Had a great meeting and finished project!"

        # 7. Update via PUT /api/v1/moods/{id} on the current day
        put_res = await ac.put(
            f"/api/v1/moods/{mood_id}",
            json={
                "mood_score": 4,
                "mood_tag": "calm",
                "note": "Relaxing evening at home",
            },
            headers=headers_a,
        )
        assert put_res.status_code == 200
        assert put_res.json()["mood_score"] == 4
        assert put_res.json()["mood_tag"] == "calm"

        # 8. Check Today Mood Endpoint
        today_res = await ac.get("/api/v1/moods/today", headers=headers_a)
        assert today_res.status_code == 200
        today_data = today_res.json()
        assert today_data["my_mood"] is not None
        assert today_data["my_mood"]["id"] == mood_id
        assert today_data["partner_mood"] is None

        # 9. Test Couple Shared Mood:
        # Create an active couple between User A and User B
        async with AsyncSessionLocal() as db_session:
            user_a_db = (await ac.get("/api/v1/auth/me", headers=headers_a)).json()
            user_b_db = (await ac.get("/api/v1/auth/me", headers=headers_b)).json()
            couple = Couple(
                user1_id=uuid.UUID(user_a_db["id"]),
                user2_id=uuid.UUID(user_b_db["id"]),
                start_date=date.today(),
                status="active",
            )
            db_session.add(couple)
            await db_session.commit()

        # User B logs mood
        res_b_log = await ac.post(
            "/api/v1/moods",
            json={
                "mood_score": 5,
                "mood_tag": "excited",
                "note": "Feeling awesome!",
                "is_shared": True,
            },
            headers=headers_b,
        )
        assert res_b_log.status_code == 201

        # User A checks today mood again -> Should see partner's mood
        today_res_after = await ac.get("/api/v1/moods/today", headers=headers_a)
        assert today_res_after.status_code == 200
        assert today_res_after.json()["partner_mood"] is not None
        assert today_res_after.json()["partner_mood"]["mood_tag"] == "excited"

        # 10. MIDNIGHT LOCKING VERIFICATION:
        # Manually create a historical mood from 3 days ago in the database
        past_entry_date = date.today() - timedelta(days=3)
        past_mood_id = uuid.uuid4()
        async with AsyncSessionLocal() as db_session:
            old_mood = UserMood(
                id=past_mood_id,
                user_id=uuid.UUID(user_a_db["id"]),
                entry_date=past_entry_date,
                mood_score=2,
                mood_tag="tired",
                note="Hard day 3 days ago",
                is_shared=True,
            )
            db_session.add(old_mood)
            await db_session.commit()

        # Check list endpoint -> historical entry must have is_locked = True
        list_res = await ac.get("/api/v1/moods", headers=headers_a)
        assert list_res.status_code == 200
        moods_list = list_res.json()
        past_item = next((m for m in moods_list if m["id"] == str(past_mood_id)), None)
        assert past_item is not None
        assert past_item["is_locked"] is True

        # Attempt to UPDATE past mood -> MUST return 403 Forbidden (Locked after midnight)
        put_past_res = await ac.put(
            f"/api/v1/moods/{past_mood_id}",
            json={"mood_score": 5, "mood_tag": "happy"},
            headers=headers_a,
        )
        assert put_past_res.status_code == 403
        assert "locked" in put_past_res.json()["detail"].lower()

        # Attempt to DELETE past mood -> MUST return 403 Forbidden (Locked after midnight)
        del_past_res = await ac.delete(f"/api/v1/moods/{past_mood_id}", headers=headers_a)
        assert del_past_res.status_code == 403
        assert "locked" in del_past_res.json()["detail"].lower()

        # 11. Delete TODAY's mood (Current day allowed)
        del_today_res = await ac.delete(f"/api/v1/moods/{mood_id}", headers=headers_a)
        assert del_today_res.status_code == 204

        # Verify today's mood is now gone
        today_res_cleared = await ac.get("/api/v1/moods/today", headers=headers_a)
        assert today_res_cleared.json()["my_mood"] is None

        # 12. Stats verification
        stats_res = await ac.get("/api/v1/moods/stats", headers=headers_a)
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["total_entries"] >= 1
        assert "tired" in stats["mood_counts"]

        # 13. Rank 10 & Note Verification:
        # Invalid score > 10
        res_invalid_score = await ac.post(
            "/api/v1/moods",
            json={"mood_score": 11, "mood_tag": "awesome"},
            headers=headers_a,
        )
        assert res_invalid_score.status_code == 422

        # Valid score = 10 with detailed note
        res_score_10 = await ac.post(
            "/api/v1/moods",
            json={
                "mood_score": 10,
                "mood_tag": "awesome",
                "note": "A truly magical and wonderful day!",
                "activities": "dating,celebration,travel",
                "is_shared": True,
            },
            headers=headers_a,
        )
        assert res_score_10.status_code == 201
        data_10 = res_score_10.json()
        assert data_10["mood_score"] == 10
        assert data_10["mood_tag"] == "awesome"
        assert data_10["note"] == "A truly magical and wonderful day!"

        # 14. Heatmap 365-day grid verification
        heatmap_res = await ac.get("/api/v1/moods/heatmap?include_partner=true", headers=headers_a)
        assert heatmap_res.status_code == 200
        heatmap_data = heatmap_res.json()
        assert heatmap_data["total_logged_days"] >= 2
        assert heatmap_data["current_streak"] >= 1
        assert len(heatmap_data["days"]) >= 365
        
        # Check today's cell in heatmap
        today_cell = next((d for d in heatmap_data["days"] if d["is_today"]), None)
        assert today_cell is not None
        assert today_cell["score"] == 10
        assert today_cell["tag"] == "awesome"
        assert today_cell["note"] == "A truly magical and wonderful day!"
        assert today_cell["partner_score"] == 5
