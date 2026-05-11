# Week 9 Plan - Completion of Basic Business Processes (Updated)

## 1. Cap nhat hien tai

Tinh den hien tai, Week 9 da dat phan lon muc tieu:

- Da co flow core: `login -> jd -> upload -> processing -> result -> history`
- Da bo user-facing mock result
- Da co `failure_reason` de frontend hien loi ro rang
- Da co loading state va processing state thuc te

Phan con lai can chot de dong Week 9:

- Chuan hoa smoke test evidence
- Chot demo walk-through script
- Chot danh sach bug con lai truoc khi vao Week 10

## 2. Muc tieu chinh Week 9

- Chot business flow khong bi dut doan
- Chot error handling voi message de hieu
- Chot ket qua test thu cong cho bo case core
- Chot handover list cho Week 10

## 3. Task con lai can lam

### 3.1 Backend

- Ra soat lai `GET /cv/{id}/status` va `GET /cv/{id}/result`
- Kiem tra tat ca case failed tra `failure_reason` nhat quan
- Kiem tra route history khong hien record mock cu nhu completed

File:

- `backend/app/api/routes/cv.py`
- `backend/app/schemas/cv.py`

### 3.2 Frontend

- Chot processing copywriting cho cac state `pending/processing/completed/failed`
- Chot result/history behavior khi backend tra `409`
- Kiem tra upload page message va retry path

File:

- `frontend/src/pages/ProcessingPage.jsx`
- `frontend/src/pages/ResultPageConnected.jsx`
- `frontend/src/pages/UploadPage.jsx`

### 3.3 QA

- Chay smoke set toi thieu 8 case:
- PDF text-based
- DOCX
- file khong phai CV
- PDF scan (OCR)
- AI provider unavailable
- upload file loi
- re-upload sau failed
- view history sau nhieu lan upload

## 4. Deliverable cuoi Week 9

- Demo full walk-through tren app that
- Smoke test checklist da danh dau va co ket qua
- Bug list con lai da phan muc P0/P1/P2
- Handover list cho Week 10 (R2 + n8n)

## 5. Definition of Done

- Khong con blocker trong core flow
- User khong con thay mock report
- Case loi chinh deu hien message ro rang
- Team co du artifact de bao cao Week 9
