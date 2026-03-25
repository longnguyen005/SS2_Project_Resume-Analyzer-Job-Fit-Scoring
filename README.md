# SS2 Project - Resume Analyzer Job Fit Scoring

Week 6 scaffold for a Resume Analyzer project using FastAPI, PostgreSQL, React/Vite, and Docker Compose.

## Week 6 Scope

- Backend initialized with FastAPI, JWT auth, database connection, and Alembic migration.
- Database schema created from the ERD.
- Basic CRUD APIs for user auth, job descriptions, and CV upload metadata.
- Frontend initialized with static screens for login, register, dashboard, JD management, upload, history, and result.
- Docker Compose setup for local development.

## Project Structure

```text
backend/   FastAPI API, models, migration, auth, upload metadata
frontend/  React + Vite static-first UI scaffold
docs/      Requirements, design, planning, testing documents
```

## Quick Start

1. Copy the environment file:

```powershell
Copy-Item .env.example .env
```

2. Start the application stack:

```bash
docker compose up --build
```

If you are on Windows, make sure Docker Desktop is running before this step.

3. Open the services:

- Frontend: `http://localhost:5173`
- Backend API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Backend APIs Ready In Week 6

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

## Suggested Demo Flow

1. Register a user from the frontend or Swagger.
2. Log in and confirm a JWT token is returned.
3. Create a job description.
4. Upload a sample PDF or DOCX file.
5. Open `GET /api/v1/cv` to verify the upload metadata exists in PostgreSQL.

## Notes

- Week 6 stops at metadata upload and static UI. AI scoring, OCR, and n8n orchestration are intentionally deferred to later weeks.
- Uploaded files are stored in a local Docker volume for now, which keeps this setup simple for development and demos.
