import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_users_crud_complete_flow() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        admin_email = f"admin_{uuid.uuid4().hex[:6]}@example.com"
        admin_password = "AdminPassword123!"

        # 1. Register admin user
        reg_admin_res = await ac.post(
            "/api/v1/auth/register",
            json={"email": admin_email, "password": admin_password, "full_name": "System Administrator"},
        )
        assert reg_admin_res.status_code == 201
        admin_token = reg_admin_res.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        admin_id = reg_admin_res.json()["user"]["id"]

        # 2. Admin creates a new standard user
        target_email = f"user_{uuid.uuid4().hex[:6]}@example.com"
        target_password = "UserPassword123!"
        create_res = await ac.post(
            "/api/v1/users",
            headers=admin_headers,
            json={
                "email": target_email,
                "password": target_password,
                "full_name": "Test Standard User",
                "role": "user",
                "is_active": True,
            },
        )
        assert create_res.status_code == 201
        user_data = create_res.json()
        target_user_id = user_data["id"]
        assert user_data["email"] == target_email
        assert user_data["full_name"] == "Test Standard User"
        assert user_data["role"] == "user"
        assert user_data["is_active"] is True
        assert "created_at" in user_data

        # 3. Create user with duplicate email should fail (400)
        dup_res = await ac.post(
            "/api/v1/users",
            headers=admin_headers,
            json={
                "email": target_email,
                "password": "AnotherPassword123!",
                "full_name": "Duplicate User",
            },
        )
        assert dup_res.status_code == 400

        # 4. Admin lists users with search & filters
        list_res = await ac.get(
            "/api/v1/users",
            headers=admin_headers,
            params={"search": target_email, "role": "user"},
        )
        assert list_res.status_code == 200
        data = list_res.json()
        assert "items" in data
        assert "total" in data
        assert data["per_page"] == 15
        users_list = data["items"]
        assert len(users_list) >= 1
        assert any(u["id"] == target_user_id for u in users_list)

        # 5. Get user details by ID
        get_res = await ac.get(f"/api/v1/users/{target_user_id}", headers=admin_headers)
        assert get_res.status_code == 200
        assert get_res.json()["email"] == target_email

        # 6. Admin updates user
        update_res = await ac.patch(
            f"/api/v1/users/{target_user_id}",
            headers=admin_headers,
            json={"full_name": "Updated Standard User", "role": "editor"},
        )
        assert update_res.status_code == 200
        assert update_res.json()["full_name"] == "Updated Standard User"
        assert update_res.json()["role"] == "editor"

        # 7. Authenticate as the newly updated user
        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": target_email, "password": target_password},
        )
        assert login_res.status_code == 200
        user_token = login_res.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # 8. Standard user cannot list all users (403 Forbidden)
        forbidden_list = await ac.get("/api/v1/users", headers=user_headers)
        assert forbidden_list.status_code == 403

        # 9. Standard user cannot create users (403 Forbidden)
        forbidden_create = await ac.post(
            "/api/v1/users",
            headers=user_headers,
            json={
                "email": f"hacker_{uuid.uuid4().hex[:6]}@example.com",
                "password": "Password123!",
            },
        )
        assert forbidden_create.status_code == 403

        # 10. Standard user can view their own profile
        own_profile = await ac.get(f"/api/v1/users/{target_user_id}", headers=user_headers)
        assert own_profile.status_code == 200
        assert own_profile.json()["id"] == target_user_id

        # 11. Standard user cannot elevate their own role
        forbidden_role_change = await ac.patch(
            f"/api/v1/users/{target_user_id}",
            headers=user_headers,
            json={"role": "admin"},
        )
        assert forbidden_role_change.status_code == 403

        # 12. Admin cannot delete their own account
        self_delete = await ac.delete(f"/api/v1/users/{admin_id}", headers=admin_headers)
        assert self_delete.status_code == 400

        # 13. Admin deletes standard user (204 No Content)
        del_res = await ac.delete(f"/api/v1/users/{target_user_id}", headers=admin_headers)
        assert del_res.status_code == 204

        # 14. Verify user is now deleted (404 Not Found)
        not_found_res = await ac.get(f"/api/v1/users/{target_user_id}", headers=admin_headers)
        assert not_found_res.status_code == 404


@pytest.mark.asyncio
async def test_user_password_update_and_login() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        admin_email = f"admin_{uuid.uuid4().hex[:6]}@example.com"
        admin_pass = "AdminPass123!"
        reg = await ac.post("/api/v1/auth/register", json={"email": admin_email, "password": admin_pass, "full_name": "Admin"})
        admin_token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Create user
        user_email = f"member_{uuid.uuid4().hex[:6]}@example.com"
        old_pass = "OldPassword123!"
        new_pass = "NewPassword456!"
        res = await ac.post("/api/v1/users", headers=headers, json={"email": user_email, "password": old_pass, "full_name": "Member"})
        user_id = res.json()["id"]

        # Update password
        put_res = await ac.put(f"/api/v1/users/{user_id}", headers=headers, json={"password": new_pass})
        assert put_res.status_code == 200

        # Login with old password fails (401)
        old_login = await ac.post("/api/v1/auth/login", json={"email": user_email, "password": old_pass})
        assert old_login.status_code == 401

        # Login with new password succeeds (200)
        new_login = await ac.post("/api/v1/auth/login", json={"email": user_email, "password": new_pass})
        assert new_login.status_code == 200


@pytest.mark.asyncio
async def test_users_unauthorized_and_not_found() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        random_id = uuid.uuid4()

        # Unauthenticated calls
        assert (await ac.get("/api/v1/users")).status_code == 401
        assert (await ac.post("/api/v1/users", json={"email": "a@b.com", "password": "123"})).status_code == 401
        assert (await ac.get(f"/api/v1/users/{random_id}")).status_code == 401
        assert (await ac.put(f"/api/v1/users/{random_id}", json={"full_name": "New"})).status_code == 401
        assert (await ac.delete(f"/api/v1/users/{random_id}")).status_code == 401

        # Admin calling non-existent user (404)
        admin_email = f"admin_{uuid.uuid4().hex[:6]}@example.com"
        reg = await ac.post("/api/v1/auth/register", json={"email": admin_email, "password": "Pass", "full_name": "Admin"})
        admin_headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

        assert (await ac.get(f"/api/v1/users/{random_id}", headers=admin_headers)).status_code == 404
        assert (await ac.put(f"/api/v1/users/{random_id}", headers=admin_headers, json={"full_name": "X"})).status_code == 404
        assert (await ac.delete(f"/api/v1/users/{random_id}", headers=admin_headers)).status_code == 404

