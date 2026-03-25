from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JobDescriptionCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description_text: str = Field(min_length=10)


class JobDescriptionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description_text: str | None = Field(default=None, min_length=10)


class JobDescriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description_text: str
    created_at: datetime
    updated_at: datetime
