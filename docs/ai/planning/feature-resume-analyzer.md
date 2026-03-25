---
phase: planning
title: "Resume Analyzer + Job Fit Scoring — Project Planning"
description: Task breakdown, milestones, dependencies, timeline, and risk mitigation for the Resume Analyzer feature.
---

# Project Planning & Task Breakdown

## Milestones
**What are the major checkpoints?**

- [ ] **Milestone 1:** Infrastructure Setup — Docker Compose with FastAPI + PostgreSQL + n8n all running
- [ ] **Milestone 2:** Authentication & User Management — JWT register/login, user model, route protection
- [ ] **Milestone 3:** CV Upload API — File upload to Cloudflare R2, DB schema + migrations, JD management
- [ ] **Milestone 4:** n8n Processing Pipeline — Webhook → text extraction → AI analysis → DB save
- [ ] **Milestone 5:** Results & History API — Score retrieval, history listing, comparison endpoint
- [ ] **Milestone 6:** Integration Testing & Polish — End-to-end flow, error handling, documentation

## Task Breakdown
**What specific work needs to be done?**

### Phase 1: Infrastructure & Foundation
- [ ] **Task 1.1:** Create `docker-compose.yml` with 3 services: `backend` (FastAPI), `db` (PostgreSQL 16), `n8n`
  - [ ] Set up environment variables (.env file) including Cloudflare R2 credentials, JWT secret
  - [ ] Health check configuration for all services
- [ ] **Task 1.2:** Scaffold FastAPI project structure
  - [ ] `app/main.py` with CORS config and lifespan
  - [ ] `app/core/config.py` — Settings via Pydantic BaseSettings (DB, n8n, R2, JWT)
  - [ ] `app/core/security.py` — JWT token utilities, password hashing
  - [ ] `app/db/session.py` — SQLAlchemy async engine + session
  - [ ] `Dockerfile` for the backend service
  - [ ] `requirements.txt` / `pyproject.toml`
- [ ] **Task 1.3:** Database schema & migrations
  - [ ] Define SQLAlchemy models: `User`, `JobDescription`, `CvUpload`, `AnalysisResult`, `CategoryScore`, `Suggestion`
  - [ ] Set up Alembic for migrations
  - [ ] Create initial migration
  - [ ] Seed script (optional, for dev)

### Phase 2: Authentication, JD Management & CV Upload
- [ ] **Task 2.1:** Authentication system
  - [ ] `POST /api/v1/auth/register` — User registration with email/password
  - [ ] `POST /api/v1/auth/login` — Login returning JWT access token
  - [ ] `app/api/deps.py` — `get_current_user` dependency for route protection
  - [ ] `app/services/auth_service.py` — Password hashing, JWT creation & verification
- [ ] **Task 2.2:** Cloudflare R2 storage service
  - [ ] `app/services/storage_service.py` — Upload/download file to Cloudflare R2 (S3-compatible API)
  - [ ] Configure R2 bucket credentials in environment variables
- [ ] **Task 2.3:** Job Description CRUD
  - [ ] `POST /api/v1/jd` — Create a reusable job description
  - [ ] `GET /api/v1/jd` — List user's saved job descriptions
- [ ] **Task 2.4:** `POST /api/v1/cv/upload` endpoint
  - [ ] Accept multipart/form-data (PDF/DOCX, max 10 MB)
  - [ ] Validate file type (MIME + extension check)
  - [ ] Upload file to Cloudflare R2
  - [ ] Insert `cv_upload` record with `user_id`, `storage_url`, `storage_key` (status: `pending`)
  - [ ] Return upload ID + status
- [ ] **Task 2.5:** Webhook trigger to n8n
  - [ ] HTTP POST to n8n webhook URL with cv_upload_id, storage_key, file_type, optional job_description_id
  - [ ] Handle n8n unavailability (retry / mark as failed)
- [ ] **Task 2.6:** Pydantic schemas for request/response validation
  - [ ] `UserCreate`, `UserResponse`, `TokenResponse`
  - [ ] `JDCreate`, `JDResponse`
  - [ ] `UploadResponse`, `AnalysisResultResponse`, `HistoryResponse`, `CompareResponse`

### Phase 2: CV Upload & File Processing
- [ ] **Task 2.1:** `POST /api/v1/cv/upload` endpoint
  - [ ] Accept multipart/form-data (PDF/DOCX, max 10 MB)
  - [ ] Validate file type (MIME + extension check)
  - [ ] Save file to shared volume
  - [ ] Insert `cv_upload` record (status: `pending`)
  - [ ] Return upload ID + status
- [ ] **Task 2.2:** Webhook trigger to n8n
  - [ ] HTTP POST to n8n webhook URL with cv_upload_id, file_path, file_type, optional JD
  - [ ] Handle n8n unavailability (retry / mark as failed)
- [ ] **Task 2.3:** Pydantic schemas for request/response validation
  - [ ] `UploadResponse`, `AnalysisResultResponse`, `HistoryResponse`, `CompareResponse`

### Phase 3: n8n Processing Pipeline
- [ ] **Task 3.1:** Create n8n workflow: Webhook Trigger
  - [ ] Receive POST with cv_upload_id, storage_key, file_type, job_description_id
  - [ ] Validate payload
- [ ] **Task 3.2:** Text extraction node
  - [ ] Download file from Cloudflare R2
  - [ ] PDF extraction via PyMuPDF (or n8n Code Node running Python/JS)
  - [ ] DOCX extraction via appropriate library
  - [ ] OCR fallback for scanned PDFs (Tesseract, if text extraction yields empty result)
  - [ ] Detect language (vi/en) from extracted text
  - [ ] Update `cv_upload.extracted_text` and `cv_upload.language` in DB
