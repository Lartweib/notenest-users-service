import pytest
from uuid import uuid4
from bson import ObjectId
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.mongo import user_collection

transport = ASGITransport(app=app)

async def inserted_user_in_db():
    verification_uuid = str(uuid4())
    user_data = {
        "_id": ObjectId(),
        "username": "testuser",
        "full_name": "string",
        "email": "string@example.com",
        "password": "$2b$12$OJf.BwMy5mDrvTKRh/HxA.QOYg3DSPrWCqRmArNmYDiwZga0PaYQ.",  # bcrypt de "string"
        "is_verified": True,
    }
    inserted_user = await user_collection.insert_one(user_data)
    inserted_user_id = inserted_user.inserted_id
    return inserted_user_id

@pytest.mark.asyncio
async def test_get_user_profile_successful(mocker):
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
        response = await ac.get(
            "/user/profile",
            headers={
                "Authorization": f"Bearer {token_access}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert response.status_code == 200, "El status code no es 200"
        assert response.json() == {
            "email": "string@example.com",
            "full_name": "string",
            "username": "testuser"
        }, "El perfil no coincide con el esperado \n -> " + str(response.json())

@pytest.mark.asyncio
async def test_get_user_profile_with_expired_token(mocker):
    user_id = await inserted_user_in_db()

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        token_expired = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmdAZXhhbXBsZS5jb20iLCJ1c2VybmFtZSI6InRlc3R1c2VyIiwiaXNfdmVyaWZpZWQiOnRydWUsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE3MzMxODA0ODN9.AudxC3e95q5SnSkr7g5RgHNT4sl6ln__mlSicW9AqfQ" # token valido pero expirado
        response = await ac.get(
            "/user/profile",
            headers={
                "Authorization": f"Bearer {token_expired}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert response.status_code == 401, "El status code no es 401"
        assert response.json()["detail"] == "Token inválido"

@pytest.mark.asyncio
async def test_get_user_profile_with_invalid_token(mocker):
    user_id = await inserted_user_in_db()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        token_expired = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmdAZXhhbXBsZS5jb20iLCJ1c2VybmFtZSI6InRlc3R1c2VyaW52YWxpZG8iLCJpc192ZXJpZmllZCI6dHJ1ZSwiZXhwIjoxNzMzMTg0MDgzfQ.VSAesIPkyTPfiAQl_KzIR2dshMKliVJzwLeH_SkYARY" # token mal formulado
        response = await ac.get(
            "/user/profile",
            headers={
                "Authorization": f"Bearer {token_expired}",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            },
        )
        assert response.status_code == 401, "El status code no es 401"
        assert response.json()["detail"] == "Token inválido"
