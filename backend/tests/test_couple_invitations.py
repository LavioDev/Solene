import uuid
from datetime import date, timedelta
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_couple_invitations_flow() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        rand_id = uuid.uuid4().hex[:8]
        user_a_email = f"user_inv_a_{rand_id}@example.com"
        user_b_email = f"user_inv_b_{rand_id}@example.com"
        user_c_email = f"user_inv_c_{rand_id}@example.com"
        password = "SecurePassword123!"

        # 1. Register and login User A and User B
        reg_a = await ac.post(
            "/api/v1/auth/register",
            json={"email": user_a_email, "password": password, "full_name": "Nguyen Van A"},
        )
        assert reg_a.status_code == 201
        token_a = (await ac.post("/api/v1/auth/login", json={"email": user_a_email, "password": password})).json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        reg_b = await ac.post(
            "/api/v1/auth/register",
            json={"email": user_b_email, "password": password, "full_name": "Tran Thi B"},
        )
        assert reg_b.status_code == 201
        token_b = (await ac.post("/api/v1/auth/login", json={"email": user_b_email, "password": password})).json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        reg_c = await ac.post(
            "/api/v1/auth/register",
            json={"email": user_c_email, "password": password, "full_name": "Le Van C"},
        )
        assert reg_c.status_code == 201
        token_c = (await ac.post("/api/v1/auth/login", json={"email": user_c_email, "password": password})).json()["access_token"]
        headers_c = {"Authorization": f"Bearer {token_c}"}

        # 2. User A creates an invitation
        res_create_inv = await ac.post("/api/v1/couples/invitations", headers=headers_a)
        assert res_create_inv.status_code == 201
        inv_data = res_create_inv.json()
        assert inv_data["code"].startswith("SL-")
        assert inv_data["status"] == "pending"
        code_1 = inv_data["code"]

        # 3. User A checks current invitation
        res_curr = await ac.get("/api/v1/couples/invitations/current", headers=headers_a)
        assert res_curr.status_code == 200
        assert res_curr.json()["code"] == code_1

        # 4. User A creates a second invitation -> first one is revoked
        res_create_inv_2 = await ac.post("/api/v1/couples/invitations", headers=headers_a)
        assert res_create_inv_2.status_code == 201
        code_2 = res_create_inv_2.json()["code"]
        assert code_2 != code_1

        # 5. Check info for old code_1 -> invalid/expired/used
        res_info_1 = await ac.get(f"/api/v1/couples/invitations/info?code={code_1}")
        assert res_info_1.status_code == 200
        assert res_info_1.json()["is_valid"] is False

        # 6. Check info for new code_2 -> valid
        res_info_2 = await ac.get(f"/api/v1/couples/invitations/info?code={code_2}")
        assert res_info_2.status_code == 200
        info_2 = res_info_2.json()
        assert info_2["is_valid"] is True
        assert info_2["inviter"]["full_name"] == "Nguyen Van A"

        # 7. Check non-existent code
        res_info_fake = await ac.get("/api/v1/couples/invitations/info?code=SL-FAKE999")
        assert res_info_fake.status_code == 200
        assert res_info_fake.json()["is_valid"] is False

        # 8. User A tries to accept own invitation -> Error 400
        res_accept_self = await ac.post(
            "/api/v1/couples/invitations/accept",
            headers=headers_a,
            json={"code": code_2, "start_date": "2024-02-14", "nickname": "Self Pair"},
        )
        assert res_accept_self.status_code == 400

        # 9. User B accepts User A's invitation -> Success 200
        start_date = (date.today() - timedelta(days=50)).isoformat()
        res_accept = await ac.post(
            "/api/v1/couples/invitations/accept",
            headers=headers_b,
            json={"code": code_2, "start_date": start_date, "nickname": "A & B Forever"},
        )
        assert res_accept.status_code == 200
        couple = res_accept.json()
        assert couple["nickname"] == "A & B Forever"
        assert couple["status"] == "active"
        assert couple["user1"]["full_name"] == "Nguyen Van A"
        assert couple["user2"]["full_name"] == "Tran Thi B"

        # 10. Check /me for both User A and User B
        res_me_a = await ac.get("/api/v1/couples/me", headers=headers_a)
        assert res_me_a.status_code == 200
        assert res_me_a.json()["id"] == couple["id"]

        res_me_b = await ac.get("/api/v1/couples/me", headers=headers_b)
        assert res_me_b.status_code == 200
        assert res_me_b.json()["id"] == couple["id"]

        # 11. User C tries to accept code_2 again -> Error (already accepted)
        res_accept_again = await ac.post(
            "/api/v1/couples/invitations/accept",
            headers=headers_c,
            json={"code": code_2, "start_date": start_date},
        )
        assert res_accept_again.status_code == 400

        # 12. User A tries to create another invitation while already in active couple -> Error 409
        res_create_while_paired = await ac.post("/api/v1/couples/invitations", headers=headers_a)
        assert res_create_while_paired.status_code == 409

        # 13. User C creates invitation and revokes it
        res_create_c = await ac.post("/api/v1/couples/invitations", headers=headers_c)
        assert res_create_c.status_code == 201
        res_revoke = await ac.delete("/api/v1/couples/invitations/current", headers=headers_c)
        assert res_revoke.status_code == 204

        res_curr_c = await ac.get("/api/v1/couples/invitations/current", headers=headers_c)
        assert res_curr_c.status_code == 200
        assert res_curr_c.json() is None
