"""Persistence worker application entrypoint.

This internal app exposes only the complete/save primitive for the n8n workflow.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.app_factory import create_application
from app.core.config import settings
from app.persistence_worker.routes import router as persistence_worker_router

worker_router = APIRouter()
worker_router.include_router(
    persistence_worker_router,
    prefix="/persistence-worker",
    tags=["persistence-worker"],
)

app = create_application(
    title=f"{settings.app_name} Persistence Worker",
    version="0.1.0-persistence-worker",
    router=worker_router,
    prefix=settings.api_v1_prefix,
)
