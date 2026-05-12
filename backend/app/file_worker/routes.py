from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.internal_auth import verify_internal_workflow_access
from app.schemas.cv_internal import InternalCvExtractResponse, InternalCvValidateResponse
from app.services.cv_extraction import build_resume_stage_response, extract_cv_text, validate_extracted_cv_text
from app.worker_stage import run_worker_stage

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/cv/{cv_id}/extract",
    response_model=InternalCvExtractResponse,
    dependencies=[Depends(verify_internal_workflow_access)],
)
async def extract_cv(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> InternalCvExtractResponse:
    cv_upload, extracted_text = await run_worker_stage(
        logger=logger,
        event_prefix="file_worker_stage",
        cv_upload_id=cv_id,
        stage="extract",
        operation=lambda: extract_cv_text(db, cv_id),
        unexpected_detail="Unexpected extraction error. Please try again later.",
        success_fields=lambda result: {"extracted_chars": len(result[1])},
    )
    return build_resume_stage_response(cv_upload, extracted_text, response_model=InternalCvExtractResponse)


@router.post(
    "/cv/{cv_id}/validate",
    response_model=InternalCvValidateResponse,
    dependencies=[Depends(verify_internal_workflow_access)],
)
async def validate_cv(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> InternalCvValidateResponse:
    cv_upload, extracted_text = await run_worker_stage(
        logger=logger,
        event_prefix="file_worker_stage",
        cv_upload_id=cv_id,
        stage="validate",
        operation=lambda: validate_extracted_cv_text(db, cv_id),
        unexpected_detail="Unexpected validation error. Please try again later.",
        success_fields=lambda result: {"validated_chars": len(result[1])},
    )
    return build_resume_stage_response(cv_upload, extracted_text, response_model=InternalCvValidateResponse)
