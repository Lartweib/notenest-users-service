import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from app.main import app

transport = ASGITransport(app=app)

@pytest.mark.asyncio
async def test_register_user_success(mocker):
    mocker.patch('app.routers.auth_router.send_verification_email', new_callable=AsyncMock)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword",
            "full_name": "Test User"
        }
        response = await ac.post("/auth/register", json=user_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Usuario registrado exitosamente, por favor verifica tu email"

@pytest.mark.asyncio
async def test_register_user_already_exists(mocker):
    mocker.patch('app.routers.auth_router.send_verification_email', new_callable=AsyncMock)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword",
            "full_name": "Test User"
        }
        await ac.post("/auth/register", json=user_data)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "El usuario con este correo ya existe"

@pytest.mark.asyncio
async def test_register_user_server_error(mocker):
    mocker.patch("app.routers.auth_router.register_new_user", new_callable=AsyncMock, return_value=None)
    mocker.patch('app.routers.auth_router.send_verification_email', new_callable=AsyncMock)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        user_data = {
            "username": "testuser",
            "email": "testuser2@example.com",
            "password": "securepassword",
            "full_name": "Test User"
        }
        response = await ac.post("/auth/register", json=user_data)
        assert response.status_code == 500
        assert response.json()["detail"] == "Hubo un problema al registrar el usuario"

