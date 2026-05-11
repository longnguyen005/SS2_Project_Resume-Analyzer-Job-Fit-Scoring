from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi import HTTPException

from app.services.cv_extraction import extract_cv_text, validate_extracted_cv_text
from app.services.cv_state import (
    CLAIM_STATUS_ALREADY_COMPLETED,
    CLAIM_STATUS_ALREADY_PROCESSING,
    CLAIM_STATUS_CLAIMED,
    FAILED_STAGE_ANALYZE,
    FAILED_STAGE_EXTRACT,
    claim_cv_processing,
    mark_cv_failed,
)


class CvProcessingTests(IsolatedAsyncioTestCase):
    async def test_claim_cv_processing_returns_already_completed_when_result_exists(self) -> None:
        cv_upload_id = uuid4()
        db = AsyncMock()
        cv_upload = SimpleNamespace(
            id=cv_upload_id,
            status="completed",
            failure_reason=None,
            failed_stage=None,
            updated_at=datetime.now(timezone.utc),
            analysis_results=[SimpleNamespace(updated_at=datetime.now(timezone.utc))],
        )

        with patch(
            "app.services.cv_state.load_cv_with_job_description",
            new=AsyncMock(return_value=cv_upload),
        ):
            claimed_cv, claim_status = await claim_cv_processing(db, cv_upload_id)

        self.assertIs(claimed_cv, cv_upload)
        self.assertEqual(claim_status, CLAIM_STATUS_ALREADY_COMPLETED)
        db.commit.assert_not_awaited()

    async def test_claim_cv_processing_blocks_recent_duplicate_processing(self) -> None:
        cv_upload_id = uuid4()
        db = AsyncMock()
        cv_upload = SimpleNamespace(
            id=cv_upload_id,
            status="processing",
            failure_reason=None,
            failed_stage=None,
            updated_at=datetime.now(timezone.utc),
            analysis_results=[],
        )

        with patch(
            "app.services.cv_state.load_cv_with_job_description",
            new=AsyncMock(return_value=cv_upload),
        ):
            claimed_cv, claim_status = await claim_cv_processing(db, cv_upload_id)

        self.assertIs(claimed_cv, cv_upload)
        self.assertEqual(claim_status, CLAIM_STATUS_ALREADY_PROCESSING)
        db.commit.assert_not_awaited()

    async def test_claim_cv_processing_reclaims_stale_processing(self) -> None:
        cv_upload_id = uuid4()
        db = AsyncMock()
        cv_upload = SimpleNamespace(
            id=cv_upload_id,
            status="processing",
            failure_reason="old error",
            failed_stage=FAILED_STAGE_ANALYZE,
            updated_at=datetime.now(timezone.utc) - timedelta(hours=1),
            analysis_results=[],
        )

        with (
            patch(
                "app.services.cv_state.load_cv_with_job_description",
                new=AsyncMock(return_value=cv_upload),
            ),
            patch("app.services.cv_state.settings.n8n_processing_claim_ttl_seconds", new=60),
        ):
            claimed_cv, claim_status = await claim_cv_processing(db, cv_upload_id)

        self.assertIs(claimed_cv, cv_upload)
        self.assertEqual(claim_status, CLAIM_STATUS_CLAIMED)
        self.assertEqual(cv_upload.status, "processing")
        self.assertEqual(cv_upload.failure_reason, None)
        self.assertEqual(cv_upload.failed_stage, None)
        db.commit.assert_awaited_once()

    async def test_mark_cv_failed_does_not_override_completed_upload(self) -> None:
        cv_upload_id = uuid4()
        db = AsyncMock()
        cv_upload = SimpleNamespace(
            id=cv_upload_id,
            status="completed",
            failure_reason=None,
            failed_stage=None,
            updated_at=datetime.now(timezone.utc),
            analysis_results=[SimpleNamespace(updated_at=datetime.now(timezone.utc))],
        )

        with patch(
            "app.services.cv_state.load_cv_with_job_description",
            new=AsyncMock(return_value=cv_upload),
        ):
            await mark_cv_failed(db, cv_upload_id, "stale failure", failed_stage=FAILED_STAGE_ANALYZE)

        self.assertEqual(cv_upload.status, "completed")
        self.assertEqual(cv_upload.failure_reason, None)
        self.assertEqual(cv_upload.failed_stage, None)
        db.commit.assert_not_awaited()

    async def test_extract_cv_text_stores_text_without_validation(self) -> None:
        cv_upload_id = uuid4()
        db = AsyncMock()
        cv_upload = SimpleNamespace(
            id=cv_upload_id,
            storage_path="uploads/raw.pdf",
            file_type="pdf",
            status="pending",
            failure_reason="old error",
            failed_stage=FAILED_STAGE_EXTRACT,
            updated_at=None,
            extracted_text=None,
            job_description=None,
            analysis_results=[],
        )

        with (
            patch(
                "app.services.cv_extraction.load_cv_with_job_description",
                new=AsyncMock(return_value=cv_upload),
            ),
            patch(
                "app.services.cv_extraction.extract_text_from_resume",
                return_value="Meeting agenda without resume sections or contact information.",
            ),
        ):
            extracted_cv, extracted_text = await extract_cv_text(db, cv_upload_id)

        self.assertIs(extracted_cv, cv_upload)
        self.assertEqual(extracted_text, "Meeting agenda without resume sections or contact information.")
        self.assertEqual(cv_upload.status, "processing")
        self.assertEqual(cv_upload.failure_reason, None)
        self.assertEqual(cv_upload.failed_stage, None)
        self.assertEqual(cv_upload.extracted_text, extracted_text)

    async def test_validate_extracted_cv_text_marks_extract_failure_for_invalid_resume(self) -> None:
        cv_upload_id = uuid4()
        db = AsyncMock()
        cv_upload = SimpleNamespace(
            id=cv_upload_id,
            status="pending",
            failure_reason=None,
            failed_stage=None,
            updated_at=None,
            extracted_text="Weekly notes for class meeting agenda and discussion items.",
            job_description=None,
            analysis_results=[],
        )

        with (
            patch(
                "app.services.cv_extraction.load_cv_with_job_description",
                new=AsyncMock(return_value=cv_upload),
            ),
            patch("app.services.cv_extraction.mark_cv_failed", new=AsyncMock()) as mark_failed_mock,
        ):
            with self.assertRaises(HTTPException) as context:
                await validate_extracted_cv_text(db, cv_upload_id)

        self.assertEqual(context.exception.status_code, 422)
        mark_failed_mock.assert_awaited_once()
        self.assertEqual(mark_failed_mock.await_args.kwargs["failed_stage"], FAILED_STAGE_EXTRACT)
        self.assertIn("does not appear to be a resume", mark_failed_mock.await_args.args[2])
