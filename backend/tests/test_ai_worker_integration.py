from __future__ import annotations

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import httpx
from fastapi import FastAPI
from sqlalchemy import delete, text

from app.ai_worker import routes as ai_worker
from app.ai_worker.routes import router as ai_worker_router
from app.core.config import settings
from app.db.session import async_session_factory, engine
from app.models import JobDescription, User
from app.services.resume_analyzer import (
    BreakdownItem,
    ChartBarItem,
    LegendItem,
    LiveAIUnavailableError,
    ResumeAnalysisPayload,
    SuggestionItem,
)


class AIWorkerIntegrationTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client: httpx.AsyncClient | None = None
        self.user_id = None

        await engine.dispose()

        try:
            async with async_session_factory() as db:
                await db.execute(text("SELECT 1"))

                user = User(
                    email=f"ai-worker-{uuid4()}@example.com",
                    hashed_password="hashed-password",
                    full_name="AI Worker Test",
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
                await db.commit()

                self.user_id = user.id
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
            await db.execute(delete(JobDescription).where(JobDescription.user_id == self.user_id))
            await db.execute(delete(User).where(User.id == self.user_id))
            await db.commit()

        await engine.dispose()

    async def test_ai_worker_analyze_success(self) -> None:
        assert self.client is not None
        headers = {"x-internal-workflow-secret": settings.n8n_internal_shared_secret}

        analyze_result = (
            ResumeAnalysisPayload(
                overall_score=84,
                grade="Very Good",
                summary="Resume shows strong alignment with backend role requirements.",
                breakdown=[
                    BreakdownItem(title="Skills", score=85, status="Excellent", tone="navy"),
                    BreakdownItem(title="Experience", score=82, status="Good", tone="navy"),
                    BreakdownItem(title="Education", score=78, status="Good", tone="navy"),
                    BreakdownItem(title="Resume Format", score=86, status="Excellent", tone="navy"),
                ],
                skill_chart=[
                    ChartBarItem(label="Technical", value=88),
                    ChartBarItem(label="Leadership", value=62),
                ],
                content_quality=[
                    LegendItem(label="Strong", value="45%", tone="green"),
                    LegendItem(label="Good", value="35%", tone="blue"),
                ],
                strengths=["Strong Python backend alignment"],
                improvements=["Add more quantified impact"],
                suggestions=[
                    SuggestionItem(
                        title="Add metrics",
                        description="Quantify backend delivery outcomes.",
                        priority="High Priority",
                        tone="red",
                    )
                ],
            ),
            "integration-test-provider",
            1.23,
        )

        with (
            patch.object(ai_worker, "analyze_resume_payload", new=AsyncMock(return_value=analyze_result)),
            self.assertLogs("app.ai_worker.routes", level="INFO") as captured_logs,
        ):
            response = await self.client.post(
                "/api/v1/ai-worker/cv/analyze",
                headers=headers,
                json={
                    "cv_upload_id": str(uuid4()),
                    "resume_text": "Valid resume text",
                    "job_description_text": "Backend engineer with Python and FastAPI.",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["provider_name"], "integration-test-provider")
        self.assertTrue(
            any("stage=analyze" in line and "ai_worker_stage_success" in line for line in captured_logs.output)
        )

    async def test_ai_worker_analyze_timeout_returns_503(self) -> None:
        assert self.client is not None
        headers = {"x-internal-workflow-secret": settings.n8n_internal_shared_secret}

        with (
            patch.object(
                ai_worker,
                "analyze_resume_payload",
                new=AsyncMock(side_effect=LiveAIUnavailableError("AI provider timed out after retries.")),
            ),
            self.assertLogs("app.ai_worker.routes", level="INFO") as captured_logs,
        ):
            response = await self.client.post(
                "/api/v1/ai-worker/cv/analyze",
                headers=headers,
                json={
                    "cv_upload_id": str(uuid4()),
                    "resume_text": "Valid resume text",
                    "job_description_text": "Backend engineer with Python and FastAPI.",
                },
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "AI provider timed out after retries.")
        self.assertTrue(
            any("stage=analyze" in line and "status_code=503" in line for line in captured_logs.output)
        )

    async def test_ai_worker_analyze_invalid_json_returns_422(self) -> None:
        assert self.client is not None
        headers = {"x-internal-workflow-secret": settings.n8n_internal_shared_secret}

        with (
            patch.object(
                ai_worker,
                "analyze_resume_payload",
                new=AsyncMock(side_effect=ValueError("AI response was not valid JSON")),
            ),
            self.assertLogs("app.ai_worker.routes", level="INFO") as captured_logs,
        ):
            response = await self.client.post(
                "/api/v1/ai-worker/cv/analyze",
                headers=headers,
                json={
                    "cv_upload_id": str(uuid4()),
                    "resume_text": "Valid resume text",
                    "job_description_text": "Backend engineer with Python and FastAPI.",
                },
            )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "AI response was not valid JSON")
        self.assertTrue(
            any("stage=analyze" in line and "status_code=422" in line for line in captured_logs.output)
        )


def _build_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(ai_worker_router, prefix=f"{settings.api_v1_prefix}/ai-worker")
    return test_app
