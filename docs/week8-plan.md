# Week 8 Plan - AI First CV Processing

## 1. Dinh huong cua Week 8

Week 8 se bo qua viec mo rong them Auth de tap trung toan bo vao flow AI phan tich CV.

Muc tieu cua tuan nay khong phai la lam he thong hoan hao, ma la lam cho pipeline phan tich CV chay duoc tu dau den cuoi:

- Upload CV
- Trich xuat text
- Xu ly phan tich
- Co status de frontend theo doi
- Tra result that
- Luu ket qua vao database
- Hien thi result tren frontend

Noi ngan gon:

- Khong uu tien OAuth
- Khong uu tien auth nang cao
- Uu tien AI pipeline va ket qua phan tich

## 2. Muc tieu chinh cua Week 8

Can dat duoc cac muc tieu sau:

- Hoan thien `GET /api/v1/cv/{id}/status`
- Hoan thien `GET /api/v1/cv/{id}/result`
- Them buoc trich xuat text tu CV PDF/DOCX
- Tao pipeline phan tich CV theo huong AI-first
- Goi AI provider o muc MVP hoac mock AI backend neu can
- Luu ket qua phan tich vao database
- Frontend hien thi result that thay cho mock data
- Processing page dua vao status that thay vi chi gia lap timer

## 3. Pham vi se lam trong Week 8

### Trong scope

- CV upload
- CV text extraction
- Status API
- Result API
- AI processing hoac mock AI processing
- Save result vao DB
- Frontend processing page
- Frontend result page
- Neu kip thi lam history that

### Ngoai scope

- Google OAuth
- GitHub OAuth
- Auth nang cao
- Email verification
- Forgot password
- Permission nang cao
- OCR nang cao cho scanned PDF phuc tap

## 4. Chia viec theo tung nhom

## 4.1 Backend

### B1. Hoan thien upload flow lam dau vao cho AI

Cong viec:

- Kiem tra lai `POST /api/v1/cv/upload`
- Dam bao upload file PDF/DOCX on dinh
- Luu metadata day du vao bang `cv_uploads`
- Gan `status` ban dau la `pending`

Ket qua mong doi:

- Moi CV upload deu co 1 `cvId` de tiep tuc xu ly

File du kien dong vao:

- `backend/app/api/routes/cv.py`
- `backend/app/schemas/cv.py`
- `backend/app/models/cv_upload.py`
- `backend/app/services/storage.py`

### B2. Trich xuat text tu PDF/DOCX

Cong viec:

- Them service trich xuat text tu file CV
- Ho tro muc co ban:
  - PDF text-based
  - DOCX
- Neu text extraction that bai thi tra trang thai loi ro rang

Ket qua mong doi:

- He thong co dau vao text de dua sang AI

File du kien dong vao:

- `backend/app/services/resume_parser.py`
- `backend/app/api/routes/cv.py`

### B3. Hoan thien status API

Cong viec:

- Xay dung `GET /api/v1/cv/{id}/status`
- Tra ve cac trang thai:
  - `pending`
  - `processing`
  - `completed`
  - `failed`
- Neu can thi tra them thong tin progress

Ket qua mong doi:

- Frontend processing page co the polling status that

File du kien dong vao:

- `backend/app/api/routes/cv.py`
- `backend/app/schemas/cv.py`

### B4. Tao result processing flow

Cong viec:

- Viet service xu ly phan tich CV
- Dau vao:
  - `resume_text`
  - `job_description_text` neu co
- Dau ra:
  - overall score
  - score breakdown
  - strengths
  - weaknesses
  - suggestions

Ket qua mong doi:

- Co result co cau truc ro rang cho frontend

File du kien dong vao:

- `backend/app/services/resume_analyzer.py`
- `backend/app/api/routes/cv.py`

### B5. Goi AI provider o muc MVP

Cong viec:

- Chuan hoa prompt tra ve JSON
- Goi AI provider o muc co ban
- Parse response thanh object noi bo
- Neu AI chua san sang, fallback sang mock result

Ket qua mong doi:

- He thong co kha nang sinh ket qua phan tich

Ghi chu:

- Week 8 khong can toi uu prompt qua som
- Muc tieu la chay duoc pipeline

### B6. Luu result vao database

Cong viec:

- Luu vao:
  - `analysis_results`
  - `category_scores`
  - `suggestions`
- Gan dung `cv_upload_id`
- Cap nhat status cua CV thanh `completed` hoac `failed`

Ket qua mong doi:

- Result duoc luu ben vung de frontend co the doc lai

File du kien dong vao:

- `backend/app/models/analysis_result.py`
- `backend/app/models/category_score.py`
- `backend/app/models/suggestion.py`
- `backend/app/api/routes/cv.py`

### B7. Hoan thien result API

Cong viec:

- Xay dung `GET /api/v1/cv/{id}/result`
- Tra schema result dung voi giao dien
- Lay du lieu tu DB thay vi chi mock

Ket qua mong doi:

- Frontend result page co du lieu that de render

File du kien dong vao:

- `backend/app/api/routes/cv.py`
- `backend/app/schemas/cv.py`

## 4.2 Frontend

### F1. Upload page giu cvId sau khi upload

Cong viec:

- Sau khi upload thanh cong, lay `cvId` tu response
- Truyen `cvId` sang processing page
- Dam bao flow tiep theo dung dung CV vua upload

Ket qua mong doi:

- Frontend khong bi mat context giua upload va processing

File du kien dong vao:

- `frontend/src/pages/UploadPage.jsx`

### F2. Processing page dua vao status that

Cong viec:

