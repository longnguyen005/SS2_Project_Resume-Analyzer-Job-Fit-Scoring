# Backend, Docker, Database - Giai thich file theo tung cong doan

Tai lieu nay duoc viet de giup hieu ro:

- Moi file trong backend dung de lam gi
- Docker dang khoi dong he thong nhu the nao
- Database duoc tao va ket noi ra sao
- Thu tu xu ly cua he thong tu luc start den luc goi API

Tai lieu nay phu hop de:

- Onboarding thanh vien moi
- Bao cao giai thich cau truc du an
- Tu hoc lai toan bo Week 6

## 1. Tong quan luong chay

Khi ban chay:

```powershell
docker compose up
```

he thong se di theo thu tu sau:

1. Docker khoi dong PostgreSQL
2. Docker kiem tra database da healthy hay chua
3. Backend start
4. Backend chay migration Alembic
5. Backend khoi tao FastAPI app
6. Frontend start
7. Frontend goi API backend qua `http://localhost:8000`

Noi ngan gon:

- Database la nen
- Backend la bo nao xu ly nghiep vu
- Frontend la giao dien goi nghiep vu
- Docker la lop dung moi truong va dieu phoi toan bo

## 2. Docker giai thich theo file

### 2.1. `docker-compose.yml`

File:

- `docker-compose.yml`

Day la file quan trong nhat o tang ha tang. File nay noi cho Docker biet:

- Co bao nhieu service can chay
- Moi service build tu dau
- Chay lenh gi
- Map port nao
- Service nao phu thuoc service nao
- Dung volume nao de luu du lieu

Trong du an nay co 3 service:

- `db`
- `backend`
- `frontend`

#### Service `db`

Muc dich:

- Chay PostgreSQL

Nhung gi no dang lam:

- Dung image `postgres:16-alpine`
- Tao database `resume_analyzer`
- Mo cong `5432`
- Luu du lieu vao volume `postgres_data`
- Co healthcheck bang `pg_isready`

Y nghia:

- Backend chi nen start khi database san sang
- Neu khong co healthcheck, backend co the start qua som va bi loi ket noi DB

#### Service `backend`

Muc dich:

- Chay FastAPI backend

Nhung gi no dang lam:

- Build tu thu muc `./backend`
- Nap bien moi truong nhu `DATABASE_URL`, `JWT_SECRET_KEY`
- Phu thuoc `db`
- Mo cong `8000`
- Mount source code backend vao container
- Mount volume uploads vao `/app/uploads`
- Chay:

