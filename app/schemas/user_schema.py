from pydantic import BaseModel

class UserResponse(BaseModel):
    message: str
    user_id: str