- Goi `GET /api/v1/cv/{id}/status`
- Poll theo chu ky ngan
- Cap nhat progress state tren giao dien
- Neu `completed` thi chuyen sang result
- Neu `failed` thi hien loi

Ket qua mong doi:

- Processing page khong con phu thuoc hoan toan vao timer

File du kien dong vao:

- `frontend/src/pages/ProcessingPage.jsx`
- `frontend/src/components/ProgressStep/ProgressStep.jsx`

### F3. Result page doc result that

Cong viec:

- Goi `GET /api/v1/cv/{id}/result`
- Mapping response vao UI hien co
- Hien:
  - overall score
  - breakdown
  - strengths
  - areas for improvement
  - suggestions

Ket qua mong doi:

- Result page doc du lieu that tu backend thay vi dung mock data co dinh

File du kien dong vao:

- `frontend/src/pages/ResultPage.jsx`

### F4. Neu kip thi lam history that

Cong viec:

- Goi `GET /api/v1/cv`
- Hien danh sach CV da duoc phan tich
- Cho click vao 1 item de mo report

Ket qua mong doi:

- Co lich su phan tich that tu DB

File du kien dong vao:

- `frontend/src/pages/HistoryPage.jsx`
- `frontend/src/components/HistoryRow/HistoryRow.jsx`

## 4.3 Async Pipeline

### A1. Lua chon huong xu ly

Trong Week 8 co 2 huong:

#### Huong 1 - Async don gian trong backend

- Upload xong
- Backend chay xu ly bang background task hoac gia lap processing
- Cap nhat status
- Frontend polling

Huong nay phu hop neu:

- Muon chot flow nhanh
- Chua muon phu thuoc n8n ngay

#### Huong 2 - Noi n8n vao backend

- Backend upload xong
- Backend trigger n8n workflow
- n8n thuc hien extraction va AI processing
- n8n cap nhat DB

Huong nay phu hop neu:

- Ban da san sang ve n8n
- Co the debug duoc workflow trong tuan nay

Khuyen nghi:

- Uu tien huong 1 truoc
- Neu con thoi gian thi moi noi n8n

## 5. Thu tu uu tien can lam

Lam dung thu tu sau de tranh vo scope:

1. Upload flow on dinh
2. Text extraction
3. Status API
4. Mock result processing backend
5. Result API
6. Frontend processing -> result
7. Luu result vao DB
8. Neu kip thi goi AI provider that
9. Neu con thoi gian nua moi xem den n8n

## 6. Lich goi y theo ngay

### Ngay 1

- Kiem tra lai upload flow
- Them text extraction cho PDF/DOCX
- Chot schema result

### Ngay 2

- Hoan thien status API
- Viet mock result processing backend
- Test `status` va `result` tren Swagger/Postman

### Ngay 3

- Noi ProcessingPage voi status API
- Noi ResultPage voi result API
- Chay full flow frontend -> backend

### Ngay 4

- Luu result vao DB
- Neu kip thi noi History page voi du lieu that
- Fix loi flow end-to-end

### Ngay 5

- Goi AI provider that neu kip
- Hoac noi n8n neu da san sang
- Chuan bi demo

## 7. Deliverable cuoi tuan

Can dat toi thieu cac deliverable sau:

- Upload CV thanh cong
- Co trich xuat text CV co ban
- Co `status API`
- Co `result API`
- Co result co cau truc
- Result duoc luu vao DB
- Frontend processing page doi theo status
- Frontend result page hien thi du lieu that

Deliverable nang cao neu kip:

- Goi AI provider that
- Noi history page voi DB
- Noi n8n vao flow async

## 8. Rui ro can luu y

- Trich xuat text PDF co the khong on dinh voi moi loai file
- AI provider co the tra JSON sai format
- Neu chua co fallback thi frontend se ket o processing
- Neu nhay vao n8n qua som thi flow co the phuc tap hon muc can thiet cua Week 8
- Neu schema result chua chot som, frontend va backend se lech nhau

## 9. Tieu chi danh gia hoan thanh Week 8

Week 8 duoc xem la dat neu:

- He thong co flow phan tich CV tu upload den result
- Processing page dua vao status that
- Result page lay du lieu that tu backend
- Result duoc luu trong DB
- Co the demo:
  - upload CV
  - processing
  - result

Neu dat them cac muc sau thi la rat tot:

- Da goi AI provider that
- Da co lich su phan tich that
- Da co async pipeline ro rang

## 10. File du kien se dong vao trong Week 8

### Backend

- `backend/app/api/routes/cv.py`
- `backend/app/schemas/cv.py`
- `backend/app/services/storage.py`
- `backend/app/services/resume_parser.py`
- `backend/app/services/resume_analyzer.py`
- `backend/app/models/cv_upload.py`
- `backend/app/models/analysis_result.py`
- `backend/app/models/category_score.py`
- `backend/app/models/suggestion.py`

### Frontend

- `frontend/src/pages/UploadPage.jsx`
- `frontend/src/pages/ProcessingPage.jsx`
- `frontend/src/pages/ResultPage.jsx`
- `frontend/src/pages/HistoryPage.jsx`
- `frontend/src/components/ProgressStep/ProgressStep.jsx`
- `frontend/src/components/HistoryRow/HistoryRow.jsx`

## 11. Ghi chu cuoi

Week 8 nen duoc xem la tuan "AI pipeline dau tien".

Khong can co AI qua thong minh.
Can co:

- flow ro rang
- output ro rang
- luu DB ro rang
- frontend hien thi ro rang

Day la tuan de bien du an tu mot web app co upload thanh mot he thong co xu ly noi dung CV that su.
