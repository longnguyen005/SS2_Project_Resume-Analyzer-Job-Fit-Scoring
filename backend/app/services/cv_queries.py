from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import AnalysisResult, CvUpload, JobDescription


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
