"""File worker application entrypoint.

This internal app exposes only resume extraction and validation primitives for
the n8n workflow.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.app_factory import create_application
from app.core.config import settings
from app.file_worker.routes import router as file_worker_router

worker_router = APIRouter()
worker_router.include_router(file_worker_router, prefix="/file-worker", tags=["file-worker"])

app = create_application(
    title=f"{settings.app_name} File Worker",
    version="0.1.0-file-worker",
    router=worker_router,
    prefix=settings.api_v1_prefix,
)
