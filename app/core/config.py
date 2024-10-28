import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    ENV: str = os.getenv("ENVIRONMENT", "des")
    DATABASE_LOCAL: str = os.getenv("MONGO_LOCAL","")
    DATABASE_PRO: str = os.getenv("DATABASE_PRO","")

    @property
    def CURRENT_DATABASE_DETAILS(self) -> str:
        return self.DATABASE_PRO if self.ENV == "pro" else self.DATABASE_LOCAL


settings = Settings()
