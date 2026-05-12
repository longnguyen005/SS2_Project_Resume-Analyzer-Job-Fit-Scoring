"""Compatibility exports for CV schemas.

New code should import public response models from `app.schemas.cv_public` and
internal workflow/worker payload models from `app.schemas.cv_internal`.
"""

from app.schemas.cv_internal import (
    InternalBreakdownItem,
    InternalChartBarItem,
    InternalCvAnalyzeRequest,
    InternalCvAnalyzeResponse,
    InternalCvClaimResponse,
    InternalCvCompleteRequest,
    InternalCvExtractResponse,
    InternalCvFailRequest,
    InternalCvResumeStageResponse,
    InternalCvValidateResponse,
    InternalLegendItem,
    InternalResumeAnalysisPayload,
    InternalSuggestionItem,
)
from app.schemas.cv_public import (
    CvHistoryAnalysisSummaryRead,
    CvHistoryItemRead,
    CvResultBreakdownItem,
    CvResultChartBar,
    CvResultLegendItem,
    CvResultRead,
    CvResultSuggestion,
    CvStatusRead,
    CvUploadRead,
)

__all__ = [
    "CvHistoryAnalysisSummaryRead",
    "CvHistoryItemRead",
    "CvResultBreakdownItem",
    "CvResultChartBar",
    "CvResultLegendItem",
    "CvResultRead",
    "CvResultSuggestion",
    "CvStatusRead",
    "CvUploadRead",
    "InternalBreakdownItem",
    "InternalChartBarItem",
    "InternalCvAnalyzeRequest",
    "InternalCvAnalyzeResponse",
    "InternalCvClaimResponse",
    "InternalCvCompleteRequest",
    "InternalCvExtractResponse",
    "InternalCvFailRequest",
    "InternalCvResumeStageResponse",
    "InternalCvValidateResponse",
    "InternalLegendItem",
    "InternalResumeAnalysisPayload",
    "InternalSuggestionItem",
]
