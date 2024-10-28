from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.CURRENT_DATABASE_DETAILS)

if settings.ENV == "test":
    db = client.test  
else:
    db = client.notenest

user_collection = db.get_collection("users")
