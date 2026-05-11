from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.services.ai_response_normalizer import (
    ANALYSIS_JSON_SCHEMA,
    ANALYSIS_SYSTEM_PROMPT,
    BreakdownItem,
    ChartBarItem,
    LegendItem,
    PROMPT_VERSION,
    ResumeAnalysisPayload,
    SuggestionItem,
    extract_message_content,
    grade_from_score,
    log_token_usage,
    parse_json_content,
    payload_from_ai_json,
    status_from_score,
    summary_from_score,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LiveAIProvider:
    label: str
    base_url: str
    api_key: str
    model: str


class LiveAIUnavailableError(RuntimeError):
    pass


async def analyze_resume(
    resume_text: str,
    job_description_text: str | None = None,
    cv_upload_id: str | None = None,
) -> tuple[ResumeAnalysisPayload, str]:
    providers = _get_live_ai_providers()
    if not providers:
        raise LiveAIUnavailableError(
            "Live AI analysis is not configured. Please configure a live AI provider and try again."
        )

    provider_failures: list[str] = []
    for provider in providers:
        try:
            logger.info(
                "event=ai_analysis_start cv_upload_id=%s provider=%s model=%s prompt_version=%s",
                cv_upload_id or "unknown",
                provider.label,
                provider.model,
                PROMPT_VERSION,
            )
            payload = await analyze_resume_with_ai(resume_text, job_description_text, provider=provider)
            logger.info(
                "event=ai_analysis_success cv_upload_id=%s provider=%s overall_score=%s",
                cv_upload_id or "unknown",
                provider.label,
                payload.overall_score,
            )
            return payload, provider.label
        except Exception as exc:
            logger.warning(
                "event=ai_analysis_failure cv_upload_id=%s provider=%s model=%s error=%s",
                cv_upload_id or "unknown",
                provider.label,
                provider.model,
                exc,
            )
            provider_failures.append(f"{provider.label} ({provider.model}): {_summarize_provider_error(exc)}")

    raise LiveAIUnavailableError(
        "Live AI analysis is temporarily unavailable. "
        f"Provider errors: {'; '.join(provider_failures)}"
    )


async def analyze_resume_with_ai(
    resume_text: str,
    job_description_text: str | None = None,
    provider: LiveAIProvider | None = None,
) -> ResumeAnalysisPayload:
    resolved_provider = provider or _get_primary_live_ai_provider()
    if resolved_provider is None:
        raise ValueError("No live AI provider is configured.")

    response_json = await _request_ai_analysis(
        resume_text=resume_text,
        job_description_text=job_description_text,
        provider=resolved_provider,
    )
    content = extract_message_content(response_json)
    normalized = parse_json_content(content)
    return payload_from_ai_json(normalized)


async def _request_ai_analysis(
    *,
    resume_text: str,
    job_description_text: str | None,
    provider: LiveAIProvider,
) -> dict:
    headers = {
        "Authorization": f"Bearer {provider.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": provider.model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(resume_text, job_description_text)},
        ],
    }

    async with httpx.AsyncClient(timeout=settings.ai_request_timeout_seconds) as client:
        response = await _post_with_retries(
            client=client,
            url=f"{provider.base_url.rstrip('/')}/chat/completions",
            headers=headers,
            payload=payload,
        )
        response.raise_for_status()
        response_data = response.json()
        log_token_usage(response_data, provider.label)
        return response_data


async def _post_with_retries(
    *,
    client: httpx.AsyncClient,
    url: str,
    headers: dict[str, str],
    payload: dict,
    max_attempts: int = 3,
) -> httpx.Response:
    retryable_statuses = {429, 500, 502, 503, 504}
    last_response: httpx.Response | None = None
    last_error: Exception | None = None

    for attempt in range(max_attempts):
        try:
            response = await client.post(url, headers=headers, json=payload)
            last_response = response
            if response.status_code not in retryable_statuses or attempt == max_attempts - 1:
                return response
        except httpx.RequestError as exc:
            last_error = exc
            if attempt == max_attempts - 1:
                raise

        await asyncio.sleep(1.2 * (2**attempt))

    if last_error is not None:
        raise last_error
    return last_response


