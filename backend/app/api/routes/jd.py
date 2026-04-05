from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import JobDescription, User
from app.schemas.jd import JobDescriptionCreate, JobDescriptionRead, JobDescriptionUpdate
from app.schemas.common import APIResponse

router = APIRouter()


@router.post("", response_model=APIResponse[JobDescriptionRead], status_code=status.HTTP_201_CREATED)
async def create_job_description(
    payload: JobDescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[JobDescriptionRead]:
    job_description = JobDescription(
        user_id=current_user.id,
        title=payload.title,
        description_text=payload.description_text,
    )
    db.add(job_description)
    await db.commit()
    await db.refresh(job_description)
    return APIResponse(
        message="Job description created successfully.",
        data=JobDescriptionRead.model_validate(job_description),
    )


@router.get("", response_model=APIResponse[list[JobDescriptionRead]])
async def list_job_descriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[JobDescriptionRead]]:
    result = await db.execute(
        select(JobDescription)
        .where(JobDescription.user_id == current_user.id)
        .order_by(JobDescription.created_at.desc())
    )
    items = [JobDescriptionRead.model_validate(item) for item in result.scalars().all()]
    return APIResponse(message="Job descriptions retrieved successfully.", data=items)


@router.get("/{jd_id}", response_model=APIResponse[JobDescriptionRead])
async def get_job_description(
    jd_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[JobDescriptionRead]:
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == jd_id,
            JobDescription.user_id == current_user.id,
        )
    )
    job_description = result.scalar_one_or_none()
    if job_description is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
    return APIResponse(
        message="Job description retrieved successfully.",
        data=JobDescriptionRead.model_validate(job_description),
    )


@router.put("/{jd_id}", response_model=APIResponse[JobDescriptionRead])
async def update_job_description(
    jd_id: UUID,
    payload: JobDescriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[JobDescriptionRead]:
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == jd_id,
            JobDescription.user_id == current_user.id,
        )
    )
    job_description = result.scalar_one_or_none()
    if job_description is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(job_description, field, value)

    await db.commit()
    await db.refresh(job_description)
    return APIResponse(
        message="Job description updated successfully.",
        data=JobDescriptionRead.model_validate(job_description),
    )


@router.delete("/{jd_id}", response_model=APIResponse[dict[str, str]])
async def delete_job_description(
    jd_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[dict[str, str]]:
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == jd_id,
            JobDescription.user_id == current_user.id,
        )
    )
    job_description = result.scalar_one_or_none()
    if job_description is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")

    await db.delete(job_description)
    await db.commit()
    return APIResponse(message="Job description deleted successfully.", data={"id": str(jd_id)})
