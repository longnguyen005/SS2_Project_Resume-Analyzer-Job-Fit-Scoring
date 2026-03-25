from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import JobDescription, User
from app.schemas.jd import JobDescriptionCreate, JobDescriptionRead, JobDescriptionUpdate

router = APIRouter()


@router.post("", response_model=JobDescriptionRead, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    payload: JobDescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescription:
    job_description = JobDescription(
        user_id=current_user.id,
        title=payload.title,
        description_text=payload.description_text,
    )
    db.add(job_description)
    await db.commit()
    await db.refresh(job_description)
    return job_description


@router.get("", response_model=list[JobDescriptionRead])
async def list_job_descriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[JobDescription]:
    result = await db.execute(
        select(JobDescription)
        .where(JobDescription.user_id == current_user.id)
        .order_by(JobDescription.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{jd_id}", response_model=JobDescriptionRead)
async def get_job_description(
    jd_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescription:
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == jd_id,
            JobDescription.user_id == current_user.id,
        )
    )
    job_description = result.scalar_one_or_none()
    if job_description is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
    return job_description


@router.put("/{jd_id}", response_model=JobDescriptionRead)
async def update_job_description(
    jd_id: UUID,
    payload: JobDescriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescription:
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
    return job_description


@router.delete(
    "/{jd_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
async def delete_job_description(
    jd_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
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
    return Response(status_code=status.HTTP_204_NO_CONTENT)
