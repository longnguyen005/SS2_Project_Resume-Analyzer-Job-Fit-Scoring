from __future__ import annotations

from app.ai_worker.routes import router as ai_worker_router
from fastapi import APIRouter

from app.core.app_factory import create_application
from app.core.config import settings

worker_router = APIRouter()
worker_router.include_router(ai_worker_router, prefix="/ai-worker", tags=["ai-worker"])

app = create_application(
    title=f"{settings.app_name} AI Worker",
    version="0.1.0-ai-worker",
    router=worker_router,
    prefix=settings.api_v1_prefix,
)
