from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin


class AnalysisResult(UUIDTimestampMixin, Base):
    __tablename__ = "analysis_results"
    __table_args__ = (Index("ix_analysis_results_cv_upload_id", "cv_upload_id"),)

    cv_upload_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cv_uploads.id", ondelete="CASCADE"))
    job_description_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="SET NULL"),
        nullable=True,
    )
    overall_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_ai_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ai_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    token_usage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    processing_time_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    cv_upload = relationship("CvUpload", back_populates="analysis_results")
    job_description = relationship("JobDescription", back_populates="analysis_results")
    category_scores = relationship("CategoryScore", back_populates="analysis_result", cascade="all, delete-orphan")
    suggestions = relationship("Suggestion", back_populates="analysis_result", cascade="all, delete-orphan")