- [ ] **Task 3.3:** AI analysis node
  - [ ] Construct prompt with extracted text + optional JD (read from `job_description` table if ID provided)
  - [ ] Call OpenAI/Gemini API via HTTP Request node
  - [ ] Prompt engineering: request structured JSON output with overall_score, category scores, feedback, suggestions
  - [ ] Support both English and Vietnamese CV analysis in prompts
  - [ ] Handle rate limiting and timeout (retry 3x)
- [ ] **Task 3.4:** Save results to PostgreSQL
  - [ ] Parse AI JSON response
  - [ ] Insert `analysis_result` row (with `job_description_id` if applicable)
  - [ ] Insert `category_score` rows (4 categories)
  - [ ] Insert `suggestion` rows
  - [ ] Update `cv_upload.status` to `completed`
  - [ ] On failure: update status to `failed`, log error

### Phase 4: Results & History API
- [ ] **Task 4.1:** `GET /api/v1/cv/{id}/result` — Fetch analysis result with category breakdown, suggestions, and JD info (own CVs only)
- [ ] **Task 4.2:** `GET /api/v1/cv/history` — Paginated list of user's own past analyses (filename, score, language, date)
- [ ] **Task 4.3:** `GET /api/v1/cv/compare` — Compare multiple CVs by IDs, return side-by-side scores (own CVs only)
- [ ] **Task 4.4:** `GET /api/v1/cv/{id}/status` — Check processing status (polling endpoint)
- [ ] **Task 4.5:** Error handling & response standardization
  - [ ] Common error response schema
  - [ ] 401 for unauthenticated requests, 403 for accessing other users' data
  - [ ] 404 for missing CVs, 400 for invalid input, 500 for pipeline failures

### Phase 5: Integration, Testing & Documentation
- [ ] **Task 5.1:** End-to-end integration test (upload → n8n processes → result available)
- [ ] **Task 5.2:** Unit tests for FastAPI endpoints (upload, result, history, compare)
- [ ] **Task 5.3:** API documentation (Swagger/OpenAPI auto-generated by FastAPI)
- [ ] **Task 5.4:** README with setup instructions, env variable reference, and usage examples
- [ ] **Task 5.5:** n8n workflow export (JSON) checked into repo

## Dependencies
**What needs to happen in what order?**

```mermaid
graph LR
    P1["Phase 1<br/>Infrastructure"] --> P2["Phase 2<br/>Auth, JD & Upload"]
    P1 --> P3["Phase 3<br/>n8n Pipeline"]
    P2 --> P3
    P3 --> P4["Phase 4<br/>Results API"]
    P4 --> P5["Phase 5<br/>Testing & Docs"]
```

- **Phase 1 must complete first** — all other phases depend on Docker services running
- **Phase 2 must include auth before upload** — upload endpoint requires JWT authentication
- **Phase 2 and Phase 3 can partially overlap** — upload API can be built while n8n webhook node is configured
- **Phase 3 depends on Phase 2** — n8n receives webhook from upload endpoint
- **Phase 4 depends on Phase 3** — results API reads data written by n8n pipeline
- **Phase 5 depends on all** — integration testing requires full pipeline

### External Dependencies
- OpenAI or Gemini API key (must be provisioned before Phase 3)
- Cloudflare account with R2 storage bucket (must be provisioned before Phase 2)
- Docker & Docker Compose installed on dev machine
- n8n community edition Docker image

## Timeline & Estimates
**When will things be done?**

| Phase | Estimated Effort | Cumulative |
|-------|-----------------|------------|
| Phase 1: Infrastructure | 3–4 hours | 3–4 hours |
| Phase 2: Auth, JD & Upload | 5–7 hours | 8–11 hours |
| Phase 3: n8n Pipeline | 4–6 hours | 12–17 hours |
| Phase 4: Results API | 2–3 hours | 14–20 hours |
| Phase 5: Testing & Docs | 3–4 hours | 17–24 hours |
| **Total** | **17–24 hours** | — |

> Buffer: Add ~20% for unknowns (AI prompt tuning, n8n debugging) → **~20–29 hours total**

## Risks & Mitigation
**What could go wrong?**

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| AI response not matching expected JSON schema | High | Medium | Validate response, add retry with rephrased prompt, fallback to regex parsing |
| n8n workflow complexity (debugging) | Medium | Medium | Keep workflow simple, add error-handling branches, log all steps |
| OCR quality on scanned PDFs | Medium | High | Use Tesseract with pre-processing (deskew, contrast), flag low-confidence extractions |
| AI API rate limiting / cost | Medium | Medium | Implement token tracking, set daily limits, cache repeated analyses |
| Docker networking issues between services | Low | High | Use explicit network in docker-compose, test connectivity early |
| Large file uploads causing memory issues | Low | Medium | Stream file to disk, don't load entire file in memory |

## Resources Needed
**What do we need to succeed?**

### Tools & Services
- Docker Desktop (or Docker Engine + Compose)
- Python 3.11+
- OpenAI API key or Google Gemini API key
- Cloudflare account with R2 bucket
- n8n community edition (Docker image: `n8nio/n8n`)
- PostgreSQL 16 (Docker image: `postgres:16`)

### Key Libraries
- `fastapi`, `uvicorn` — Web framework
- `sqlalchemy[asyncio]`, `asyncpg` — Database ORM
- `alembic` — Migrations
- `python-jose[cryptography]` — JWT token handling
- `passlib[bcrypt]` — Password hashing
- `boto3` — Cloudflare R2 (S3-compatible) client
- `pymupdf` (fitz) — PDF text extraction
- `python-docx` — DOCX text extraction
- `python-multipart` — File upload parsing
- `httpx` — Async HTTP client (for n8n webhook calls)
- `pydantic-settings` — Configuration management
