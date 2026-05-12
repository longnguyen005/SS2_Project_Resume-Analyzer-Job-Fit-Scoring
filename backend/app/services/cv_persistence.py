from __future__ import annotations

from datetime import datetime, timezone
from typing import NamedTuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnalysisResult, CategoryScore, CvUpload, Suggestion
from app.schemas.cv_internal import InternalCvCompleteRequest
from app.schemas.cv_public import (
    CvHistoryAnalysisSummaryRead,
    CvHistoryItemRead,
    CvResultBreakdownItem,
    CvResultChartBar,
    CvResultLegendItem,
    CvResultRead,
    CvResultSuggestion,
    CvStatusRead,
    CvUploadRead,
)
from app.services.ai_response_normalizer import (
    BreakdownItem,
    ChartBarItem,
    LegendItem,
    ResumeAnalysisPayload,
    SuggestionItem,
    grade_from_score,
    status_from_score,
    summary_from_score,
)
from app.services.cv_queries import get_latest_analysis_result, load_cv_with_job_description


class CompleteAnalysisResult(NamedTuple):
    status: str
    provider_name: str | None
    processing_time_seconds: float | None
    already_completed: bool = False


def build_cv_upload_read(cv_upload: CvUpload) -> CvUploadRead:
    return CvUploadRead.model_validate(cv_upload)


def build_cv_status_read(cv_upload: CvUpload) -> CvStatusRead:
    return CvStatusRead(
        id=cv_upload.id,
        status=cv_upload.status,
        failure_reason=cv_upload.failure_reason,
        failed_stage=cv_upload.failed_stage,
        updated_at=cv_upload.updated_at,
    )


def deserialize_complete_payload(payload: InternalCvCompleteRequest) -> ResumeAnalysisPayload:
    return ResumeAnalysisPayload(
        overall_score=payload.analysis.overall_score,
        grade=payload.analysis.grade,
        summary=payload.analysis.summary,
        breakdown=[
            BreakdownItem(
                title=item.title,
                score=item.score,
                status=item.status,
                tone=item.tone,
            )
            for item in payload.analysis.breakdown
        ],
        skill_chart=[
            ChartBarItem(label=item.label, value=item.value)
            for item in payload.analysis.skill_chart
        ],
        content_quality=[
            LegendItem(label=item.label, value=item.value, tone=item.tone)
            for item in payload.analysis.content_quality
        ],
        strengths=payload.analysis.strengths,
        improvements=payload.analysis.improvements,
        suggestions=[
            SuggestionItem(
                title=item.title,
                description=item.description,
                priority=item.priority,
                tone=item.tone,
            )
            for item in payload.analysis.suggestions
        ],
    )


async def save_analysis_result(
    db: AsyncSession,
    cv_upload_id: UUID,
    analysis_payload: ResumeAnalysisPayload,
    provider_name: str,
    processing_time_seconds: float | None,
) -> CvUpload:
    cv_upload = await load_cv_with_job_description(db, cv_upload_id)
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")

    for existing_result in list(cv_upload.analysis_results):
        await db.delete(existing_result)
    await db.flush()

    analysis_result = AnalysisResult(
        cv_upload_id=cv_upload.id,
        job_description_id=cv_upload.job_description_id,
        overall_score=analysis_payload.overall_score,
        raw_ai_response={
            "grade": analysis_payload.grade,
            "summary": analysis_payload.summary,
            "strengths": analysis_payload.strengths,
            "improvements": analysis_payload.improvements,
            "skill_chart": [{"label": item.label, "value": item.value} for item in analysis_payload.skill_chart],
            "content_quality": [
                {"label": item.label, "value": item.value, "tone": item.tone}
                for item in analysis_payload.content_quality
            ],
        },
        ai_provider=provider_name,
        token_usage=None,
        processing_time_seconds=processing_time_seconds,
    )
    db.add(analysis_result)
    await db.flush()

    for item in analysis_payload.breakdown:
        db.add(
            CategoryScore(
                analysis_result_id=analysis_result.id,
                category=item.title,
                score=item.score,
                feedback=item.status,
            )
        )

    for item in analysis_payload.suggestions:
        db.add(
            Suggestion(
                analysis_result_id=analysis_result.id,
                category=item.title,
                priority=item.priority,
                suggestion_text=item.description,
            )
        )

    cv_upload.status = "completed"
    cv_upload.failure_reason = None
    cv_upload.failed_stage = None
    cv_upload.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(cv_upload)
    return cv_upload


