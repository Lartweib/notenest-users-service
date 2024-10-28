from app.db.mongo import user_collection
from app.core.security import hash_password
from app.models.user_model import User


async def check_user_exists(email: str):
    return await user_collection.find_one({"email": email})

async def register_new_user(user: User):
    user.password = hash_password(user.password)
    user_data = user.model_dump()
    user_data["is_verified"] = False
    result = await user_collection.insert_one(user_data)
    return result.inserted_id if result.inserted_id else None
