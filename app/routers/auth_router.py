import json
from bson import json_util
from fastapi import APIRouter, HTTPException, Request
from app.core.config import settings
from app.core.security import verify_password
from app.models.user_model import User
from app.schemas.user_schema import UserResponse
from app.schemas.login_schema import LoginRequest
from app.services.auth_service import generate_token_pair
from app.services.email_service import send_verification_email
from app.services.user_service import register_new_user, get_user_if_exists
from app.core.exceptions import UserAgentInvalidException, TokenGenerationException

ACCESS_TOKEN_EXPIRE_TIMES = settings.ACCESS_TOKEN_EXPIRE_TIMES
REFRESH_TOKEN_EXPIRE_TIMES = settings.REFRESH_TOKEN_EXPIRE_TIMES

router = APIRouter()

@router.post("/register", response_model=UserResponse, response_description="Registrar un nuevo usuario")
async def register_user(user: User):

    if await get_user_if_exists(user.email, "email"):
        raise HTTPException(status_code=400, detail="El usuario con este correo ya existe")
    if await get_user_if_exists(user.username, "username"):
        raise HTTPException(status_code=400, detail="El usuario con este nombre de usuario ya existe")

    user_data = await register_new_user(user)

    if user_data:
        await send_verification_email(user.email, user_data["verification_uuid"])
        return UserResponse(message="Usuario registrado exitosamente, por favor verifica tu email", user_id=str(user_data["_id"]))
    else:
        raise HTTPException(status_code=500, detail="Hubo un problema al registrar el usuario")


@router.post("/login")
async def login(request: Request, login_request: LoginRequest):
    email = login_request.email
    password = login_request.password
    user_agent = request.headers.get("user-agent",None)
    if not user_agent:
        raise HTTPException(status_code=400, detail="Header 'User-Agent' no proporcionado")
    
    user = await get_user_if_exists(email, "email")
    if not user:
        raise HTTPException(status_code=400, detail="El usuario no existe")
    
    hashed_password = user["password"]
    if not verify_password(password, hashed_password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    if not user["is_verified"]:
        raise HTTPException(status_code=401, detail="Usuario no verificado")
    
    try:
        token_pair = await generate_token_pair(user, user_agent)
    except UserAgentInvalidException:
        raise HTTPException(status_code=400, detail="La cabecera user-agent es inválida")
    except TokenGenerationException:
        raise HTTPException(status_code=500, detail="Hubo un problema al generar el token")


    return {
        "message": "Login exitoso",
        "access_token": token_pair["access_token"],
        "refresh_token": token_pair["refresh_token"]
    }
