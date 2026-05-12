from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, status

from app.api.internal_auth import verify_internal_workflow_access
from app.schemas.cv_internal import InternalCvAnalyzeRequest, InternalCvAnalyzeResponse
from app.services.cv_analysis import analyze_resume_payload, serialize_analysis_payload
from app.services.resume_analyzer import LiveAIUnavailableError
from app.worker_stage import run_worker_stage

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/cv/analyze",
    response_model=InternalCvAnalyzeResponse,
    dependencies=[Depends(verify_internal_workflow_access)],
)
async def analyze_cv(
    payload: InternalCvAnalyzeRequest,
) -> InternalCvAnalyzeResponse:
    result = await run_worker_stage(
        logger=logger,
        event_prefix="ai_worker_stage",
        cv_upload_id=payload.cv_upload_id,
        stage="analyze",
        operation=lambda: analyze_resume_payload(
            resume_text=payload.resume_text,
            job_description_text=payload.job_description_text,
        ),
        unexpected_detail="Unexpected analysis error. Please try again later.",
        mapped_exceptions=(
            (LiveAIUnavailableError, status.HTTP_503_SERVICE_UNAVAILABLE),
            (ValueError, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ),
        success_fields=lambda result: {
            "provider": result.provider_name,
            "processing_time_seconds": result.processing_time_seconds,
        },
    )
    return InternalCvAnalyzeResponse(
        provider_name=result.provider_name,
        processing_time_seconds=result.processing_time_seconds,
        analysis=serialize_analysis_payload(result.analysis_payload),
    )
