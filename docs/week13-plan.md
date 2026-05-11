# Week 13 Plan - Hardening and Performance Tuning (Updated)

## 1. Cap nhat hien tai

Neu Week 12 da freeze xong release candidate, Week 13 se dong vai tro hardening tuan cuoi:

- Lam cho pipeline R2 + n8n + AI on dinh trong tai lieu that
- Giam do lech ket qua giua cac lan cham cung 1 CV
- Chot observability de team debug nhanh truoc final

## 2. Muc tieu chinh Week 13

- Tang success rate end-to-end trong batch test
- Giam processing latency trung binh upload -> result
- Chot scoring consistency (han che dao dong khong can thiet)
- Dong bug P1/P2 con lai lien quan reliability

## 3. Scope Week 13

### Trong scope

- Pipeline hardening (retry, timeout, idempotency)
- AI request tuning (temperature, schema guard, parse guard)
- Performance tuning cho hot path API va workflow
- Logging/metrics de truy vet failure theo `cv_id`

### Ngoai scope

- Feature nghiep vu moi ngoai commitment
- Thay doi lon ve giao dien khong phuc vu tinh on dinh

## 4. Task chi tiet theo nhom

## 4.1 Backend

### B1. Scoring consistency

- Co dinh tham so model de giam variance (uu tien `temperature=0`)
- Version hoa prompt va parser schema (`prompt_version`)
- Neu can, them post-processing normalization de score khong nhay bat thuong

File:

- `backend/app/services/resume_analyzer.py`
- `backend/app/schemas/cv.py`

### B2. API and DB hot path tuning

- Toi uu query cho history/status/result
- Them index cho truy van co tan suat cao (neu benchmark chi ra)
- Bao dam route tra loi nhanh khi processing dang chay

File:

- `backend/app/api/routes/cv.py`
- `backend/app/models/*.py`
- `backend/alembic/versions/*.py`

## 4.2 n8n / Workflow

### N1. Reliability and recovery

- Retry co gioi han cho provider timeout/503
- Idempotency theo `cv_id` de tranh cham lai trung
- Failure branch ghi ro `failure_reason` va stop cleanly

File:

- `n8n/workflows/cv-analysis-pipeline.json`

## 4.3 Frontend

### F1. Stability UX

- Chot state rendering nhat quan cho pending/processing/failed
- Hien thong bao de hieu khi provider unavailable
- Bao dam nguoi dung co duong retry ro rang

File:

- `frontend/src/pages/ProcessingPage.jsx`
- `frontend/src/pages/ResultPageConnected.jsx`

## 4.4 QA

### Q1. Hardening test set

- Cham lap lai cung 1 CV nhieu lan de do do lech
- Test provider timeout, 503, rate limit
- Test n8n restart giua luong xu ly

### Q2. Benchmark

- Latency P50/P90 upload -> result
- Success rate theo 50-100 job test noi bo

## 5. Deliverable cuoi Week 13

- Hardening report (success rate + top failure causes)
- Benchmark report truoc/sau optimize
- Danh sach bug P1/P2 da dong hoac co owner + deadline

## 6. Definition of Done

- Success rate dat muc muc tieu noi bo (de xuat >= 90% batch test)
- Scoring variance giam ro rang so voi truoc hardening
- Frontend hien loi nhat quan va khong con blocker reliability
- Team san sang vao Week 14 de dong tai lieu
