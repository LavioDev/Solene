import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_auth_flow() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        test_email = "solene_test@example.com"
        test_password = "SecurePassword123!"

        # 1. Register
        reg_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": test_email, "password": test_password, "full_name": "Solene Admin"},
        )
        assert reg_response.status_code in (201, 400)  # 400 if already exists in test rerun

        # 2. Login
        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": test_email, "password": test_password},
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        assert "refresh_token" in login_response.cookies

        access_token = login_data["access_token"]

        # 3. Get /me with in-memory Bearer token
        me_response = await ac.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == test_email

        # 4. Refresh token via HttpOnly cookie
        refresh_response = await ac.post(
            "/api/v1/auth/refresh",
            cookies=login_response.cookies,
        )
        assert refresh_response.status_code == 200
        assert "access_token" in refresh_response.json()
