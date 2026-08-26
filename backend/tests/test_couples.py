import uuid
from datetime import date, timedelta
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_couple_full_crud_and_security() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        rand_id = uuid.uuid4().hex[:8]
        user_a_email = f"user_a_{rand_id}@example.com"
        user_b_email = f"user_b_{rand_id}@example.com"
        user_c_email = f"user_c_{rand_id}@example.com"
        password = "SecurePassword123!"

        # 1. Register Users A, B, C
        reg_a = await ac.post(
            "/api/v1/auth/register",
            json={"email": user_a_email, "password": password, "full_name": "Nguyen Van A"},
        )
        assert reg_a.status_code == 201
        user_a_data = reg_a.json()
        user_a_id = user_a_data["user"]["id"]

        login_a = await ac.post("/api/v1/auth/login", json={"email": user_a_email, "password": password})
        assert login_a.status_code == 200
        token_a = login_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        reg_b = await ac.post(
            "/api/v1/auth/register",
            json={"email": user_b_email, "password": password, "full_name": "Tran Thi B"},
        )
        assert reg_b.status_code == 201
        user_b_data = reg_b.json()
        user_b_id = user_b_data["user"]["id"]

        login_b = await ac.post("/api/v1/auth/login", json={"email": user_b_email, "password": password})
        assert login_b.status_code == 200
        token_b = login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        reg_c = await ac.post(
            "/api/v1/auth/register",
            json={"email": user_c_email, "password": password, "full_name": "Le Van C"},
        )
        assert reg_c.status_code == 201
        user_c_data = reg_c.json()
        user_c_id = user_c_data["user"]["id"]

        # Demote User C to standard 'user' role to test non-admin security isolation
        await ac.patch(
            f"/api/v1/users/{user_c_id}",
            headers=headers_a,
            json={"role": "user"},
        )

        login_c = await ac.post("/api/v1/auth/login", json={"email": user_c_email, "password": password})
        assert login_c.status_code == 200
        token_c = login_c.json()["access_token"]
        headers_c = {"Authorization": f"Bearer {token_c}"}

        # 2. Validation: Cannot pair with non-existent user
        fake_id = str(uuid.uuid4())
        res_non_exist = await ac.post(
            "/api/v1/couples",
            json={"user2_id": fake_id, "start_date": "2023-01-01"},
            headers=headers_a,
        )
        assert res_non_exist.status_code == 404

        # 3. Validation: Cannot pair with oneself
        res_self = await ac.post(
            "/api/v1/couples",
            json={"user2_id": user_a_id, "start_date": "2023-01-01"},
            headers=headers_a,
        )
        assert res_self.status_code == 400

        # 4. Check /me before creating couple -> 404
        me_before = await ac.get("/api/v1/couples/me", headers=headers_a)
        assert me_before.status_code == 404

        # 5. Create couple (User A with User B)
        start_date = date.today() - timedelta(days=100)
        start_date_str = start_date.isoformat()
        couple_payload = {
            "user2_id": user_b_id,
            "start_date": start_date_str,
            "nickname": "A & B Happy Forever",
            "cover_url": "https://example.com/cover.jpg",
            "status": "active",
        }
        res_create = await ac.post("/api/v1/couples", json=couple_payload, headers=headers_a)
        assert res_create.status_code == 201
        couple = res_create.json()
        assert couple["user1_id"] == user_a_id
        assert couple["user2_id"] == user_b_id
        assert couple["start_date"] == start_date_str
        assert couple["nickname"] == "A & B Happy Forever"
        assert couple["days_together"] >= 100
        assert couple["user1"]["email"] == user_a_email
        assert couple["user2"]["email"] == user_b_email
        couple_id = couple["id"]

        # 6. User A gets /me
        me_a = await ac.get("/api/v1/couples/me", headers=headers_a)
        assert me_a.status_code == 200
        assert me_a.json()["id"] == couple_id
        assert me_a.json()["nickname"] == "A & B Happy Forever"

        # 7. User B gets /me (User B is partner in the couple)
        me_b = await ac.get("/api/v1/couples/me", headers=headers_b)
        assert me_b.status_code == 200
        assert me_b.json()["id"] == couple_id

        # 8. User C gets /me -> 404
        me_c = await ac.get("/api/v1/couples/me", headers=headers_c)
        assert me_c.status_code == 404

        # 9. Get specific couple by ID
        get_a = await ac.get(f"/api/v1/couples/{couple_id}", headers=headers_a)
        assert get_a.status_code == 200
        assert get_a.json()["id"] == couple_id

        # Security: User C (role 'user') cannot access couple endpoints (403 Forbidden)
        get_c = await ac.get(f"/api/v1/couples/{couple_id}", headers=headers_c)
        assert get_c.status_code == 403

        # 10. List couples
        list_a = await ac.get("/api/v1/couples", headers=headers_a)
        assert list_a.status_code == 200
        assert "items" in list_a.json()
        assert len(list_a.json()["items"]) >= 1

        list_c = await ac.get("/api/v1/couples", headers=headers_c)
        assert list_c.status_code == 403

        # Security: User C cannot create couples
        create_c = await ac.post(
            "/api/v1/couples",
            json={"user2_id": user_a_id, "start_date": "2023-01-01"},
            headers=headers_c,
        )
        assert create_c.status_code == 403

        # 11. Update Couple (PUT)
        update_payload = {
            "nickname": "A & B Forever and Always",
            "status": "active",
            "cover_url": "https://example.com/new_cover.jpg",
        }
        # Security: User C cannot update
        put_c = await ac.put(f"/api/v1/couples/{couple_id}", json=update_payload, headers=headers_c)
        assert put_c.status_code == 403

        # Admin (User A) can update
        put_a = await ac.put(f"/api/v1/couples/{couple_id}", json=update_payload, headers=headers_a)
        assert put_a.status_code == 200
        assert put_a.json()["nickname"] == "A & B Forever and Always"
        assert put_a.json()["cover_url"] == "https://example.com/new_cover.jpg"

        # 12. Partial Update (PATCH)
        new_start_date = date.today() - timedelta(days=200)
        patch_res = await ac.patch(
            f"/api/v1/couples/{couple_id}",
            json={"start_date": new_start_date.isoformat()},
            headers=headers_a,
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["days_together"] >= 200

        # 13. Delete Couple
        # Security: User C cannot delete
        del_c = await ac.delete(f"/api/v1/couples/{couple_id}", headers=headers_c)
        assert del_c.status_code == 403

        # User A (Admin) deletes
        del_a = await ac.delete(f"/api/v1/couples/{couple_id}", headers=headers_a)
        assert del_a.status_code == 204

        # 14. Verify deletion
        get_deleted = await ac.get(f"/api/v1/couples/{couple_id}", headers=headers_a)
        assert get_deleted.status_code == 404

        me_after = await ac.get("/api/v1/couples/me", headers=headers_a)
        assert me_after.status_code == 404
