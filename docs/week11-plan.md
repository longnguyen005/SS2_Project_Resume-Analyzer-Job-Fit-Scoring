# Week 11 Plan - Stability and Advanced Logic Integration (Updated)

## 1. Cap nhat hien tai

Sau Week 10, gia su R2 va webhook skeleton da xong, Week 11 se chot processing pipeline that.

Trang thai implementation hien tai:

- Workflow live: `claim -> extract -> validate -> analyze -> complete/fail`
- `file-worker` phu trach `extract/validate`
- `ai-worker` phu trach `analyze`
- `persistence-worker` phu trach `complete/save DB`
- backend giu `upload`, public read APIs, `claim`, `fail`

Luu y quan trong:

- OCR fallback da co trong backend parser
- Muc tieu Week 11 la dua OCR/extraction vao n8n pipeline chinh

## 2. Muc tieu chinh Week 11

- Hoan thien n8n full pipeline: extract -> analyze -> save DB
- Chuyen processing chinh sang n8n
- Dong bo status update va failure_reason tu n8n ve DB
- Tang stability AI call (retry/timeout/parse guard)

## 3. Scope Week 11

### Trong scope / trang thai hien tai

- n8n orchestration theo stage
- extraction/validation branch qua `file-worker`
- AI branch parse va validate response qua `ai-worker`
- DB write branch qua `persistence-worker`
- backend trigger upload flow va expose `claim/fail` + public query APIs

### Ngoai scope

- Toi uu hieu nang sau cung (de Week 13)
- Feature moi ngoai commitment

## 4. Task chi tiet theo nhom

### 4.1 n8n

- Workflow branch 1: claim
- Workflow branch 2: extract text (PDF/DOCX)
- Workflow branch 3: validate resume text
- Workflow branch 4: AI analysis + JSON validation
- Workflow branch 5: save DB + update status
- Failure branch: update `failed` + `failure_reason`

File:

- `n8n/workflows/cv-analysis-http-pipeline-staged.json`

### 4.2 Backend

- Upload route trigger n8n
- Khong con local-processing fallback trong backend
- Internal route chi con `claim/fail`
- Chot ownership/security check cho status/result/history

File:

- `backend/app/api/routes/cv.py`
- `backend/app/services/workflow_trigger.py`

### 4.3 Frontend

- Processing UI theo status that tu pipeline n8n
- Message ro cho timeout/OCR/AI failure
- Retry path ro rang

File:

- `frontend/src/pages/ProcessingPage.jsx`
- `frontend/src/pages/ResultPageConnected.jsx`

### 4.4 QA

- Bo test nang cao:
- scanned PDF
- corrupted/password PDF
- long CV
- AI timeout/rate limit
- n8n restart giua workflow

## 5. Deliverable cuoi Week 11

- Demo full pipeline di qua n8n
- OCR branch chay duoc trong workflow
- Stability report V1 (success rate + top failure causes)

## 6. Definition of Done

- Processing chinh khong con phu thuoc backend local pipeline
- Status/result cap nhat nhat quan tu n8n
- Khong con bug blocker trong flow core
- Co so lieu de vao code freeze Week 12
