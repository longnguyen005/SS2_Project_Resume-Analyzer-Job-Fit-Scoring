from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.api.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.schemas.common import APIErrorResponse, ErrorDetail


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0-week6",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.exception_handler(HTTPException)
async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, str):
        payload = APIErrorResponse(message=exc.detail)
    elif isinstance(exc.detail, list):
        payload = APIErrorResponse(
            message="Request failed.",
            errors=[
                ErrorDetail(
                    field=".".join(str(part) for part in item.get("loc", [])) or None,
                    message=item.get("msg", "Invalid value."),
                    type=item.get("type"),
                )
                for item in exc.detail
                if isinstance(item, dict)
            ],
        )
    else:
        payload = APIErrorResponse(message="Request failed.")

    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(_: Request, exc: RequestValidationError) -> JSONResponse:
    payload = APIErrorResponse(
        message="Validation failed.",
        errors=[
            ErrorDetail(
                field=".".join(str(part) for part in error.get("loc", [])) or None,
                message=error.get("msg", "Invalid value."),
                type=error.get("type"),
            )
            for error in exc.errors()
        ],
    )
    return JSONResponse(status_code=422, content=payload.model_dump())


@app.exception_handler(Exception)
async def handle_unexpected_exception(_: Request, __: Exception) -> JSONResponse:
    payload = APIErrorResponse(message="Internal server error.")
    return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=payload.model_dump())


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    async with engine.begin() as connection:
        await connection.execute(text("SELECT 1"))
    return {"status": "ok"}
