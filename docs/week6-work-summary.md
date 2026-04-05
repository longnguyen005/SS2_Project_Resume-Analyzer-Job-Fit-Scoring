# Tong ket cong viec Week 6 - Resume Analyzer

Tai lieu nay tong hop day du nhung gi da duoc trien khai trong Week 6 cho du an `Resume Analyzer + Job Fit Scoring`.

Muc tieu cua file nay:

- Giai thich ro Week 6 can lam gi theo Weekly Progress
- Tong hop toan bo nghiep vu da duoc trien khai
- Giai thich chi tiet phan backend, frontend, database, docker
- Liet ke cac loi da gap va da sua
- Xac dinh ro pham vi da xong va nhung gi chua lam trong Week 6

## 1. Muc tieu cua Week 6

Theo Weekly Progress, Week 6 co ten:

`Project Initialization, Database & Static UI`

Dieu nay co nghia la trong tuan nay du an chua can hoan thien AI scoring, OCR, n8n workflow day du, ma can dat duoc cac muc tieu nen tang sau:

- Khoi tao source code cho backend va frontend
- Ket noi va khoi tao database that
- Tao schema bang theo ERD
- Xay dung cac API co ban de demo duoc
- Dung giao dien tinh de chuan bi cho viec noi API o Week 7
- Dong goi du an bang Docker de co the chay local de demo

Noi ngan gon, Week 6 la tuan dung "bo xuong" cua toan bo he thong.

## 2. Tong quan nhung gi da duoc lam

Trong Week 6, cac hang muc sau da duoc trien khai:

- Tao bo khung backend bang FastAPI
- Tao migration va schema cho PostgreSQL
- Tao auth co ban voi `register/login`
- Tao CRUD co ban cho `Job Description`
- Tao nghiep vu upload CV o muc metadata
- Tao frontend React/Vite voi cac man hinh chinh
- Tao Docker Compose de chay `db + backend + frontend`
- Tao file huong dan chay du an
- Sua cac loi runtime khi khoi dong backend

## 3. Nghiep vu da duoc trien khai

Phan nay la phan nghiep vu thuc te cua he thong da lam duoc trong Week 6.

### 3.1. Nghiep vu dang ky tai khoan

Nguoi dung co the tao tai khoan moi bang email, password va full name.

Da trien khai:

- API `POST /api/v1/auth/register`
- Luu user vao bang `users`
- Hash password truoc khi luu
- Kiem tra email da ton tai hay chua

Y nghia nghiep vu:

- Day la diem bat dau de moi du lieu sau nay duoc gan voi dung user
- Moi CV, JD, ket qua phan tich deu phai thuoc ve mot tai khoan cu the

File lien quan:

- `backend/app/api/routes/auth.py`
- `backend/app/schemas/auth.py`
- `backend/app/models/user.py`
- `backend/app/core/security.py`

### 3.2. Nghiep vu dang nhap

Nguoi dung co the dang nhap de nhan JWT token.

Da trien khai:

- API `POST /api/v1/auth/login`
- Xac thuc email va password
- Tra ve `access_token`

Y nghia nghiep vu:

- Day la lop bao mat toi thieu cho he thong
- Cac nghiep vu upload CV, tao Job Description, xem du lieu rieng deu can user da dang nhap

File lien quan:

- `backend/app/api/routes/auth.py`
- `backend/app/api/deps.py`
- `backend/app/core/security.py`
- `backend/app/schemas/auth.py`

### 3.3. Nghiep vu quan ly Job Description

Nguoi dung co the luu Job Description de dung lai nhieu lan.

Da trien khai:

- `POST /api/v1/jd`
- `GET /api/v1/jd`
- `GET /api/v1/jd/{jd_id}`
- `PUT /api/v1/jd/{jd_id}`
- `DELETE /api/v1/jd/{jd_id}`

Y nghia nghiep vu:

- He thong Resume Analyzer can cham CV theo mot vi tri cu the
- Job Description can duoc luu lai de dung lai khi nguoi dung upload nhieu phien ban CV
- Day la nghiep vu rat quan trong cho bai toan `Job Fit Scoring`

File lien quan:

- `backend/app/api/routes/jd.py`
- `backend/app/schemas/jd.py`
- `backend/app/models/job_description.py`
- `backend/app/api/deps.py`

### 3.4. Nghiep vu upload CV o muc metadata

Nguoi dung co the upload file CV de tao ban ghi metadata trong he thong.

