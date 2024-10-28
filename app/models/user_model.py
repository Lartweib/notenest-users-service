from pydantic import BaseModel, EmailStr

class User(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    password: str 
