# Resume Analyzer - Job Fit Scoring

## 1. Tong quan

`Resume Analyzer - Job Fit Scoring` la du an full-stack ho tro phan tich CV va danh gia muc do phu hop cua ung vien voi vi tri ung tuyen. He thong cho phep nguoi dung dang ky/dang nhap, quan ly Job Description, tai CV, trich xuat noi dung tu file PDF/DOCX, gui phan tich bang AI va hien thi ket qua cham diem theo nhieu tieu chi.

Du an duoc to chuc theo huong tach biet ro cac thanh phan:

- `frontend`: giao dien nguoi dung bang React + Vite
- `backend`: REST API bang FastAPI + SQLAlchemy + PostgreSQL
- `n8n`: workflow orchestration trung tam cho pipeline xu ly CV
- `docs`: tai lieu yeu cau, thiet ke, ke hoach va huong dan

## 2. Muc tieu du an

- Xay dung quy trinh danh gia CV theo huong ATS-friendly.
- Ho tro so sanh CV voi Job Description de dua ra diem phu hop.
- Tu dong hoa mot phan quy trinh bang OCR, AI va workflow webhook.
- Tao nen tang de tiep tuc mo rong sang scoring chi tiet, luu lich su va toi uu trai nghiem nguoi dung.

## 3. Tinh nang chinh

### Nguoi dung va xac thuc

- Dang ky tai khoan bang email/password
- Dang nhap lay JWT token
- Lay thong tin nguoi dung hien tai
- Dang nhap bang OAuth voi Google/GitHub khi duoc cau hinh

### Quan ly Job Description

- Tao Job Description
- Xem danh sach Job Description theo tung nguoi dung
- Xem chi tiet, cap nhat va xoa Job Description

### Upload va phan tich CV

- Upload CV dinh dang PDF/DOCX
- Luu file local hoac mo rong sang object storage
- Trich xuat text tu resume
- OCR fallback cho truong hop file scan
- Kiem tra file co phai resume hop le hay khong
- Goi AI provider theo giao thuc OpenAI-compatible de phan tich CV
- Tra ve diem tong, breakdown, strengths, improvements va suggestions

### Theo doi ket qua

- Xem lich su upload CV
- Kiem tra trang thai xu ly
- Xem ket qua phan tich chi tiet sau khi hoan tat

### Workflow va tich hop

- Trigger webhook sang `n8n` sau khi upload
- Pipeline `n8n` staged cho `extract -> validate -> analyze -> complete/fail`
- Dong bo `status`, `failure_reason`, `failed_stage` tu pipeline ve database
- Workflow export chinh cua repo la `n8n/workflows/cv-analysis-http-pipeline-staged.json`
- Cac export workflow tam/skeleton khong nam trong runtime contract va khong duoc commit

## 4. Kien truc tong the

```text
Frontend (React/Vite)
        |
        v
Backend API (FastAPI)
        |
        +--> PostgreSQL
        |
        +--> Local Uploads / R2-compatible Storage
        |
        +--> n8n Webhook
                |
                +--> file-worker (extract / validate)
                +--> ai-worker (analyze)
                +--> persistence-worker (complete / save DB)
```

Luong chinh hien tai:

1. Nguoi dung dang nhap va tao Job Description.
2. Nguoi dung upload CV tu frontend.
3. Backend luu file, ghi metadata vao PostgreSQL va trigger webhook n8n.
4. n8n dieu phoi pipeline `claim -> extract -> validate -> analyze -> complete/fail`.
5. `file-worker`, `ai-worker`, `persistence-worker` thuc hien cac stage xu ly chinh.
6. Backend giu vai tro upload/public APIs va internal `claim/fail`.
7. Frontend doc `status/result/history` va hien thi ket qua cham diem.

## 5. Cong nghe su dung

### Frontend

- React 18
- Vite 5
- React Router
- Lucide React / React Icons

### Backend

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- JWT authentication
- Authlib cho OAuth
- PyMuPDF / pypdf / python-docx de doc CV
- Tesseract OCR + pytesseract
- httpx de goi AI provider

### Ha tang va van hanh

- Docker
- Docker Compose
- n8n

## 6. Cau truc thu muc

