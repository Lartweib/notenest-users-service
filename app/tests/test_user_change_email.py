import pytest
from uuid import uuid4
from bson import ObjectId
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.mongo import user_collection
from unittest.mock import AsyncMock

transport = ASGITransport(app=app)

async def inserted_user_in_db(username="testuser", full_name="string", email="string@example.com"):
    verification_uuid = str(uuid4())
    user_data = {
        "_id": ObjectId(),
        "username": username,
        "full_name": full_name,
        "email": email,
        "password": "$2b$12$OJf.BwMy5mDrvTKRh/HxA.QOYg3DSPrWCqRmArNmYDiwZga0PaYQ.",  # bcrypt de "string"
        "is_verified": True,
    }
    inserted_user = await user_collection.insert_one(user_data)
    inserted_user_id = inserted_user.inserted_id
    return inserted_user_id

@pytest.mark.asyncio
async def test_change_email_successful(mocker):
    user_id = await inserted_user_in_db()
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/login",
            json={"email": "string@example.com", "password": "string"},
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
            },
        )
        token_access = response.json()["access_token"]

    mocker.patch("app.routers.user_router.send_verification_email", new_callable=AsyncMock)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            "/user/change-email",
            json={"email": "new_email@example.com"},
            headers={"Authorization": f"Bearer {token_access}", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )

        assert response.status_code == 200, "El status code no es 200"
        assert response.json()["message"] == "Email modificado exitosamente, por favor verificalo"

        user = await user_collection.find_one({"email": "new_email@example.com"})
        assert user is not None, "El email no se actualizó en la base de datos"
        assert user["username"] == "testuser", "El username no coincide tras el cambio de email"


@pytest.mark.asyncio
async def test_change_email_invalid_token(mocker):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            "/user/change-email",
            json={"email": "new_email@example.com"},
            headers={"Authorization": "Bearer invalid_token", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )

        assert response.status_code == 400, "El status code no es 400"
        assert response.json()["detail"] == "Token inválido"


@pytest.mark.asyncio
async def test_change_email_expired_token(mocker):
    token_expired = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmdAZXhhbXBsZS5jb20iLCJ1c2VybmFtZSI6InRlc3R1c2VyIiwiaXNfdmVyaWZpZWQiOnRydWUsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE3MzMxODA0ODN9.AudxC3e95q5SnSkr7g5RgHNT4sl6ln__mlSicW9AqfQ"

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            "/user/change-email",
            json={"email": "new_email@example.com"},
            headers={"Authorization": f"Bearer {token_expired}", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )

        assert response.status_code == 400, "El status code no es 400"
        assert response.json()["detail"] == "Token inválido"


@pytest.mark.asyncio
async def test_change_email_already_in_use(mocker):
    await inserted_user_in_db()
    await inserted_user_in_db(email="existing_email@example.com")

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/login",
            json={"email": "string@example.com", "password": "string"},
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )
        token_access = response.json()["access_token"]

        response = await ac.patch(
            "/user/change-email",
            json={"email": "existing_email@example.com"},
            headers={"Authorization": f"Bearer {token_access}", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )

        assert response.status_code == 400, "El status code no es 400"
        assert response.json()["detail"] == "El email ya está en uso"


@pytest.mark.asyncio
async def test_change_email_database_update_failure(mocker):
    user_id = await inserted_user_in_db()

    mocker.patch("app.routers.user_router.change_user_email", new_callable=AsyncMock, return_value=None)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/login",
            json={"email": "string@example.com", "password": "string"},
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )
        token_access = response.json()["access_token"]

        response = await ac.patch(
            "/user/change-email",
            json={"email": "new_email@example.com"},
            headers={"Authorization": f"Bearer {token_access}", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )

        assert response.status_code == 500, "El status code no es 500"
        assert response.json()["detail"] == "Hubo un problema al actualizar el email"


@pytest.mark.asyncio
async def test_change_email_consistency_in_response_and_database(mocker):
    user_id = await inserted_user_in_db()

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/login",
            json={"email": "string@example.com", "password": "string"},
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )
        token_access = response.json()["access_token"]

        response = await ac.patch(
            "/user/change-email",
            json={"email": "new_email@example.com"},
            headers={"Authorization": f"Bearer {token_access}", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )

        assert response.status_code == 200, "El status code no es 200"
        assert response.json()["message"] == "Email modificado exitosamente, por favor verificalo"

        user_in_db = await user_collection.find_one({"email": "new_email@example.com"})
        assert user_in_db is not None, "El usuario no fue encontrado en la base de datos tras el cambio de email"