Da trien khai:

- `POST /api/v1/cv/upload`
- Chap nhan file PDF/DOCX
- Kiem tra content type va extension
- Kiem tra gioi han dung luong file
- Luu file vao local volume
- Tao ban ghi `cv_uploads`
- Gan trang thai mac dinh la `pending`

Y nghia nghiep vu:

- Day la diem vao cua he thong Resume Analyzer
- Trong Week 6, muc tieu chua phai la AI chay that, ma la upload duoc file va luu duoc metadata
- Viec nay giup chuan bi cho Week 7-10 de noi sang n8n va AI

File lien quan:

- `backend/app/api/routes/cv.py`
- `backend/app/services/storage.py`
- `backend/app/schemas/cv.py`
- `backend/app/models/cv_upload.py`
- `backend/app/core/config.py`

### 3.5. Nghiep vu xem danh sach upload va trang thai

Da trien khai:

- `GET /api/v1/cv`
- `GET /api/v1/cv/{cv_id}`
- `GET /api/v1/cv/{cv_id}/status`

Y nghia nghiep vu:

- Day la phan nen cho history va status polling
- Frontend co the dung de hien thi trang thai xu ly cua CV
- Tuy chua co pipeline AI day du, nhung API da san sang de mo rong

File lien quan:

- `backend/app/api/routes/cv.py`
- `backend/app/schemas/cv.py`
- `backend/app/models/cv_upload.py`

### 3.6. Nghiep vu health check he thong

Da trien khai:

- `GET /health`

Y nghia nghiep vu:

- Dung de kiem tra nhanh backend va database co dang song hay khong
- Ho tro demo va debug nhanh trong qua trinh phat trien

File lien quan:

- `backend/app/main.py`
- `backend/app/db/session.py`

## 4. Phan backend da lam gi

Backend duoc xay dung bang FastAPI.

### 4.1. Da tao bo khung backend

Da tao cac thanh phan chinh:

- `backend/app/main.py`
- `backend/app/api/`
- `backend/app/core/`
- `backend/app/db/`
- `backend/app/models/`
- `backend/app/schemas/`
- `backend/app/services/`
- `backend/alembic/`

Y nghia:

- Day la cau truc nen de cac tuan sau co the mo rong ma khong bi roi
- Tach ro route, schema, service, model, session

File lien quan:

- `backend/app/main.py`
- `backend/app/api/router.py`
- `backend/app/db/session.py`
- `backend/app/models/`
- `backend/app/schemas/`
- `backend/app/services/`

### 4.2. Da tao config va security

Da trien khai:

- Doc bien moi truong
- Cau hinh DB
- Cau hinh JWT
- Cau hinh upload dir
- Password hashing

Y nghia:

- Toan bo he thong co the chay trong moi truong local bang env
- De de chuyen sang staging/production sau nay

File lien quan:

- `backend/app/core/config.py`
- `backend/app/core/security.py`
- `.env.example`

### 4.3. Da tao route va dependency auth

Da trien khai:

- `get_db`
- `get_current_user`
- `OAuth2PasswordBearer`

Y nghia:

- API duoc bao ve bang token
- Moi request nhay cam deu co the xac dinh user hien tai

File lien quan:

- `backend/app/api/deps.py`
- `backend/app/api/routes/auth.py`
- `backend/app/core/security.py`

## 5. Phan database da lam gi

Database su dung PostgreSQL.

### 5.1. Da tao database service

Trong Docker Compose, da tao service `db` bang image:

- `postgres:16-alpine`

Database mac dinh:

- `resume_analyzer`

File lien quan:

- `docker-compose.yml`
- `.env.example`

### 5.2. Da tao migration dau tien

Da tao file:

- `backend/alembic/versions/0001_week6_init.py`

Migration nay tao cac bang:

- `users`
- `job_descriptions`
- `cv_uploads`
- `analysis_results`
- `category_scores`
- `suggestions`

File lien quan:

- `backend/alembic/versions/0001_week6_init.py`
- `backend/alembic/env.py`
- `backend/alembic.ini`
- `backend/app/models/`

### 5.3. Y nghia cua viec tao day du 6 bang ngay tu Week 6

Mac du Week 6 moi dung den mot phan nghiep vu, nhung viec tao truoc schema day du co loi:

- Bam sat ERD da thiet ke tu Week 4-5
- Tranh viec sua schema qua nhieu lan
- Tao nen san de cac tuan sau lam AI result ma khong phai dap schema lai tu dau

