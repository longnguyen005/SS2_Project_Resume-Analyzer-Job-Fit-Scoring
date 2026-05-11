from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CvUpload
from app.services.cv_state import (
    FAILED_STAGE_EXTRACT,
    load_cv_with_job_description,
    mark_cv_failed,
    reset_cv_processing_state,
    utc_now,
)
from app.services.resume_parser import ResumeParseError, extract_text_from_resume
from app.services.resume_validation import validate_resume_text


async def extract_cv_text(db: AsyncSession, cv_upload_id: UUID) -> tuple[CvUpload, str]:
    cv_upload = await load_cv_with_job_description(db, cv_upload_id)
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")

    await reset_cv_processing_state(db, cv_upload)

    try:
        extracted_text = extract_text_from_resume(cv_upload.storage_path, cv_upload.file_type)
    except ResumeParseError as exc:
        await mark_cv_failed(db, cv_upload_id, str(exc), failed_stage=FAILED_STAGE_EXTRACT)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    cv_upload.extracted_text = extracted_text
    cv_upload.failure_reason = None
    cv_upload.failed_stage = None
    cv_upload.updated_at = utc_now()
    await db.commit()
    await db.refresh(cv_upload)
    return cv_upload, extracted_text


async def validate_extracted_cv_text(
    db: AsyncSession,
    cv_upload_id: UUID,
    extracted_text: str | None = None,
) -> tuple[CvUpload, str]:
    cv_upload = await load_cv_with_job_description(db, cv_upload_id)
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")

    resume_text = extracted_text if extracted_text is not None else (cv_upload.extracted_text or "")
    validation_result = validate_resume_text(resume_text)
    if not validation_result.is_valid:
        reason = validation_result.reason or "The uploaded document is not a resume."
        await mark_cv_failed(db, cv_upload_id, reason, failed_stage=FAILED_STAGE_EXTRACT)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=reason)

    await reset_cv_processing_state(db, cv_upload)
    return cv_upload, resume_text
