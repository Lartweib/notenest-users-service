import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from bson import ObjectId
from app.db.mongo import user_collection
from unittest.mock import AsyncMock
from app.core.security import decode_token
from app.services.user_service import get_user_if_exists


transport = ASGITransport(app=app)

async def add_user_in_db():
    user_data = {
        "_id": ObjectId(),
        "username": "testuser",
        "full_name": "string",
        "email": "test@example.com",
        "password": "$2b$12$OJf.BwMy5mDrvTKRh/HxA.QOYg3DSPrWCqRmArNmYDiwZga0PaYQ.",  # bcrypt de "string"
        "is_verified": True,
        "refresh_tokens": []
    }
    inserted_user = await user_collection.insert_one(user_data)
    inserted_user_id = inserted_user.inserted_id
    return True if inserted_user_id else False

async def login_user(header=None):
    if header is None:
        header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "string"},
            headers=header
        )
        return response

@pytest.mark.asyncio
async def test_refresh_token_authentication_failure():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/refresh-token",
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )
        assert response.status_code == 401, "El status code no es 401"
        assert response.json() == {"detail": "Credenciales inválidas o faltantes. Por favor, autentíquese."}, "El mensaje de error no coincide"

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/refresh-token",
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0", "Authorization": "Bearer 123456"}
        )
        assert response.status_code == 400, "El status code no es 401"
        assert response.json() == {"detail": "Token inválido"}, "El mensaje de error no coincide"

@pytest.mark.asyncio
async def test_refresh_token_success():
    await add_user_in_db()
    tokens = await login_user()
    refresh_token = tokens.json()["refresh_token"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/refresh-token",
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0", "Authorization": f"Bearer {refresh_token}"}
        )
        
        assert response.status_code == 200, "El status code no es 200"
        
        refresh_token_payload = decode_token(response.json()["refresh_token"])
        access_token_payload = decode_token(response.json()["access_token"])
        
        assert "access_token" in response.json(), "No se ha devuelto el access token"
        assert "refresh_token" in response.json(), "No se ha devuelto el refresh token"
        assert response.json()["access_token"] != refresh_token, "El access token y el refresh token son iguales"
        assert refresh_token_payload["type"] == "refresh", "El tipo del refresh token no es correcto"
        assert access_token_payload["type"] == "access", "El tipo del access token no es correcto"
        assert refresh_token_payload["sub"] == "test@example.com", "El sub del refresh token no es correcto"
        assert access_token_payload["sub"] == "test@example.com", "El sub del access token no es correcto"

@pytest.mark.asyncio
async def test_previus_refresh_token_invalid():
    await add_user_in_db()
    tokens = await login_user()
    refresh_token = tokens.json()["refresh_token"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/refresh-token",
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0", "Authorization": f"Bearer {refresh_token}"}
        )

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/refresh-token",
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0", "Authorization": f"Bearer {refresh_token}"}
        )

        assert response.status_code == 400, "El status code no es 400"
        assert response.json() == {"detail": "Token inválido"}, "El mensaje de error no coincide"

@pytest.mark.asyncio
async def test_refresh_uuid_update_success():
    await add_user_in_db()

    tokens = await login_user()
    refresh_token = tokens.json()["refresh_token"]
    refresh_token_data = decode_token(refresh_token)
    refresh_token_uuid_1 = refresh_token_data["uuid"]
    
    user = await get_user_if_exists("test@example.com", "email")
    refresh_token_created_at_1 = user["refresh_tokens"][0]["created_at"]
    refresh_token_updated_at_1 = user["refresh_tokens"][0]["updated_at"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/refresh-token",
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0", "Authorization": f"Bearer {refresh_token}"}
        )

        assert response.status_code == 200, "El status code no es 200"
        user_updated = await get_user_if_exists("test@example.com", "email")
        assert len(user_updated["refresh_tokens"]) == 1, "No se ha actualizado el refresh token"
        refresh_token_created_at_2 = user_updated["refresh_tokens"][0]["created_at"]
        refresh_token_updated_at_2 = user_updated["refresh_tokens"][0]["updated_at"]
        refresh_token_uuid_2 = user_updated["refresh_tokens"][0]["uuid"]
        assert refresh_token_uuid_1 != refresh_token_uuid_2, "El uuid del refresh token no se ha actualizado"
        assert refresh_token_created_at_1 == refresh_token_created_at_2, "El created_at del refresh token se ha actualizado"
        assert refresh_token_updated_at_1 != refresh_token_updated_at_2, "El updated_at del refresh token no se ha actualizado"

@pytest.mark.asyncio
async def test_refresh_token_multiple_devices():
    await add_user_in_db()

    tokens_device_1 = await login_user(
        header={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
        }
    )
    refresh_token_device_1 = tokens_device_1.json()["refresh_token"]

    tokens_device_2 = await login_user(
        header={
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        }
    )
    refresh_token_device_2 = tokens_device_2.json()["refresh_token"]

    user = await get_user_if_exists("test@example.com", "email")
    assert len(user["refresh_tokens"]) == 2, "No se han registrado los dos dispositivos correctamente"

    refresh_uuid_device_1 = user["refresh_tokens"][0]["uuid"]
    refresh_uuid_device_2 = user["refresh_tokens"][1]["uuid"]
    created_at_device_1 = user["refresh_tokens"][0]["created_at"]
    created_at_device_2 = user["refresh_tokens"][1]["created_at"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/refresh-token",
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
                "Authorization": f"Bearer {refresh_token_device_1}"
            }
        )

    assert response.status_code == 200, "No se pudo hacer el refresh correctamente con el primer dispositivo"

    user_updated = await get_user_if_exists("test@example.com", "email")
    assert len(user_updated["refresh_tokens"]) == 2, "El número de dispositivos no coincide tras el refresh"

    updated_uuid_device_1 = user_updated["refresh_tokens"][0]["uuid"]
    assert refresh_uuid_device_1 != updated_uuid_device_1, "El UUID del primer dispositivo no se ha actualizado"

    updated_uuid_device_2 = user_updated["refresh_tokens"][1]["uuid"]
    assert refresh_uuid_device_2 == updated_uuid_device_2, "El UUID del segundo dispositivo ha cambiado inesperadamente"

    updated_created_at_device_1 = user_updated["refresh_tokens"][0]["created_at"]
    updated_created_at_device_2 = user_updated["refresh_tokens"][1]["created_at"]
    assert created_at_device_1 == updated_created_at_device_1, "El campo `created_at` del primer dispositivo se ha modificado incorrectamente"
    assert created_at_device_2 == updated_created_at_device_2, "El campo `created_at` del segundo dispositivo se ha modificado incorrectamente"

    updated_at_device_1 = user_updated["refresh_tokens"][0]["updated_at"]
    updated_at_device_2 = user_updated["refresh_tokens"][1]["updated_at"]
    assert updated_at_device_1 != user["refresh_tokens"][0]["updated_at"], "El `updated_at` del primer dispositivo no se ha actualizado correctamente"
    assert updated_at_device_2 == user["refresh_tokens"][1]["updated_at"], "El `updated_at` del segundo dispositivo se ha modificado incorrectamente"

