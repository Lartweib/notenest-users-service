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
async def test_edit_profile_successful_single_field(mocker):
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

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            "/user/edit-profile",
            json={"username": "new_username"},
            headers={
                "Authorization": f"Bearer {token_access}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert response.status_code == 200, "El status code no es 200"
        assert response.json() == {
            "email": "string@example.com",
            "full_name": "string",
            "username": "new_username"
        }, "El perfil no coincide con el esperado \n -> " + str(response.json())

@pytest.mark.asyncio
async def test_edit_profile_successful_multiple_fields(mocker):
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

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            "/user/edit-profile",
            json={
                "username": "new_username",
                "full_name": "new_full_name"
                },
            headers={
                "Authorization": f"Bearer {token_access}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert response.status_code == 200, "El status code no es 200"
        assert response.json() == {
            "email": "string@example.com",
            "full_name": "new_full_name",
            "username": "new_username"
        }, "El perfil no coincide con el esperado \n -> " + str(response.json())

@pytest.mark.asyncio
async def test_edit_profile_invalid_token(mocker):
    user_id = await inserted_user_in_db()

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        token_expired = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmdAZXhhbXBsZS5jb20iLCJ1c2VybmFtZSI6InRlc3R1c2VyIiwiaXNfdmVyaWZpZWQiOnRydWUsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE3MzMxODA0ODN9.AudxC3e95q5SnSkr7g5RgHNT4sl6ln__mlSicW9AqfQ" # token valido pero expirado
        response = await ac.patch(
            "/user/edit-profile",
            json={
                "username": "new_username",
                "full_name": "new_full_name"
                },
            headers={
                "Authorization": f"Bearer {token_expired}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert response.status_code == 400, "El status code no es 400"
        assert response.json()["detail"] == "Token inválido"

@pytest.mark.asyncio
async def test_edit_profile_expired_token(mocker):
    user_id = await inserted_user_in_db()

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        token_expired = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmdAZXhhbXBsZS5jb20iLCJ1c2VybmFtZSI6InRlc3R1c2VyaW52YWxpZG8iLCJpc192ZXJpZmllZCI6dHJ1ZSwiZXhwIjoxNzMzMTg0MDgzfQ.VSAesIPkyTPfiAQl_KzIR2dshMKliVJzwLeH_SkYARY" # token mal formulado
        response = await ac.patch(
            "/user/edit-profile",
            json={
                "username": "new_username",
                "full_name": "new_full_name"
                },
            headers={
                "Authorization": f"Bearer {token_expired}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert response.status_code == 400, "El status code no es 400"
        assert response.json()["detail"] == "Token inválido"

@pytest.mark.asyncio
async def test_edit_profile_missing_token(mocker):
    user_id = await inserted_user_in_db()

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            "/user/edit-profile",
            json={
                "username": "new_username",
                "full_name": "new_full_name"
                },
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert response.status_code == 401, "El status code no es 400"
        assert response.json()["detail"] == "Credenciales inválidas o faltantes. Por favor, autentíquese.", "El mensaje de error no coincide"

@pytest.mark.asyncio
async def test_edit_profile_no_data_provided(mocker):
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

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            "/user/edit-profile",
            headers={
                "Authorization": f"Bearer {token_access}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert response.status_code == 422, "El status code no es 400"

@pytest.mark.asyncio
async def test_edit_profile_username_already_in_use(mocker):
    user_id_1 = await inserted_user_in_db()
    user_id_2 = await inserted_user_in_db("testuser2", "string2", "string2@example.com")

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/login",
            json={"email": "string@example.com", "password": "string"},
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
            },
        )
        token_access = response.json()["access_token"]

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            "/user/edit-profile",
            json={"username": "testuser2"},
            headers={
                "Authorization": f"Bearer {token_access}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert response.status_code == 400, "El status code no es 400"
        assert response.json()["detail"] == "El nombre de usuario ya está en uso"

@pytest.mark.asyncio
async def test_edit_profile_database_update_failure(mocker):
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

    mock_update_user_data = mocker.patch("app.routers.user_router.update_user_data", new_callable=AsyncMock, return_value=False)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            "/user/edit-profile",
            json={"username": "testuser2"},
            headers={
                "Authorization": f"Bearer {token_access}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert mock_update_user_data.called, "El mock no fue llamado"
        assert response.status_code == 500, "El status code no es 500"
        assert response.json()["detail"] == "Hubo un problema al actualizar el usuario"

@pytest.mark.asyncio
async def test_edit_profile_consistency_in_response_and_database(mocker):
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

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            "/user/edit-profile",
            json={
                "username": "new_username",
                "full_name": "new_full_name"
                },
            headers={
                "Authorization": f"Bearer {token_access}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert response.status_code == 200, "El status code no es 200"
        assert response.json() == {
            "email": "string@example.com",
            "full_name": "new_full_name",
            "username": "new_username"
        }, "El perfil no coincide con el esperado \n -> " + str(response.json())
        response_api = response.json()

    user_in_db = await user_collection.find_one({"email": "string@example.com"})

    assert user_in_db["email"] == response_api["email"], "El email en la respuesta no coincide con la base de datos"
    assert user_in_db["username"] == response_api["username"], "El username en la respuesta no coincide con la base de datos"
    assert user_in_db["full_name"] == response_api["full_name"], "El full_name en la respuesta no coincide con la base de datos"

