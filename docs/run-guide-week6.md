# Huong dan chay du an - Week 6

Tai lieu nay huong dan cach khoi dong du an `Resume Analyzer` o giai doan Week 6, bao gom:

- Chay bang Docker Compose
- Chay rieng Backend
- Chay rieng Frontend

Week 6 hien tap trung vao:

- FastAPI backend
- PostgreSQL database
- React/Vite frontend
- Upload metadata co ban
- Auth va Job Description CRUD co ban

AI scoring, OCR, n8n workflow thuc te se duoc bo sung o cac week sau.

## 1. Yeu cau truoc khi chay

Ban can cai dat san:

- Docker Desktop
- Node.js 20+
- npm 10+
- Python 3.11+ neu muon chay backend khong dung Docker

Kiem tra nhanh:

```powershell
docker --version
docker compose version
node -v
npm -v
```

Neu chay bang Docker, hay dam bao Docker Desktop dang mo truoc khi dung `docker compose`.

## 2. Cau truc lien quan den viec chay

```text
backend/             FastAPI app + Alembic + models
frontend/            React/Vite app
docker-compose.yml   Chay db + backend + frontend
.env.example         Bien moi truong mau
```

## 3. Tao file moi truong

Tai thu muc goc cua du an, tao file `.env` tu file mau:

```powershell
Copy-Item .env.example .env
```

Mac dinh file nay da du de chay local.

## 4. Cach 1 - Chay toan bo bang Docker

Day la cach nen dung de demo Week 6.

### Buoc 1: Build va start

```powershell
docker compose up --build
```

### Buoc 2: Truy cap cac service

- Frontend: `http://localhost:5173`
- Backend Swagger: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- PostgreSQL: `localhost:5432`

### Buoc 3: Dung he thong

```powershell
docker compose down
```

Neu muon xoa volume database:

```powershell
docker compose down -v
```

## 5. Cach 2 - Chay rieng Backend

Dung cach nay khi ban muon debug backend nhanh hon.

### Buoc 1: Chay database bang Docker

```powershell
docker compose up -d db
```

### Buoc 2: Di vao thu muc backend

```powershell
cd backend
```

### Buoc 3: Tao virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Buoc 4: Cai dependency

```powershell
pip install -r requirements.txt
```

### Buoc 5: Cai bien moi truong backend

Neu can, tao file `backend/.env` voi noi dung toi thieu:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/resume_analyzer
DATABASE_URL_SYNC=postgresql+psycopg://postgres:postgres@localhost:5432/resume_analyzer
JWT_SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=10
CORS_ORIGINS=http://localhost:5173
```

### Buoc 6: Chay migration

```powershell
alembic upgrade head
```

### Buoc 7: Chay backend

```powershell
uvicorn app.main:app --reload
```

Sau do mo:

- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## 6. Cach 3 - Chay rieng Frontend

Dung cach nay khi ban muon sua giao dien nhanh.

### Buoc 1: Di vao thu muc frontend

```powershell
cd frontend
```

### Buoc 2: Cai dependency

```powershell
npm install
```

### Buoc 3: Tao file env cho frontend neu can

Tao file `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Buoc 4: Chay frontend

```powershell
npm run dev
```

Sau do mo:

- Frontend: `http://localhost:5173`

## 7. Thu tu chay duoc khuyen nghi khi dev

Neu ban khong dung Docker cho tat ca:

1. Chay `db`
2. Chay backend
3. Chay frontend
4. Mo frontend va test login/register
5. Mo Swagger de test API song song

## 8. API san sang trong Week 6

Backend hien co cac API co ban:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/jd`
- `GET /api/v1/jd`
- `GET /api/v1/jd/{jd_id}`
- `PUT /api/v1/jd/{jd_id}`
- `DELETE /api/v1/jd/{jd_id}`
- `POST /api/v1/cv/upload`
- `GET /api/v1/cv`
- `GET /api/v1/cv/{cv_id}`
- `GET /api/v1/cv/{cv_id}/status`

## 9. Cach test nhanh sau khi chay

Ban nen test theo thu tu:

1. Mo `http://localhost:8000/health` de kiem tra backend va database.
2. Mo `http://localhost:8000/docs`.
3. Goi `POST /api/v1/auth/register` de tao tai khoan.
4. Goi `POST /api/v1/auth/login` de lay token.
5. Dung token de tao Job Description.
6. Upload mot file PDF/DOCX bang `POST /api/v1/cv/upload`.
7. Goi `GET /api/v1/cv` de kiem tra metadata da duoc luu.

## 10. Loi thuong gap

### Docker khong chay

Nguyen nhan:

- Docker Desktop chua mo
- Docker daemon chua start

Cach xu ly:

- Mo Docker Desktop
- Chay lai:

```powershell
docker compose up --build
```

### Backend khong ket noi duoc database

Kiem tra:

- Container `db` da chay chua
- `DATABASE_URL` va `DATABASE_URL_SYNC` co dung host khong
- Neu chay local backend thi host phai la `localhost`, khong phai `db`

### Frontend khong goi duoc backend

Kiem tra:

- Backend da chay chua
- `VITE_API_BASE_URL` co dung la `http://localhost:8000/api/v1` khong
- CORS da cho phep `http://localhost:5173` chua

## 11. Ghi chu cho Week 6

Trang thai hien tai la scaffold nen:

- Frontend moi o muc static-first
- Login/Register da co the goi backend that
- AI scoring chua duoc kich hoat
- n8n moi la placeholder
- Upload hien tai luu file local volume va metadata vao database

## 12. Lenh hay dung

```powershell
docker compose up --build
docker compose down
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```
