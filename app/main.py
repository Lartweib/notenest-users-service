from fastapi import FastAPI
from app.routers.auth_router import router as auth_router
from app.routers.verification_router import router as verification_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Authorization"])
app.include_router(verification_router, prefix="/verification", tags=["Verification"])
