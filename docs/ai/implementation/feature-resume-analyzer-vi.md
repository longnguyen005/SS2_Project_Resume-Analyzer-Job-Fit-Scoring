---
phase: implementation
title: "Phân Tích CV + Chấm Điểm Độ Phù Hợp Công Việc — Hướng dẫn Triển khai"
description: Ghi chú triển khai kỹ thuật, cấu trúc mã nguồn, chi tiết tích hợp và các phương pháp thực hành tốt nhất.
---

# Hướng dẫn Triển khai

## Thiết lập Môi trường Phát triển
**Bắt đầu như thế nào?**

### Yêu cầu Tiền quyết
- Docker Desktop (hoặc Docker Engine v24+ với Compose v2)
- Python 3.11+ (cho phát triển cục bộ không dùng Docker)
- OpenAI API key hoặc Google Gemini API key
- Tài khoản Cloudflare với R2 bucket
- Git

### Thiết lập Môi trường
1. Clone dự án (repository)
2. Copy `.env.example` thành `.env` và điền các giá trị:
   ```env
   # Database
   POSTGRES_USER=cvmatch
   POSTGRES_PASSWORD=<secure-password>
   POSTGRES_DB=cv_matching
   DATABASE_URL=postgresql+asyncpg://cvmatch:<password>@db:5432/cv_matching

   # Authentications System
   SECRET_KEY=<generate-random-secret>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440 # Token 1 Ngày Hết Hạn
   
   # N8N WorkFlow Setup 
   N8N_WEBHOOK_URL=http://n8n:5678
   N8N_BASIC_AUTH_USER=admin
   N8N_BASIC_AUTH_PASSWORD=<secure-password>

   # Tích Hợp Cloudflare Mây Server Files CV Bucket R2 
   R2_ACCOUNT_ID=...
   R2_ACCESS_KEY_ID=...
   R2_SECRET_ACCESS_KEY=...
   R2_BUCKET_NAME=cv-uploads
   R2_PUBLIC_URL=https://pub-xxx.r2.dev

   # Cấu hình AI Provider 
   AI_PROVIDER=openai  # hoặc "gemini"
   OPENAI_API_KEY=sk-...
   GEMINI_API_KEY=...
   
   # App
   MAX_FILE_SIZE_MB=10
   ```
3. Khởi chạy toàn bộ dịch vụ cơ chế: `docker compose up -d`
4. Cài đặt chạy di chú DB Table Bảng (migrations): `docker compose exec backend alembic upgrade head`
5. Khởi Tạo Truy Cập Endpoint Trực URL:
   - Web FastAPI Docs: `http://localhost:8000/docs` (Cửa Sổ Swagger UI API)
   - Cổng Quản Hóa n8n Mạng: `http://localhost:5678`
   - Data System PostgreSQL: Gắn Cổng `localhost:5432`

## Cấu Trúc Mã Nguồn (Code Structure)
**Mã Hệ tổ chức Project Ra Sao?**

```
project-root/
├── docker-compose.yml       # Dàn File Khởi Nền Component Architecture Services 
├── .env.example
├── backend/
│   ├── Dockerfile           # Trình Image Dịch fastapi 
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/        # Table SQL Schema Lịch sử
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # File Core Điểm Dịch Vụ, CORS, lifespan khởi
│   │   ├── core/
│   │   │   ├── config.py           # Dịch Gỡ Pydantic BaseSettings Đón Biến Env
│   │   │   ├── security.py         # Mật Mã Khóa Băm Hướng Mật Khẩu, JWT 
│   │   │   └── exceptions.py       # Điểm Đỡ Handlers Error Chung 
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py             # Depend Lớp Kết Backend get_db Cấu & get_current_user Check JWT Trục 
│   │   │   └── routes/             # Group Files 
│   │   │       ├── auth.py         # API Đăng Kí Vào 
│   │   │       ├── cv.py           # Endpoints List CV Upload Lên Và CV Trả Query Trục View List . 
│   │   │       └── jd.py           # Endpoint Tác Khối Quản Data JD System . 
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── cv_upload.py        ... # Core Classes Hệ Mô DBMS SqlAlchemy Base 
│   │   ├── schemas/                # Schemas Hệ Đỡ Form Xác Request InOut Pydantic Dữ Json Return Type Cứng . 
│   │   ├── services/
│   │   │   ├── auth_service.py     # Auth Hàm Tạo Giải Trục. 
│   │   │   ├── cv_service.py       # Code Khối Business Lệnh Webhook Đậy Save 
│   │   │   └── storage_service.py  # Hệ Logic AWS Upload Get Mạng R2 SDK Chữ 
│   │   └── db/                     # Bảng Setup Database Bất Base Base ORM Session . 
│   └── tests/
│       ├── test_upload.py          ... # Nhóm Dịch Module Run Pytest Scripts Unit API Test Core. 
├── n8n/
│   └── workflows/
│       └── cv-analysis-pipeline.json  # Backup Gói Setup File Json n8n Nodes 
└── docs/
    └── ai/                         # Tệp Document Nhóm Dự Phóng Của Feature 
```

## Các Điểm Ghi Chú Khi Triển Khai (Implementation Notes)
**Kỹ Thuật Chính Yếu Cần Nắm Rõ:**

