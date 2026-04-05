# Week 7 Plan - Frontend and Backend Integration

## 1. Muc tieu cua Week 7

Week 7 tap trung vao viec chuyen he thong tu trang thai static-first cua Week 6 sang trang thai co the chay duoc flow nghiep vu that o muc co ban.

Muc tieu chinh:

- Noi frontend voi backend that cho cac nghiep vu cot loi
- Hoan thien auth flow de frontend co the dang nhap va su dung API protected
- Hoan thien job description flow de tao va xem danh sach JD
- Hoan thien upload CV flow de frontend co the gui file len backend
- Tao duoc luong demo co ban: `login -> tao JD -> upload CV -> processing -> result`

Week 7 chua bat buoc lam AI scoring that 100 percent. Neu can, co the dung mock result o dau ra de frontend co du lieu hien thi.

## 2. Pham vi can dat trong tuan nay

### Frontend

- Noi `LoginPage` voi API `POST /api/v1/auth/login`
- Noi `RegisterPage` voi API `POST /api/v1/auth/register`
- Luu `access_token` vao localStorage
- Tu dong gui token khi goi API protected
- Noi `JobDescriptionsPage` voi API:
  - `POST /api/v1/jd`
  - `GET /api/v1/jd`
- Noi `UploadPage` voi API `POST /api/v1/cv/upload`
- Dieu huong sau upload thanh cong sang `ProcessingPage`
- Tu `ProcessingPage` chuyen sang `ResultPage`
- Hien thi loading, success, error state ro rang

### Backend

- Kiem tra lai auth flow cho frontend su dung on dinh
- Chuan hoa response schema cho auth, JD, upload CV
- Dam bao API protected nhan JWT token dung
- Hoan thien `POST /api/v1/cv/upload`
- Dam bao luu metadata vao bang `cv_uploads`
- Bo sung hoac hoan thien:
  - `GET /api/v1/cv`
  - `GET /api/v1/cv/{id}/status`
  - `GET /api/v1/cv/{id}/result` (co the la mock response trong Week 7)
- Test lai toan bo flow bang Swagger/Postman

## 3. Cong viec can lam ben Frontend

### 3.1 Auth Integration

- Hoan thien submit form login
- Luu token sau khi login thanh cong
- Hien thi thong bao neu login that bai
- Kiem tra token truoc khi vao cac trang can auth

Ket qua mong doi:

- User co the dang nhap tu frontend
- Token duoc luu va dung lai cho request tiep theo

### 3.2 Job Description Integration

- Tai danh sach JD tu backend khi vao trang
- Tao JD moi bang form
- Sau khi tao thanh cong, refresh lai danh sach
- Hien thi message thanh cong hoac loi

Ket qua mong doi:

- Frontend khong con dung mock JD
- Du lieu hien thi la du lieu that tu database

### 3.3 Upload CV Integration

- Chon file PDF/DOCX tren giao dien
- Goi API upload bang `FormData`
- Gui kem `job_description_id` neu co
- Hien thi ten file da chon
- Hien thi trang thai upload
- Neu upload thanh cong thi chuyen sang trang processing

Ket qua mong doi:

- User upload duoc file tu frontend
- Backend luu duoc metadata va file

### 3.4 Processing and Result Flow

- Giu processing page o dang gia lap nhu hien tai
- Sau khi processing xong, chuyen sang result
- Result page co the dung mock data neu backend chua tra AI result that

Ket qua mong doi:

- Co 1 flow demo tron ven de bao cao

## 4. Cong viec can lam ben Backend

### 4.1 Auth Hoan Chinh

- Xac nhan login tra token dung format
- Xac nhan API protected doc duoc token tu header `Authorization`
- Kiem tra loi `401 Unauthorized`

Ket qua mong doi:

- Frontend dang nhap xong goi duoc cac API can auth

### 4.2 Job Description API

