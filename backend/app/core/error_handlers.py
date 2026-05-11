"""Shared exception handlers for all FastAPI application instances.

Eliminates duplicate handler code across main.py, file_worker_main.py,
ai_worker_main.py, and persistence_worker_main.py.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.schemas.common import APIErrorResponse, ErrorDetail


def register_error_handlers(app: FastAPI) -> None:
    """Attach standard error handlers to a FastAPI application."""

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        if isinstance(exc.detail, str):
            body = APIErrorResponse(message=exc.detail)
        elif isinstance(exc.detail, list):
            body = APIErrorResponse(
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
            body = APIErrorResponse(message="Request failed.")

        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(_: Request, exc: RequestValidationError) -> JSONResponse:
        body = APIErrorResponse(
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
        return JSONResponse(status_code=422, content=body.model_dump())

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(_: Request, __: Exception) -> JSONResponse:
        body = APIErrorResponse(message="Internal server error.")
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=body.model_dump())