def _get_live_ai_providers() -> list[LiveAIProvider]:
    if settings.ai_mode.lower() != "live":
        return []

    providers: list[LiveAIProvider] = []
    primary_provider = _get_primary_live_ai_provider()
    if primary_provider is not None:
        providers.append(primary_provider)

    fallback_provider = _get_fallback_live_ai_provider(primary_provider)
    if fallback_provider is not None:
        providers.append(fallback_provider)

    return providers


def _get_primary_live_ai_provider() -> LiveAIProvider | None:
    if not _is_provider_configured(
        base_url=settings.ai_base_url,
        api_key=settings.ai_api_key,
        model=settings.ai_model,
    ):
        return None

    return LiveAIProvider(
        label=settings.ai_provider_label,
        base_url=settings.ai_base_url,
        api_key=settings.ai_api_key,
        model=settings.ai_model,
    )


def _get_fallback_live_ai_provider(primary_provider: LiveAIProvider | None) -> LiveAIProvider | None:
    fallback_base_url = settings.ai_fallback_base_url or settings.ai_base_url
    fallback_api_key = settings.ai_fallback_api_key or settings.ai_api_key
    fallback_model = settings.ai_fallback_model.strip()

    if not _is_provider_configured(
        base_url=fallback_base_url,
        api_key=fallback_api_key,
        model=fallback_model,
    ):
        return None

    fallback_provider = LiveAIProvider(
        label=settings.ai_fallback_provider_label,
        base_url=fallback_base_url,
        api_key=fallback_api_key,
        model=fallback_model,
    )
    if primary_provider is not None and fallback_provider == primary_provider:
        return None
    return fallback_provider


def _is_provider_configured(base_url: str, api_key: str, model: str) -> bool:
    return bool(base_url and str(api_key).strip() and model.strip())


def _build_user_prompt(resume_text: str, job_description_text: str | None) -> str:
    return (
        "Analyze the following input fields.\n\n"
        "Input contract:\n"
        "- resume_text: extracted resume or CV text.\n"
        "- job_description_text: target job description text; it may be empty.\n"
        "- If resume_text is very short, nearly blank, or lacks enough resume evidence, treat the case as insufficient data and score conservatively.\n\n"
        f"resume_text:\n{resume_text}\n\n"
        f"job_description_text:\n{job_description_text or ''}\n\n"
        "Important instructions:\n"
        "- Use only evidence present in resume_text and job_description_text.\n"
        "- Treat missing evidence as missing, not implied.\n"
        "- If job_description_text is empty, evaluate against a reasonable general standard for the most likely role this resume targets.\n"
        "- If the document does not look like a resume or CV, or if the document is unclear, explain that clearly in the summary and score conservatively.\n"
        "- Compute the final overall score from the weighted breakdown exactly as instructed in the system prompt.\n"
        "- Keep feedback practical, concise, evidence-based, and recruiter-relevant.\n"
        "- Return exactly one JSON object with no markdown or extra text.\n\n"
        "Return JSON using this exact shape and naming:\n"
        f"{json.dumps(ANALYSIS_JSON_SCHEMA, ensure_ascii=True)}"
    )


def _summarize_provider_error(exc: Exception) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        if status_code == 429:
            return "rate limited"
        if status_code == 503:
            return "service unavailable"
        if status_code >= 500:
            return f"provider server error {status_code}"
        return f"http error {status_code}"
    return str(exc)


# Compatibility aliases for existing imports/tests while Phase 2 is in progress.
_grade_from_score = grade_from_score
_status_from_score = status_from_score
_summary_from_score = summary_from_score
