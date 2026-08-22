import uuid
from datetime import datetime, timezone, timedelta
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_task_full_crud_and_isolation() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        rand_id = uuid.uuid4().hex[:8]
        user_a_email = f"user_a_{rand_id}@example.com"
        user_b_email = f"user_b_{rand_id}@example.com"
        password = "SecurePassword123!"


        # Register User A
        await ac.post(
            "/api/v1/auth/register",
            json={"email": user_a_email, "password": password, "full_name": "User A"},
        )
        login_a = await ac.post("/api/v1/auth/login", json={"email": user_a_email, "password": password})
        assert login_a.status_code == 200
        token_a = login_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Register User B
        await ac.post(
            "/api/v1/auth/register",
            json={"email": user_b_email, "password": password, "full_name": "User B"},
        )
        login_b = await ac.post("/api/v1/auth/login", json={"email": user_b_email, "password": password})
        assert login_b.status_code == 200
        token_b = login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 1. Validation error: end_time before start_time
        now = datetime.now(timezone.utc)
        invalid_payload = {
            "title": "Invalid Task",
            "start_time": (now + timedelta(hours=2)).isoformat(),
            "end_time": (now + timedelta(hours=1)).isoformat(),
        }
        res_invalid = await ac.post("/api/v1/tasks", json=invalid_payload, headers=headers_a)
        assert res_invalid.status_code == 422

        # 2. Create Task 1 (User A)
        start_time_1 = now + timedelta(hours=1)
        end_time_1 = now + timedelta(hours=3)
        task_1_payload = {
            "title": "Hoàn thành báo cáo quý",
            "content": "Tổng hợp số liệu từ các phòng ban và xuất file PDF",
            "is_completed": False,
            "start_time": start_time_1.isoformat(),
            "end_time": end_time_1.isoformat(),
            "priority": "high",
        }
        create_res = await ac.post("/api/v1/tasks", json=task_1_payload, headers=headers_a)
        assert create_res.status_code == 201
        task_1 = create_res.json()
        assert task_1["title"] == "Hoàn thành báo cáo quý"
        assert task_1["content"] == "Tổng hợp số liệu từ các phòng ban và xuất file PDF"
        assert task_1["is_completed"] is False
        assert task_1["priority"] == "high"
        task_1_id = task_1["id"]

        # Create Task 2 (User A - already completed)
        task_2_payload = {
            "title": "Họp giao ban buổi sáng",
            "content": "Thảo luận tiến độ dự án Solène",
            "is_completed": True,
            "start_time": (now - timedelta(hours=2)).isoformat(),
            "end_time": (now - timedelta(hours=1)).isoformat(),
            "priority": "medium",
        }
        create_res_2 = await ac.post("/api/v1/tasks", json=task_2_payload, headers=headers_a)
        assert create_res_2.status_code == 201
        task_2 = create_res_2.json()
        task_2_id = task_2["id"]

        # 3. List tasks User A (all, filtered)
        list_all = await ac.get("/api/v1/tasks", headers=headers_a)
        assert list_all.status_code == 200
        tasks = list_all.json()
        assert len(tasks) >= 2

        # Filter is_completed=True
        list_completed = await ac.get("/api/v1/tasks?is_completed=true", headers=headers_a)
        assert list_completed.status_code == 200
        completed_tasks = list_completed.json()
        assert all(t["is_completed"] is True for t in completed_tasks)
        assert any(t["id"] == task_2_id for t in completed_tasks)

        # Filter is_completed=False
        list_uncompleted = await ac.get("/api/v1/tasks?is_completed=false", headers=headers_a)
        assert list_uncompleted.status_code == 200
        uncompleted_tasks = list_uncompleted.json()
        assert all(t["is_completed"] is False for t in uncompleted_tasks)
        assert any(t["id"] == task_1_id for t in uncompleted_tasks)

        # 4. Get specific task by ID
        get_res = await ac.get(f"/api/v1/tasks/{task_1_id}", headers=headers_a)
        assert get_res.status_code == 200
        assert get_res.json()["id"] == task_1_id

        # 5. Update Task 1 (PUT)
        updated_payload = {
            "title": "Hoàn thành báo cáo quý (Đã chỉnh sửa)",
            "content": "Bổ sung biểu đồ thống kê",
            "is_completed": False,
            "priority": "urgent",
        }
        put_res = await ac.put(f"/api/v1/tasks/{task_1_id}", json=updated_payload, headers=headers_a)
        assert put_res.status_code == 200
        assert put_res.json()["title"] == "Hoàn thành báo cáo quý (Đã chỉnh sửa)"
        assert put_res.json()["priority"] == "urgent"

        # 6. Toggle status
        toggle_res = await ac.patch(f"/api/v1/tasks/{task_1_id}/toggle", headers=headers_a)
        assert toggle_res.status_code == 200
        assert toggle_res.json()["is_completed"] is True

        toggle_res_back = await ac.patch(
            f"/api/v1/tasks/{task_1_id}/toggle",
            json={"is_completed": False},
            headers=headers_a,
        )
        assert toggle_res_back.status_code == 200
        assert toggle_res_back.json()["is_completed"] is False

        # 7. Security Isolation: User B cannot access or modify User A's task
        res_b_get = await ac.get(f"/api/v1/tasks/{task_1_id}", headers=headers_b)
        assert res_b_get.status_code == 404

        res_b_put = await ac.put(
            f"/api/v1/tasks/{task_1_id}",
            json={"title": "Hacked Title"},
            headers=headers_b,
        )
        assert res_b_put.status_code == 404

        res_b_delete = await ac.delete(f"/api/v1/tasks/{task_1_id}", headers=headers_b)
        assert res_b_delete.status_code == 404

        # 8. Filter by date range and pagination
        list_range = await ac.get(
            "/api/v1/tasks",
            params={
                "start_from": (now - timedelta(hours=3)).isoformat(),
                "end_to": (now - timedelta(minutes=30)).isoformat(),
            },
            headers=headers_a,
        )
        assert list_range.status_code == 200
        range_tasks = list_range.json()
        assert len(range_tasks) == 1
        assert range_tasks[0]["id"] == task_2_id

        # Pagination test
        list_paged = await ac.get("/api/v1/tasks", params={"skip": 0, "limit": 1}, headers=headers_a)
        assert list_paged.status_code == 200
        assert len(list_paged.json()) == 1


        # 9. Delete Task 1 (User A)
        delete_res = await ac.delete(f"/api/v1/tasks/{task_1_id}", headers=headers_a)
        assert delete_res.status_code == 204

        # Verify deletion
        get_deleted_res = await ac.get(f"/api/v1/tasks/{task_1_id}", headers=headers_a)
        assert get_deleted_res.status_code == 404

