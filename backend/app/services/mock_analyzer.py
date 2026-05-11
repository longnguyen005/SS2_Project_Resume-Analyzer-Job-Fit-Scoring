"""Deterministic mock resume analysis for development and testing.

Extracted from resume_analyzer.py to isolate test/dev concerns from
production AI orchestration (SRP). Easy to locate and remove when
mock mode is deprecated.
"""

from __future__ import annotations

import hashlib
import random

from app.services.ai_response_normalizer import (
    BreakdownItem,
    ChartBarItem,
    LegendItem,
    ResumeAnalysisPayload,
    SuggestionItem,
    bounded_score,
    grade_from_score,
    status_from_score,
    summary_from_score,
    weighted_overall_score,
)

_STRENGTHS_POOL = [
    "Resume structure is clear and easy to scan quickly.",
    "Core skills are visible and reasonably aligned with technical roles.",
    "Experience bullets suggest practical project exposure.",
    "Education and supporting background are presented clearly.",
    "The resume keeps a concise recruiter-friendly format.",
]

_IMPROVEMENTS_POOL = [
    "Add more measurable achievements with specific metrics or outcomes.",
    "Use more role-specific keywords to improve job alignment.",
    "Strengthen project bullets with business or product impact.",
    "Improve consistency in formatting, spacing, and section ordering.",
    "Highlight collaboration, leadership, or ownership examples more clearly.",
]

_SUGGESTIONS_POOL = [
    SuggestionItem(
        title="Add Quantified Impact",
        description="Rewrite key bullet points with measurable outcomes such as growth, savings, delivery speed, or user impact.",
        priority="High Priority",
        tone="red",
    ),
    SuggestionItem(
        title="Tailor Keywords To The Role",
        description="Mirror the wording of the target job description so the resume aligns better with the intended role.",
        priority="High Priority",
        tone="yellow",
    ),
    SuggestionItem(
        title="Strengthen Action Verbs",
        description="Start bullets with stronger action verbs like built, optimized, led, automated, and delivered.",
        priority="Medium Priority",
        tone="blue",
    ),
    SuggestionItem(
        title="Improve Formatting Consistency",
        description="Make dates, spacing, and section headings more consistent to improve readability.",
        priority="Low Priority",
        tone="blue",
    ),
    SuggestionItem(
        title="Highlight Business Value",
        description="Explain why your work mattered, not only what you did, especially for projects and recent roles.",
        priority="Medium Priority",
        tone="yellow",
    ),
]


def build_mock_resume_analysis(resume_text: str, job_description_text: str | None = None) -> ResumeAnalysisPayload:
    """Generate a deterministic mock analysis seeded by content hash."""
    seed_input = f"{resume_text}\n##JD##\n{job_description_text or ''}"
    seed = int(hashlib.sha256(seed_input.encode("utf-8")).hexdigest()[:8], 16)
    rng = random.Random(seed)

    word_count = len([token for token in resume_text.split() if token.strip()])
    has_job_description = bool(job_description_text and job_description_text.strip())

    base_floor = 72 if word_count > 120 else 66
    jd_bonus = 4 if has_job_description else 0

    skills_score = bounded_score(base_floor + jd_bonus + rng.randint(6, 16))
    experience_score = bounded_score(base_floor + rng.randint(4, 15))
    education_score = bounded_score(base_floor + rng.randint(5, 14))
    format_score = bounded_score(base_floor + rng.randint(3, 12))
    overall_score = weighted_overall_score(
        skills_score=skills_score,
        experience_score=experience_score,
        education_score=education_score,
        resume_format_score=format_score,
    )

    technical_score = bounded_score(skills_score + rng.randint(-3, 4))
    leadership_score = bounded_score(experience_score + rng.randint(-7, 3))
    communication_score = bounded_score(format_score + rng.randint(-2, 6))
    problem_solving_score = bounded_score(skills_score + rng.randint(-4, 5))

    strong_pct = rng.randint(52, 68)
    good_pct = rng.randint(20, 32)
    needs_work_pct = max(100 - strong_pct - good_pct, 8)

    improvements_pool = list(_IMPROVEMENTS_POOL)
    if has_job_description:
        improvements_pool.append("Mirror important language from the target job description more directly.")

    return ResumeAnalysisPayload(
        overall_score=overall_score,
        grade=grade_from_score(overall_score),
        summary=summary_from_score(overall_score),
        breakdown=[
            BreakdownItem(title="Skills", score=skills_score, status=status_from_score(skills_score), tone="navy"),
            BreakdownItem(title="Experience", score=experience_score, status=status_from_score(experience_score), tone="navy"),
            BreakdownItem(title="Education", score=education_score, status=status_from_score(education_score), tone="navy"),
            BreakdownItem(title="Resume Format", score=format_score, status=status_from_score(format_score), tone="navy"),
        ],
        skill_chart=[
            ChartBarItem(label="Technical", value=technical_score),
            ChartBarItem(label="Leadership", value=leadership_score),
            ChartBarItem(label="Communication", value=communication_score),
            ChartBarItem(label="Problem Solving", value=problem_solving_score),
        ],
        content_quality=[
            LegendItem(label="Strong", value=f"{strong_pct}%", tone="green"),
            LegendItem(label="Good", value=f"{good_pct}%", tone="blue"),
            LegendItem(label="Needs Work", value=f"{needs_work_pct}%", tone="orange"),
        ],
        strengths=rng.sample(_STRENGTHS_POOL, 4),
        improvements=rng.sample(improvements_pool, 3),
        suggestions=rng.sample(_SUGGESTIONS_POOL, 4),
    )