- Kiem tra `POST /api/v1/jd`
- Kiem tra `GET /api/v1/jd`
- Dam bao chi tra JD cua user dang nhap
- Tra loi ro rang khi co loi validate

Ket qua mong doi:

- Frontend lay va tao JD on dinh

### 4.3 CV Upload API

- Kiem tra upload file PDF/DOCX
- Validate dung file type va kich thuoc
- Luu file vao storage
- Luu metadata vao `cv_uploads`
- Tra response de frontend co the xu ly tiep

Ket qua mong doi:

- Upload flow tu frontend den backend hoat dong that

### 4.4 CV Status and Result API

- Hoan thien `GET /api/v1/cv`
- Hoan thien `GET /api/v1/cv/{id}/status`
- Hoan thien `GET /api/v1/cv/{id}/result`
- Trong Week 7, `result` co the tra mock data de frontend demo

Ket qua mong doi:

- Frontend co du lieu de render processing va result page

## 5. Deliverable cuoi tuan

Den cuoi Week 7, can co cac deliverable sau:

- Frontend login/register voi backend thanh cong
- Frontend tao va lay danh sach Job Description tu backend
- Frontend upload CV that len backend
- Backend luu user, JD, CV upload vao database
- Co demo flow co ban:
  - Dang nhap
  - Tao JD
  - Upload CV
  - Sang processing
  - Sang result

## 6. Thu tu uu tien de lam

Lam theo thu tu nay de tranh bi tac:

1. Auth flow
2. Job Description flow
3. Upload CV flow
4. Processing -> Result flow
5. Error handling va UI polish

## 7. Lich goi y theo ngay

### Ngay 1

- Kiem tra lai backend auth
- Noi login/register frontend voi backend

### Ngay 2

- Noi trang Job Description voi backend
- Test tao va lay danh sach JD

### Ngay 3

- Noi upload CV voi backend
- Kiem tra metadata luu vao DB

### Ngay 4

- Noi flow processing -> result
- Mock result neu backend chua co AI result that

### Ngay 5

- Test end-to-end
- Fix loi
- Chuan bi demo

## 8. Rui ro can luu y

- Token khong duoc gui dung se gay `401 Unauthorized`
- Upload sai `Content-Type` se bi loi request
- Frontend co the van dang dung mock data ma chua thay bang API that
- API tra loi khong dong nhat se lam frontend kho xu ly
- Neu co gang lam AI that qua som se de vo scope Week 7

## 9. Tieu chi danh gia hoan thanh Week 7

Week 7 duoc xem la dat neu:

- Frontend khong chi con la giao dien tinh
- Co it nhat 3 nghiep vu da noi API that:
  - Login
  - Job Description
  - Upload CV
- Database co du lieu that sinh ra tu frontend
- Demo flow chay duoc tu dau den cuoi o muc co ban

## 10. File du kien se dong vao trong Week 7

### Frontend

- `frontend/src/pages/LoginPage.jsx`
- `frontend/src/pages/RegisterPage.jsx`
- `frontend/src/pages/JobDescriptionsPage.jsx`
- `frontend/src/pages/UploadPage.jsx`
- `frontend/src/pages/ProcessingPage.jsx`
- `frontend/src/pages/ResultPage.jsx`
- `frontend/src/lib/mockData.js`

### Backend

- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/jd.py`
- `backend/app/api/routes/cv.py`
- `backend/app/api/deps.py`
- `backend/app/schemas/auth.py`
- `backend/app/schemas/jd.py`
- `backend/app/schemas/cv.py`
- `backend/app/services/storage.py`

## 11. Ghi chu quan trong

Week 7 khong can co AI scoring hoan chinh. Dieu quan trong nhat la:

- Flow that da duoc noi giua frontend va backend
- Database nhan duoc du lieu that
- He thong chay duoc de demo

Neu con thoi gian, co the bat dau mock status/result thong minh hon. Neu khong, uu tien cao nhat van la integration core flow.
