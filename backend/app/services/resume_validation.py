from __future__ import annotations

import re
from dataclasses import dataclass


EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,5}\d{2,4}")
PROFILE_PATTERN = re.compile(r"\b(linkedin|github|portfolio)\b", re.IGNORECASE)

SECTION_PATTERNS = {
    "summary": re.compile(r"\b(summary|profile|objective)\b", re.IGNORECASE),
    "skills": re.compile(r"\b(skills|technical skills|competencies|technologies|tech stack)\b", re.IGNORECASE),
    "experience": re.compile(
        r"\b(experience|employment|work history|professional experience|internship|career history)\b",
        re.IGNORECASE,
    ),
    "education": re.compile(r"\b(education|academic background|degree|university|college)\b", re.IGNORECASE),
    "projects": re.compile(r"\b(projects|project experience|personal projects)\b", re.IGNORECASE),
    "certifications": re.compile(r"\b(certifications|certificates|licenses)\b", re.IGNORECASE),
}


@dataclass(slots=True)
class ResumeValidationResult:
    is_valid: bool
    reason: str | None = None


def validate_resume_text(resume_text: str) -> ResumeValidationResult:
    normalized_text = resume_text.strip()
    if not normalized_text:
        return ResumeValidationResult(
            is_valid=False,
            reason="No readable text was extracted from the uploaded document.",
        )

    lowered_text = normalized_text.lower()
    section_hits = sum(1 for pattern in SECTION_PATTERNS.values() if pattern.search(lowered_text))
    contact_hits = sum(
        [
            bool(EMAIL_PATTERN.search(normalized_text)),
            bool(PHONE_PATTERN.search(normalized_text)),
            bool(PROFILE_PATTERN.search(lowered_text)),
        ]
    )

    date_hits = len(re.findall(r"\b(19|20)\d{2}\b", normalized_text))
    bullet_hits = normalized_text.count("\n-") + normalized_text.count("\n•") + normalized_text.count("\n*")

    looks_like_resume = (
        (section_hits >= 2 and contact_hits >= 1)
        or (section_hits >= 3)
        or (section_hits >= 2 and date_hits >= 2)
        or (section_hits >= 2 and bullet_hits >= 2)
    )

    if looks_like_resume:
        return ResumeValidationResult(is_valid=True)

    return ResumeValidationResult(
        is_valid=False,
        reason=(
            "The uploaded document does not appear to be a resume or CV. "
            "Please upload a document that includes resume sections such as skills, experience, or education."
        ),
    )