```text
.
|-- backend/
|   |-- app/
|   |   |-- api/          # public routes + internal workflow claim/fail
|   |   |-- core/         # config, security, oauth
|   |   |-- db/           # session, base
|   |   |-- models/       # SQLAlchemy models
|   |   |-- schemas/      # public API schemas + internal workflow payload schemas
|   |   |-- file_worker/  # extract / validate worker app
|   |   |-- ai_worker/    # analyze worker app
|   |   |-- persistence_worker/ # complete / save DB worker app
|   |   `-- services/     # parser, analyzer, persistence, storage, workflow trigger
|   |-- alembic/
|   |-- alembic.ini
|   |-- Dockerfile
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- context/
|   |   |-- lib/         # API client, status model, polling hook, read models
|   |   `-- pages/
|   |-- Dockerfile
|   `-- package.json
|-- n8n/
|   |-- workflows/
|   `-- README.md
|-- docs/
|-- docker-compose.yml
|-- .env.example
`-- README.md
```

Frontend runtime notes:

- `/dashboard`, `/history`, `/processing`, and `/result` use backend data; legacy mock upload/result UI has been removed.
- CV status handling is centralized in `frontend/src/lib/cvStatusModel.js`.
- Processing status polling is centralized in `frontend/src/lib/useCvStatusPolling.js`.
- `frontend/src/lib/mockData.js` is limited to static HomePage marketing content.

## 7. Mo hinh du lieu chinh

He thong hien tai duoc xay quanh cac thuc the chinh:

- `User`: thong tin tai khoan
- `JobDescription`: mo ta cong viec do nguoi dung tao
- `CvUpload`: metadata cua moi lan upload CV
- `AnalysisResult`: ket qua phan tich tong the
- `CategoryScore`: diem theo tung nhom tieu chi
- `Suggestion`: goi y cai thien cho CV

## 8. Yeu cau moi truong

De chay du an local, nen co:

- Docker Desktop
- Docker Compose
- Node.js 20+
- npm 10+
- Python 3.11+ neu muon chay backend khong qua Docker

Kiem tra nhanh:

```powershell
docker --version
docker compose version
node -v
npm -v
python --version
```

## 9. Bien moi truong

Tao file `.env` tu mau:

```powershell
Copy-Item .env.example .env
```

### Nhom bien quan trong

#### Database

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `DATABASE_URL_SYNC`

#### Backend

- `APP_NAME`
- `API_V1_PREFIX`
- `BACKEND_PUBLIC_URL`
- `FRONTEND_PUBLIC_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `SESSION_SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `CORS_ORIGINS`

#### Upload va OCR

- `UPLOAD_DIR`
- `MAX_FILE_SIZE_MB`
- `OCR_FALLBACK_ENABLED`
- `OCR_LANGUAGES`
- `OCR_LANGUAGE_FALLBACK`
- `OCR_RENDER_SCALE`

#### AI Provider

- `AI_PROVIDER_LABEL`
- `AI_BASE_URL`
- `AI_API_KEY`
- `AI_MODEL`
- `AI_FALLBACK_PROVIDER_LABEL`
- `AI_FALLBACK_BASE_URL`
- `AI_FALLBACK_API_KEY`
- `AI_FALLBACK_MODEL`
- `AI_REQUEST_TIMEOUT_SECONDS`

#### OAuth

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`

#### Frontend

- `VITE_API_BASE_URL`

#### n8n

- `N8N_WEBHOOK_URL`
- `N8N_BASIC_AUTH_USER`
- `N8N_BASIC_AUTH_PASSWORD`
- `N8N_INTERNAL_SHARED_SECRET`
- `N8N_WEBHOOK_TIMEOUT_SECONDS`
- `N8N_WEBHOOK_MAX_ATTEMPTS`
- `N8N_PROCESSING_CLAIM_TTL_SECONDS`

#### n8n container

- `N8N_PUBLIC_URL`
- `N8N_HOST`
- `N8N_PROTOCOL`
- `N8N_BASIC_AUTH_ACTIVE`

Luu y:

