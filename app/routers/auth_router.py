from fastapi import APIRouter, HTTPException
from app.models.user_model import User
from app.schemas.user_schema import UserResponse
from app.services.email_service import send_verification_email
from app.services.user_service import register_new_user, check_user_exists


router = APIRouter()

@router.post("/register", response_model=UserResponse, response_description="Registrar un nuevo usuario")
async def register_user(user: User):

    if await check_user_exists(user.email, "email"):
        raise HTTPException(status_code=400, detail="El usuario con este correo ya existe")
    if await check_user_exists(user.username, "username"):
        raise HTTPException(status_code=400, detail="El usuario con este nombre de usuario ya existe")

    user_data = await register_new_user(user)

    if user_data:
        await send_verification_email(user.email, user_data["verification_uuid"])
        return UserResponse(message="Usuario registrado exitosamente, por favor verifica tu email", user_id=str(user_data["_id"]))
    else:
        raise HTTPException(status_code=500, detail="Hubo un problema al registrar el usuario")


