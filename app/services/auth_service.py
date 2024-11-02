import jwt
from uuid import uuid4
from user_agents import parse
from datetime import timedelta, datetime, timezone
from app.core.config import settings
from app.core.security import create_token, decode_token
from app.services.user_service import update_user_refresh_tokens, get_user_if_exists
from app.core.exceptions import UserAgentInvalidException, TokenGenerationException, RefreshTokenDataInvalidException, RefreshTokenExpiredException

ACCESS_TOKEN_EXPIRE_TIMES = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_TIMES)
REFRESH_TOKEN_EXPIRE_TIMES = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_TIMES)


def extract_device_data(user_agent: str):
    try:
        user_agent_parsed = parse(user_agent)

        if user_agent_parsed.is_mobile:
            device_type = "mobile"
        elif user_agent_parsed.is_tablet:
            device_type = "tablet"
        elif user_agent_parsed.is_pc:
            device_type = "pc"
        else:
            raise ValueError("Tipo de dispositivo desconocido")

        os = user_agent_parsed.os.family
        browser = user_agent_parsed.browser.family

        if not os or not browser:
            raise ValueError("Datos del sistema operativo o navegador inválidos")

        return {"type": device_type, "os": os, "browser": browser}

    except Exception as e:
        raise UserAgentInvalidException()


def create_refresh_token_entry(user: dict, device_data: dict, refresh_uuid: str):
    new_refresh_token_entry = {
        "uuid": refresh_uuid,
        "device": device_data,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    refresh_tokens = user.get("refresh_tokens", [])
    refresh_tokens.append(new_refresh_token_entry)

    return refresh_tokens


async def generate_token_pair(user: dict, user_agent: str):
    device_data = extract_device_data(user_agent)
    if not device_data:
        return {"error": "User agent invalido"}
    refresh_uuid = str(uuid4())
    updated_refresh_tokens = create_refresh_token_entry(user, device_data, refresh_uuid)
    update_user = await update_user_refresh_tokens(
        user["email"], updated_refresh_tokens
    )

    if not update_user:
        raise TokenGenerationException()

    base_payload = {"sub": user["email"], "username": user["username"]}
    access_token_payload = base_payload.copy()
    access_token_payload.update({"is_verified": user["is_verified"], "type": "access"})
    access_token = create_token(
        data=access_token_payload, expires_delta=ACCESS_TOKEN_EXPIRE_TIMES
    )

    refresh_payload = base_payload.copy()
    refresh_payload.update({"uuid": refresh_uuid, "type": "refresh"})
    refresh_token = create_token(
        data=refresh_payload, expires_delta=REFRESH_TOKEN_EXPIRE_TIMES
    )

    return {"access_token": access_token, "refresh_token": refresh_token}


async def handle_refresh_token(refresh_token: str):
    try:
        payload = decode_token(refresh_token)
    except jwt.ExpiredSignatureError:
        raise RefreshTokenExpiredException()
    except jwt.InvalidTokenError:
        raise RefreshTokenDataInvalidException()
    
    token_type = payload.get("type")
    if token_type != "refresh":
        raise RefreshTokenDataInvalidException()
    
    email = payload.get("sub")
    uuid = payload.get("uuid")
    if not email or not uuid or not token_type:
        raise RefreshTokenDataInvalidException()

    user = await get_user_if_exists(email, "email")
    if not user:
        raise RefreshTokenDataInvalidException()

    valid_token_entry = None
    for device in user.get("refresh_tokens", []):
        if device["uuid"] == uuid:
            valid_token_entry = device
            break

    if not valid_token_entry:
        raise RefreshTokenDataInvalidException()

    new_refresh_uuid = str(uuid4())
    valid_token_entry["uuid"] = new_refresh_uuid
    valid_token_entry["updated_at"] = datetime.now(timezone.utc)

    updated = await update_user_refresh_tokens(user["email"], user["refresh_tokens"])
    if not updated:
        raise TokenGenerationException()

    base_payload = {"sub": user["email"], "username": user["username"]}

    access_token_payload = base_payload.copy()
    access_token_payload.update({"is_verified": user["is_verified"], "type": "access"})
    access_token = create_token(
        data=access_token_payload, expires_delta=ACCESS_TOKEN_EXPIRE_TIMES
    )

    refresh_payload = base_payload.copy()
    refresh_payload.update({"uuid": new_refresh_uuid, "type": "refresh"})
    new_refresh_token = create_token(
        data=refresh_payload, expires_delta=REFRESH_TOKEN_EXPIRE_TIMES
    )

    return {"access_token": access_token, "refresh_token": new_refresh_token}
