---
phase: testing
title: "Resume Analyzer + Job Fit Scoring - Testing Strategy"
description: Testing approach, test cases, and quality assurance plan for the Resume Analyzer feature.
---

# Testing Strategy

## Current Implementation Notes (2026-05-11)

- Worker route integration tests exist for `file-worker`, `ai-worker`, and `persistence-worker`
- Internal workflow integration tests focus on `claim/fail` and duplicate protection
- Black-box webhook tests now cover stable n8n cases:
  - invalid resume -> `failed`
  - already completed upload -> `completed`
- The active runtime contract is:
  - `backend -> n8n -> file-worker -> ai-worker -> persistence-worker`
- User-facing result pages no longer rely on mock analysis output

## Test Coverage Goals
**What level of testing do we aim for?**

- Unit test coverage: 90%+ for backend service and route logic
- Integration tests: All API endpoints + n8n webhook trigger
- End-to-end: Full pipeline (`upload -> n8n -> file-worker -> ai-worker -> persistence-worker -> result query`)
- All acceptance criteria from requirements doc covered by at least one test

## Unit Tests
**What individual components need testing?**

### CV Upload Service
- [ ] Test successful PDF upload - file saved, DB record created with `pending` status
- [ ] Test successful DOCX upload - same validations apply
- [ ] Test invalid file type rejection (e.g., `.exe`, `.jpg`) - returns 400
- [ ] Test file size exceeding 10 MB - returns 413
- [ ] Test missing file in request - returns 422
- [ ] Test UUID filename generation - no collisions

### CV Result Service
- [ ] Test result retrieval by valid ID - returns full score breakdown
- [ ] Test result retrieval for non-existent ID - returns 404
- [ ] Test result retrieval for `pending` status - returns 409 with processing message
- [ ] Test result retrieval for `failed` status - returns 409 with failure reason

### History Service
- [ ] Test history listing with pagination (page 1, page_size 10)
- [ ] Test history listing with no records - returns empty list
- [ ] Test history ordering - most recent first

### Comparison Service
- [ ] Test comparing 2 valid CVs - returns side-by-side scores
- [ ] Test comparing with non-existent ID - returns 404
- [ ] Test comparing with only 1 ID - returns 400

### Text Extraction
- [ ] Test PDF with selectable text - extracts correctly
- [ ] Test PDF with only images (scanned) - falls back to OCR
- [ ] Test DOCX extraction - extracts correctly
- [ ] Test empty/corrupted file - returns appropriate error

## Integration Tests
**How do we test component interactions?**

- [ ] **Upload -> Webhook:** Upload file via API, verify n8n webhook was called with correct payload
- [ ] **n8n -> DB:** Trigger n8n workflow manually, verify DB records are created correctly
- [ ] **Full pipeline (live ai-worker path):** Upload -> n8n processes -> DB updated -> result API returns scores
- [ ] **DB connection pool:** Concurrent requests do not exhaust connections
- [ ] **Docker networking:** All services can communicate (`backend <-> db <-> n8n <-> workers`)

## End-to-End Tests
**What user flows need validation?**

- [ ] **Happy path:** Upload PDF -> wait -> GET result -> verify score breakdown + suggestions
- [ ] **With JD:** Upload PDF + Job Description -> verify Job Fit scoring reflects JD context
- [ ] **History flow:** Upload 3 CVs -> GET history -> verify all 3 appear in correct order
- [ ] **Comparison flow:** Upload 2 CVs -> GET compare -> verify side-by-side output
- [ ] **Error recovery:** Upload -> n8n fails -> status shows `failed` -> re-upload works

## Test Data
**What data do we use for testing?**

### Test Fixtures
- `tests/fixtures/sample_resume.pdf` - Standard resume with clear text
- `tests/fixtures/scanned_resume.pdf` - Image-only PDF (for OCR testing)
- `tests/fixtures/sample_resume.docx` - DOCX format resume
- `tests/fixtures/empty.pdf` - Empty/minimal PDF
- `tests/fixtures/large_file.pdf` - 11 MB file (exceeds limit)
- `tests/fixtures/not_a_resume.pdf` - Random document (edge case)

### Test Data Helpers
- Sample AI response JSON matching expected schema for parser and unit-level isolation tests
- Mock n8n webhook (using `httpx` mock or `respx` library) only for isolated trigger tests
- Test database seeded with pre-existing records for history/comparison tests

## Test Reporting & Coverage
**How do we verify and communicate test results?**

- Run tests: `docker compose exec backend pytest --cov=app --cov-report=html`
- Coverage threshold: fail CI if below 90%
- Coverage report output: `backend/htmlcov/index.html`
- All test results logged to stdout in CI

## Manual Testing
**What requires human validation?**

### API Testing (via Swagger UI)
- [ ] Open `http://localhost:8000/docs`
- [ ] Upload a real PDF via `/api/v1/cv/upload`
- [ ] Poll `/api/v1/cv/{id}/status` until `completed`
- [ ] View result at `/api/v1/cv/{id}/result`
- [ ] Verify score breakdown looks reasonable for the given CV
- [ ] Verify suggestions are specific and actionable

### n8n Workflow Testing
- [ ] Open n8n at `http://localhost:5678`
- [ ] Verify workflow is imported and active
- [ ] Trigger workflow manually with test data
- [ ] Check execution log for errors
- [ ] Verify DB records created correctly

### Docker Compose Validation
- [ ] `docker compose up -d` - all services start without errors
- [ ] `docker compose ps` - all services healthy
- [ ] `docker compose down && docker compose up -d` - restart works cleanly
- [ ] Volumes persist data across restarts

## Performance Testing
**How do we validate performance?**

- [ ] Measure end-to-end time for single CV upload + analysis (target: < 30s)
- [ ] Measure API response time for history endpoint with 100 records (target: < 200ms)
- [ ] Test concurrent uploads (5 simultaneous) - all process without error
- [ ] Monitor memory usage during PDF processing (especially large files)

## Bug Tracking
**How do we manage issues?**

- Use GitHub Issues for bug tracking
- Severity levels:
  - **Critical:** Pipeline fails entirely, no results returned
  - **High:** Incorrect scores, data loss, security issue
  - **Medium:** Slow performance, minor display issues
  - **Low:** Cosmetic, non-blocking
- Regression strategy: every bug should get a corresponding test case before the fix is merged
