# Hardening Report — Resume Analyzer v1

> **Date**: 2026-05-11  
> **Scope**: Week 12–13 hardening tasks  
> **Author**: Auto-generated from code analysis + implementation

---

## 1. Summary

This report documents all reliability, observability, and stability improvements applied to the Resume Analyzer system during the hardening phase.

---

## 2. Changes Applied

### 2.1 Stuck Job Recovery (P0 Fix)

**Problem**: If the n8n pipeline crashes mid-workflow (or n8n restarts), CVs remain in `processing` status permanently. Users see "Processing…" indefinitely with no resolution.

**Solution**: Added a **background task** in `backend/app/main.py` that runs every 5 minutes:
- Detects CVs with `status = 'processing'` AND `updated_at` older than `n8n_processing_claim_ttl_seconds` (default 900s / 15 min)
- Automatically marks them as `failed` with `failure_reason = "Processing timed out. The analysis pipeline did not complete in time. Please upload the file again."`
- Logs each recovery event with affected `cv_ids`

**Files modified**: `backend/app/main.py`

---

### 2.2 Structured Logging with cv_id Correlation

**Problem**: Debugging pipeline failures required manual log correlation across multiple services. No consistent structured format.

**Solution**: Implemented structured event logging across all pipeline components:

| Component | Events Logged |
|-----------|--------------|
| `cv.py` (routes) | `cv_upload_created` with cv_id, user_id, filename, file_type, size, jd_id |
| `workflow_trigger.py` | `n8n_webhook_trigger_attempt`, `n8n_webhook_trigger_success`, `n8n_webhook_trigger_failure` |
| `cv_state.py` | `cv_claimed`, `cv_claim_skip` (already_processing/completed), `cv_claim_expired`, `cv_marked_failed` |
| `storage_service.py` | `r2_upload_success`, `r2_upload_failure`, `r2_not_configured` |
| `resume_analyzer.py` | `ai_analysis_start`, `ai_analysis_success`, `ai_analysis_failure`, `ai_token_usage`, `scoring_drift_detected` |
| `main.py` | `stuck_jobs_recovered`, `stuck_job_recovery_error` |

**Log format**: `event=<name> cv_upload_id=<id> key=value key=value`

**Files modified**: `cv_state.py`, `storage_service.py`, `resume_analyzer.py`, `cv.py`, `main.py`

---

### 2.3 Scoring Consistency Improvements

**Problem**: AI scoring could vary between runs of the same CV.

**Measures implemented**:

| Measure | Status | File |
|---------|--------|------|
| `temperature=0` | ✅ Already in place | `resume_analyzer.py` |
| `response_format: json_object` | ✅ Already in place | `resume_analyzer.py` |
| Weighted overall_score recalculated server-side | ✅ Already in place | `resume_analyzer.py` |
| **Prompt version tracking** (`PROMPT_VERSION = "v2.1-hardened"`) | ✅ **NEW** | `resume_analyzer.py` |
| **Scoring drift detection** (warn if AI score differs > 3 from calculated) | ✅ **NEW** | `resume_analyzer.py` |
| **Token usage logging** (track prompt/completion/total tokens) | ✅ **NEW** | `resume_analyzer.py` |

**Files modified**: `resume_analyzer.py`

---

### 2.4 Pipeline Reliability (R2 + n8n + AI)

| Component | Reliability Measure | Status |
|-----------|-------------------|--------|
| **R2** | Local fallback when R2 upload fails | ✅ Already in place |
| **R2** | Structured logging for success/failure | ✅ **NEW** |
| **n8n webhook** | Retry with configurable max_attempts (default 2) | ✅ Already in place |
| **n8n webhook** | Timeout configurable (default 5s) | ✅ Already in place |
| **n8n pipeline** | Claim-based idempotency (prevents duplicate processing) | ✅ Already in place |
| **n8n pipeline** | Claim TTL with expiry logging | ✅ **NEW** |
| **n8n pipeline** | Stuck job auto-recovery | ✅ **NEW** |
| **AI** | Multi-provider fallback (primary → fallback) | ✅ Already in place |
| **AI** | Retry 3x with exponential backoff | ✅ Already in place |
| **AI** | Structured logging for provider failures | ✅ **NEW** |

---

### 2.5 API Contract Freeze

**Created**: `docs/api-contract.md` — Formal documentation of all API endpoints with exact request/response schemas, error codes, and authentication requirements. Marked as **FROZEN**.

---

### 2.6 Performance Indexes

**Created**: `backend/alembic/versions/0005_performance_indexes.py`

New database indexes:
- `ix_cv_uploads_user_id_created_at` — Speeds up history listing (user's CVs sorted by date)
- `ix_analysis_results_cv_upload_id` — Speeds up result lookups by CV
- `ix_job_descriptions_user_id` — Speeds up JD listing for a user

---

### 2.7 Frontend UI State Polish

All critical UI states verified and complete:

| Page | Loading | Empty | Error | Failed/Retry | Completed |
|------|---------|-------|-------|------|-----------|
| ProcessingPage | ✅ | ✅ | ✅ | ✅ **Enhanced** | ✅ |
| ResultPageConnected | ✅ | ✅ | ✅ (with retry) | ✅ (409 handling) | ✅ |
| HistoryPage | ✅ | ✅ | ✅ | N/A | ✅ |
| UploadPage | ✅ | N/A | ✅ | N/A | ✅ |

**Enhancement**: Added prominent "Upload Again" and "View History" buttons on ProcessingPage when processing fails.

---

## 3. Bug Summary

| ID | Severity | Description | Status |
|----|---------|-------------|--------|
| B1 | P0 | CVs stuck in `processing` forever if n8n crashes | ✅ Fixed (stuck job recovery) |
| B2 | P1 | No structured logging — difficult to trace failures by cv_id | ✅ Fixed (event logging) |
| B3 | P1 | No scoring drift detection — inconsistencies go unnoticed | ✅ Fixed (drift warning) |
| B4 | P2 | No DB indexes for hot queries — latency risk at scale | ✅ Fixed (migration 0005) |
| B5 | P2 | ProcessingPage only had small "Return to Upload" link on failure | ✅ Fixed (retry buttons) |
| B6 | P2 | No token usage tracking — cost monitoring blind spot | ✅ Fixed (token logging) |
| B7 | P2 | R2 failure logs lacked storage_key and user_id | ✅ Fixed (structured logging) |

---

## 4. Remaining Risks

| Risk | Mitigation | Owner |
|------|-----------|-------|
| AI provider 503/429 during high load | Multi-provider fallback + 3x retry | Backend |
| R2 permission/CORS misconfiguration | Local fallback + structured error logs | DevOps |
| n8n workflow timeout on large documents | Configurable timeout + stuck job recovery | Backend |
| Score variance between AI runs | temperature=0 + drift detection logging | Backend |
| Frontend stuck on processing page | Auto-detect failure via TTL + retry UX | Frontend |

---

## 5. How to Deploy

```bash
# 1. Apply DB migration
docker exec resume-analyzer-backend alembic upgrade head

# 2. Restart backend (picks up stuck job recovery)
docker-compose restart backend

# 3. Verify health
curl http://localhost:8000/health
```