async def complete_analysis_result(
    db: AsyncSession,
    cv_upload_id: UUID,
    payload: InternalCvCompleteRequest,
) -> CompleteAnalysisResult:
    cv_upload = await load_cv_with_job_description(db, cv_upload_id)
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")

    latest_analysis = get_latest_analysis_result(cv_upload)
    if cv_upload.status == "completed" and latest_analysis is not None:
        return CompleteAnalysisResult(
            status="completed",
            provider_name=latest_analysis.ai_provider,
            processing_time_seconds=latest_analysis.processing_time_seconds,
            already_completed=True,
        )

    await save_analysis_result(
        db=db,
        cv_upload_id=cv_upload_id,
        analysis_payload=deserialize_complete_payload(payload),
        provider_name=payload.provider_name,
        processing_time_seconds=payload.processing_time_seconds,
    )
    return CompleteAnalysisResult(
        status="completed",
        provider_name=payload.provider_name,
        processing_time_seconds=payload.processing_time_seconds,
    )


def build_cv_result_read(cv_upload: CvUpload, analysis_result: AnalysisResult) -> CvResultRead:
    raw_response = analysis_result.raw_ai_response or {}

    breakdown = [
        CvResultBreakdownItem(
            title=item.category,
            score=item.score,
            status=item.feedback or status_from_score(item.score),
            tone="navy",
        )
        for item in analysis_result.category_scores
    ]

    suggestions = [
        CvResultSuggestion(
            title=item.category,
            description=item.suggestion_text,
            priority=item.priority,
            tone=_suggestion_tone_from_priority(item.priority),
        )
        for item in analysis_result.suggestions
    ]

    return CvResultRead(
        cv_id=cv_upload.id,
        filename=cv_upload.filename,
        analyzed_at=analysis_result.updated_at,
        analysis_provider=analysis_result.ai_provider,
        overall_score=analysis_result.overall_score or 0,
        grade=str(raw_response.get("grade") or grade_from_score(analysis_result.overall_score or 0)),
        summary=str(raw_response.get("summary") or summary_from_score(analysis_result.overall_score or 0)),
        breakdown=breakdown,
        skill_chart=[
            CvResultChartBar(label=str(item["label"]), value=int(item["value"]))
            for item in raw_response.get("skill_chart", [])
        ],
        content_quality=[
            CvResultLegendItem(
                label=str(item["label"]),
                value=str(item["value"]),
                tone=str(item["tone"]),
            )
            for item in raw_response.get("content_quality", [])
        ],
        strengths=[str(item) for item in raw_response.get("strengths", [])],
        improvements=[str(item) for item in raw_response.get("improvements", [])],
        suggestions=suggestions,
    )


def build_cv_history_item_read(cv_upload: CvUpload) -> CvHistoryItemRead:
    analysis_result = None
    if cv_upload.analysis_results:
        analysis_result = max(cv_upload.analysis_results, key=lambda item: item.updated_at)

    analysis_summary = None
    if analysis_result is not None:
        analysis_summary = CvHistoryAnalysisSummaryRead(
            overall_score=analysis_result.overall_score,
            grade=grade_from_score(analysis_result.overall_score or 0)
            if analysis_result.overall_score is not None
            else None,
            analyzed_at=analysis_result.updated_at,
            analysis_provider=analysis_result.ai_provider,
        )

    return CvHistoryItemRead(
        id=cv_upload.id,
        job_description_id=cv_upload.job_description_id,
        filename=cv_upload.filename,
        file_type=cv_upload.file_type,
        file_size_bytes=cv_upload.file_size_bytes,
        status=cv_upload.status,
        failure_reason=cv_upload.failure_reason,
        failed_stage=cv_upload.failed_stage,
        created_at=cv_upload.created_at,
        updated_at=cv_upload.updated_at,
        analysis_summary=analysis_summary,
    )


def build_cv_history_reads(cv_uploads: list[CvUpload]) -> list[CvHistoryItemRead]:
    return [build_cv_history_item_read(item) for item in cv_uploads]


def _suggestion_tone_from_priority(priority: str) -> str:
    normalized = priority.lower()
    if "high" in normalized:
        return "red"
    if "low" in normalized:
        return "blue"
    return "yellow"
