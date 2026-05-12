from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.internal_auth import verify_internal_workflow_access
from app.schemas.cv_internal import InternalCvCompleteRequest
from app.services.cv_persistence import complete_analysis_result
from app.worker_stage import run_worker_stage

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/cv/{cv_id}/complete",
    dependencies=[Depends(verify_internal_workflow_access)],
)
async def complete_cv(
    cv_id: UUID,
    payload: InternalCvCompleteRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    result = await run_worker_stage(
        logger=logger,
        event_prefix="persistence_worker_stage",
        cv_upload_id=cv_id,
        stage="complete",
        operation=lambda: complete_analysis_result(db, cv_id, payload),
        unexpected_detail="Could not save the analysis result. Please upload the file again or try again later.",
        unexpected_log_detail="save_failed",
        success_fields=lambda result: {
            "provider": result.provider_name or "unknown",
            "processing_time_seconds": result.processing_time_seconds,
            "result": "already_completed" if result.already_completed else "saved",
        },
    )
    return {"status": result.status}
