import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="app/core/.env")

class Settings:
    def __init__(self):
        #Environment
        self.ENV = os.getenv("ENVIRONMENT", "des")
        #Database
        self.CURRENT_DATABASE_DETAILS = os.getenv("MONGO_LOCAL") if self.ENV == "des" else os.getenv("DATABASE_PRO")
        #Email
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME") if self.ENV == "pro" else os.getenv("SMTP_USERNAME_DES")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") if self.ENV == "pro" else os.getenv("SMTP_PASSWORD_DES")
        self.SMTP_HOST = os.getenv("SMTP_HOST") if self.ENV == "pro" else os.getenv("SMTP_HOST_DES")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT")) if self.ENV == "pro" else int(os.getenv("SMTP_PORT_DES"))
        self.EMAIL_FROM = os.getenv("EMAIL_FROM") if self.ENV == "pro" else os.getenv("EMAIL_FROM_DES")   
        self.EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME") if self.ENV == "pro" else os.getenv("EMAIL_FROM_NAME_DES")
        self.FRONTEND_URL = os.getenv("FRONTEND_URL") if self.ENV == "pro" else os.getenv("FRONTEND_URL_DES")
        #Security
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")
        self.ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))

settings = Settings()
