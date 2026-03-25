---
phase: planning
title: "Phân Tích CV + Chấm Điểm Độ Phù Hợp Công Việc — Kế Hoạch Dự Án"
description: Phân chia nhiệm vụ, các cột mốc, sự phụ thuộc, tiến độ và giảm thiểu rủi ro cho tính năng Resume Analyzer.
---

# Kế Hoạch Dự Án & Phân Chia Nhiệm Vụ

## Các Cột Mốc (Milestones)
**Các mốc kiểm tra chính là gì?**

- [ ] **Mốc 1:** Thiết lập Hạ tầng — Docker Compose với FastAPI + PostgreSQL + n8n cùng lúc chạy
- [ ] **Mốc 2:** API Server Tải lên CV — Endpoint tải file lên, lưu thẳng file trên Cloudflare R2, Cấu trúc bảng DB + Schema API, quản lí JD Model
- [ ] **Mốc 3:** Xây n8n Workflow — Bắt nhận Webhook → Trích Content Text văn bản → Tích Hợp AI Phân Tích → Record Lại Vào Postgres Database 
- [ ] **Mốc 4:** Viết API Query Result & Update Hệ Thống History — Lấy API bảng điểm trả về Front End, Tạo endpoint danh sách History cá nhân, so sánh 
- [ ] **Mốc 5:** Chạy Thử Integration Test — Validate Luồng End-to-end Endpoints, Viết Swagger docs , Handle Error Code 

## Phân Chia Nhiệm Vụ (Task Breakdown)
**Những công việc cụ thể nào cần thực hiện?**

### Giai đoạn 1: Cơ sở hạ tầng & Nền tảng (Infrastructure & Foundation)
- [ ] **Task 1.1:** Tạo file `docker-compose.yml` gồm `backend` (FastAPI), `db` (PostgreSQL 16) và `n8n`
- [ ] **Task 1.2:** Dựng khung thư mục dự án FastAPI (lifespan, CORS, config setting, routers core)
- [ ] **Task 1.3:** Setup Database Schema & Migration System bằng Alembic

### Giai đoạn 2: Quản Lý Xác thực JWT, Lưu JD & API Nhận Tải CV File Tải Lên
- [ ] **Task 2.1:** Viết Hệ Thống Login Đăng Ký Authentications - Mật Khẩu Hash Và Generate Trả Hệ Token JWT Core.
- [ ] **Task 2.2:** Service Lưu Đám Mây API Boto Cloudflare Bucket Hệ Sinh Thái R2 Amazon.
- [ ] **Task 2.3:** CRUD Quản Trị Job Description
- [ ] **Task 2.4:** Endpoint `POST /api/v1/cv/upload` nhận Data form, chặn các Files > 10MB Type sai
- [ ] **Task 2.5:** Viết Code Trigger HTTPX Gọi Phát WebHook tới API Endpoint System Của n8n Gửi Thông Báo Kéo File 

### Giai đoạn 3: Luồng Công Cụ n8n Pipeline Core Tự Động Phân Tích
- [ ] **Task 3.1:** Setup n8n Workflow với Hook Webhook Node làm Endpoint bắt đầu.
- [ ] **Task 3.2:** Node Lấy Extract Dữ Liệu Chữ. Download Form CV Từ Cloudflare Đám Mây. Python Node Thư Viện đọc Text PDF PyMuPDF . Chạy If/Else Lọc Data nếu rỗng Chuyển Node Tesseract Image PDF Quét
- [ ] **Task 3.3:** Nhúng Code API Kết nối Provider Trí Tuệ AI OpenAI hay Vertex AI Google Gemini. Xoay Prompt Gọi Phân Tích Hệ Điểm Từng Tiêu Chí 
- [ ] **Task 3.4:** Kết Nối Database Node Postgres. Trả Database Cập Nhật Bảng Update Thành `status: "completed"`. Append (lưu dữ liệu List) Result Phân Nhánh Cho Model DB. 

### Giai đoạn 4: API Truy Cuốn Dữ liệu Trả Frontend
- [ ] **Task 4.1:** API Route `GET /api/v1/cv/{id}/result`
- [ ] **Task 4.2:** API Route `GET /api/v1/cv/history`
- [ ] **Task 4.3:** Xây Error Handling Chuẩn Code Mã Vạch 400 401 403 404 Đầu Cuối Dễ Xử Lý Cho Client . 

### Giai đoạn 5: Tích hợp, Deploy Thử Nghiệm Tests
- [ ] **Task 5.1:** E2E Tests. End To End Request Flow Data System
- [ ] **Task 5.2:** Làm File Markdown Hướng Dẫn ReadME Setup Chạy Lệnh Mở 
- [ ] **Task 5.3:** Xuất File .json N8n Gộp Push Code Lên Git Repository Theo Dõi Cùng Nhau 

## Thời gian Ước Tính & Gói Cột Mốc Thời Gian (Estimate) 
| Giai đoạn | Thời gian | Tính Lũy | 
| --------- | --------  | -------  |
| Phase 1: Môi trường | 3–4 giờ | 3–4 giờ |
| Phase 2: CV/JD/Auth API | 5–7 giờ | 8–11 giờ |
| Phase 3: Pieline N8N | 4–6 giờ | 12–17 giờ | 
| Phase 4: API Kết Quả | 2-3 giờ | 14-20 giờ |
| Phase 5: Hỗ trợ Test Build | 3-4 giờ | 17-24 giờ |
**Tổng:** Khoảng 20–29 tiếng làm việc (đã cộng rủi ro dự phòng)

## Rủi ro & Biện pháp Dự Phòng
1. **AI Parsing Error Format Json Lỗi**: Cần set up Rule Regex, Thử Gọi Code Fallbacks Vòng Lặp Auto 
2. **Scan Text OCR Nhiễu**: Xài Thư Tesseract Kĩ Nâng Cấp Deskew Góc Cạnh Chữ . 
3. **Limit Rate Request Timeout APIs AI Provider**: Cần Limit Tracking Và Dòng Cache DB Đỡ Gọi Liên Tục Lên Provider Bị Chặn IP .
