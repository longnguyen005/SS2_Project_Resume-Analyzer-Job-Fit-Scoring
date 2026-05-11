from __future__ import annotations

import asyncio
import shutil
import tempfile
from pathlib import Path
from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

import httpx
from sqlalchemy import delete, select, text

from app.core.config import settings
from app.db.session import async_session_factory, engine
from app.models import AnalysisResult, CvUpload, JobDescription, User


class N8NWebhookBlackboxIntegrationTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.user_id = None
        self.job_description_id = None
        self.cv_upload_id = None
        self._temp_dirs: list[str] = []

        await engine.dispose()

        try:
            async with async_session_factory() as db:
                await db.execute(text("SELECT 1"))

                user = User(
                    email=f"n8n-webhook-blackbox-{uuid4()}@example.com",
                    hashed_password="hashed-password",
                    full_name="n8n Webhook Blackbox Test",
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
                await db.commit()

                self.user_id = user.id
                self.job_description_id = job_description.id
        except Exception as exc:
            self.skipTest(f"Integration database is not available in this environment: {exc}")

    async def asyncTearDown(self) -> None:
        if self.user_id is not None:
            async with async_session_factory() as db:
                await db.execute(delete(CvUpload).where(CvUpload.user_id == self.user_id))
                await db.execute(delete(JobDescription).where(JobDescription.user_id == self.user_id))
                await db.execute(delete(User).where(User.id == self.user_id))
                await db.commit()

        for temp_dir in self._temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)

        await engine.dispose()

    async def test_webhook_invalid_resume_marks_failed_blackbox(self) -> None:
        assert self.user_id is not None
        assert self.job_description_id is not None

        invalid_docx_path = self._create_docx(
            "meeting-notes.docx",
            [
                "Weekly meeting agenda",
                "Discuss classroom schedule and admin notes",
                "Coordinate homework follow-up and attendance",
            ],
        )

        async with async_session_factory() as db:
            cv_upload = CvUpload(
                user_id=self.user_id,
                job_description_id=self.job_description_id,
                filename="meeting-notes.docx",
                stored_filename="meeting-notes.docx",
                storage_path=invalid_docx_path,
                storage_key=None,
                storage_url=None,
                file_type="docx",
                file_size_bytes=2048,
                status="pending",
                failure_reason=None,
                failed_stage=None,
                extracted_text=None,
            )
            db.add(cv_upload)
            await db.commit()
            await db.refresh(cv_upload)
            self.cv_upload_id = cv_upload.id

        response = await self._post_webhook(self.cv_upload_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "failed")

        status, failure_reason, failed_stage = await self._wait_for_cv_state(self.cv_upload_id)
        self.assertEqual(status, "failed")
        self.assertEqual(failed_stage, "extract")
        self.assertIsNotNone(failure_reason)
        self.assertIn("does not appear to be a resume or CV", failure_reason)

    async def test_webhook_already_completed_returns_completed_blackbox(self) -> None:
        assert self.user_id is not None
        assert self.job_description_id is not None

        async with async_session_factory() as db:
            cv_upload = CvUpload(
                user_id=self.user_id,
                job_description_id=self.job_description_id,
                filename="resume.pdf",
                stored_filename="resume.pdf",
                storage_path="/app/uploads/completed-blackbox.pdf",
                storage_key=None,
                storage_url=None,
                file_type="pdf",
                file_size_bytes=1024,
                status="completed",
                failure_reason=None,
                failed_stage=None,
                extracted_text="Python backend resume text.",
            )
            db.add(cv_upload)
            await db.flush()

            db.add(
                AnalysisResult(
                    cv_upload_id=cv_upload.id,
                    job_description_id=self.job_description_id,
                    overall_score=84,
                    raw_ai_response={"grade": "Very Good", "summary": "Stored result"},
                    ai_provider="integration-test-provider",
                    token_usage=None,
                    processing_time_seconds=1.23,
                )
            )
            await db.commit()
            await db.refresh(cv_upload)
            self.cv_upload_id = cv_upload.id

        response = await self._post_webhook(self.cv_upload_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "completed")

        async with async_session_factory() as db:
            cv_upload = await db.scalar(select(CvUpload).where(CvUpload.id == self.cv_upload_id))
            analysis_results = (await db.execute(select(AnalysisResult).where(AnalysisResult.cv_upload_id == self.cv_upload_id))).scalars().all()

        self.assertIsNotNone(cv_upload)
        self.assertEqual(cv_upload.status, "completed")
        self.assertIsNone(cv_upload.failure_reason)
        self.assertIsNone(cv_upload.failed_stage)
        self.assertEqual(len(analysis_results), 1)

    async def _post_webhook(self, cv_upload_id) -> httpx.Response:
        async with httpx.AsyncClient(timeout=90) as client:
            return await client.post(
                settings.n8n_webhook_url,
                headers={"x-internal-workflow-secret": settings.n8n_internal_shared_secret},
                json={"cv_upload_id": str(cv_upload_id)},
            )

    async def _wait_for_cv_state(self, cv_upload_id, timeout_seconds: int = 20) -> tuple[str, str | None, str | None]:
        deadline = asyncio.get_running_loop().time() + timeout_seconds
        while True:
            async with async_session_factory() as db:
                cv_upload = await db.scalar(select(CvUpload).where(CvUpload.id == cv_upload_id))

            if cv_upload is not None and cv_upload.status in {"failed", "completed"}:
                return cv_upload.status, cv_upload.failure_reason, cv_upload.failed_stage

            if asyncio.get_running_loop().time() >= deadline:
                self.fail(f"Timed out waiting for CV upload {cv_upload_id} to reach a terminal state.")

            await asyncio.sleep(0.5)

    def _create_docx(self, filename: str, paragraphs: list[str]) -> str:
        upload_root = Path(settings.upload_dir)
        upload_root.mkdir(parents=True, exist_ok=True)
        temp_dir = tempfile.mkdtemp(prefix="n8n-blackbox-", dir=str(upload_root))
        self._temp_dirs.append(temp_dir)
        destination = Path(temp_dir) / filename

        from docx import Document

        document = Document()
        for paragraph in paragraphs:
            document.add_paragraph(paragraph)
        document.save(destination)
        return str(destination)
