# Benchmark Report — Resume Analyzer v1

> **Date**: 2026-05-11  
> **Version**: v1.0  
> **Status**: Template — fill in actual measurements after running tests

---

## 1. Test Environment

| Component | Version |
|-----------|---------|
| Backend | FastAPI 0.1.0 |
| Database | PostgreSQL 16 (Docker) |
| n8n | 1.84.1 (Docker) |
| AI Provider | Gemini (primary) |
| Storage | Cloudflare R2 |
| OS | Docker Compose (local dev) |

---

## 2. Latency — Upload to Result

Measure the complete pipeline duration: user clicks "Upload" until result is available.

### How to Measure
```bash
# 1. Note the timestamp before uploading
# 2. Upload a CV via UI or API
# 3. Poll /cv/{id}/status until status = "completed"
# 4. Record the difference
```

### Results

| Test | File | Size | Pipeline Duration | Notes |
|------|------|------|------------------|-------|
| T1 | _sample.pdf_ | _KB_ | _seconds_ | |
| T2 | _sample.pdf_ | _KB_ | _seconds_ | |
| T3 | _sample.docx_ | _KB_ | _seconds_ | |
| T4 | _scanned.pdf_ | _KB_ | _seconds_ | OCR path |
| T5 | _large.pdf_ | _KB_ | _seconds_ | Multi-page |

| Metric | Value |
|--------|-------|
| P50 (median) | _s_ |
| P90 | _s_ |
| Max | _s_ |

### Latency Breakdown (approximate per stage)

| Stage | Duration | Notes |
|-------|----------|-------|
| Upload + R2 save | _ms_ | Includes file validation |
| n8n webhook trigger | _ms_ | |
| Text extraction | _ms_ | |
| AI analysis | _ms_ | Typically the bottleneck |
| DB persistence | _ms_ | |

---

## 3. Scoring Consistency

Run the **same CV** through the pipeline multiple times and record the overall score.

### How to Measure
```bash
# Upload the same PDF file 5+ times
# Record the overall_score from /cv/{id}/result for each run
```

### Results

| Run | Overall Score | Skills | Experience | Education | Format |
|-----|--------------|--------|-----------|-----------|--------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

| Metric | Value |
|--------|-------|
| Mean | |
| Std Dev | |
| Max Drift | |
| Variance acceptable? (std dev ≤ 3) | ☐ Yes / ☐ No |

### Configuration
- `temperature`: 0
- `prompt_version`: v2.1-hardened
- `response_format`: json_object
- `overall_score`: Server-side recalculated from weighted breakdown

---

## 4. Pipeline Success Rate

Run a batch of N uploads and record success/failure outcomes.

### How to Measure
```bash
# Upload N different CVs (target: 20-50)
# Record final status for each
```

### Results

| Metric | Count | Rate |
|--------|-------|------|
| Total uploads | | 100% |
| Completed | | _% |
| Failed (extract) | | _% |
| Failed (analyze) | | _% |
| Failed (orchestration) | | _% |
| Stuck (auto-recovered) | | _% |

| Target | Actual | Status |
|--------|--------|--------|
| Success rate ≥ 90% | _% | ☐ Pass / ☐ Fail |

### Top Failure Causes

| Rank | Cause | Count | Notes |
|------|-------|-------|-------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

---

## 5. API Response Times

Measure response times for key API endpoints under normal load.

| Endpoint | Method | Avg | P90 | Notes |
|----------|--------|-----|-----|-------|
| `/auth/login` | POST | _ms_ | _ms_ | |
| `/cv/upload` | POST | _ms_ | _ms_ | Until HTTP 201 returned |
| `/cv/{id}/status` | GET | _ms_ | _ms_ | Polling endpoint |
| `/cv/{id}/result` | GET | _ms_ | _ms_ | With eager loading |
| `/cv` (history) | GET | _ms_ | _ms_ | After index migration |
| `/jd` | GET | _ms_ | _ms_ | |

---

## 6. Database Query Performance

After applying migration `0005_performance_indexes`:

| Query | Before Index | After Index | Improvement |
|-------|-------------|-------------|-------------|
| CV history (user_id + created_at) | _ms_ | _ms_ | _% |
| Stuck job recovery (status + updated_at) | _ms_ | _ms_ | _% |
| Analysis result by cv_upload_id | _ms_ | _ms_ | _% |
| JD listing by user_id | _ms_ | _ms_ | _% |

---

## 7. Conclusions

- [ ] Latency P90 is within acceptable range (target: < 30s)
- [ ] Scoring variance is acceptable (target: std dev ≤ 3)
- [ ] Pipeline success rate meets target (≥ 90%)
- [ ] API response times are acceptable for user experience
- [ ] DB indexes improve query performance measurably

### Recommendations

_Fill in after running benchmarks_
