from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import HTTPBearerToken
from app.core.security import decode_token
from app.services.user_service import get_user_if_exists

router = APIRouter()


@router.get("/profile")
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearerToken())):
    access_token = credentials.credentials
    payload = decode_token(access_token)
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
