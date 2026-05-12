from __future__ import annotations

import asyncio
import logging
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import CvUpload
from app.services.cv_queries import load_cv_with_job_description
from app.services.cv_state import FAILED_STAGE_ORCHESTRATION, mark_cv_failed

logger = logging.getLogger(__name__)


class WorkflowTriggerError(RuntimeError):
    pass


async def trigger_cv_analysis_workflow_by_id(db: AsyncSession, cv_upload_id: UUID) -> bool:
    cv_upload = await load_cv_with_job_description(db, cv_upload_id)
    if cv_upload is None:
        return False

    try:
        return await trigger_cv_analysis_workflow(cv_upload)
    except WorkflowTriggerError as exc:
        logger.warning("n8n processing trigger failed for cv_upload_id=%s: %s", cv_upload_id, exc)
        await mark_cv_failed(
            db,
            cv_upload_id,
            str(exc),
            failed_stage=FAILED_STAGE_ORCHESTRATION,
        )
        return False


async def trigger_cv_analysis_workflow(cv_upload: CvUpload) -> bool:
    if not settings.n8n_is_configured:
        return False

    payload = {
        "cv_upload_id": str(cv_upload.id),
        "user_id": str(cv_upload.user_id),
        "job_description_id": str(cv_upload.job_description_id) if cv_upload.job_description_id else None,
        "file_type": cv_upload.file_type,
        "filename": cv_upload.filename,
        "stored_filename": cv_upload.stored_filename,
        "storage_path": cv_upload.storage_path,
        "storage_key": cv_upload.storage_key,
        "storage_url": cv_upload.storage_url,
        "status": cv_upload.status,
    }

    headers = {
        "x-internal-workflow-secret": settings.n8n_internal_shared_secret,
    }

    auth: tuple[str, str] | None = None
    if settings.n8n_basic_auth_user.strip() and settings.n8n_basic_auth_password.strip():
        auth = (settings.n8n_basic_auth_user, settings.n8n_basic_auth_password)

    timeout = max(settings.n8n_webhook_timeout_seconds, 1)
    max_attempts = max(settings.n8n_webhook_max_attempts, 1)
    last_error: Exception | None = None

    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(max_attempts):
            retry_count = attempt
            try:
                logger.info(
                    "n8n_webhook_trigger_attempt cv_upload_id=%s retry_count=%s timeout_seconds=%s",
                    cv_upload.id,
                    retry_count,
                    timeout,
                )
                response = await client.post(settings.n8n_webhook_url, json=payload, headers=headers, auth=auth)
                response.raise_for_status()
                logger.info(
                    "n8n_webhook_trigger_success cv_upload_id=%s retry_count=%s status_code=%s",
                    cv_upload.id,
                    retry_count,
                    response.status_code,
                )
                return True
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                last_error = exc
                logger.warning(
                    "n8n_webhook_trigger_failure cv_upload_id=%s retry_count=%s error=%s",
                    cv_upload.id,
                    retry_count,
                    exc,
                )
                if attempt == max_attempts - 1:
                    break
                await asyncio.sleep(0.8 * (2**attempt))

    raise WorkflowTriggerError(_format_workflow_error(last_error))


def _format_workflow_error(exc: Exception | None) -> str:
    if exc is None:
        return "Unknown n8n webhook error."
    if isinstance(exc, httpx.HTTPStatusError):
        return f"n8n webhook returned HTTP {exc.response.status_code}."
    if isinstance(exc, httpx.RequestError):
        return f"Could not reach n8n webhook: {exc}"
    return str(exc)