```sh
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Y nghia:

- Moi lan backend start, migration se chay de dam bao schema la moi nhat
- Uvicorn se khoi dong FastAPI server
- `--reload` giup sua code xong backend tu reload trong luc dev

#### Service `frontend`

Muc dich:

- Chay React/Vite frontend

Nhung gi no dang lam:

- Build tu `./frontend`
- Nap `VITE_API_BASE_URL`
- Phu thuoc backend
- Mo cong `5173`
- Mount source code frontend vao container
- Chay:

```sh
npm install && npm run dev -- --host 0.0.0.0 --port 5173
```

Y nghia:

- Frontend chay che do dev
- Co the sua file va reload nhanh

### 2.2. `.env.example`

File:

- `.env.example`

Day la file mau cho bien moi truong.

No dang chua:

- Ten DB
- User DB
- Password DB
- Chuoi ket noi async va sync
- JWT secret
- CORS
- Upload dir
- API base URL cho frontend

Y nghia:

- Tach config khoi code
- Cho phep doi moi truong de dang
- Ho tro team clone repo va chay nhanh

## 3. Backend giai thich theo thu muc

Backend nam trong:

- `backend/`

### 3.1. `backend/requirements.txt`

File:

- `backend/requirements.txt`

Muc dich:

- Liet ke cac thu vien backend can cai

Vai tro cua cac nhom thu vien:

- `fastapi`, `uvicorn`: web framework va app server
- `sqlalchemy`, `asyncpg`, `psycopg`: truy cap PostgreSQL
- `alembic`: migration
- `python-jose`: JWT
- `passlib`: hash password
- `python-multipart`: ho tro upload file
- `pydantic-settings`: doc env

Y nghia:

- Khong co file nay thi Dockerfile va moi truong local khong biet can cai gi

### 3.2. `backend/Dockerfile`

File:

- `backend/Dockerfile`

Muc dich:

- Dinh nghia cach build backend container

Trinh tu:

1. Lay image `python:3.11-slim`
2. Set workdir la `/app`
3. Copy `requirements.txt`
4. Cai dependency
5. Copy source code
6. Chay `uvicorn`

Y nghia:

- Bien source backend thanh mot image co the chay o moi may

## 4. Backend giai thich theo luong code

### 4.1. App entrypoint

File:

- `backend/app/main.py`

Muc dich:

- Khoi tao FastAPI app
- Bat CORS
- Dang ky router
- Tao healthcheck

Cong doan:

1. Import settings
2. Tao app FastAPI
3. Add `CORSMiddleware`
4. Include router `/api/v1`
5. Tao route `/health`

Y nghia:

- Day la cua vao chinh cua backend
- Neu file nay loi, app se khong boot

### 4.2. Config va security

#### `backend/app/core/config.py`

Muc dich:

- Doc cau hinh tu env

Dang quan ly:

- DB URL
- JWT config
- Upload dir
- File size limit
- CORS

Y nghia:

- Toan bo app khong hard-code thong tin nhay cam

#### `backend/app/core/security.py`

Muc dich:

- Hash password
- Verify password
- Tao JWT
- Giai ma JWT

Day la noi xu ly:

- User register
- User login
- Request can auth

Y nghia:

- Bao mat tai khoan va route

### 4.3. Database layer

#### `backend/app/db/base.py`

Muc dich:

- Tao `Base` chung cho tat ca ORM model

Y nghia:

- Model nao cung ke thua tu day

#### `backend/app/db/session.py`

Muc dich:

- Tao `engine`
- Tao `async_session_factory`

Y nghia:

- Moi request can truy van DB se lay session tu day

### 4.4. API layer

#### `backend/app/api/router.py`

Muc dich:

- Gom tat ca route nho thanh mot router lon

Dang include:

- `auth`
- `jd`
- `cv`

Y nghia:

- `main.py` chi can include 1 router tong

#### `backend/app/api/deps.py`

Muc dich:

- Chua dependency dung chung

Quan trong nhat:

- `get_db()`: cap session DB
- `get_current_user()`: doc token va lay user hien tai

Y nghia:

- Giu code route gon
- Tach logic dung chung ra khoi business logic

### 4.5. Route business logic

#### `backend/app/api/routes/auth.py`

Muc dich:

- Xu ly register
- Xu ly login

Flow register:

1. Nhan request JSON
2. Kiem tra email da ton tai chua
3. Hash password
4. Tao user moi
5. Luu vao DB
6. Tra user response

Flow login:

1. Nhan `username/password`
2. Tim user theo email
3. Verify password
4. Tao access token
5. Tra token

#### `backend/app/api/routes/jd.py`

Muc dich:

- CRUD cho Job Description

Flow chung:

1. Yeu cau JWT
2. Lay current user
3. Chi thao tac tren JD cua chinh user do

Y nghia:

- Bao dam data isolation

#### `backend/app/api/routes/cv.py`

Muc dich:

- Upload CV
- Lay danh sach CV
- Lay chi tiet CV
- Lay status CV

Flow upload:

1. Nhan file multipart
2. Neu co `job_description_id` thi kiem tra no co thuoc user khong
3. Goi service luu file
4. Tao record `cv_uploads`
5. Tra metadata ve cho client

Y nghia:

- Day la diem vao cho pipeline AI tu cac week sau

### 4.6. Schema layer

Schema la noi dinh nghia hinh dang du lieu vao/ra cua API.

#### `backend/app/schemas/auth.py`

Muc dich:

- Dinh nghia `UserCreate`, `UserRead`, `TokenResponse`

#### `backend/app/schemas/jd.py`

Muc dich:

- Dinh nghia schema tao, sua, doc Job Description

#### `backend/app/schemas/cv.py`

Muc dich:

- Dinh nghia schema tra ve cho upload CV va status

Y nghia cua schemas:

- Validate input
- Chuan hoa output
- Swagger doc de doc hon

### 4.7. Service layer

#### `backend/app/services/storage.py`

Muc dich:

- Xu ly logic luu file upload

Cong viec:

1. Kiem tra MIME type
2. Kiem tra extension
3. Tao ten file moi bang UUID
4. Tao folder theo user
5. Ghi file xuong o cung
6. Kiem tra size file

Y nghia:

- Tach logic file khoi route
- Sau nay co the thay local storage bang R2 ma khong sua qua nhieu route

## 5. Database giai thich theo model

Tat ca model nam trong:

- `backend/app/models/`

### 5.1. `mixins.py`

Muc dich:

- Dinh nghia phan dung chung cho model:
  - `id`
  - `created_at`
  - `updated_at`

Y nghia:

- Tranh lap code giua nhieu bang

### 5.2. `user.py`

Bang:

- `users`

Chua:

- Email
- Hashed password
- Full name
- Active status

Vai tro:

- La chu so huu cua toan bo du lieu he thong

### 5.3. `job_description.py`

Bang:

- `job_descriptions`

Chua:

- `user_id`
- `title`
- `description_text`

Vai tro:

- Luu mo ta cong viec de dung lai nhieu lan

### 5.4. `cv_upload.py`

Bang:

- `cv_uploads`

Chua:

- `user_id`
- `job_description_id`
- `filename`
- `stored_filename`
- `storage_path`
- `file_type`
- `file_size_bytes`
- `status`

Vai tro:

- Ghi nhan moi lan user upload CV

### 5.5. `analysis_result.py`

Bang:

- `analysis_results`

Vai tro:

- Danh cho ket qua AI o cac tuan sau

Hien tai:

- Da co schema
- Chua dung nghiep vu that trong Week 6

### 5.6. `category_score.py`

Bang:

- `category_scores`

Vai tro:

- Luu diem tung tieu chi

### 5.7. `suggestion.py`

Bang:

- `suggestions`

Vai tro:

- Luu goi y cai thien CV

### 5.8. `models/__init__.py`

Muc dich:

- Import tat ca model ve mot cho

Y nghia:

- Giup SQLAlchemy resolve relationship dung
- Day cung la noi da sua de fix loi mapper trong qua trinh khoi dong

## 6. Alembic va migration

### 6.1. `backend/alembic.ini`

Muc dich:

- File config cho Alembic

### 6.2. `backend/alembic/env.py`

Muc dich:

- Noi Alembic voi SQLAlchemy metadata
- Cho Alembic biet can migrate schema nao

Y nghia:

- Khong co file nay thi Alembic khong biet phai tao bang gi

### 6.3. `backend/alembic/versions/0001_week6_init.py`

Muc dich:

- Migration dau tien cua du an

Cong viec cua migration:

- Tao bang
- Tao khoa ngoai
- Tao index

Y nghia:

- Bien ERD thanh bang that trong PostgreSQL

## 7. Thu tu nghiep vu tu luc user thao tac

### 7.1. User register

File di qua:

1. `backend/app/main.py`
2. `backend/app/api/router.py`
3. `backend/app/api/routes/auth.py`
4. `backend/app/core/security.py`
5. `backend/app/models/user.py`
6. `backend/app/db/session.py`

### 7.2. User login

File di qua:

1. `backend/app/api/routes/auth.py`
2. `backend/app/core/security.py`
3. `backend/app/models/user.py`

### 7.3. User tao Job Description

File di qua:

1. `backend/app/api/routes/jd.py`
2. `backend/app/api/deps.py`
3. `backend/app/models/job_description.py`
4. `backend/app/db/session.py`

### 7.4. User upload CV

File di qua:

1. `backend/app/api/routes/cv.py`
2. `backend/app/api/deps.py`
3. `backend/app/services/storage.py`
4. `backend/app/models/cv_upload.py`
5. `backend/app/db/session.py`

## 8. Hieu theo cach de nho

Neu nho theo tang, ban co the nho nhu sau:

- Docker: dung moi truong va khoi dong he thong
- Database: luu du lieu
- Alembic: tao bang trong database
- Core: config va bao mat
- DB session: ket noi DB
- Models: hinh dang bang
- Schemas: hinh dang request/response
- Services: logic dung chung
- Routes: nghiep vu API
- Main: diem vao cua backend

## 9. Ket luan

Neu hieu toan bo file theo dung trinh tu, ban se thay Week 6 dang lam dung 3 viec nen tang:

1. Dung moi truong chay duoc
2. Dung backend co nghiep vu co ban
3. Dung database co schema that

Day la ly do Week 6 rat quan trong:

- Chua can AI
- Chua can pipeline phuc tap
- Nhung bat buoc phai co bo khung dung

Sau khi nen nay on, Week 7 tro di moi co the noi frontend that, hoan thien upload flow, va sau do moi tien toi AI analysis.
