from __future__ import annotations

from fastapi import Header, HTTPException, status

from app.core.config import settings


def verify_internal_workflow_access(
    x_internal_workflow_secret: str | None = Header(default=None),
) -> None:
    if not settings.n8n_internal_shared_secret.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal workflow secret is not configured.",
        )

    if x_internal_workflow_secret != settings.n8n_internal_shared_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid internal workflow secret.")
