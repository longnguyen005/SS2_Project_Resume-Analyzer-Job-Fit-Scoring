"""Pure-logic module for parsing, validating, and normalizing AI analysis responses.

Extracted from resume_analyzer.py to follow Single Responsibility Principle.
This module contains NO I/O — only data transformation.
It is shared by live AI analysis, persistence read-model builders, and legacy
test fixtures.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

PROMPT_VERSION = "v2.1-hardened"
ANALYSIS_JSON_SCHEMA = {
    "overall_score": 82,
    "grade": "Very Good",
    "summary": "Brief evidence-based summary of the resume quality and fit.",
    "breakdown": [
        {"title": "Skills", "score": 84, "status": "Good"},
        {"title": "Experience", "score": 80, "status": "Good"},
        {"title": "Education", "score": 79, "status": "Good"},
        {"title": "Resume Format", "score": 83, "status": "Good"},
    ],
    "skill_chart": [
        {"label": "Technical", "value": 85},
        {"label": "Leadership", "value": 73},
        {"label": "Communication", "value": 78},
        {"label": "Problem Solving", "value": 82},
    ],
    "content_quality": [
        {"label": "Strong", "value": "60%", "tone": "green"},
        {"label": "Good", "value": "25%", "tone": "blue"},
        {"label": "Needs Work", "value": "15%", "tone": "orange"},
    ],
    "strengths": [
        "Strength 1",
        "Strength 2",
        "Strength 3",
    ],
    "improvements": [
        "Improvement 1",
        "Improvement 2",
        "Improvement 3",
    ],
    "suggestions": [
        {
            "title": "Add quantified impact",
            "description": "Rewrite at least two bullets with measurable outcomes.",
            "priority": "High Priority",
            "tone": "red",
        },
        {
            "title": "Improve role alignment",
            "description": "Mirror more job-relevant keywords in skills and experience sections.",
            "priority": "Medium Priority",
            "tone": "yellow",
        },
        {
            "title": "Tighten formatting",
            "description": "Keep dates, spacing, and bullet styles consistent.",
            "priority": "Low Priority",
            "tone": "blue",
        },
    ],
}
ANALYSIS_SYSTEM_PROMPT = """
You are an expert ATS-style resume reviewer.

Your task is to analyze the provided resume_text and optional job_description_text,
then return exactly one JSON object that matches the requested schema.

Rules:
- Use only evidence present in the input text.
- Do not invent experience, skills, education, or achievements.
- If the document does not look like a resume or lacks enough evidence, score conservatively.
- Keep output recruiter-focused, concise, and practical.
- The overall_score must be computed from the weighted breakdown:
  - Skills: 35%
  - Experience: 35%
  - Education: 15%
  - Resume Format: 15%