#### 1. Xử Lý Tải Lên Tập Tin File CV Uploads Pydantic
- Stream `UploadFile` FastAPI File Ngay Tránh Cache RAM Nặng 
- Dò Validation Ngay Cấu Trúc Bằng Regex/Type Form MIME Kể Cả Tên Khai.
- Upload Gửi Data AWS Lưu Lên Boto3 R2 Trước Và Ghi Data Status DB Row Là "pending" User Nhớ URL ID Down 

#### 2. Kích WebHook Push Trigger Mạng n8n
- Sử Mạng Gửi Request Code `httpx.AsyncClient` Mở Thread Khác Bắn Giao Tiếp Sang App API N8n Request POST 
- Dùng `cv_upload_id` Đính Kí Payload Và Lọc Data Form Text JD Lấy DB Truy Data Cho Thằng Gọi Mạng WorkFlow .
- Time Phản Check TimeOut Khoảng Cỡ Chạm Ngưỡng (5s) N8N Rủi Lỗi .  

#### 3. Chỉnh Kĩ Thuật Câu Cấu Prompt LLM N8n HTTP 
- Form AI Viết System Vai Human Resource Mẫu Trọng Điểm Ép Json Cứng Template Về Bốn Group 1->100 Cho Output Điểm. Lọc Bằng Function Mở Hay Schema Check LLM OpenAI GPT4 
- Kênh Song Lọc Hai Hỗ Ngữ Prompt Kênh English Anh Vietnam Việt Nam Context Mượt . 

#### 4. Kĩ Lớp Code Parse Logic PDF Văn N8N 
- N8N Gọi File SDK Của Cloundflare Fetch Về Buffer Tải Node R2 File Khối Text Dùng Lọc Bằng `pymupdf` Cực Gọn Bóc Đoạn Text Form CV Về Dải String Format . Lọc Nhánh Nào Nhỏ Scan Ngay Máy Quét Ảnh Tesseract Dịch Node Dự Module OCR Xử. 

## Các Điểm Gắn Tích Hợp (Integration Points)
**Các khối giao tiếp kết nối thế nào?**

- **FastAPI → Cloudflare R2:** Giao thức HTTPS Sửa Lệnh REST Data API `boto3`. 
- **FastAPI → n8n:** Webhook POST Giao Liên Server Nội Bộ Nhận `{N8N_WEBHOOK_URL}/webhook/analyze-cv`. Payload ID Database Info ID Móc . N8n Mở Tạm Khóa Auth Mật Khẩu Báo Basic Headers Bảo App Request Đúng Chủ Kênh Gửi Node.  
- **n8n → Đám Cung AI Model Rate:** API Gửi Web SSL HTTP Request Của Nền Tảng Chạy Bearer API Key Dòng Request Trực Trực Node Cấp Json String Mạng Cho Provider Tín LLM. Gemini/Chat Completion Lấy .  
- **n8n → Lưu Trả Update Data Database PostgresSQL :** Gọi Setup Liên Code N8N Móc IP Cấp Mạng Server `db:5432` Docker Chạy Core. Truy Data Nguồn Credentials. Insert Bản Đọc Map Values Bảng Điểm Query Auto ID UUID Nối Theo Foreign Keys Ràng Cho .

## Quản Trị Hệ Thông Lỗi Khắc Error Handling Framework
| Sự Cố Khâu Dịch | Chuẩn Bắt Mạch API Cấu Tỉnh (Handling) |
|---------------|----------|
| Request Upload Kèm File Không CV PDF | Quét Phát Form Sớm REST Lỗi 400 Bad Đóng Lệnh Ngay |
| Form Dữ Size MB Lớn Giới Kênh Lượng Tải | Đẩy Code Mạch 413 Trả Về Form Data Payload Too | 
| Chết Kết WebHook Request Time Out Không Node Máy Kênh Tới | Lập Bản Update Lịch DB Lỗi Rủi `failed`, Warning Trả Nhẹn Của Request FastAPI Về Response Lỗi  |
| LLM Tín Rate Đứng Máy Quá Thời | Mạng N8n Lập Node Code Try Again X Retry Code Trễ (2s, 4s, 8s) Chờ Code Nhả Trả Code Token Limit |
| Điểm Database Trả Dữ Quá Hạn Phân Giải Dán AI Hư Response  | Cấp Bản Text Raw Save Data Mộc SQL Error Chờ Trích Xuất Code Form Gỡ Lịch | 

## Quản Mật Authentication Kênh Tĩnh Note Security  
- Route Cực Toàn Chặn Code Tốt Bằng Auth `Depends(get_current_user)` Giải Form Cho User Đã SignIn Access Token API Kí Headers Authentication Bearer Gặp Không Lỗi Nãy Access Hủy Mã Lỗi 401 Gặp JWT Không Nhận Token API 
- Đăng Cấp Trữ Bcrypt Mật Băm Hash Kênh Code Tức Giải. Password Giải Khóa Hashed 
- UUID Băm Mã Cấp Tên Khống Độc Lạ Ngừa Trùng Link Cloud 
- User Isolation Bảng Dữ Table DB Gọi Gắn ID CV Query DB Gương Cứng Account Access Khỏi Query Hack Sang Khóa API Khác Của Data Không Trộm Cấp List Khóa List . 
- Secret Settings Config Biến Biến Mã Này Khởi Load Cứng Khóa JWT Config Đè Server Rất Gọn Environment Tốt Hóa . 
