"""ORM models."""

from app.models.analysis_result import AnalysisResult
from app.models.category_score import CategoryScore
from app.models.cv_upload import CvUpload
from app.models.job_description import JobDescription
from app.models.suggestion import Suggestion
from app.models.user import User

__all__ = [
    "AnalysisResult",
    "CategoryScore",
    "CvUpload",
    "JobDescription",
    "Suggestion",
    "User",
]
