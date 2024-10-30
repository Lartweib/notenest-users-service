from fastapi import APIRouter, HTTPException
from app.services.user_service import update_user_to_verified, get_user_email_by_uuid

router = APIRouter()

@router.get("/email/{verification_uuid}", response_description="Verificar correo electrónico")
async def verify_email(verification_uuid: str):
    email = await get_user_email_by_uuid(verification_uuid)

    if not email:
        raise HTTPException(status_code=400, detail="No se encontró el usuario")

    updated_user = await update_user_to_verified(email)

    if updated_user:
        return {"message": "Correo verificado exitosamente"}
    else:
        raise HTTPException(status_code=400, detail="No se encontró el usuario o ya está verificado")