File lien quan:

- `docs/ai/design/feature-resume-analyzer.md`
- `backend/alembic/versions/0001_week6_init.py`

## 6. Phan frontend da lam gi

Frontend duoc xay dung bang React + Vite.

### 6.1. Da khoi tao project frontend

Da tao:

- `frontend/package.json`
- `frontend/src/main.jsx`
- `frontend/src/App.jsx`
- `frontend/src/styles.css`

File lien quan:

- `frontend/package.json`
- `frontend/vite.config.js`
- `frontend/src/main.jsx`
- `frontend/src/App.jsx`
- `frontend/src/styles.css`

### 6.2. Da tao cac man hinh chinh

Da co cac page:

- Dashboard
- Login
- Register
- Job Descriptions
- Upload CV
- History
- Result

Y nghia:

- Day la phan `static UI` dung voi yeu cau cua Week 6
- Frontend chua can day du logic nghiep vu, nhung can co day du bo cuc, flow va giao dien de demo

File lien quan:

- `frontend/src/pages/DashboardPage.jsx`
- `frontend/src/pages/LoginPage.jsx`
- `frontend/src/pages/RegisterPage.jsx`
- `frontend/src/pages/JobDescriptionsPage.jsx`
- `frontend/src/pages/UploadPage.jsx`
- `frontend/src/pages/HistoryPage.jsx`
- `frontend/src/pages/ResultPage.jsx`
- `frontend/src/lib/mockData.js`

### 6.3. Da co auth flow co ban

Da trien khai:

- Form register co the goi backend that
- Form login co the goi backend that
- Luu token vao `localStorage`

Y nghia:

- Day la cau noi giua Week 6 va Week 7
- Tuan sau chi can noi tiep cac man hinh con lai vao API that

File lien quan:

- `frontend/src/pages/LoginPage.jsx`
- `frontend/src/pages/RegisterPage.jsx`
- `backend/app/api/routes/auth.py`

## 7. Phan Docker da lam gi

Da tao file:

- `docker-compose.yml`

### 7.1. Cac service da co

- `db`
- `backend`
- `frontend`

File lien quan:

- `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`

### 7.2. Y nghia cua Docker trong Week 6

- Giup chay du an bang mot lenh
- De demo cho giang vien
- Giam loi do moi truong local giua cac may khac nhau

File lien quan:

- `docker-compose.yml`
- `README.md`
- `docs/run-guide-week6.md`

### 7.3. Da tao file env mau

Da tao:

- `.env.example`

Y nghia:

- Giup team clone repo xong co the tao file `.env` de chay ngay
- Quan ly cau hinh thong nhat

File lien quan:

- `.env.example`
- `backend/app/core/config.py`
- `docker-compose.yml`

## 8. Loi da gap trong qua trinh trien khai va da sua

Day la phan rat quan trong vi no cho thay trong Week 6 khong chi la scaffold, ma con bao gom viec xu ly runtime issue.

### 8.1. Loi parse `CORS_ORIGINS`

Hien tuong:

- Backend crash khi startup
- `pydantic-settings` bao loi parse field `cors_origins`

Nguyen nhan:

- Code khai bao `cors_origins` la `list[str]`
- Env lai truyen chuoi thuong `http://localhost:5173`
- Thu vien co parse chuoi nay theo JSON va bi loi

Da sua:

- Doi `cors_origins` thanh chuoi
- Tu tach thanh danh sach bang property

File lien quan:

- `backend/app/core/config.py`
- `backend/app/main.py`
- `docker-compose.yml`

### 8.2. Loi FastAPI voi `204 No Content`

Hien tuong:

- Route xoa JD bi crash khi app load

Nguyen nhan:

- FastAPI khong cho `204` co response body
- Route xoa khai bao theo cach gay assertion error

Da sua:

- Dung `Response(status_code=204)`
- Khai bao `response_model=None`

File lien quan:

- `backend/app/api/routes/jd.py`

### 8.3. Loi SQLAlchemy khong resolve duoc `AnalysisResult`

Hien tuong:

- Khi goi API co truy van DB, ORM crash voi loi mapper

Nguyen nhan:

- Model registry chua duoc import day du
- Quan he giua cac class duoc khai bao bang string, nhung SQLAlchemy chua nap du class can thiet

Da sua:

- Gom import model trong `app.models`
- Route va dependency su dung import tu `app.models`

File lien quan:

