import pytest, asyncio, os
from dotenv import load_dotenv
from app.db.mongo import user_collection

load_dotenv(dotenv_path=".env.test")

# Configuración del event loop para evitar el error de Event loop is closed
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def clear_users():
    await user_collection.delete_many({})

