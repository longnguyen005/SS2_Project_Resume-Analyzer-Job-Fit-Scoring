"""Top-level API router.

Public user-facing routes stay under the standard prefixes such as `/auth`,
`/jd`, and `/cv`.

Internal workflow endpoints stay isolated under `/internal/cv`. Worker routes
are intentionally not mounted here; each worker app exposes only its own
internal router from its dedicated entrypoint.
"""

from fastapi import APIRouter

from app.api.routes import auth, cv, internal_workflow, jd

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(jd.router, prefix="/jd", tags=["job-descriptions"])
api_router.include_router(cv.router, prefix="/cv", tags=["cv"])
api_router.include_router(internal_workflow.router, prefix="/internal/cv", tags=["internal-cv"])
