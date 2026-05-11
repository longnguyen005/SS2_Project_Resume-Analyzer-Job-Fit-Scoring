# API Contract — Resume Analyzer v1 (FROZEN)

> **Status**: FROZEN as of Week 12  
> **Base URL**: `{BACKEND_PUBLIC_URL}/api/v1`  
> **Auth**: JWT Bearer token (except registration and login)  

---

## Common Response Envelope

All successful responses use:

```json
{
  "success": true,
  "message": "Human-readable message.",
  "data": { ... }
}
```

All error responses use:

```json
{
  "success": false,
  "message": "Human-readable error message.",
  "errors": [
    { "field": "body.email", "message": "Invalid email address.", "type": "value_error" }
  ]
}
```

### Standard HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Successful GET/PUT/DELETE |
| 201 | Successful POST (resource created) |
| 400 | Bad request / validation error |
| 401 | Unauthenticated (missing or invalid JWT) |
| 404 | Resource not found (or not owned by user) |
| 409 | Conflict (e.g., analysis not completed yet) |
| 422 | Request validation failed (Pydantic) |
| 500 | Internal server error |
| 503 | Service unavailable (n8n/R2 not configured) |

---

## 1. Authentication (`/auth`)

### POST `/auth/register`

Create a new user account.

**Request** (`application/json`):
```json
{
  "email": "user@example.com",
  "password": "min8chars",
  "full_name": "Full Name"
}
```

