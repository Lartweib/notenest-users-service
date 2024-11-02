from uuid import uuid4
from app.db.mongo import user_collection
from app.core.security import hash_password
from app.models.user_model import User

async def get_user_if_exists(data: str, type: str = "email"):
    if type == "email":
        return await user_collection.find_one({"email": data})
    elif type == "username":
        return await user_collection.find_one({"username": data})
    else:
        return None

async def get_user_email_by_uuid(verification_uuid: str):
    user = await user_collection.find_one({"verification_uuid": verification_uuid})
    return user["email"] if user else None

async def register_new_user(user: User):
    user.password = hash_password(user.password)
    user_data = user.model_dump()
    user_data["verification_uuid"] = str(uuid4())
    user_data["is_verified"] = False
    result = await user_collection.insert_one(user_data)
    if result.inserted_id:
        created_user = await user_collection.find_one({"_id": result.inserted_id})
        return created_user
    else: 
        return None

async def update_user_to_verified(email: str):
    result = await user_collection.update_one(
        {"email": email},
        {
            "$set": {"is_verified": True}, 
            "$unset": {"verification_uuid": ""}
        }
    )
    return result.modified_count == 1

async def update_user_refresh_tokens(email: str, refresh_tokens: list):
    result = await user_collection.update_one(
        {"email": email},
        {"$set": {"refresh_tokens": refresh_tokens}}
    )

    return result.modified_count == 1
