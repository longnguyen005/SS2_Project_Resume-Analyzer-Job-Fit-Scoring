"""Public API application entrypoint.

This app owns user-facing HTTP APIs, backend-only workflow helpers under
`/internal/cv`, and stuck-job recovery. Stage work is delegated to n8n and the
dedicated worker apps.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from sqlalchemy import select, text, update

from app.api.router import api_router
from app.core.app_factory import create_application, configure_logging
from app.core.config import settings
from app.db.session import async_session_factory, engine
from app.models import CvUpload

configure_logging()

logger = logging.getLogger(__name__)

STUCK_JOB_CHECK_INTERVAL_SECONDS = 300  # 5 minutes


async def _recover_stuck_jobs() -> None:
    """Periodically detect and fail CVs stuck in 'processing' beyond the TTL."""
    while True:
        await asyncio.sleep(STUCK_JOB_CHECK_INTERVAL_SECONDS)
        try:
            ttl = settings.n8n_processing_claim_ttl_seconds
            cutoff = datetime.now(timezone.utc) - timedelta(seconds=ttl)
            async with async_session_factory() as db:
                result = await db.execute(
                    select(CvUpload.id).where(
                        CvUpload.status == "processing",
                        CvUpload.updated_at < cutoff,
                    )
                )
                stuck_ids = [row[0] for row in result.all()]
                if stuck_ids:
                    await db.execute(
                        update(CvUpload)
                        .where(CvUpload.id.in_(stuck_ids))
                        .values(
                            status="failed",
                            failure_reason="Processing timed out. The analysis pipeline did not complete in time. Please upload the file again.",
                            failed_stage="orchestration",
                            updated_at=datetime.now(timezone.utc),
                        )
                    )
                    await db.commit()
                    logger.warning(
                        "event=stuck_jobs_recovered count=%s ttl_seconds=%s cv_ids=%s",
                        len(stuck_ids), ttl, [str(cid) for cid in stuck_ids],
                    )
        except Exception:
            logger.exception("event=stuck_job_recovery_error")


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(_recover_stuck_jobs())
    yield
    task.cancel()
    await engine.dispose()


app = create_application(
    title=settings.app_name,
    version="0.1.0-week6",
    router=api_router,
    prefix=settings.api_v1_prefix,
    lifespan=lifespan,
    include_cors=True,
    include_sessions=True,
)


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    async with engine.begin() as connection:
        await connection.execute(text("SELECT 1"))
    return {"status": "ok"}
