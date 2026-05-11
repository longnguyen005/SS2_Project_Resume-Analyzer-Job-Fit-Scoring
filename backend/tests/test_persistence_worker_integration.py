from __future__ import annotations

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import httpx
from fastapi import FastAPI
from sqlalchemy import delete, select, text

from app.core.config import settings
from app.db.session import async_session_factory, engine
from app.models import AnalysisResult, CvUpload, JobDescription, User
from app.persistence_worker import routes as persistence_worker
from app.persistence_worker.routes import router as persistence_worker_router


class PersistenceWorkerIntegrationTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client: httpx.AsyncClient | None = None
        self.user_id = None
        self.cv_upload_id = None
        self.job_description_id = None

        await engine.dispose()

        try:
            async with async_session_factory() as db:
                await db.execute(text("SELECT 1"))

                user = User(
                    email=f"persistence-worker-{uuid4()}@example.com",
                    hashed_password="hashed-password",
                    full_name="Persistence Worker Test",
                    is_active=True,
                )
                db.add(user)
                await db.flush()

                job_description = JobDescription(
                    user_id=user.id,
                    title="Backend Engineer",
                    description_text="Build backend systems with Python, FastAPI, and PostgreSQL.",
                )
                db.add(job_description)
                await db.flush()

                cv_upload = CvUpload(
                    user_id=user.id,
                    job_description_id=job_description.id,
                    filename="resume.pdf",
                    stored_filename="resume.pdf",
                    storage_path="/tmp/resume.pdf",
                    storage_key=None,
                    storage_url=None,
                    file_type="pdf",
                    file_size_bytes=1024,
                    status="processing",
                    failure_reason=None,
                    failed_stage=None,
                    extracted_text="Python backend engineer resume text.",
                )
                db.add(cv_upload)
                await db.commit()

                self.user_id = user.id
                self.job_description_id = job_description.id
                self.cv_upload_id = cv_upload.id
        except Exception as exc:
            self.skipTest(f"Integration database is not available in this environment: {exc}")

        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=_build_test_app()),
            base_url="http://testserver",
        )

    async def asyncTearDown(self) -> None:
        if self.client is not None:
            await self.client.aclose()

        if self.user_id is None:
            return

        async with async_session_factory() as db:
            await db.execute(delete(CvUpload).where(CvUpload.user_id == self.user_id))
            await db.execute(delete(JobDescription).where(JobDescription.user_id == self.user_id))
            await db.execute(delete(User).where(User.id == self.user_id))
            await db.commit()

        await engine.dispose()

    async def test_persistence_worker_complete_success(self) -> None:
        assert self.client is not None
        headers = {"x-internal-workflow-secret": settings.n8n_internal_shared_secret}

        with self.assertLogs("app.persistence_worker.routes", level="INFO") as captured_logs:
            response = await self.client.post(
                f"/api/v1/persistence-worker/cv/{self.cv_upload_id}/complete",
                headers=headers,
                json=_build_complete_payload(),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "completed")
        self.assertTrue(
            any("stage=complete" in line and "persistence_worker_stage_success" in line for line in captured_logs.output)
        )

        async with async_session_factory() as db:
            cv_upload = await db.scalar(select(CvUpload).where(CvUpload.id == self.cv_upload_id))
            analysis_result = await db.scalar(select(AnalysisResult).where(AnalysisResult.cv_upload_id == self.cv_upload_id))

        self.assertIsNotNone(cv_upload)
        self.assertEqual(cv_upload.status, "completed")
        self.assertIsNone(cv_upload.failure_reason)
        self.assertIsNone(cv_upload.failed_stage)
        self.assertIsNotNone(analysis_result)
        self.assertEqual(analysis_result.ai_provider, "integration-test-provider")

    async def test_persistence_worker_complete_save_fail_returns_500(self) -> None:
        assert self.client is not None
        headers = {"x-internal-workflow-secret": settings.n8n_internal_shared_secret}

        with (
            patch.object(
                persistence_worker,
                "save_analysis_result",
                new=AsyncMock(side_effect=RuntimeError("database write failed")),
            ),
            self.assertLogs("app.persistence_worker.routes", level="INFO") as captured_logs,
        ):
            response = await self.client.post(
                f"/api/v1/persistence-worker/cv/{self.cv_upload_id}/complete",
                headers=headers,
                json=_build_complete_payload(),
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()["detail"],
            "Could not save the analysis result. Please upload the file again or try again later.",
        )
        self.assertTrue(
            any("stage=complete" in line and "status_code=500" in line for line in captured_logs.output)
        )


def _build_complete_payload() -> dict:
    return {
        "provider_name": "integration-test-provider",
        "processing_time_seconds": 1.23,
        "analysis": {
            "overall_score": 84,
            "grade": "Very Good",
            "summary": "Resume shows direct Python backend experience and relevant stack alignment.",
            "breakdown": [
                {"title": "Skills", "score": 85, "status": "Excellent", "tone": "navy"},
                {"title": "Experience", "score": 82, "status": "Good", "tone": "navy"},
                {"title": "Education", "score": 78, "status": "Good", "tone": "navy"},
                {"title": "Resume Format", "score": 86, "status": "Excellent", "tone": "navy"},
            ],
            "skill_chart": [
                {"label": "Technical", "value": 88},
                {"label": "Leadership", "value": 62},
                {"label": "Communication", "value": 76},
                {"label": "Problem Solving", "value": 84},
            ],
            "content_quality": [
                {"label": "Strong", "value": "45%", "tone": "green"},
                {"label": "Good", "value": "35%", "tone": "blue"},
                {"label": "Needs Work", "value": "20%", "tone": "orange"},
            ],
            "strengths": [
                "Direct Python backend development experience",
                "Relevant FastAPI and PostgreSQL stack",
                "Clear API-focused project evidence",
            ],
            "improvements": [
                "Could add more quantified impact",
                "Could clarify ownership scope",
                "Could improve structure consistency",
            ],
            "suggestions": [
                {
                    "title": "Add metrics",
                    "description": "Quantify backend impact with latency, throughput, or scale numbers.",
                    "priority": "High Priority",
                    "tone": "red",
                },
                {
                    "title": "Clarify ownership",
                    "description": "State which systems or modules were owned directly.",
                    "priority": "Medium Priority",
                    "tone": "yellow",
                },
                {
                    "title": "Improve formatting",
                    "description": "Use more consistent section spacing and bullet structure.",
                    "priority": "Low Priority",
                    "tone": "blue",
                },
            ],
        },
    }


def _build_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(persistence_worker_router, prefix=f"{settings.api_v1_prefix}/persistence-worker")
    return test_app
