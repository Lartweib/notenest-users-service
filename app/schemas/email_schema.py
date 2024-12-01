from pydantic import BaseModel, EmailStr

class ChangeEmail(BaseModel):
    email: EmailStr
