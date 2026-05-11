from __future__ import annotations

import logging
from time import perf_counter
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.internal_auth import verify_internal_workflow_access
from app.schemas.cv import InternalCvExtractResponse, InternalCvResumeStageResponse, InternalCvValidateResponse
from app.services.cv_extraction import extract_cv_text, validate_extracted_cv_text

router = APIRouter()
logger = logging.getLogger(__name__)


def _duration_ms(started_at: float) -> int:
    return int((perf_counter() - started_at) * 1000)


@router.post(
    "/cv/{cv_id}/extract",
    response_model=InternalCvExtractResponse,
    dependencies=[Depends(verify_internal_workflow_access)],
)
async def extract_cv(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> InternalCvExtractResponse:
    started_at = perf_counter()
    logger.info("file_worker_stage_start cv_upload_id=%s stage=extract", cv_id)
    try:
        cv_upload, extracted_text = await extract_cv_text(db, cv_id)
    except HTTPException as exc:
        logger.warning(
            "file_worker_stage_failure cv_upload_id=%s stage=extract status_code=%s detail=%s duration_ms=%s",
            cv_id,
            exc.status_code,
            exc.detail,
            _duration_ms(started_at),
        )
        raise
    except Exception:
        logger.exception(
            "file_worker_stage_failure cv_upload_id=%s stage=extract status_code=500 detail=unexpected_error duration_ms=%s",
            cv_id,
            _duration_ms(started_at),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected extraction error. Please try again later.",
        )

    logger.info(
        "file_worker_stage_success cv_upload_id=%s stage=extract extracted_chars=%s duration_ms=%s",
        cv_id,
        len(extracted_text),
        _duration_ms(started_at),
    )
    return _build_resume_stage_response(cv_upload, extracted_text, response_model=InternalCvExtractResponse)


@router.post(
    "/cv/{cv_id}/validate",
    response_model=InternalCvValidateResponse,
    dependencies=[Depends(verify_internal_workflow_access)],
)
async def validate_cv(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> InternalCvValidateResponse:
    started_at = perf_counter()
    logger.info("file_worker_stage_start cv_upload_id=%s stage=validate", cv_id)
    try:
        cv_upload, extracted_text = await validate_extracted_cv_text(db, cv_id)
    except HTTPException as exc:
        logger.warning(
            "file_worker_stage_failure cv_upload_id=%s stage=validate status_code=%s detail=%s duration_ms=%s",
            cv_id,
            exc.status_code,
            exc.detail,
            _duration_ms(started_at),
        )
        raise
    except Exception:
        logger.exception(
            "file_worker_stage_failure cv_upload_id=%s stage=validate status_code=500 detail=unexpected_error duration_ms=%s",
            cv_id,
            _duration_ms(started_at),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected validation error. Please try again later.",
        )

    logger.info(
        "file_worker_stage_success cv_upload_id=%s stage=validate validated_chars=%s duration_ms=%s",
        cv_id,
        len(extracted_text),
        _duration_ms(started_at),
    )
    return _build_resume_stage_response(cv_upload, extracted_text, response_model=InternalCvValidateResponse)


def _build_resume_stage_response(
    cv_upload,
    extracted_text: str,
    *,
    response_model: type[InternalCvExtractResponse] | type[InternalCvValidateResponse] | type[InternalCvResumeStageResponse],
):
    return response_model(
        cv_upload_id=cv_upload.id,
        filename=cv_upload.filename,
        file_type=cv_upload.file_type,
        storage_key=cv_upload.storage_key,
        storage_url=cv_upload.storage_url,
        resume_text=extracted_text,
        job_description_text=cv_upload.job_description.description_text if cv_upload.job_description else None,
    )
