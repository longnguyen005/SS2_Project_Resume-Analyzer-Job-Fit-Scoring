---
phase: requirements
title: "Resume Analyzer + Job Fit Scoring — Requirements"
description: Upload PDF CV → extract content → AI scoring → improvement suggestions → save results → view analysis history.
---

# Requirements & Problem Understanding

## Problem Statement
**What problem are we solving?**

- Job seekers lack objective, structured feedback on their resumes before applying
- HR/recruiters spend excessive time manually screening CVs against job descriptions
- There is no automated way to score a CV against a specific JD and get actionable improvement suggestions
- **Who is affected?** Job seekers, recruiters, HR teams, career coaches
- **Current workaround:** Manual review, generic online resume checkers with limited AI capabilities

## Goals & Objectives
**What do we want to achieve?**

### Primary Goals
- Allow users to upload a PDF/DOCX CV and receive an AI-generated score (0–100)
- Provide a detailed breakdown by criteria: **Skills, Experience, Education, Format**
- Generate actionable improvement suggestions per category
- Store analysis results and allow users to view history

### Secondary Goals
- Support comparison of multiple CVs against the same JD
- Support optional Job Description (JD) input for Job Fit Scoring
- Provide trend tracking across multiple uploads (score improvement over time)

### Non-Goals (out of scope for v1)
- Real-time collaborative editing of resumes
- ATS (Applicant Tracking System) integration
- Resume generation / auto-rewrite
- Social login (Google, GitHub OAuth) — v1 uses email/password only

## User Stories & Use Cases
**How will users interact with the solution?**

1. **As a job seeker**, I want to upload my CV (PDF/DOCX) so that I can get an objective AI score and improvement suggestions.
2. **As a job seeker**, I want to see a breakdown of my score by Skills, Experience, Education, and Format so that I know exactly where to improve.
3. **As a job seeker**, I want to optionally provide a Job Description so that the AI can score my CV against specific job requirements (Job Fit Scoring).
4. **As a user**, I want to view my analysis history so that I can track my resume improvements over time.
5. **As a user**, I want to compare multiple CVs side-by-side so that I can pick the strongest version.
6. **As a recruiter**, I want to batch-upload multiple CVs and see ranked scores against a JD.

### Key Workflows
1. **Upload & Analyze Flow:** Upload PDF → Backend receives file → n8n pipeline triggers → Text extraction → AI analysis → Score + suggestions saved to DB → Results returned to user
2. **History View Flow:** User opens history → sees list of past analyses → clicks one to view full details
3. **Comparison Flow:** User selects 2+ CVs → side-by-side score comparison displayed

### Edge Cases
- Corrupted or password-protected PDF uploads
- Scanned image-only PDFs (requires OCR fallback)
- Very short or empty CVs
- Extremely long CVs (>20 pages)
- Non-resume documents uploaded by mistake
- AI service timeout or rate limiting

## Success Criteria
**How will we know when we're done?**

- [ ] Users can upload PDF and DOCX files successfully
- [ ] User registration and login with JWT authentication works correctly
- [ ] Text is extracted accurately from uploaded documents (including OCR for scanned PDFs)
- [ ] AI returns a score (0–100) with breakdown across 4 categories
- [ ] AI analysis supports both English and Vietnamese CVs
- [ ] Improvement suggestions are specific and actionable per category
- [ ] Results are persisted in PostgreSQL and retrievable via history endpoint
- [ ] Users can only access their own CVs and analysis results
- [ ] Job descriptions can be saved and reused across analyses
- [ ] Files are stored on Cloudflare R2 cloud storage
- [ ] End-to-end pipeline (upload → score → display) completes in < 30 seconds
- [ ] n8n workflow triggers reliably from backend webhook
- [ ] Docker Compose brings up all services (FastAPI, PostgreSQL, n8n) in a single command

## Constraints & Assumptions
**What limitations do we need to work within?**

### Technical Constraints
- **Stack is fixed:** FastAPI + PostgreSQL + n8n + Docker Compose
- AI provider: OpenAI or Gemini (API key required, rate limits apply)
- PDF text extraction: PyMuPDF for native PDFs, OCR (Tesseract) for scanned PDFs
- File size limit: max 10 MB per upload
- Supported formats: PDF, DOCX only
- File storage: Cloudflare R2 (S3-compatible)
- Authentication: JWT-based (email/password)
- Multi-language: English + Vietnamese CV support

### Business Constraints
- JWT authentication required (email/password registration)
- AI API costs must be monitored (token usage tracking)

### Assumptions
- Users will primarily upload single-page to 5-page CVs
- AI responses (OpenAI/Gemini) will follow the prompted JSON schema consistently
- n8n community edition is sufficient (no enterprise features needed)
- PostgreSQL runs as a Docker container (no managed cloud DB for v1)
- Users have a Cloudflare account with R2 storage configured

## Questions & Open Items
**What do we still need to clarify?**

1. ~~**AI Provider:** Should we default to OpenAI (GPT-4) or Google Gemini? Or make it configurable?~~ → **Resolved:** Not configurable, use fixed provider
2. ~~**JD Input:** Is the Job Description input mandatory or optional for v1?~~ → **Resolved:** Optional, with dedicated JD management (save & reuse)
3. ~~**Authentication:** Should we add basic auth (API key or simple login) even for v1?~~ → **Resolved:** Yes, JWT authentication with email/password
4. ~~**File Storage:** Do we keep uploaded files permanently or delete after extraction?~~ → **Resolved:** Permanent storage on Cloudflare R2
5. ~~**Frontend:** Is a frontend UI in scope, or is this API-only for v1?~~ → **Resolved:** Yes, frontend UI is in scope
6. ~~**Scoring Weights:** Are the 4 categories equally weighted, or should weights be configurable?~~ → **Resolved:** Not configurable, equal weights
7. ~~**Multi-language:** Should the AI analysis support Vietnamese CVs in v1?~~ → **Resolved:** Yes, support English + Vietnamese
