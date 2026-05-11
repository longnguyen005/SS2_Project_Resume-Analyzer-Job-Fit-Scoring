from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models import AnalysisResult, CvUpload, JobDescription
from app.schemas.cv import CvStatusRead, CvUploadRead
from app.services.storage import StoredUpload

logger = logging.getLogger(__name__)

FAILED_STAGE_ORCHESTRATION = "orchestration"
FAILED_STAGE_EXTRACT = "extract"
FAILED_STAGE_ANALYZE = "analyze"
FAILED_STAGE_COMPLETE = "complete"

CLAIM_STATUS_CLAIMED = "claimed"
CLAIM_STATUS_ALREADY_PROCESSING = "already_processing"
CLAIM_STATUS_ALREADY_COMPLETED = "already_completed"


class CvStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def create_cv_upload_record(
    db: AsyncSession,
    *,
    user_id: UUID,
    job_description_id: UUID | None,
    filename: str,
    stored_upload: StoredUpload,
    file_type: str,
) -> CvUpload:
    cv_upload = CvUpload(
        user_id=user_id,
        job_description_id=job_description_id,
        filename=filename or stored_upload.stored_filename,
        stored_filename=stored_upload.stored_filename,
        storage_path=stored_upload.storage_path,
        storage_key=stored_upload.storage_key,
        storage_url=stored_upload.storage_url,
        file_type=file_type,
        file_size_bytes=stored_upload.file_size_bytes,
        status=CvStatus.PENDING,
        failure_reason=None,
        failed_stage=None,
    )
    db.add(cv_upload)
    await db.commit()
    await db.refresh(cv_upload)
    return cv_upload


async def list_user_cv_uploads(db: AsyncSession, user_id: UUID) -> list[CvUpload]:
    result = await db.execute(
        select(CvUpload)
        .options(selectinload(CvUpload.analysis_results))
        .where(CvUpload.user_id == user_id)
        .order_by(CvUpload.created_at.desc())
    )
    return list(result.scalars().all())


async def ensure_job_description_owned_by_user(
    db: AsyncSession,
    job_description_id: UUID,
    user_id: UUID,
) -> None:
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_description_id,
            JobDescription.user_id == user_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")


async def get_user_cv_upload(
    db: AsyncSession,
    cv_upload_id: UUID,
    user_id: UUID,
    *,
    include_analysis_details: bool = False,
) -> CvUpload | None:
    query = select(CvUpload).where(CvUpload.id == cv_upload_id, CvUpload.user_id == user_id)
    if include_analysis_details:
        query = query.options(
            selectinload(CvUpload.analysis_results).selectinload(AnalysisResult.category_scores),
            selectinload(CvUpload.analysis_results).selectinload(AnalysisResult.suggestions),
        )
    else:
        query = query.options(selectinload(CvUpload.analysis_results))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def load_cv_with_job_description(db: AsyncSession, cv_upload_id: UUID) -> CvUpload | None:
    result = await db.execute(
        select(CvUpload)
        .options(
            selectinload(CvUpload.job_description),
            selectinload(CvUpload.analysis_results).selectinload(AnalysisResult.category_scores),
            selectinload(CvUpload.analysis_results).selectinload(AnalysisResult.suggestions),
        )
        .where(CvUpload.id == cv_upload_id)
    )
    return result.scalar_one_or_none()


def get_latest_analysis_result(cv_upload: CvUpload) -> AnalysisResult | None:
    if not cv_upload.analysis_results:
        return None
    return max(cv_upload.analysis_results, key=lambda item: item.updated_at)


def serialize_cv_upload(cv_upload: CvUpload) -> CvUploadRead:
    return CvUploadRead.model_validate(cv_upload)


def serialize_cv_status(cv_upload: CvUpload) -> CvStatusRead:
    return CvStatusRead(
        id=cv_upload.id,
        status=cv_upload.status,
        failure_reason=cv_upload.failure_reason,
        failed_stage=cv_upload.failed_stage,
        updated_at=cv_upload.updated_at,
    )


async def claim_cv_processing(db: AsyncSession, cv_upload_id: UUID) -> tuple[CvUpload | None, str | None]:
    cv_upload = await load_cv_with_job_description(db, cv_upload_id)
    if cv_upload is None:
        return None, None

    latest_analysis = get_latest_analysis_result(cv_upload)
    if cv_upload.status == CvStatus.COMPLETED and latest_analysis is not None:
        logger.info(
            "event=cv_claim_skip cv_upload_id=%s reason=already_completed",
            cv_upload_id,
        )
        return cv_upload, CLAIM_STATUS_ALREADY_COMPLETED

    if cv_upload.status == CvStatus.PROCESSING:
        age_seconds = max((utc_now() - cv_upload.updated_at).total_seconds(), 0)
        if age_seconds < settings.n8n_processing_claim_ttl_seconds:
            logger.info(
                "event=cv_claim_skip cv_upload_id=%s reason=already_processing age_seconds=%.0f",
                cv_upload_id,
                age_seconds,
            )
            return cv_upload, CLAIM_STATUS_ALREADY_PROCESSING
        logger.warning(
            "event=cv_claim_expired cv_upload_id=%s age_seconds=%.0f ttl_seconds=%s",
            cv_upload_id,
            age_seconds,
            settings.n8n_processing_claim_ttl_seconds,
        )

    cv_upload.status = CvStatus.PROCESSING
    cv_upload.failure_reason = None
    cv_upload.failed_stage = None
    cv_upload.updated_at = utc_now()
    await db.commit()
    await db.refresh(cv_upload)
    logger.info("event=cv_claimed cv_upload_id=%s", cv_upload_id)
    return cv_upload, CLAIM_STATUS_CLAIMED


async def mark_cv_failed(
    db: AsyncSession,
    cv_upload_id: UUID,
    failure_reason: str,
    failed_stage: str | None = None,
) -> None:
    cv_upload = await load_cv_with_job_description(db, cv_upload_id)
    if cv_upload is None:
        return

    latest_analysis = get_latest_analysis_result(cv_upload)
    if cv_upload.status == CvStatus.COMPLETED and latest_analysis is not None:
        logger.info(
            "event=cv_fail_skip cv_upload_id=%s reason=already_completed",
            cv_upload_id,
        )
        return

    cv_upload.status = CvStatus.FAILED
    cv_upload.failure_reason = failure_reason
    cv_upload.failed_stage = failed_stage
    cv_upload.updated_at = utc_now()
    await db.commit()
    logger.warning(
        "event=cv_marked_failed cv_upload_id=%s stage=%s reason=%s",
        cv_upload_id,
        failed_stage or "unknown",
        failure_reason,
    )


async def reset_cv_processing_state(db: AsyncSession, cv_upload: CvUpload) -> None:
    cv_upload.status = CvStatus.PROCESSING
    cv_upload.failure_reason = None
    cv_upload.failed_stage = None
    cv_upload.updated_at = utc_now()
    await db.commit()
    await db.refresh(cv_upload)
