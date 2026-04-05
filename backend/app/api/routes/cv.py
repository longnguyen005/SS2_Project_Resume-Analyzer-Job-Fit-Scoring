from __future__ import annotations

import random
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import CvUpload, JobDescription, User
from app.schemas.common import APIResponse
from app.schemas.cv import (
    CvResultBreakdownItem,
    CvResultChartBar,
    CvResultLegendItem,
    CvResultRead,
    CvResultSuggestion,
    CvStatusRead,
    CvUploadRead,
)
from app.services.storage import save_upload

router = APIRouter()


@router.post("/upload", response_model=APIResponse[CvUploadRead], status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    job_description_id: UUID | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[CvUploadRead]:
    if job_description_id is not None:
        result = await db.execute(
            select(JobDescription).where(
                JobDescription.id == job_description_id,
                JobDescription.user_id == current_user.id,
            )
        )
        job_description = result.scalar_one_or_none()
        if job_description is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")

    try:
        stored_filename, storage_path, file_size = await save_upload(file, str(current_user.id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    file_type = (file.filename or "").split(".")[-1].lower()
    cv_upload = CvUpload(
        user_id=current_user.id,
        job_description_id=job_description_id,
        filename=file.filename or stored_filename,
        stored_filename=stored_filename,
        storage_path=storage_path,
        file_type=file_type,
        file_size_bytes=file_size,
        status="pending",
    )
    db.add(cv_upload)
    await db.commit()
    await db.refresh(cv_upload)
    return APIResponse(message="CV uploaded successfully.", data=CvUploadRead.model_validate(cv_upload))


@router.get("", response_model=APIResponse[list[CvUploadRead]])
async def list_cv_uploads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[CvUploadRead]]:
    result = await db.execute(
        select(CvUpload).where(CvUpload.user_id == current_user.id).order_by(CvUpload.created_at.desc())
    )
    items = [CvUploadRead.model_validate(item) for item in result.scalars().all()]
    return APIResponse(message="CV uploads retrieved successfully.", data=items)


@router.get("/{cv_id}", response_model=APIResponse[CvUploadRead])
async def get_cv_upload(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[CvUploadRead]:
    result = await db.execute(
        select(CvUpload).where(CvUpload.id == cv_id, CvUpload.user_id == current_user.id)
    )
    cv_upload = result.scalar_one_or_none()
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")
    return APIResponse(message="CV upload retrieved successfully.", data=CvUploadRead.model_validate(cv_upload))


@router.get("/{cv_id}/status", response_model=APIResponse[CvStatusRead])
async def get_cv_status(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[CvStatusRead]:
    result = await db.execute(
        select(CvUpload).where(CvUpload.id == cv_id, CvUpload.user_id == current_user.id)
    )
    cv_upload = result.scalar_one_or_none()
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")
    return APIResponse(
        message="CV status retrieved successfully.",
        data=CvStatusRead(id=cv_upload.id, status=cv_upload.status, updated_at=cv_upload.updated_at),
    )


@router.get("/{cv_id}/result", response_model=APIResponse[CvResultRead])
async def get_cv_result(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[CvResultRead]:
    result = await db.execute(
        select(CvUpload).where(CvUpload.id == cv_id, CvUpload.user_id == current_user.id)
    )
    cv_upload = result.scalar_one_or_none()
    if cv_upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV upload not found")

    if cv_upload.status != "completed":
        cv_upload.status = "completed"
        await db.commit()
        await db.refresh(cv_upload)

    mock_result = _build_mock_result(cv_upload)
    return APIResponse(message="CV result retrieved successfully.", data=mock_result)


def _build_mock_result(cv_upload: CvUpload) -> CvResultRead:
    seed = cv_upload.id.int % (2**32)
    rng = random.Random(seed)

    skills_score = rng.randint(78, 94)
    experience_score = rng.randint(72, 91)
    education_score = rng.randint(76, 93)
    format_score = rng.randint(74, 89)
    overall_score = round((skills_score + experience_score + education_score + format_score) / 4)

    technical_score = min(100, skills_score + rng.randint(-3, 4))
    leadership_score = rng.randint(68, 88)
    communication_score = rng.randint(74, 92)
    problem_solving_score = rng.randint(77, 94)

    strong = rng.randint(52, 68)
    good = rng.randint(20, 32)
    needs_work = max(100 - strong - good, 8)

    strengths_pool = [
        "Clear overall structure that is easy to scan quickly.",
        "Relevant technical skills are visible in the resume content.",
        "Experience section shows solid alignment with target roles.",
        "Education and supporting credentials are presented clearly.",
        "The document appears concise and recruiter-friendly.",
    ]
    improvements_pool = [
        "Add more measurable achievements with concrete numbers.",
        "Include more role-specific keywords from the job description.",
        "Strengthen project impact statements with outcomes.",
        "Improve formatting consistency across sections.",
        "Make leadership and collaboration examples more explicit.",
    ]
    suggestions_pool = [
        {
            "title": "Add Quantified Impact",
            "description": "Rewrite key bullet points with measurable outcomes such as growth, savings, scale, or delivery speed.",
            "priority": "High Priority",
            "tone": "red",
        },
        {
            "title": "Tailor Keywords To The Role",
            "description": "Mirror the wording of the target job description so your resume matches role-specific expectations more closely.",
            "priority": "High Priority",
            "tone": "yellow",
        },
        {
            "title": "Strengthen Action Verbs",
            "description": "Start bullets with stronger verbs like built, optimized, led, automated, and delivered.",
            "priority": "Medium Priority",
            "tone": "blue",
        },
        {
            "title": "Improve Formatting Consistency",
            "description": "Make dates, bullet indentation, and heading styles more consistent to improve readability.",
            "priority": "Low Priority",
            "tone": "blue",
        },
        {
            "title": "Highlight Business Value",
            "description": "Explain why your work mattered, not only what you did, especially for projects and recent roles.",
            "priority": "Medium Priority",
            "tone": "yellow",
        },
    ]

    strengths = rng.sample(strengths_pool, 4)
    improvements = rng.sample(improvements_pool, 3)
    suggestions = [
        CvResultSuggestion(**item)
        for item in rng.sample(suggestions_pool, 4)
    ]

    return CvResultRead(
        cv_id=cv_upload.id,
        filename=cv_upload.filename,
        analyzed_at=cv_upload.updated_at,
        overall_score=overall_score,
        grade=_grade_from_score(overall_score),
        summary=_summary_from_score(overall_score),
        breakdown=[
            CvResultBreakdownItem(title="Skills", score=skills_score, status=_status_from_score(skills_score), tone="navy"),
            CvResultBreakdownItem(
                title="Experience",
                score=experience_score,
                status=_status_from_score(experience_score),
                tone="navy",
            ),
            CvResultBreakdownItem(
                title="Education",
                score=education_score,
                status=_status_from_score(education_score),
                tone="navy",
            ),
            CvResultBreakdownItem(
                title="Resume Format",
                score=format_score,
                status=_status_from_score(format_score),
                tone="navy",
            ),
        ],
        skill_chart=[
            CvResultChartBar(label="Technical", value=technical_score),
            CvResultChartBar(label="Leadership", value=leadership_score),
            CvResultChartBar(label="Communication", value=communication_score),
            CvResultChartBar(label="Problem Solving", value=problem_solving_score),
        ],
        content_quality=[
            CvResultLegendItem(label="Strong", value=f"{strong}%", tone="green"),
            CvResultLegendItem(label="Good", value=f"{good}%", tone="blue"),
            CvResultLegendItem(label="Needs Work", value=f"{needs_work}%", tone="orange"),
        ],
        strengths=strengths,
        improvements=improvements,
        suggestions=suggestions,
    )


def _grade_from_score(score: int) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 80:
        return "Very Good"
    if score >= 70:
        return "Good"
    return "Needs Improvement"


def _status_from_score(score: int) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 75:
        return "Good"
    return "Needs Work"


def _summary_from_score(score: int) -> str:
    if score >= 90:
        return "Your resume is strongly positioned. A few refinements can make it even more competitive."
    if score >= 80:
        return "Your resume is performing well. The suggestions below can help increase clarity and impact."
    if score >= 70:
        return "Your resume has a solid foundation, but several sections can be improved for stronger alignment."
    return "Your resume needs more refinement before it is ready for strong applications."
