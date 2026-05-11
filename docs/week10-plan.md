# Week 10 Plan - General Testing and Architecture Kick-off (Updated)

## 1. Cap nhat hien tai

Week 10 se la tuan chuyen tu local-first sang cloud/workflow-first.

Da co san:

- Flow core on dinh tu Week 9
- AI live + failure handling
- OCR fallback trong backend parser

Chua co:

- Cloudflare R2 storage that
- n8n webhook/pipeline that

## 2. Muc tieu chinh Week 10

- Trien khai Cloudflare R2 cho upload file
- Chuyen metadata `cv_upload` sang huong cloud storage
- Tao webhook trigger tu backend sang n8n (skeleton)
- Bao dam khong regression flow user hien tai

## 3. Scope va uu tien

### Uu tien 1: R2

- Tao service upload/download object
- Them env va secret config cho R2
- Chuyen upload route sang luu object tren R2

### Uu tien 2: schema migration

- Them field `storage_key`, `storage_url` (neu chua co)
- Chot migration script va rollback path

### Uu tien 3: n8n skeleton

- Tao workflow webhook nhan payload tu backend
- Validate payload va tra ack
- Chua thay processing chinh sang n8n trong tuan nay

## 4. Task chi tiet theo nhom

### 4.1 Backend

- Tao `storage_service.py` cho R2
- Cap nhat `config.py` voi bien R2
- Refactor `POST /cv/upload` de dung R2
- Tao `workflow_trigger.py` de call n8n webhook

File:

- `backend/app/services/storage_service.py`
- `backend/app/services/workflow_trigger.py`
- `backend/app/api/routes/cv.py`
- `backend/app/core/config.py`
- `backend/alembic/versions/*.py`

### 4.2 n8n

- Tao workflow skeleton `cv-analysis-skeleton.json`
- Node webhook + validation + logging

File:

- `n8n/workflows/cv-analysis-skeleton.json`

### 4.3 Frontend

- Regression check upload/processing/result/history
- Bo sung message neu processing tre bat thuong

## 5. Deliverable cuoi Week 10

- Upload file len R2 thanh cong
- DB metadata cloud storage da cap nhat
- Webhook backend -> n8n skeleton chay duoc
- Regression report (khong co blocker moi)

## 6. Definition of Done

- 100% upload moi di qua R2
- Core flow van chay tren frontend
- n8n webhook skeleton nhan payload that
- Co danh sach issue can vao Week 11
