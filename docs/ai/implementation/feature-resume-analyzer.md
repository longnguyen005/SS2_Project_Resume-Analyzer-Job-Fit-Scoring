---
phase: implementation
title: "Resume Analyzer + Job Fit Scoring — Implementation Guide"
description: Technical implementation notes, code structure, integration details, and best practices.
---

# Implementation Guide

## Development Setup
**How do we get started?**

### Prerequisites
- Docker Desktop (or Docker Engine v24+ with Compose v2)
- Python 3.11+ (for local development without Docker)
- OpenAI API key or Google Gemini API key
- Git

### Environment Setup
1. Clone the repository
2. Copy `.env.example` to `.env` and fill in values:
   ```env
   # Database
   POSTGRES_USER=cvmatch
   POSTGRES_PASSWORD=<secure-password>
   POSTGRES_DB=cv_matching
   DATABASE_URL=postgresql+asyncpg://cvmatch:<password>@db:5432/cv_matching

   # n8n
   N8N_WEBHOOK_URL=http://n8n:5678
   N8N_BASIC_AUTH_USER=admin
   N8N_BASIC_AUTH_PASSWORD=<secure-password>

   # AI Provider
   AI_PROVIDER=openai  # or "gemini"
   OPENAI_API_KEY=sk-...
   GEMINI_API_KEY=...

   # App
   UPLOAD_DIR=/data/uploads
   MAX_FILE_SIZE_MB=10
   ```
3. Start all services: `docker compose up -d`
4. Run migrations: `docker compose exec backend alembic upgrade head`
5. Access services:
   - FastAPI: `http://localhost:8000/docs` (Swagger UI)
   - n8n: `http://localhost:5678`
   - PostgreSQL: `localhost:5432`

## Code Structure
**How is the code organized?**

```
project-root/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app, CORS, lifespan
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic BaseSettings
│   │   │   └── exceptions.py       # Custom exception handlers
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py             # Dependency injection (DB session)
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       └── cv.py           # All CV endpoints
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── cv_upload.py
│   │   │   ├── analysis_result.py
│   │   │   ├── category_score.py
│   │   │   └── suggestion.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── cv.py               # Pydantic schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── cv_service.py       # Business logic
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── base.py             # SQLAlchemy Base
│   │       └── session.py          # Engine + session factory
│   └── tests/
│       ├── conftest.py
│       ├── test_upload.py
│       ├── test_results.py
│       └── test_history.py
├── n8n/
│   └── workflows/
│       └── cv-analysis-pipeline.json  # Exported n8n workflow
└── docs/
    └── ai/
        └── ...                     # Feature documentation
```

### Naming Conventions
- **Files:** snake_case (Python convention)
- **Classes:** PascalCase (e.g., `CvUpload`, `AnalysisResult`)
- **Endpoints:** kebab-case URLs (e.g., `/api/v1/cv/upload`)
- **Database tables:** snake_case (e.g., `cv_upload`, `category_score`)

## Implementation Notes
**Key technical details to remember:**

### Core Features

#### 1. File Upload
- Use `UploadFile` from FastAPI for streaming file reception
- Validate MIME type (`application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`)
- Generate UUID-based filename to avoid collisions    
- Save to `UPLOAD_DIR` volume shared with n8n container

#### 2. n8n Webhook Integration
- Use `httpx.AsyncClient` to POST to n8n webhook
- Fire-and-forget pattern: don't wait for n8n to complete
- Include `cv_upload_id` so n8n can update the correct DB record
- Implement timeout (5s) and retry logic for webhook call

#### 3. AI Prompt Engineering
- Structure the prompt to request a JSON response with exact schema
- Include few-shot examples in the system prompt for consistent output
- If JD is provided, include it in the prompt for Job Fit scoring
- Parse and validate AI response against expected schema before saving

#### 4. Text Extraction Strategy
```
If file_type == "pdf":
    text = pymupdf_extract(file_path)
    if len(text.strip()) < 50:  # likely scanned
        text = ocr_extract(file_path)
elif file_type == "docx":
    text = python_docx_extract(file_path)
```

### Patterns & Best Practices
- **Repository pattern** for database operations (separate from service logic)
- **Dependency injection** via FastAPI's `Depends()` for DB sessions
- **Async everywhere** — use `asyncpg` driver, `httpx.AsyncClient`
- **Configuration via environment** — never hardcode secrets or URLs
- **Structured logging** — use Python's `logging` with JSON formatter for production

## Integration Points
**How do pieces connect?**

### FastAPI → n8n
- Protocol: HTTP POST (webhook)
- URL: `{N8N_WEBHOOK_URL}/webhook/analyze-cv`
- Auth: n8n basic auth (if configured)
- Shared volume: both containers mount `/data/uploads`

### n8n → AI Provider
- Protocol: HTTPS REST API
- OpenAI: `POST https://api.openai.com/v1/chat/completions`
- Gemini: `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent`
- Auth: Bearer token (API key)

### n8n → PostgreSQL
- Protocol: Direct TCP connection via n8n Postgres node
- Connection: `db:5432` (Docker internal network)
- Credentials: stored in n8n credential manager

### FastAPI → PostgreSQL
- Protocol: `asyncpg` via SQLAlchemy async engine
- Connection pool: min 5, max 20 connections

## Error Handling
**How do we handle failures?**

| Error Scenario | Handling |
|---------------|----------|
| Invalid file type | Return 400 with clear error message |
| File too large | Return 413 (Payload Too Large) |
| n8n webhook unreachable | Mark status as `failed`, log error, return 202 with warning |
| AI API timeout | n8n retries 3x with exponential backoff (2s, 4s, 8s) |
| AI response unparseable | Save raw response, mark as `failed`, log for debugging |
| DB connection failure | FastAPI returns 503, rely on connection pool retry |
| OCR produces garbage | Flag low-confidence extraction in DB, include warning in response |

## Performance Considerations
**How do we keep it fast?**

- **File upload:** Stream to disk, don't buffer in memory
- **DB queries:** Index `cv_upload.created_at` for history pagination, `analysis_result.cv_upload_id` for lookups
- **Connection pooling:** SQLAlchemy async pool (min 5, max 20)
- **AI calls:** Single biggest bottleneck (~5–15s); cache results by file hash to avoid re-analyzing identical CVs
- **n8n:** Use workflow execution timeout (60s) to prevent hanging

## Security Notes
**What security measures are in place?**

- **File upload validation:** Check MIME type + extension + magic bytes
- **Path traversal prevention:** Use UUID filenames, never use user-provided filenames in paths
- **Input sanitization:** Pydantic validates all API inputs
- **Secrets management:** All API keys and passwords via environment variables
- **CORS:** Configured to allow only specific origins (configurable)
- **Rate limiting:** Implement via middleware (e.g., `slowapi`) — 10 uploads/minute per IP
