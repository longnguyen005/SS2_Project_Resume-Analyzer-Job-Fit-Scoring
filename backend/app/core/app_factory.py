from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.db.session import engine


_LOGGING_CONFIGURED = False


def configure_logging() -> None:
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    _LOGGING_CONFIGURED = True


def default_lifespan() -> Callable:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        await engine.dispose()

    return lifespan


def create_application(
    *,
    title: str,
    version: str,
    router: APIRouter,
    prefix: str,
    tags: list[str] | None = None,
    lifespan: Callable | None = None,
    include_cors: bool = False,
    include_sessions: bool = False,
) -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=title,
        version=version,
        lifespan=lifespan or default_lifespan(),
    )

    if include_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    if include_sessions:
        app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)

    app.include_router(router, prefix=prefix, tags=tags)
    register_error_handlers(app)
    return app