**Response** (`201`):
```json
{
  "success": true,
  "message": "Account created successfully.",
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Full Name",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

**Errors**: `400` if email already registered, `422` if validation fails.

---

### POST `/auth/login`

Authenticate and receive a JWT token.

**Request** (`application/x-www-form-urlencoded`):
```
username=user@example.com&password=min8chars
```

**Response** (`200`):
```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer"
  }
}
```

**Errors**: `401` if invalid credentials.

---

### GET `/auth/me`

Get current authenticated user. Requires `Authorization: Bearer <token>`.

**Response** (`200`):
```json
{
  "success": true,
  "message": "Current user retrieved successfully.",
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Full Name",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

---

### GET `/auth/oauth/{provider}/login`

Initiate OAuth login flow for `google` or `github`. Redirects to provider.

### GET `/auth/oauth/{provider}/callback`

OAuth callback. Redirects to `{FRONTEND_URL}/oauth/callback?access_token=...` or `?error=...`.

---

## 2. Job Descriptions (`/jd`)

All endpoints require `Authorization: Bearer <token>`.  
Users can only access their own job descriptions.

### POST `/jd`

Create a new job description.

**Request** (`application/json`):
```json
{
  "title": "Backend Developer",
  "description_text": "We are looking for a backend developer with..."
}
```

**Response** (`201`):
```json
{
  "success": true,
  "message": "Job description created successfully.",
  "data": {
    "id": "uuid",
    "title": "Backend Developer",
    "description_text": "We are looking for...",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
  }
}
```

---

### GET `/jd`

List all job descriptions owned by the current user (sorted by `created_at DESC`).

**Response** (`200`):
```json
{
  "success": true,
  "message": "Job descriptions retrieved successfully.",
  "data": [ { "id": "uuid", "title": "...", "description_text": "...", "created_at": "...", "updated_at": "..." } ]
}
```

---

### GET `/jd/{jd_id}`

Get a single job description by ID.

**Response** (`200`): Single JD object in `data`.  
**Errors**: `404` if not found or not owned.

---

### PUT `/jd/{jd_id}`

Update a job description. Partial updates supported (only send fields to change).

**Request** (`application/json`):
```json
{ "title": "Updated Title" }
```

**Response** (`200`): Updated JD object in `data`.  
**Errors**: `404` if not found or not owned.

---

### DELETE `/jd/{jd_id}`

Delete a job description.

**Response** (`200`):
```json
{
  "success": true,
  "message": "Job description deleted successfully.",
  "data": { "id": "uuid" }
}
```

**Errors**: `404` if not found or not owned.

---

## 3. CV Operations (`/cv`)

All endpoints require `Authorization: Bearer <token>`.  
Users can only access their own CVs.

### POST `/cv/upload`

Upload a CV for analysis.

**Request** (`multipart/form-data`):
- `file` (required): PDF or DOCX, max 10 MB
- `job_description_id` (optional): UUID of a saved job description

**Response** (`201`):
```json
{
  "success": true,
  "message": "CV uploaded successfully. Analysis has started in the background.",
  "data": {
    "id": "uuid",
    "job_description_id": "uuid | null",
    "filename": "resume.pdf",
    "stored_filename": "abc123.pdf",
    "storage_path": "/app/uploads/user_id/abc123.pdf",
    "storage_key": "uploads/user_id/abc123.pdf | null",
    "storage_url": "https://... | null",
    "file_type": "pdf",
    "file_size_bytes": 123456,
    "language": null,
    "status": "pending",
    "failure_reason": null,
    "failed_stage": null,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
  }
}
```

Implementation note:

- Upload success means the backend has accepted the file, stored metadata, and triggered the staged n8n workflow.
- The active background runtime contract is `backend -> n8n -> file-worker -> ai-worker -> persistence-worker`.

**Errors**: `400` unsupported file type or size exceeded, `404` JD not found, `503` n8n not configured.

---

### GET `/cv`

List all CVs owned by the current user with analysis summary (sorted by `created_at DESC`).

**Response** (`200`):
```json
{
  "success": true,
  "message": "CV uploads retrieved successfully.",
  "data": [
    {
      "id": "uuid",
      "job_description_id": "uuid | null",
      "filename": "resume.pdf",
      "file_type": "pdf",
      "file_size_bytes": 123456,
      "status": "completed | pending | processing | failed",
      "failure_reason": "string | null",
      "failed_stage": "orchestration | extract | analyze | complete | null",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z",
      "analysis_summary": {
        "overall_score": 82,
        "grade": "Very Good",
        "analyzed_at": "2026-01-01T00:00:00Z",
        "analysis_provider": "gemini"
      }
    }
  ]
}
```

---

### GET `/cv/{cv_id}`

Get a single CV upload record by ID.

**Response** (`200`): Full `CvUploadRead` object in `data`.  
**Errors**: `404` if not found or not owned.

---

### GET `/cv/{cv_id}/status`

Poll the processing status of a CV upload.

**Response** (`200`):
```json
{
  "success": true,
  "message": "CV status retrieved successfully.",
  "data": {
    "id": "uuid",
    "status": "pending | processing | completed | failed",
    "failure_reason": "string | null",
    "failed_stage": "orchestration | extract | analyze | complete | null",
    "updated_at": "2026-01-01T00:00:00Z"
  }
}
```

---

### GET `/cv/{cv_id}/result`

Get full analysis result for a completed CV.

**Response** (`200`):
```json
{
  "success": true,
  "message": "CV result retrieved successfully.",
  "data": {
    "cv_id": "uuid",
    "filename": "resume.pdf",
    "analyzed_at": "2026-01-01T00:00:00Z",
    "analysis_provider": "gemini",
    "overall_score": 82,
    "grade": "Very Good",
    "summary": "The resume shows...",
    "breakdown": [
      { "title": "Skills", "score": 85, "status": "Excellent", "tone": "navy" },
      { "title": "Experience", "score": 80, "status": "Good", "tone": "navy" },
      { "title": "Education", "score": 78, "status": "Good", "tone": "navy" },
      { "title": "Resume Format", "score": 82, "status": "Good", "tone": "navy" }
    ],
    "skill_chart": [
      { "label": "Technical", "value": 85 },
      { "label": "Leadership", "value": 70 }
    ],
    "content_quality": [
      { "label": "Strong", "value": "60%", "tone": "green" },
      { "label": "Good", "value": "25%", "tone": "blue" },
      { "label": "Needs Work", "value": "15%", "tone": "orange" }
    ],
    "strengths": ["Point 1", "Point 2", "Point 3"],
    "improvements": ["Point 1", "Point 2", "Point 3"],
    "suggestions": [
      {
        "title": "Add Quantified Impact",
        "description": "Rewrite key bullet points...",
        "priority": "High Priority",
        "tone": "red"
      }
    ]
  }
}
```

**Errors**: `404` if not found, `409` if analysis is still pending/processing or has already failed.

---

## 4. Internal Workflow (`/internal/cv`)

Used by n8n pipeline workers. Requires `x-internal-workflow-secret` header.

### POST `/internal/cv/{cv_id}/claim`

Claim a CV for processing (idempotent).

**Response**: `{ "cv_upload_id": "uuid", "claim_status": "claimed | already_processing | already_completed" }`

### POST `/internal/cv/{cv_id}/fail`

Mark a CV as failed.

**Request**: `{ "failure_reason": "...", "failed_stage": "extract | analyze | complete" }`

---

## 5. Health Check

### GET `/health`

**Response**: `{ "status": "ok" }`

No authentication required.
