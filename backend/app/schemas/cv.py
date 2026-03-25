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
    file_type: str
    file_size_bytes: int
    language: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class CvStatusRead(BaseModel):
    id: UUID
    status: str
    updated_at: datetime
