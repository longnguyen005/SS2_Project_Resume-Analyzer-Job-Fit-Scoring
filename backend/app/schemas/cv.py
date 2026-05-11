from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CvUploadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_description_id: UUID | None
    filename: str
    stored_filename: str
    storage_path: str
    storage_key: str | None
    storage_url: str | None
    file_type: str
    file_size_bytes: int
    language: str | None
    status: str
    failure_reason: str | None
    failed_stage: str | None
    created_at: datetime
    updated_at: datetime


class CvHistoryAnalysisSummaryRead(BaseModel):
    overall_score: int | None
    grade: str | None
    analyzed_at: datetime | None
    analysis_provider: str | None = None


class CvHistoryItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_description_id: UUID | None
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    failure_reason: str | None = None
    failed_stage: str | None = None
    created_at: datetime
    updated_at: datetime
    analysis_summary: CvHistoryAnalysisSummaryRead | None = None


class CvStatusRead(BaseModel):
    id: UUID
    status: str
    failure_reason: str | None = None
    failed_stage: str | None = None
    updated_at: datetime


class CvResultBreakdownItem(BaseModel):
    title: str
    score: int
    status: str
    tone: str


class CvResultChartBar(BaseModel):
    label: str
    value: int


class CvResultLegendItem(BaseModel):
    label: str
    value: str
    tone: str


class CvResultSuggestion(BaseModel):
    title: str
    description: str
    priority: str
    tone: str


class CvResultRead(BaseModel):
    cv_id: UUID
    filename: str
    analyzed_at: datetime
    analysis_provider: str | None = None
    overall_score: int
    grade: str
    summary: str
    breakdown: list[CvResultBreakdownItem]
    skill_chart: list[CvResultChartBar]
    content_quality: list[CvResultLegendItem]
    strengths: list[str]
    improvements: list[str]
    suggestions: list[CvResultSuggestion]


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
