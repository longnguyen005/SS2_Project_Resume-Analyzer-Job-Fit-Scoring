"""Shared execution and logging helpers for internal worker routes."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Mapping, Sequence
from time import perf_counter
from typing import TypeVar
from uuid import UUID

from fastapi import HTTPException, status


T = TypeVar("T")
ExceptionStatusMapping = tuple[type[Exception], int]


async def run_worker_stage(
    *,
    logger: logging.Logger,
    event_prefix: str,
    cv_upload_id: UUID,
    stage: str,
    operation: Callable[[], Awaitable[T]],
    unexpected_detail: str,
    unexpected_log_detail: str = "unexpected_error",
    mapped_exceptions: Sequence[ExceptionStatusMapping] = (),
    success_fields: Callable[[T], Mapping[str, object]] | None = None,
) -> T:
    started_at = perf_counter()
    logger.info("%s_start cv_upload_id=%s stage=%s duration_ms=0", event_prefix, cv_upload_id, stage)

    try:
        result = await operation()
    except HTTPException as exc:
        logger.warning(
            "%s_failure cv_upload_id=%s stage=%s duration_ms=%s status_code=%s detail=%s",
            event_prefix,
            cv_upload_id,
            stage,
            _duration_ms(started_at),
            exc.status_code,
            exc.detail,
        )
        raise
    except Exception as exc:
        mapped_status = _mapped_status_code(exc, mapped_exceptions)
        if mapped_status is not None:
            logger.warning(
                "%s_failure cv_upload_id=%s stage=%s duration_ms=%s status_code=%s detail=%s",
                event_prefix,
                cv_upload_id,
                stage,
                _duration_ms(started_at),
                mapped_status,
                exc,
            )
            raise HTTPException(status_code=mapped_status, detail=str(exc)) from exc

        logger.exception(
            "%s_failure cv_upload_id=%s stage=%s duration_ms=%s status_code=500 detail=%s",
            event_prefix,
            cv_upload_id,
            stage,
            _duration_ms(started_at),
            unexpected_log_detail,
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=unexpected_detail) from exc

    fields = dict(success_fields(result)) if success_fields is not None else {}
    logger.info(
        "%s_success cv_upload_id=%s stage=%s duration_ms=%s%s",
        event_prefix,
        cv_upload_id,
        stage,
        _duration_ms(started_at),
        _format_log_fields(fields),
    )
    return result


def _duration_ms(started_at: float) -> int:
    return int((perf_counter() - started_at) * 1000)


def _mapped_status_code(exc: Exception, mapped_exceptions: Sequence[ExceptionStatusMapping]) -> int | None:
    for exception_type, status_code in mapped_exceptions:
        if isinstance(exc, exception_type):
            return status_code
    return None


def _format_log_fields(fields: Mapping[str, object]) -> str:
    if not fields:
        return ""
    return "".join(f" {key}={value}" for key, value in fields.items())
