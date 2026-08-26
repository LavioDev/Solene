import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_permission_and_manager_flow() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        admin_email = f"admin_{uuid.uuid4().hex[:6]}@example.com"
        admin_password = "AdminPassword123!"

        # 1. Register an admin user in database
        from app.core.database import AsyncSessionLocal
        from app.modules.auth.models import User
        from app.core.security import hash_password

        async with AsyncSessionLocal() as session:
            admin_user = User(
                email=admin_email,
                hashed_password=hash_password(admin_password),
                full_name="Super Administrator",
                role="admin",
                is_active=True,
            )
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

        # 2. Login as Admin
        login_admin_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": admin_email, "password": admin_password},
        )
        assert login_admin_res.status_code == 200
        admin_token = login_admin_res.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        assert login_admin_res.json()["user"]["permissions"] == ["*"]

        # 3. Admin lists all available system permissions
        perms_res = await ac.get("/api/v1/permissions", headers=admin_headers)
        assert perms_res.status_code == 200
        all_perms = perms_res.json()
        assert len(all_perms) >= 6
        perm_map = {p["code"]: p["id"] for p in all_perms}
        assert "users:read" in perm_map
        assert "users:create" in perm_map
        assert "users:update" in perm_map
        assert "couples:read" in perm_map
        assert "couples:create" in perm_map
        assert "couples:update" in perm_map

        # 4. Admin creates a Manager user
        manager_email = f"manager_{uuid.uuid4().hex[:6]}@example.com"
        manager_password = "ManagerPassword123!"
        create_mgr_res = await ac.post(
            "/api/v1/users",
            headers=admin_headers,
            json={
                "email": manager_email,
                "password": manager_password,
                "full_name": "Operations Manager",
                "role": "manager",
                "is_active": True,
            },
        )
        assert create_mgr_res.status_code == 201
        manager_id = create_mgr_res.json()["id"]

        # 5. Login as Manager (without permissions yet)
        login_mgr_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": manager_email, "password": manager_password},
        )
        assert login_mgr_res.status_code == 200
        mgr_token = login_mgr_res.json()["access_token"]
        mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

        # 6. Manager without permissions tries to list users -> 403 Forbidden
        denied_list_res = await ac.get("/api/v1/users", headers=mgr_headers)
        assert denied_list_res.status_code == 403

        # 7. Admin assigns 'users:read', 'users:create', 'couples:read', 'couples:create', 'couples:update' to Manager
        grant_perm_ids = [
            perm_map["users:read"],
            perm_map["users:create"],
            perm_map["couples:read"],
            perm_map["couples:create"],
            perm_map["couples:update"],
        ]
        assign_res = await ac.put(
            f"/api/v1/permissions/users/{manager_id}",
            headers=admin_headers,
            json={"permission_ids": grant_perm_ids},
        )
        assert assign_res.status_code == 200
        assert len(assign_res.json()) == 5

        # 8. Manager now lists users -> 200 OK
        ok_list_res = await ac.get("/api/v1/users", headers=mgr_headers)
        assert ok_list_res.status_code == 200

        # 9. Manager creates a regular user -> 201 Created
        end_user_email = f"enduser_{uuid.uuid4().hex[:6]}@example.com"
        create_user_res = await ac.post(
            "/api/v1/users",
            headers=mgr_headers,
            json={
                "email": end_user_email,
                "password": "EndUserPassword123!",
                "full_name": "Standard End User",
                "role": "user",
            },
        )
        assert create_user_res.status_code == 201
        end_user_id = create_user_res.json()["id"]

        # 10. INVARIANT GUARD 1: Manager tries to create an Admin -> 403 Forbidden
        escalation_res = await ac.post(
            "/api/v1/users",
            headers=mgr_headers,
            json={
                "email": f"hacker_admin_{uuid.uuid4().hex[:6]}@example.com",
                "password": "Password123!",
                "full_name": "Fake Admin",
                "role": "admin",
            },
        )
        assert escalation_res.status_code == 403

        # 11. INVARIANT GUARD 2: Manager tries to delete a user -> 403 Forbidden
        delete_attempt_res = await ac.delete(f"/api/v1/users/{end_user_id}", headers=mgr_headers)
        assert delete_attempt_res.status_code == 403

        # 12. Create another user to form a couple
        end_user_2_email = f"enduser2_{uuid.uuid4().hex[:6]}@example.com"
        create_user2_res = await ac.post(
            "/api/v1/users",
            headers=mgr_headers,
            json={
                "email": end_user_2_email,
                "password": "EndUserPassword123!",
                "full_name": "Partner User",
                "role": "user",
            },
        )
        assert create_user2_res.status_code == 201
        end_user_2_id = create_user2_res.json()["id"]

        # 13. Manager creates a couple relationship
        create_couple_res = await ac.post(
            "/api/v1/couples",
            headers=mgr_headers,
            json={
                "user1_id": end_user_id,
                "user2_id": end_user_2_id,
                "start_date": "2024-02-14",
                "status": "active",
            },
        )
        assert create_couple_res.status_code == 201
        couple_id = create_couple_res.json()["id"]

        # 14. INVARIANT GUARD 3: Manager tries to delete a couple -> 403 Forbidden
        delete_couple_attempt = await ac.delete(f"/api/v1/couples/{couple_id}", headers=mgr_headers)
        assert delete_couple_attempt.status_code == 403

        # 15. Admin deletes couple and user -> 204 No Content
        admin_del_couple = await ac.delete(f"/api/v1/couples/{couple_id}", headers=admin_headers)
        assert admin_del_couple.status_code == 204

        admin_del_user = await ac.delete(f"/api/v1/users/{end_user_id}", headers=admin_headers)
        assert admin_del_user.status_code == 204
