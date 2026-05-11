"""Top-level API router.

Public user-facing routes stay under the standard prefixes such as `/auth`,
`/jd`, and `/cv`.

Internal workflow endpoints stay isolated under `/internal/cv` so the n8n
pipeline and workers have a single, explicit integration surface.
"""

from fastapi import APIRouter

from app.api.routes import auth, cv, internal_workflow, jd

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(jd.router, prefix="/jd", tags=["job-descriptions"])
api_router.include_router(cv.router, prefix="/cv", tags=["cv"])
api_router.include_router(internal_workflow.router, prefix="/internal/cv", tags=["internal-cv"])
