from fastapi import APIRouter

from app.api.routes import auth, cv, jd

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(jd.router, prefix="/jd", tags=["job-descriptions"])
api_router.include_router(cv.router, prefix="/cv", tags=["cv"])
