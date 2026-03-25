from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import CvUpload, JobDescription, User
from app.schemas.cv import CvStatusRead, CvUploadRead
from app.services.storage import save_upload

router = APIRouter()


@router.post("/upload", response_model=CvUploadRead, status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    job_description_id: UUID | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CvUpload:
    if job_description_id is not None:
        result = await db.execute(
            select(JobDescription).where(
                JobDescription.id == job_description_id,
                JobDescription.user_id == current_user.id,
            )
        )
        job_description = result.scalar_one_or_none()
        if job_description is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")

    try:
        stored_filename, storage_path, file_size = await save_upload(file, str(current_user.id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    file_type = (file.filename or "").split(".")[-1].lower()
    cv_upload = CvUpload(
        user_id=current_user.id,
        job_description_id=job_description_id,
        filename=file.filename or stored_filename,
        stored_filename=stored_filename,
        storage_path=storage_path,
        file_type=file_type,
        file_size_bytes=file_size,
        status="pending",
    )
    db.add(cv_upload)
    await db.commit()
    await db.refresh(cv_upload)
    return cv_upload


@router.get("", response_model=list[CvUploadRead])
async def list_cv_uploads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CvUpload]:
    result = await db.execute(
        select(CvUpload).where(CvUpload.user_id == current_user.id).order_by(CvUpload.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{cv_id}", response_model=CvUploadRead)
async def get_cv_upload(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CvUpload:
    result = await db.execute(
        select(CvUpload).where(CvUpload.id == cv_id, CvUpload.user_id == current_user.id)
    )
    cv_upload = result.scalar_one_or_none()
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")
    return cv_upload


@router.get("/{cv_id}/status", response_model=CvStatusRead)
async def get_cv_status(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CvStatusRead:
    result = await db.execute(
        select(CvUpload).where(CvUpload.id == cv_id, CvUpload.user_id == current_user.id)
    )
    cv_upload = result.scalar_one_or_none()
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")
    return CvStatusRead(id=cv_upload.id, status=cv_upload.status, updated_at=cv_upload.updated_at)
