import uuid
from datetime import date
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_memory_full_crud_and_sharing() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        rand_id = uuid.uuid4().hex[:8]
        user_a_email = f"user_a_{rand_id}@example.com"
        user_b_email = f"user_b_{rand_id}@example.com"
        password = "SecurePassword123!"

        # 1. Register User A and User B
        reg_a = await ac.post(
            "/api/v1/auth/register",
            json={"email": user_a_email, "password": password, "full_name": "User A"},
        )
        assert reg_a.status_code == 201
        login_a = await ac.post("/api/v1/auth/login", json={"email": user_a_email, "password": password})
        token_a = login_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        reg_b = await ac.post(
            "/api/v1/auth/register",
            json={"email": user_b_email, "password": password, "full_name": "User B"},
        )
        assert reg_b.status_code == 201
        login_b = await ac.post("/api/v1/auth/login", json={"email": user_b_email, "password": password})
        token_b = login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 2. Create Memory 1 (RANDOM with multiple images)
        payload_1 = {
            "title": "Chuyến đi Đà Lạt đầu tiên",
            "content": "Những khoảnh khắc tuyệt đẹp bên nhau tại đồi chè Cầu Đất",
            "image_urls": [
                "https://example.com/photo1.jpg",
                "https://example.com/photo2.jpg",
            ],
            "category": "travel",
            "display_type": "RANDOM",
            "is_shared": True,
        }
        res_create_1 = await ac.post("/api/v1/memories", json=payload_1, headers=headers_a)
        assert res_create_1.status_code == 201
        memory_1 = res_create_1.json()
        assert memory_1["title"] == payload_1["title"]
        assert memory_1["content"] == payload_1["content"]
        assert memory_1["display_type"] == "RANDOM"
        assert len(memory_1["images"]) == 2
        memory_1_id = memory_1["id"]

        # 3. Create Memory 2 (DATE display type)
        payload_2 = {
            "title": "Sinh nhật bất ngờ",
            "content": "Bữa tiệc ấm cúng tại nhà",
            "image_url": "https://example.com/bday.jpg",
            "category": "birthday",
            "display_type": "DATE",
            "target_date": "2026-05-20",
            "is_shared": True,
        }
        res_create_2 = await ac.post("/api/v1/memories", json=payload_2, headers=headers_a)
        assert res_create_2.status_code == 201
        memory_2 = res_create_2.json()
        assert memory_2["display_type"] == "DATE"
        assert memory_2["target_date"] == "2026-05-20"
        memory_2_id = memory_2["id"]

        # 4. List Memories (User A)
        res_list = await ac.get("/api/v1/memories", headers=headers_a)
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert list_data["total"] == 2
        assert len(list_data["items"]) == 2

        # 5. Filter by display_type
        res_filtered = await ac.get("/api/v1/memories?display_type=DATE", headers=headers_a)
        assert res_filtered.status_code == 200
        filtered_data = res_filtered.json()
        assert filtered_data["total"] == 1
        assert filtered_data["items"][0]["id"] == memory_2_id

        # 6. Search by term
        res_search = await ac.get("/api/v1/memories?search=Đà+Lạt", headers=headers_a)
        assert res_search.status_code == 200
        search_data = res_search.json()
        assert search_data["total"] == 1
        assert search_data["items"][0]["id"] == memory_1_id

        # 7. Update Memory 1
        payload_update = {
            "title": "Chuyến đi Đà Lạt đầu tiên (Đã cập nhật)",
            "content": "Bổ sung thêm kỷ niệm quán cà phê hoàng hôn",
            "display_type": "RANDOM",
        }
        res_update = await ac.put(f"/api/v1/memories/{memory_1_id}", json=payload_update, headers=headers_a)
        assert res_update.status_code == 200
        updated_data = res_update.json()
        assert updated_data["title"] == payload_update["title"]
        assert updated_data["content"] == payload_update["content"]

        # 8. User B cannot edit User A's Memory
        res_unauth_edit = await ac.put(
            f"/api/v1/memories/{memory_1_id}",
            json={"title": "Hacked Title"},
            headers=headers_b,
        )
        assert res_unauth_edit.status_code == 404

        # 9. Verify event_router integration with Memory target_date
        res_events = await ac.get(
            "/api/v1/events/occurrences?start_date=2026-05-01&end_date=2026-05-31",
            headers=headers_a,
        )
        assert res_events.status_code == 200
        events_data = res_events.json()
        assert any(e["event_id"] == memory_2_id and e["category"] == "memory" for e in events_data)

        # 10. Delete Memory 1
        res_delete = await ac.delete(f"/api/v1/memories/{memory_1_id}", headers=headers_a)
        assert res_delete.status_code == 204

        # Verify deletion in list
        res_list_after = await ac.get("/api/v1/memories", headers=headers_a)
        assert res_list_after.json()["total"] == 1
