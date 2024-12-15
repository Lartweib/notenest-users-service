from pydantic import BaseModel, EmailStr, model_validator

class UserResponse(BaseModel):
    message: str
    user_id: str

class EditProfile(BaseModel):
    username: str | None = None
    full_name: str | None = None

    @model_validator(mode="after")
    def validate_data(cls, instance):
        if not (instance.username or instance.full_name):
            raise ValueError("Debe proporcionar al menos un campo para actualizar el perfil")
        return instance
