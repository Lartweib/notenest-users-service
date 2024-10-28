from fastapi import APIRouter, HTTPException
from app.models.user_model import User
from app.schemas.user_schema import UserResponse
from app.services.user_service import register_new_user, check_user_exists

router = APIRouter()

@router.post("/register", response_model=UserResponse, response_description="Registrar un nuevo usuario")
async def register_user(user: User):

    if await check_user_exists(user.email):
        raise HTTPException(status_code=400, detail="El usuario con este correo ya existe")


    user_id = await register_new_user(user)
    if user_id:
        return UserResponse(message="Usuario registrado exitosamente, por favor verifica tu email", user_id=str(user_id))
    else:
        raise HTTPException(status_code=500, detail="Hubo un problema al registrar el usuario")
