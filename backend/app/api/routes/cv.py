from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.db.session import async_session_factory
from app.models import User
from app.schemas.common import APIResponse
from app.schemas.cv import CvHistoryItemRead, CvResultRead, CvStatusRead, CvUploadRead
from app.services.cv_persistence import build_cv_history_reads, build_cv_result_read
from app.services.cv_state import (
    create_cv_upload_record,
    ensure_job_description_owned_by_user,
    get_latest_analysis_result,
    get_user_cv_upload,
    list_user_cv_uploads,
    serialize_cv_status,
    serialize_cv_upload,
)
from app.services.storage import StorageServiceError, save_upload
from app.services.workflow_trigger import trigger_cv_analysis_workflow_by_id

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=APIResponse[CvUploadRead], status_code=status.HTTP_201_CREATED)
async def upload_cv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_description_id: UUID | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[CvUploadRead]:
    if not settings.n8n_is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="n8n processing is enabled but not fully configured.",
        )

    if job_description_id is not None:
        await ensure_job_description_owned_by_user(db, job_description_id, current_user.id)

    try:
        stored_upload = await save_upload(file, str(current_user.id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except StorageServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    file_type = (file.filename or "").split(".")[-1].lower()
    cv_upload = await create_cv_upload_record(
        db,
        user_id=current_user.id,
        job_description_id=job_description_id,
        filename=file.filename or stored_upload.stored_filename,
        stored_upload=stored_upload,
        file_type=file_type,
    )

    logger.info(
        "event=cv_upload_created cv_upload_id=%s user_id=%s filename=%s file_type=%s file_size_bytes=%s jd_id=%s",
        cv_upload.id,
        current_user.id,
        cv_upload.filename,
        cv_upload.file_type,
        cv_upload.file_size_bytes,
        job_description_id,
    )

    background_tasks.add_task(_trigger_n8n_processing, cv_upload.id)

    return APIResponse(
        message="CV uploaded successfully. Analysis has started in the background.",
        data=serialize_cv_upload(cv_upload),
    )


@router.get("", response_model=APIResponse[list[CvHistoryItemRead]])
async def list_cv_uploads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[CvHistoryItemRead]]:
    items = build_cv_history_reads(await list_user_cv_uploads(db, current_user.id))
    return APIResponse(message="CV uploads retrieved successfully.", data=items)


@router.get("/{cv_id}", response_model=APIResponse[CvUploadRead])
async def get_cv_upload(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[CvUploadRead]:
    cv_upload = await get_user_cv_upload(db, cv_id, current_user.id)
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")
    return APIResponse(message="CV upload retrieved successfully.", data=serialize_cv_upload(cv_upload))


@router.get("/{cv_id}/status", response_model=APIResponse[CvStatusRead])
async def get_cv_status(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[CvStatusRead]:
    cv_upload = await get_user_cv_upload(db, cv_id, current_user.id)
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")

    return APIResponse(
        message="CV status retrieved successfully.",
        data=serialize_cv_status(cv_upload),
    )


@router.get("/{cv_id}/result", response_model=APIResponse[CvResultRead])
async def get_cv_result(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[CvResultRead]:
    cv_upload = await get_user_cv_upload(db, cv_id, current_user.id, include_analysis_details=True)
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")

    if cv_upload.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=cv_upload.failure_reason or "CV analysis is not completed yet",
        )

    analysis_result = get_latest_analysis_result(cv_upload)
    if analysis_result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV analysis result not found")

    return APIResponse(
        message="CV result retrieved successfully.",
        data=build_cv_result_read(cv_upload, analysis_result),
    )


async def _trigger_n8n_processing(cv_upload_id: UUID) -> None:
    async with async_session_factory() as db:
        await trigger_cv_analysis_workflow_by_id(db, cv_upload_id)
