from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class InternalBreakdownItem(BaseModel):
    title: str
    score: int
    status: str
    tone: str = "navy"


class InternalChartBarItem(BaseModel):
    label: str
    value: int


class InternalLegendItem(BaseModel):
    label: str
    value: str
    tone: str


class InternalSuggestionItem(BaseModel):
    title: str
    description: str
    priority: str
    tone: str = "yellow"


class InternalResumeAnalysisPayload(BaseModel):
    overall_score: int
    grade: str
    summary: str
    breakdown: list[InternalBreakdownItem]
    skill_chart: list[InternalChartBarItem]
    content_quality: list[InternalLegendItem]
    strengths: list[str]
    improvements: list[str]
    suggestions: list[InternalSuggestionItem]


class InternalCvResumeStageResponse(BaseModel):
    cv_upload_id: UUID
    filename: str
    file_type: str
    storage_key: str | None
    storage_url: str | None
    resume_text: str
    job_description_text: str | None = None


class InternalCvExtractResponse(InternalCvResumeStageResponse):
    pass


class InternalCvValidateResponse(InternalCvResumeStageResponse):
    pass


class InternalCvClaimResponse(BaseModel):
    cv_upload_id: UUID
    claim_status: str


class InternalCvAnalyzeRequest(BaseModel):
    cv_upload_id: UUID
    resume_text: str
    job_description_text: str | None = None


class InternalCvAnalyzeResponse(BaseModel):
    provider_name: str
    processing_time_seconds: float
    analysis: InternalResumeAnalysisPayload


class InternalCvCompleteRequest(BaseModel):
    provider_name: str
    processing_time_seconds: float | None = None
    analysis: InternalResumeAnalysisPayload


class InternalCvFailRequest(BaseModel):
    failure_reason: str
    failed_stage: str | None = None
