from __future__ import annotations

import logging
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.internal_auth import verify_internal_workflow_access
from app.schemas.cv import InternalCvAnalyzeRequest, InternalCvAnalyzeResponse
from app.services.cv_analysis import analyze_resume_payload, serialize_analysis_payload
from app.services.resume_analyzer import LiveAIUnavailableError

router = APIRouter()
logger = logging.getLogger(__name__)


def _duration_ms(started_at: float) -> int:
    return int((perf_counter() - started_at) * 1000)


@router.post(
    "/cv/analyze",
    response_model=InternalCvAnalyzeResponse,
    dependencies=[Depends(verify_internal_workflow_access)],
)
async def analyze_cv(
    payload: InternalCvAnalyzeRequest,
) -> InternalCvAnalyzeResponse:
    started_at = perf_counter()
    logger.info("ai_worker_stage_start cv_upload_id=%s stage=analyze", payload.cv_upload_id)
    try:
        analysis_payload, provider_name, processing_time_seconds = await analyze_resume_payload(
            resume_text=payload.resume_text,
            job_description_text=payload.job_description_text,
        )
    except LiveAIUnavailableError as exc:
        logger.warning(
            "ai_worker_stage_failure cv_upload_id=%s stage=analyze status_code=503 detail=%s duration_ms=%s",
            payload.cv_upload_id,
            exc,
            _duration_ms(started_at),
        )
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except ValueError as exc:
        logger.warning(
            "ai_worker_stage_failure cv_upload_id=%s stage=analyze status_code=422 detail=%s duration_ms=%s",
            payload.cv_upload_id,
            exc,
            _duration_ms(started_at),
        )
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception:
        logger.exception(
            "ai_worker_stage_failure cv_upload_id=%s stage=analyze status_code=500 detail=unexpected_error duration_ms=%s",
            payload.cv_upload_id,
            _duration_ms(started_at),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected analysis error. Please try again later.",
        )

    logger.info(
        "ai_worker_stage_success cv_upload_id=%s stage=analyze provider=%s processing_time_seconds=%s duration_ms=%s",
        payload.cv_upload_id,
        provider_name,
        processing_time_seconds,
        _duration_ms(started_at),
    )
    return InternalCvAnalyzeResponse(
        provider_name=provider_name,
        processing_time_seconds=processing_time_seconds,
        analysis=serialize_analysis_payload(analysis_payload),
    )

