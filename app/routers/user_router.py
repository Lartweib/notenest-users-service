import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import HTTPBearerToken
from app.core.security import decode_token
from app.services.user_service import get_user_if_exists, update_user_data, change_user_email
from app.schemas.user_schema import EditProfile
from app.schemas.email_schema import ChangeEmail
from app.services.email_service import send_verification_email
from app.schemas.user_schema import UserResponse


router = APIRouter()

@router.get("/profile")
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearerToken())):
    access_token = credentials.credentials
    try:
        payload = decode_token(access_token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")

    if payload.get("type","") != "access":
        raise HTTPException(status_code=401, detail="Token no válido")
    user = await get_user_if_exists(payload.get("sub"), "email")
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")   
    return {
        "email": user["email"],
        "username": user["username"],
        "full_name": user["full_name"]
    }

@router.patch("/edit-profile")
async def edit_profile(data_to_update: EditProfile, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearerToken())):
    access_token = credentials.credentials
    try:
        payload = decode_token(access_token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    if payload.get("type","") != "access":
        raise HTTPException(status_code=401, detail="Token no válido")
    user = await get_user_if_exists(payload.get("sub"), "email")
    if not user:
        raise HTTPException(status_code=401, detail="Token no válido") 
    data_to_update = data_to_update.dict(exclude_none=True)
    if data_to_update.get("username", False) and await get_user_if_exists(data_to_update["username"], "username"):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    user_updated = await update_user_data(user["email"], data_to_update)
    if not user_updated:
        raise HTTPException(status_code=500, detail="Hubo un problema al actualizar el usuario")
    user_updated = await get_user_if_exists(user["email"])
    return {
        "email": user_updated["email"],
        "username": user_updated["username"],
        "full_name": user_updated["full_name"]
    }

@router.patch("/change-email")
async def change_email(new_email: ChangeEmail, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearerToken())):
    new_email = new_email.dict()["email"]
    access_token = credentials.credentials
    try:
        payload = decode_token(access_token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    if payload.get("type","") != "access":
        raise HTTPException(status_code=401, detail="Token no válido")
    user = await get_user_if_exists(payload.get("sub"), "email")
    if not user:
        raise HTTPException(status_code=401, detail="Token no válido") 
    if await get_user_if_exists(new_email, "email"):
        raise HTTPException(status_code=400, detail="El email ya está en uso")
    uuid = await change_user_email(user["email"], new_email)
    if not uuid:
        raise HTTPException(status_code=500, detail="Hubo un problema al actualizar el email")
    await send_verification_email(user["email"], uuid, "change_email")
    return UserResponse(message="Email modificado exitosamente, por favor verificalo", user_id=str(user["_id"]))