- `backend/app/models/__init__.py`
- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/jd.py`
- `backend/app/api/routes/cv.py`
- `backend/app/api/deps.py`

### 8.4. Loi `bcrypt` trong password hashing

Hien tuong:

- Dang ky user tra ve `500`
- Log backend bao loi `bcrypt`

Nguyen nhan:

- Backend hashing stack `passlib + bcrypt` trong image hien tai khong tuong thich on dinh

Da sua:

- Chuyen qua `pbkdf2_sha256`

Y nghia:

- Van dam bao password duoc hash
- On dinh hon cho moi truong Week 6

File lien quan:

- `backend/app/core/security.py`
- `backend/requirements.txt`

### 8.5. Loi Docker build timeout

Hien tuong:

- Build image moi bi loi `TLS handshake timeout`

Nguyen nhan:

- Docker khong keo duoc base image tu Docker Hub do loi mang

Ket luan:

- Day la loi network/environment, khong phai loi source code

File lien quan:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.yml`

## 9. Da xac minh duoc gi sau khi sua

Sau khi sua, da kiem tra lai thanh cong:

- `GET /health` tra ve `200 OK`
- `POST /api/v1/auth/register` tra ve `201 Created`
- `POST /api/v1/auth/login` tra ve `200 OK`
- `POST /api/v1/jd` tra ve `201 Created`

Dieu nay cho thay:

- Backend da boot thanh cong
- Ket noi database on
- ORM hoat dong dung
- Auth flow chay duoc
- JWT dependency chay duoc

## 10. Week 6 da hoan thanh den dau

### Da hoan thanh

- Co source code backend that
- Co source code frontend that
- Co database schema that
- Co Docker Compose
- Co auth flow co ban
- Co Job Description CRUD
- Co upload CV metadata
- Co static UI cho cac man hinh chinh
- Co file huong dan chay du an

### Chua lam trong Week 6

- Chua ket noi n8n that
- Chua OCR
- Chua AI scoring
- Chua result generation that
- Chua compare CV
- Chua hoan thien full history data view
- Chua co test tu dong
- Chua co cloud storage R2 that

## 11. Tuan nay da lam gi theo ngon ngu de bao cao

Neu can viet vao report hoac bao cao giang vien, co the tom tat Week 6 nhu sau:

Trong Week 6, nhom da hoan thanh giai doan khoi tao he thong. Cu the, nhom da xay dung bo khung backend bang FastAPI, thiet lap PostgreSQL va migration schema theo ERD, trien khai cac API co ban cho authentication, Job Description management va upload CV metadata. Dong thoi, nhom da khoi tao frontend bang React/Vite va xay dung day du cac man hinh tinh phuc vu flow chinh cua he thong. Ngoai ra, nhom da dockerize du an de co the chay local va demo thong qua Docker Compose. Trong qua trinh trien khai, nhom cung da phat hien va sua mot so loi runtime lien quan den config, model mapping va password hashing, giup backend van hanh on dinh hon.

## 12. Huong di tiep theo sau Week 6

Week 7 nen tiep tuc theo dung huong sau:

- Noi frontend voi backend that cho auth, JD, history
- Hoan thien upload flow tren giao dien
- Bat dau hien thi du lieu that thay vi mock data
- Chuan bi workflow cho viec xu ly async

Week 8-10 nen tiep tuc:

- Noi n8n
- OCR
- AI scoring
- Luu ket qua phan tich
- Hien thi result that

## 13. File lien quan

Cac file quan trong cua Week 6:

- `docker-compose.yml`
- `backend/app/main.py`
- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/jd.py`
- `backend/app/api/routes/cv.py`
- `backend/alembic/versions/0001_week6_init.py`
- `frontend/src/App.jsx`
- `frontend/src/pages/`
- `docs/run-guide-week6.md`

Neu muon doi chieu theo nghiep vu, ban nen doc file nay cung voi:

- `docs/ai/requirements/feature-resume-analyzer.md`
- `docs/ai/design/feature-resume-analyzer.md`
- `docs/run-guide-week6.md`

## 14. Ket luan

Week 6 da hoan thanh dung vai tro cua mot tuan khoi tao he thong:

- Co bo khung du an that
- Co backend that
- Co database that
- Co frontend that
- Co docker de chay local
- Co nghiep vu co ban de demo

Day la nen tang bat buoc de cac tuan sau co the tap trung vao integration, AI processing va business flow hoan chinh.
