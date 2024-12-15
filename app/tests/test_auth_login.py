import pytest
from bson import ObjectId
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.mongo import user_collection


transport = ASGITransport(app=app)

@pytest.mark.asyncio
async def test_login_successful(mocker):
    user_data = {
        "email": "string@example.com",
        "username": "testuser",
        "password": "$2b$12$OJf.BwMy5mDrvTKRh/HxA.QOYg3DSPrWCqRmArNmYDiwZga0PaYQ.",  # bcrypt de "string"
        "is_verified": True,
        "refresh_tokens": []
    }
    
    mocker.patch("app.routers.auth_router.get_user_if_exists", new_callable=AsyncMock, return_value=user_data)
    mocker.patch("app.services.auth_service.update_user_refresh_tokens", new_callable=AsyncMock, return_value=True)
        
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "string@example.com", "password": "string"},
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )

        assert response.status_code == 200, "El status code no es 200"
        assert "access_token" in response.json(), "No se generó un access token"
        assert "refresh_token" in response.json(), "No se generó un refresh token"

@pytest.mark.asyncio
async def test_login_user_not_exist(mocker):
    mocker.patch("app.routers.auth_router.get_user_if_exists", new_callable=AsyncMock, return_value=None)
    
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "string@example.com", "password": "string"},
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )

        assert response.status_code == 400, "El status code no es 400"
        assert response.json() == {"detail": "El usuario no existe"}, "El mensaje de error no coincide"

@pytest.mark.asyncio
async def test_login_user_not_verified(mocker):
    user_data = {
        "email": "string@example.com",
        "username": "testuser",
        "password": "$2b$12$OJf.BwMy5mDrvTKRh/HxA.QOYg3DSPrWCqRmArNmYDiwZga0PaYQ.",  # bcrypt de "string"
        "is_verified": False,
        "refresh_tokens": []
    }

    mocker.patch("app.routers.auth_router.get_user_if_exists", new_callable=AsyncMock, return_value=user_data)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/auth/login",
                json={"email": "string@example.com", "password": "string"},
                headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
            )

            assert response.status_code == 401, "El status code no es 401"
            assert response.json() == {"detail": "Usuario no verificado"}, "El mensaje de error no coincide"

@pytest.mark.asyncio
async def test_login_wrong_password(mocker):
    user_data = {
        "email": "string@example.com",
        "username": "testuser",
        "password": "$2b$12$OJf.BwMy5mDrvTKRh/HxA.QOYg3DSPrWCqRmArNmYDiwZga0PaYQ.",  # bcrypt de "string"
        "is_verified": False,
        "refresh_tokens": []
    }

    mocker.patch("app.routers.auth_router.get_user_if_exists", new_callable=AsyncMock, return_value=user_data)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/auth/login",
                json={"email": "string@example.com", "password": "string123"},
                headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
            )

            assert response.status_code == 401, "El status code no es 401"
            assert response.json() == {"detail": "Contraseña incorrecta"}, "El mensaje de error no coincide"

@pytest.mark.asyncio
async def test_login_user_agent_invalid(mocker):
    user_data = {
        "email": "string@example.com",
        "username": "testuser",
        "password": "$2b$12$OJf.BwMy5mDrvTKRh/HxA.QOYg3DSPrWCqRmArNmYDiwZga0PaYQ.",  # bcrypt de "string"
        "is_verified": True,
        "refresh_tokens": []
    }

    mocker.patch("app.routers.auth_router.get_user_if_exists", new_callable=AsyncMock, return_value=user_data)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/auth/login",
                json={"email": "string@example.com", "password": "string"},
                headers={"user-agent": "Mozilla/5.0"}
            )

            assert response.status_code == 400, "El status code no es 400"
            assert response.json() == {"detail": "La cabecera user-agent es inválida"}, "El mensaje de error no coincide"

@pytest.mark.asyncio
async def test_login_not_user_agent(mocker):
    user_data = {
        "email": "string@example.com",
        "username": "testuser",
        "password": "$2b$12$OJf.BwMy5mDrvTKRh/HxA.QOYg3DSPrWCqRmArNmYDiwZga0PaYQ.",  # bcrypt de "string"
        "is_verified": True,
        "refresh_tokens": []
    }

    mocker.patch("app.routers.auth_router.get_user_if_exists", new_callable=AsyncMock, return_value=user_data)

    async with AsyncClient(transport=transport, base_url="http://test") as client:

            response = await client.post(
                "/auth/login",
                json={"email": "string@example.com", "password": "string"},
                headers={"user-agent":""}
            )

            assert response.status_code == 400, "El status code no es 400"
            assert response.json() == {"detail": "Header 'User-Agent' no proporcionado"}, "El mensaje de error no coincide"

@pytest.mark.asyncio
async def test_login_token_generation_error(mocker):
    user_data = {
        "email": "string@example.com",
        "username": "testuser",
        "password": "$2b$12$OJf.BwMy5mDrvTKRh/HxA.QOYg3DSPrWCqRmArNmYDiwZga0PaYQ.",  # bcrypt de "string"
        "is_verified": True,
        "refresh_tokens": []
    }
    
    mocker.patch("app.routers.auth_router.get_user_if_exists", new_callable=AsyncMock, return_value=user_data)
    mocker.patch("app.services.auth_service.update_user_refresh_tokens", new_callable=AsyncMock, return_value=False)
        
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "string@example.com", "password": "string"},
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )

        assert response.status_code == 500, "El status code no es 500"
        assert response.json() == {"detail": "Hubo un problema al generar el token"}, "El mensaje de error no coincide"

@pytest.mark.asyncio
async def test_login_user_success_register_in_bbdd(mocker):
    user_data = {
        "_id": ObjectId(),
        "username": "testuser",
        "full_name": "string",
        "email": "test@example.com",
        "password": "$2b$12$OJf.BwMy5mDrvTKRh/HxA.QOYg3DSPrWCqRmArNmYDiwZga0PaYQ.",  # bcrypt de "string"
        "is_verified": True
    }

    inserted_user = await user_collection.insert_one(user_data)
    inserted_user_id = inserted_user.inserted_id
    assert inserted_user_id is not None

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "string"},
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
        )

        assert response.status_code == 200, "El status code no es 200"
        assert "access_token" in response.json(), "No se generó un access token"
        assert "refresh_token" in response.json(), "No se generó un refresh token"
    
    user = await user_collection.find_one({"email":"test@example.com"})
    # Verificar si se actualizó correctamente
    assert user is not None, "El usuario no se encontró en la base de datos después del login"
    assert "refresh_tokens" in user, "El campo refresh_tokens no se encontró en el usuario"

    # Verificar que se haya añadido un nuevo token de refresh
    assert len(user["refresh_tokens"]) > 0, "El campo refresh_tokens no fue actualizado"
    assert "uuid" in user["refresh_tokens"][-1], "No se generó un UUID para el refresh token"
    assert user["refresh_tokens"][-1]["device"]["type"] == "pc", "El tipo de dispositivo no coincide"
    assert user["refresh_tokens"][-1]["device"]["os"] == "Windows", "El sistema operativo no coincide"
    assert user["refresh_tokens"][-1]["device"]["browser"] == "Edge", "El navegador no coincide"
