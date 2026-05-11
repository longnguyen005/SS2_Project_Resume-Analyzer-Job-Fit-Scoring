# Week 8 Task Breakdown - Theo Tung File

## 1. Muc tieu cua tai lieu nay

Tai lieu nay chia Week 8 thanh cac task rat cu the theo tung file de co the bat dau code ngay, khong bi mo ho.

Muc tieu cua Week 8:

- Upload CV xong co `cvId`
- Co text extraction tu PDF/DOCX
- Co `status API`
- Co `result API`
- Co du lieu ket qua duoc luu vao database
- Frontend processing page polling status that
- Frontend result page hien thi result that

## 2. Thu tu lam viec trong ngay

Lam theo dung thu tu nay:

1. Backend schemas va models
2. Backend parser service
3. Backend analyzer service
4. Backend route `cv.py`
5. Frontend `UploadPage`
6. Frontend `ProcessingPage`
7. Frontend `ResultPage`
8. Test end-to-end

## 3. Backend tasks theo tung file

## 3.1 `backend/app/schemas/cv.py`

### Viec can lam

- Kiem tra lai schema cho upload response
- Them schema cho:
  - `CvStatusResponse`
  - `CvResultResponse`
  - `CategoryScoreResponse`
  - `SuggestionResponse`

### Can co toi thieu

- `id`
- `status`
- `overall_score`
- `categories`
- `strengths`
- `areas_for_improvement`
- `suggestions`
- `processing_time_seconds` neu muon

### Done khi

- Backend co response model ro rang cho `status` va `result`

---

## 3.2 `backend/app/models/cv_upload.py`

### Viec can lam

- Kiem tra lai cac field:
  - `status`
  - `filename`
  - `stored_filename`
  - `storage_path`
  - `file_type`
  - `file_size_bytes`
  - `job_description_id`
- Neu chua co thi them field phu hop cho Week 8

### Done khi

- Bang `cv_uploads` du thong tin de theo doi 1 CV trong pipeline

---

## 3.3 `backend/app/models/analysis_result.py`

### Viec can lam

- Kiem tra field lien ket voi `cv_upload_id`
- Kiem tra field tong quat nhu:
  - `overall_score`
  - `summary`
  - `strengths`
  - `areas_for_improvement`
  - `raw_ai_response` neu can

### Done khi

- Bang `analysis_results` luu duoc phan ket qua tong quan

---

## 3.4 `backend/app/models/category_score.py`

### Viec can lam

- Kiem tra model category score
- Dam bao co the luu:
  - ten category
  - diem so
  - nhan xet ngan neu can

### Done khi

- Co the luu breakdown score cho result page

---

## 3.5 `backend/app/models/suggestion.py`

### Viec can lam

- Kiem tra model suggestion
- Dam bao co the luu:
  - title
  - description
  - priority
  - tone neu can

### Done khi

- Co the luu recommendations cho result page

---

## 3.6 `backend/app/services/resume_parser.py`

### Viec can lam

- Tao file moi neu chua co
- Viet ham parse PDF
- Viet ham parse DOCX
- Tao 1 ham chung, vi du:
  - `extract_text_from_resume(file_path, file_type)`

### Logic nen lam

- Neu file type = `pdf` -> parse PDF
- Neu file type = `docx` -> parse DOCX
- Neu khong doc duoc -> raise error ro rang

### Muc tieu MVP

- Ho tro PDF text-based
- Ho tro DOCX
- Chua can OCR nang cao ngay

### Done khi

- Co the dua file vao va lay ra text

---

## 3.7 `backend/app/services/resume_analyzer.py`

### Viec can lam

- Tao file moi neu chua co
- Viet 2 ham ro rang:
  - 1 ham mock result
  - 1 ham analyze bang AI that neu kip

### Ham toi thieu nen co

- `build_mock_result(resume_text, job_description_text=None)`
- `analyze_resume_with_ai(resume_text, job_description_text=None)`

### MVP

Neu AI that chua xong, van phai co mock result backend theo schema that

### Done khi

- Backend luon co the sinh ra result dung format

---

## 3.8 `backend/app/api/routes/cv.py`

### Viec can lam

Day la file quan trong nhat cua Week 8.

Can xu ly cac route:

#### `POST /api/v1/cv/upload`

- upload file
- luu file
- tao record `cv_uploads`
- status = `pending`
- tra `cvId`

#### `GET /api/v1/cv/{id}/status`

- tim CV theo id
- check owner
- tra status hien tai

#### `GET /api/v1/cv/{id}/result`

- tim result theo `cv_upload_id`
- check owner
- tra result theo schema

