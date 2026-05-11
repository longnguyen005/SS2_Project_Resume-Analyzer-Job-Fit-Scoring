from __future__ import annotations

import logging
from time import perf_counter
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.internal_auth import verify_internal_workflow_access
from app.schemas.cv import InternalCvCompleteRequest
from app.services.cv_persistence import deserialize_complete_payload, save_analysis_result
from app.services.cv_state import get_latest_analysis_result, load_cv_with_job_description

router = APIRouter()
logger = logging.getLogger(__name__)


def _duration_ms(started_at: float) -> int:
    return int((perf_counter() - started_at) * 1000)


@router.post(
    "/cv/{cv_id}/complete",
    dependencies=[Depends(verify_internal_workflow_access)],
)
async def complete_cv(
    cv_id: UUID,
    payload: InternalCvCompleteRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    started_at = perf_counter()
    logger.info("persistence_worker_stage_start cv_upload_id=%s stage=complete", cv_id)
    cv_upload = await load_cv_with_job_description(db, cv_id)
    if cv_upload is None:
        logger.warning(
            "persistence_worker_stage_failure cv_upload_id=%s stage=complete status_code=404 detail=CV upload not found duration_ms=%s",
            cv_id,
            _duration_ms(started_at),
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")

    latest_analysis = get_latest_analysis_result(cv_upload)
    if cv_upload.status == "completed" and latest_analysis is not None:
        logger.info(
            "persistence_worker_stage_success cv_upload_id=%s stage=complete result=already_completed duration_ms=%s",
            cv_id,
            _duration_ms(started_at),
        )
        return {"status": "completed"}

    analysis_payload = deserialize_complete_payload(payload)
    try:
        await save_analysis_result(
            db=db,
            cv_upload_id=cv_id,
            analysis_payload=analysis_payload,
            provider_name=payload.provider_name,
            processing_time_seconds=payload.processing_time_seconds,
        )
    except HTTPException as exc:
        logger.warning(
            "persistence_worker_stage_failure cv_upload_id=%s stage=complete status_code=%s detail=%s duration_ms=%s",
            cv_id,
            exc.status_code,
            exc.detail,
            _duration_ms(started_at),
        )
        raise
    except Exception:
        logger.exception(
            "persistence_worker_stage_failure cv_upload_id=%s stage=complete status_code=500 detail=save_failed duration_ms=%s",
            cv_id,
            _duration_ms(started_at),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save the analysis result. Please upload the file again or try again later.",
        )

    logger.info(
        "persistence_worker_stage_success cv_upload_id=%s stage=complete provider=%s processing_time_seconds=%s duration_ms=%s",
        cv_id,
        payload.provider_name,
        payload.processing_time_seconds,
        _duration_ms(started_at),
    )
    return {"status": "completed"}

