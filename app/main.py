from fastapi import FastAPI
from app.routers.auth_router import router as auth_router
from app.routers.verification_router import router as verification_router
from app.routers.user_router import router as user_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Authorization"])
app.include_router(verification_router, prefix="/verification", tags=["Verification"])
app.include_router(user_router, prefix="/user", tags=["User"])