#### Neu can: `GET /api/v1/cv`

- tra lich su CV
- de frontend history page dung

### Logic xu ly tam thoi de chay duoc

Sau upload:

- parse text
- tao mock result hoac AI result
- luu vao DB
- cap nhat status thanh `completed`

Neu loi:

- cap nhat status thanh `failed`

### Done khi

- 3 API `upload`, `status`, `result` chay duoc bang Swagger/Postman

---

## 3.9 `backend/app/services/storage.py`

### Viec can lam

- Kiem tra lai validate file type
- Kiem tra lai validate file size
- Dam bao file duoc luu voi duong dan ro rang

### Done khi

- Upload flow on dinh va phan parser nhan duoc file path dung

## 4. Frontend tasks theo tung file

## 4.1 `frontend/src/pages/UploadPage.jsx`

### Viec can lam

- Sau upload thanh cong, lay `cvId` tu response
- Dung `navigate` sang processing page
- Truyen `cvId` qua:
  - route state
  - hoac query param

### Cach lam goi y

- Dung `navigate(\"/processing\", { state: { cvId } })`

### Done khi

- Upload xong frontend khong bi mat thong tin CV vua tao

---

## 4.2 `frontend/src/pages/ProcessingPage.jsx`

### Viec can lam

- Lay `cvId` tu state hoac query
- Goi `GET /api/v1/cv/{id}/status`
- Poll theo interval
- Neu status = `completed` -> `navigate(\"/result\", { state: { cvId } })`
- Neu status = `failed` -> hien message loi

### Giu lai gi?

- Van co the giu UI progress 1 2 3 hien tai
- Nhung trang thai chuyen dua tren backend status that

### Done khi

- Processing page doc duoc status that va dieu huong dung

---

## 4.3 `frontend/src/pages/ResultPage.jsx`

### Viec can lam

- Lay `cvId`
- Goi `GET /api/v1/cv/{id}/result`
- Mapping response vao:
  - overall score
  - breakdown cards
  - strengths
  - improvement
  - suggestions

### Cach lam goi y

- Tao state:
  - `loading`
  - `error`
  - `resultData`

### Done khi

- Result page hien data that tu backend

---

## 4.4 `frontend/src/pages/HistoryPage.jsx`

### Viec can lam

- Neu con thoi gian, noi `GET /api/v1/cv`
- Lay danh sach CV uploads va ket qua tom tat
- Hien trong bang history

### Done khi

- History page giam phu thuoc vao mock data

---

## 4.5 `frontend/src/components/ProgressStep/ProgressStep.jsx`

### Viec can lam

- Kiem tra state hien thi:
  - `pending`
  - `active`
  - `completed`
  - `failed` neu can

### Done khi

- UI processing ro rang hon khi backend status thay doi

---

## 4.6 `frontend/src/lib/mockData.js`

### Viec can lam

- Giam dan phan phu thuoc vao mock result
- Chi giu mock data lam fallback neu API that loi

### Done khi

- Frontend uu tien data that, mock data chi la fallback

## 5. Ke hoach code trong ngay hom nay

Neu bat dau ngay hom nay, lam theo dung sequence sau:

### Buoc 1

Hoan thien backend schema va route:

- `backend/app/schemas/cv.py`
- `backend/app/api/routes/cv.py`

### Buoc 2

Them parser service:

- `backend/app/services/resume_parser.py`

### Buoc 3

Them analyzer service:

- `backend/app/services/resume_analyzer.py`

### Buoc 4

Test backend bang Swagger:

- upload
- status
- result

### Buoc 5

Noi frontend:

- `frontend/src/pages/UploadPage.jsx`
- `frontend/src/pages/ProcessingPage.jsx`
- `frontend/src/pages/ResultPage.jsx`

## 6. Tieu chi hoan thanh trong ngay

Hom nay duoc xem la dat neu:

- Upload xong backend tra duoc `cvId`
- Co `GET /api/v1/cv/{id}/status`
- Co `GET /api/v1/cv/{id}/result`
- Frontend processing page nhan duoc `cvId`
- Frontend result page co the doc result tu backend

## 7. Tieu chi hoan thanh Week 8

Week 8 duoc xem la dat neu:

- Co flow that:
  - upload
  - processing
  - result
- Co parser text co ban
- Co result luu DB
- Frontend khong con phu thuoc chinh vao mock data o result

## 8. Ghi chu cuoi

Khi code Week 8, hay luon uu tien:

1. Flow chay duoc
2. API on dinh
3. Frontend hien dung data

Khong can toi uu AI qua som. Chi can dam bao pipeline co the chay va demo duoc.