- Runtime contract mac dinh hien tai la `backend -> n8n -> file-worker -> ai-worker -> persistence-worker`.
- `API_V1_PREFIX` phai khop voi `VITE_API_BASE_URL` va cac URL worker trong workflow n8n.
- `N8N_WEBHOOK_TIMEOUT_SECONDS=60` duoc chon cho workerized staged pipeline; neu giam xuong qua thap, webhook co the fail som truoc khi workflow ket thuc.
- `R2_ENABLED=false` trong contract mac dinh. Chi bat `true` khi da cau hinh day du `R2_ENDPOINT_URL`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`.
- Import workflow `n8n/workflows/cv-analysis-http-pipeline-staged.json` vao n8n va activate sau khi import.
- File JSON export trong repo duoc giu `active: false` de tranh commit trang thai runtime cua moi truong local.
- Chi `n8n/workflows/cv-analysis-http-pipeline-staged.json` la workflow source of truth. Khong commit export tam hoac local n8n database.

### Luu y

- Khong commit secret that vao repository.
- Nen thay `JWT_SECRET_KEY`, `SESSION_SECRET_KEY` va API keys truoc khi demo hoac deploy.
- Neu chay backend ngoai Docker, host trong `DATABASE_URL` can doi tu `db` thanh `localhost`.

## 10. Cach chay nhanh bang Docker

Day la cach duoc khuyen nghi de khoi dong toan bo he thong.

### Buoc 1: Khoi dong stack

```powershell
docker compose up --build
```

### Buoc 2: Truy cap cac service

- Frontend: `http://localhost:5173`
- Backend API docs: `http://localhost:8000/docs`
- Backend health check: `http://localhost:8000/health`
- PostgreSQL: `localhost:5432`
- n8n: `http://localhost:5678`
- `file-worker`, `ai-worker`, `persistence-worker`: noi bo trong Docker network

### Buoc 3: Dung he thong

```powershell
docker compose down
```

Neu muon xoa ca volume:

```powershell
docker compose down -v
```

## 11. Chay tung thanh phan khi dev

### Chay rieng backend

```powershell
docker compose up -d db
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Backend mac dinh chay tai `http://localhost:8000`.

### Chay rieng frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend mac dinh chay tai `http://localhost:5173`.

### Chay rieng n8n

Neu can test webhook flow:

```powershell
docker compose up -d n8n
```

## 12. API chinh

### Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/auth/oauth/{provider}/login`
- `GET /api/v1/auth/oauth/{provider}/callback`

### Job Descriptions

- `POST /api/v1/jd`
- `GET /api/v1/jd`
- `GET /api/v1/jd/{jd_id}`
- `PUT /api/v1/jd/{jd_id}`
- `DELETE /api/v1/jd/{jd_id}`

### CV

- `POST /api/v1/cv/upload`
- `GET /api/v1/cv`
- `GET /api/v1/cv/{cv_id}`
- `GET /api/v1/cv/{cv_id}/status`
- `GET /api/v1/cv/{cv_id}/result`

Swagger UI:

- `http://localhost:8000/docs`

## 13. Quy trinh test nhanh

Sau khi he thong khoi dong, co the test nhanh theo thu tu:

1. Mo `http://localhost:8000/health` de kiem tra backend va database.
2. Dang ky tai khoan hoac dang nhap tu frontend.
3. Tao mot Job Description.
4. Upload mot file CV PDF/DOCX.
5. Theo doi trang thai xu ly tai history/processing.
6. Mo ket qua phan tich de xem overall score, breakdown va suggestions.

## 14. Tai lieu lien quan

- [docs/run-guide-week6.md](docs/run-guide-week6.md)
- [docs/backend-docker-database-explained.md](docs/backend-docker-database-explained.md)
- [n8n/README.md](n8n/README.md)
- [docs/ai/requirements/README.md](docs/ai/requirements/README.md)
- [docs/ai/design/README.md](docs/ai/design/README.md)
- [docs/ai/implementation/README.md](docs/ai/implementation/README.md)
- [docs/ai/testing/README.md](docs/ai/testing/README.md)

## 15. Trang thai hien tai

Du an da co nen tang hoat dong cho:

- auth va social login co cau hinh
- Job Description CRUD
- upload CV va luu metadata
- parse text + OCR fallback
- AI analysis theo live provider
- luu lich su va ket qua cham diem
- pipeline `n8n` staged voi 3 worker rieng: `file-worker`, `ai-worker`, `persistence-worker`

Mot so phan van co the tiep tuc mo rong:

- OCR/download branch cloud-native hon trong `n8n`
- black-box test rong hon cho webhook va failure matrix
- storage cloud production-ready
- logging, monitoring va retry strategy chi tiet hon
- test tu dong cho backend/frontend
- tai lieu deployment cho moi truong production

## 16. Luu y bao mat

- Khong su dung secret mac dinh trong moi truong production.
- Khong dua API key that vao `.env.example`.
- Han che chia se file `.env` tren repository hoac kenh cong khai.
