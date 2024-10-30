import pytest
from uuid import uuid4
from bson import ObjectId
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.mongo import user_collection

transport = ASGITransport(app=app)

@pytest.mark.asyncio
async def test_register_user_and_mock_email(mocker):

    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword",
            "full_name": "Test User"
        }

        mock_send_email = mocker.patch(
            'app.routers.auth_router.send_verification_email',
            new_callable=AsyncMock
        )

        response = await async_client.post("/auth/register", json=user_data)

        assert response.status_code == 200
        assert response.json()["message"] == "Usuario registrado exitosamente, por favor verifica tu email"

        mock_send_email.assert_called_once()
        assert mock_send_email.call_args[0][0] == user_data["email"]

@pytest.mark.asyncio
async def test_validate_user_in_bbdd():
    
    verification_uuid = str(uuid4())
    user_data = {
        "_id": ObjectId(),
        "username": "testuser",
        "full_name": "string",
        "email": "testuser@example.com",
        "verification_uuid": verification_uuid,
        "is_verified": False
    }

    inserted_user = await user_collection.insert_one(user_data)
    inserted_user_id = inserted_user.inserted_id
    assert inserted_user_id is not None

    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        response = await async_client.get(f"/auth/verify-email/{verification_uuid}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Correo verificado exitosamente"

