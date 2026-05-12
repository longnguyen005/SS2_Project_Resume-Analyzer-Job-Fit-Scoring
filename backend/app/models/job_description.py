from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin


class JobDescription(UUIDTimestampMixin, Base):
    __tablename__ = "job_descriptions"
    __table_args__ = (Index("ix_job_descriptions_user_id", "user_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description_text: Mapped[str] = mapped_column(Text, nullable=False)

    user = relationship("User", back_populates="job_descriptions")
    cv_uploads = relationship("CvUpload", back_populates="job_description")
    analysis_results = relationship("AnalysisResult", back_populates="job_description")