- Return raw JSON only. No markdown, no explanations outside the JSON object.
""".strip()

BREAKDOWN_TITLES = ("Skills", "Experience", "Education", "Resume Format")
ROOT_SCHEMA_KEYS = frozenset(
    {
        "overall_score",
        "grade",
        "summary",
        "breakdown",
        "skill_chart",
        "content_quality",
        "strengths",
        "improvements",
        "suggestions",
    }
)
BREAKDOWN_SCHEMA_KEYS = frozenset({"title", "score", "status"})
SKILL_CHART_SCHEMA_KEYS = frozenset({"label", "value"})
CONTENT_QUALITY_SCHEMA_KEYS = frozenset({"label", "value", "tone"})
SUGGESTION_SCHEMA_KEYS = frozenset({"title", "description", "priority", "tone"})
BREAKDOWN_WEIGHTS = {
    "Skills": 0.35,
    "Experience": 0.35,
    "Education": 0.15,
    "Resume Format": 0.15,
}


# ---------------------------------------------------------------------------
# Public dataclasses
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class BreakdownItem:
    title: str
    score: int
    status: str
    tone: str


@dataclass(slots=True)
class ChartBarItem:
    label: str
    value: int


@dataclass(slots=True)
class LegendItem:
    label: str
    value: str
    tone: str


@dataclass(slots=True)
class SuggestionItem:
    title: str
    description: str
    priority: str
    tone: str


@dataclass(slots=True)
class ResumeAnalysisPayload:
    overall_score: int
    grade: str
    summary: str
    breakdown: list[BreakdownItem]
    skill_chart: list[ChartBarItem]
    content_quality: list[LegendItem]
    strengths: list[str]
    improvements: list[str]
    suggestions: list[SuggestionItem]


# ---------------------------------------------------------------------------
# Public scoring helpers (used by cv.py routes — no longer private)
# ---------------------------------------------------------------------------

def grade_from_score(score: int) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 80:
        return "Very Good"
    if score >= 70:
        return "Good"
    if score >= 60:
        return "Needs Improvement"
    return "Weak"


def status_from_score(score: int) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    return "Needs Work"


def summary_from_score(score: int) -> str:
    if score >= 90:
        return "The resume shows clear, role-relevant evidence with strong structure, relevant skills, and concrete experience."
    if score >= 80:
        return "The resume shows relevant evidence and solid structure, but stronger detail on impact, scope, or targeting would improve it."
    if score >= 70:
        return "The resume includes useful background, but several claims need stronger evidence, clearer scope, or tighter alignment."
    if score >= 60:
        return "The resume shows partial evidence, but missing detail, impact, or clarity materially limits its effectiveness."
    return "The document provides limited resume evidence, so the evaluation is conservative and the score is low."


def bounded_score(score: int) -> int:
    return max(0, min(score, 100))


def calculate_overall_score(breakdown: list[BreakdownItem]) -> int:
    scores = {item.title: item.score for item in breakdown}
    return weighted_overall_score(
        skills_score=scores.get("Skills", 0),
        experience_score=scores.get("Experience", 0),
        education_score=scores.get("Education", 0),
        resume_format_score=scores.get("Resume Format", 0),
    )


def weighted_overall_score(
    *,
    skills_score: int,
    experience_score: int,
    education_score: int,
    resume_format_score: int,
) -> int:
    return round(
        (skills_score * BREAKDOWN_WEIGHTS["Skills"])
        + (experience_score * BREAKDOWN_WEIGHTS["Experience"])
        + (education_score * BREAKDOWN_WEIGHTS["Education"])
        + (resume_format_score * BREAKDOWN_WEIGHTS["Resume Format"])
    )


# ---------------------------------------------------------------------------
# AI response parsing
# ---------------------------------------------------------------------------

def extract_message_content(response_json: dict) -> str:
    choices = response_json.get("choices") or []
    if not choices:
        raise ValueError("AI response did not include any choices")

    message = choices[0].get("message") or {}
    content = message.get("content")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(str(item.get("text", "")))
        if text_parts:
            return "\n".join(text_parts)

    raise ValueError("AI response content was empty or unsupported")


def parse_json_content(content: str) -> dict:
    stripped = content.strip()

    if stripped.startswith("```"):
        raise ValueError("AI response must be raw JSON without markdown code fences")

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError("AI response was not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise ValueError("AI response JSON root must be an object")

    _ensure_allowed_keys(parsed, ROOT_SCHEMA_KEYS, "root object")
    return parsed


def payload_from_ai_json(data: dict) -> ResumeAnalysisPayload:
    provided_overall_score = bounded_score(_coerce_int(data.get("overall_score"), default=60))
    breakdown = normalize_breakdown(data.get("breakdown"), provided_overall_score)
    overall_score = calculate_overall_score(breakdown)

    score_drift = abs(provided_overall_score - overall_score)
    if score_drift > 3:
        logger.warning(
            "event=scoring_drift_detected ai_overall_score=%s calculated_overall_score=%s drift=%s prompt_version=%s",
            provided_overall_score, overall_score, score_drift, PROMPT_VERSION,
        )

    skill_chart = normalize_skill_chart(data.get("skill_chart"), breakdown)
    content_quality = normalize_content_quality(data.get("content_quality"))
    strengths = normalize_string_list(
        data.get("strengths"),
        minimum=3,
        maximum=4,
        fallback=[
            "The resume text includes some identifiable professional background.",
            "At least some skills, experience, or education details are explicitly present.",
            "The document provides enough resume structure for a limited evidence-based review.",
        ],
    )
    improvements = normalize_string_list(
        data.get("improvements"),
        minimum=3,
        maximum=3,
        fallback=[
            "Add clearer evidence for tools, technologies, or domain-specific skills.",
            "Add actions, scope, and measurable results to roles or projects.",
            "Improve section clarity, dates, and contact or profile details where incomplete.",
        ],
    )
    suggestions = normalize_suggestions(data.get("suggestions"))

    return ResumeAnalysisPayload(
        overall_score=overall_score,
        grade=grade_from_score(overall_score),
        summary=_normalize_summary(data.get("summary"), overall_score),
        breakdown=breakdown,
        skill_chart=skill_chart,
        content_quality=content_quality,
        strengths=strengths,
        improvements=improvements,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def normalize_breakdown(value: object, overall_score: int) -> list[BreakdownItem]:
    scores_by_title: dict[str, int] = {}
    ordered_scores: list[int] = []
    if isinstance(value, list):
        for raw_item in value[:4]:
            if not isinstance(raw_item, dict):
                continue
            _ensure_allowed_keys(raw_item, BREAKDOWN_SCHEMA_KEYS, "breakdown item")
            score = bounded_score(_coerce_int(raw_item.get("score"), default=overall_score))
            title = _canonical_breakdown_title(raw_item.get("title"))
            if title is not None and title not in scores_by_title:
                scores_by_title[title] = score
                continue
            ordered_scores.append(score)

    remaining_titles = [title for title in BREAKDOWN_TITLES if title not in scores_by_title]
    for score in ordered_scores:
        if not remaining_titles:
            break
        scores_by_title[remaining_titles.pop(0)] = score

    items: list[BreakdownItem] = []
    for title in BREAKDOWN_TITLES:
        score = scores_by_title.get(title, overall_score)
        items.append(BreakdownItem(title=title, score=score, status=status_from_score(score), tone="navy"))
    return items


def normalize_skill_chart(value: object, breakdown: list[BreakdownItem]) -> list[ChartBarItem]:
    items: list[ChartBarItem] = []

    if isinstance(value, list):
        for raw_item in value[:4]:
            if not isinstance(raw_item, dict):
                continue
            _ensure_allowed_keys(raw_item, SKILL_CHART_SCHEMA_KEYS, "skill_chart item")
            items.append(
                ChartBarItem(
                    label=str(raw_item.get("label") or f"Area {len(items) + 1}"),
                    value=bounded_score(_coerce_int(raw_item.get("value"), default=70)),
                )
            )

    if items:
        return items

    fallback = breakdown[:4]
    labels = ["Technical", "Leadership", "Communication", "Problem Solving"]
    return [
        ChartBarItem(label=labels[index], value=fallback[index].score if index < len(fallback) else 70)
        for index in range(4)
    ]


def normalize_content_quality(value: object) -> list[LegendItem]:
    items: list[LegendItem] = []

    if isinstance(value, list):
        for raw_item in value[:3]:
            if not isinstance(raw_item, dict):
                continue
            _ensure_allowed_keys(raw_item, CONTENT_QUALITY_SCHEMA_KEYS, "content_quality item")
            items.append(
                LegendItem(
                    label=str(raw_item.get("label") or f"Segment {len(items) + 1}"),
                    value=str(raw_item.get("value") or "0%"),
                    tone=str(raw_item.get("tone") or "blue"),
                )
            )

    if items:
        return items

    return [
        LegendItem(label="Strong", value="60%", tone="green"),
        LegendItem(label="Good", value="25%", tone="blue"),
        LegendItem(label="Needs Work", value="15%", tone="orange"),
    ]


def normalize_string_list(value: object, minimum: int, maximum: int, fallback: list[str]) -> list[str]:
    items = [str(item).strip() for item in value] if isinstance(value, list) else []
    items = [item for item in items if item]

    if minimum <= len(items) <= maximum:
        return items
    if len(items) > maximum:
        return items[:maximum]
    return fallback[:minimum]


def normalize_suggestions(value: object) -> list[SuggestionItem]:
    items: list[SuggestionItem] = []

    if isinstance(value, list):
        for raw_item in value[:4]:
            if not isinstance(raw_item, dict):
                continue
            _ensure_allowed_keys(raw_item, SUGGESTION_SCHEMA_KEYS, "suggestion item")
            priority = str(raw_item.get("priority") or "Medium Priority")
            tone = str(raw_item.get("tone") or _tone_from_priority(priority))
            items.append(
                SuggestionItem(
                    title=str(raw_item.get("title") or f"Suggestion {len(items) + 1}"),
                    description=str(raw_item.get("description") or "Refine this section to strengthen your resume."),
                    priority=priority,
                    tone=tone,
                )
            )

    if 3 <= len(items) <= 4:
        return items
    if len(items) > 4:
        return items[:4]

    return [
        SuggestionItem(
            title="Add Quantified Impact",
            description="Rewrite at least two bullets with measurable business or project outcomes.",
            priority="High Priority",
            tone="red",
        ),
        SuggestionItem(
            title="Improve Role Alignment",
            description="Mirror more keywords from the job description in skills and experience sections.",
            priority="Medium Priority",
            tone="yellow",
        ),
        SuggestionItem(
            title="Tighten Formatting",
            description="Make section spacing, dates, and bullet styles fully consistent across the resume.",
            priority="Low Priority",
            tone="blue",
        ),
    ]


def log_token_usage(response_data: dict, provider_label: str) -> None:
    usage = response_data.get("usage")
    if not isinstance(usage, dict):
        return
    logger.info(
        "event=ai_token_usage provider=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
        provider_label,
        usage.get("prompt_tokens", "?"),
        usage.get("completion_tokens", "?"),
        usage.get("total_tokens", "?"),
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _normalize_summary(value: object, overall_score: int) -> str:
    summary = str(value).strip() if value is not None else ""
    return summary or summary_from_score(overall_score)


def _coerce_int(value: object, default: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _tone_from_priority(priority: str) -> str:
    lowered = priority.lower()
    if "high" in lowered:
        return "red"
    if "low" in lowered:
        return "blue"
    return "yellow"


def _canonical_breakdown_title(value: object) -> str | None:
    normalized = str(value or "").strip().lower()
    title_map = {
        "skills": "Skills",
        "experience": "Experience",
        "education": "Education",
        "resume format": "Resume Format",
        "format": "Resume Format",
    }
    return title_map.get(normalized)


def _ensure_allowed_keys(value: dict, allowed_keys: frozenset[str], label: str) -> None:
    extra_keys = sorted(set(value) - allowed_keys)
    if extra_keys:
        raise ValueError(f"AI response {label} included unexpected fields: {', '.join(extra_keys)}")
