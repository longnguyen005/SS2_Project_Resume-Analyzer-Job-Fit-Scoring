from __future__ import annotations

from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

import httpx
from fastapi import FastAPI
from sqlalchemy import delete, select, text

from app.api.routes import internal_workflow
from app.core.config import settings
from app.db.session import async_session_factory, engine
from app.models import AnalysisResult, CvUpload, JobDescription, User


class DuplicateTriggerIntegrationTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client: httpx.AsyncClient | None = None
        self.user_id = None
        self.job_description_id = None
        self.cv_upload_id = None

        await engine.dispose()

        try:
            async with async_session_factory() as db:
                await db.execute(text("SELECT 1"))

                user = User(
                    email=f"duplicate-trigger-{uuid4()}@example.com",
                    hashed_password="hashed-password",
                    full_name="Duplicate Trigger Test",
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
                    status="pending",
                    failure_reason=None,
                    failed_stage=None,
                    extracted_text="Python developer with FastAPI, SQLAlchemy, PostgreSQL and REST API experience.",
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

    async def test_duplicate_claim_returns_already_processing_on_second_request(self) -> None:
        assert self.client is not None
        headers = {"x-internal-workflow-secret": settings.n8n_internal_shared_secret}

        with self.assertLogs("app.api.routes.internal_workflow", level="INFO") as captured_logs:
            first_response = await self.client.post(
                f"/api/v1/internal/cv/{self.cv_upload_id}/claim",
                headers={**headers, "x-n8n-retry-count": "0"},
            )
            second_response = await self.client.post(
                f"/api/v1/internal/cv/{self.cv_upload_id}/claim",
                headers={**headers, "x-n8n-retry-count": "1"},
            )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(first_response.json()["claim_status"], "claimed")
        self.assertEqual(second_response.json()["claim_status"], "already_processing")
        self.assertTrue(
            any(
                f"cv_upload_id={self.cv_upload_id}" in line
                and "claim_status=already_processing" in line
                and "retry_count=1" in line
                for line in captured_logs.output
            )
        )

        async with async_session_factory() as db:
            cv_upload = await db.scalar(select(CvUpload).where(CvUpload.id == self.cv_upload_id))

        self.assertIsNotNone(cv_upload)
        self.assertEqual(cv_upload.status, "processing")
        self.assertIsNone(cv_upload.failure_reason)
        self.assertIsNone(cv_upload.failed_stage)

    async def test_stale_fail_does_not_override_completed_upload_after_duplicate_flow(self) -> None:
        assert self.client is not None
        headers = {"x-internal-workflow-secret": settings.n8n_internal_shared_secret}

        claim_response = await self.client.post(
            f"/api/v1/internal/cv/{self.cv_upload_id}/claim",
            headers={**headers, "x-n8n-retry-count": "0"},
        )
        self.assertEqual(claim_response.status_code, 200)
        self.assertEqual(claim_response.json()["claim_status"], "claimed")

        async with async_session_factory() as db:
            analysis_result = AnalysisResult(
                cv_upload_id=self.cv_upload_id,
                job_description_id=self.job_description_id,
                overall_score=84,
                raw_ai_response={"grade": "Very Good", "summary": "Stored result"},
                ai_provider="integration-test-provider",
                token_usage=None,
                processing_time_seconds=1.23,
            )
            db.add(analysis_result)

            cv_upload = await db.scalar(select(CvUpload).where(CvUpload.id == self.cv_upload_id))
            self.assertIsNotNone(cv_upload)
            cv_upload.status = "completed"
            cv_upload.failure_reason = None
            cv_upload.failed_stage = None
            await db.commit()

        with self.assertLogs("app.api.routes.internal_workflow", level="WARNING") as captured_logs:
            stale_fail_response = await self.client.post(
                f"/api/v1/internal/cv/{self.cv_upload_id}/fail",
                headers=headers,
                json={
                    "failure_reason": "Late retry branch should not override completed data.",
                    "failed_stage": "analyze",
                },
            )

        self.assertEqual(stale_fail_response.status_code, 200)
        self.assertEqual(stale_fail_response.json()["status"], "failed")
        self.assertTrue(
            any(
                f"cv_upload_id={self.cv_upload_id}" in line
                and "stage=analyze" in line
                for line in captured_logs.output
            )
        )

        async with async_session_factory() as db:
            cv_upload = await db.scalar(select(CvUpload).where(CvUpload.id == self.cv_upload_id))

        self.assertIsNotNone(cv_upload)
        self.assertEqual(cv_upload.status, "completed")
        self.assertIsNone(cv_upload.failure_reason)
        self.assertIsNone(cv_upload.failed_stage)

        completed_claim_response = await self.client.post(
            f"/api/v1/internal/cv/{self.cv_upload_id}/claim",
            headers={**headers, "x-n8n-retry-count": "2"},
        )
        self.assertEqual(completed_claim_response.status_code, 200)
        self.assertEqual(completed_claim_response.json()["claim_status"], "already_completed")


def _build_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(internal_workflow.router, prefix=f"{settings.api_v1_prefix}/internal/cv")
    return test_app
