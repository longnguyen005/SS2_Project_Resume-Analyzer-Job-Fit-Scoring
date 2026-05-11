from __future__ import annotations

import logging
from time import perf_counter
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.internal_auth import verify_internal_workflow_access
from app.schemas.cv import InternalCvClaimResponse, InternalCvFailRequest
from app.services.cv_state import claim_cv_processing, mark_cv_failed

router = APIRouter()
logger = logging.getLogger(__name__)


def _duration_ms(started_at: float) -> int:
    return int((perf_counter() - started_at) * 1000)


@router.post(
    "/{cv_id}/claim",
    response_model=InternalCvClaimResponse,
    dependencies=[Depends(verify_internal_workflow_access)],
)
async def claim_cv(
    cv_id: UUID,
    x_n8n_retry_count: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> InternalCvClaimResponse:
    started_at = perf_counter()
    cv_upload, claim_status = await claim_cv_processing(db, cv_id)
    if cv_upload is None or claim_status is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")

    logger.info(
        "cv_processing_claim cv_upload_id=%s claim_status=%s retry_count=%s duration_ms=%s",
        cv_upload.id,
        claim_status,
        x_n8n_retry_count or "0",
        _duration_ms(started_at),
    )

    return InternalCvClaimResponse(
        cv_upload_id=cv_upload.id,
        claim_status=claim_status,
    )


@router.post(
    "/{cv_id}/fail",
    dependencies=[Depends(verify_internal_workflow_access)],
)
async def fail_cv(
    cv_id: UUID,
    payload: InternalCvFailRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    logger.warning(
        "cv_stage_failure_sync cv_upload_id=%s stage=%s detail=%s duration_ms=0",
        cv_id,
        payload.failed_stage or "unknown",
        payload.failure_reason,
    )
    await mark_cv_failed(db, cv_id, payload.failure_reason, failed_stage=payload.failed_stage)
    return {"status": "failed"}

