from __future__ import annotations

from time import perf_counter

from app.services.ai_response_normalizer import ResumeAnalysisPayload
from app.services.resume_analyzer import analyze_resume


async def analyze_resume_payload(
    resume_text: str,
    job_description_text: str | None,
) -> tuple[ResumeAnalysisPayload, str, float]:
    started_at = perf_counter()
    payload, provider_name = await analyze_resume(
        resume_text=resume_text,
        job_description_text=job_description_text,
    )
    return payload, provider_name, round(perf_counter() - started_at, 2)


def serialize_analysis_payload(analysis_payload: ResumeAnalysisPayload) -> dict:
    return {
        "overall_score": analysis_payload.overall_score,
        "grade": analysis_payload.grade,
        "summary": analysis_payload.summary,
        "breakdown": [
            {
                "title": item.title,
                "score": item.score,
                "status": item.status,
                "tone": item.tone,
            }
            for item in analysis_payload.breakdown
        ],
        "skill_chart": [
            {
                "label": item.label,
                "value": item.value,
            }
            for item in analysis_payload.skill_chart
        ],
        "content_quality": [
            {
                "label": item.label,
                "value": item.value,
                "tone": item.tone,
            }
            for item in analysis_payload.content_quality
        ],
        "strengths": analysis_payload.strengths,
        "improvements": analysis_payload.improvements,
        "suggestions": [
            {
                "title": item.title,
                "description": item.description,
                "priority": item.priority,
                "tone": item.tone,
            }
            for item in analysis_payload.suggestions
        ],
    }
