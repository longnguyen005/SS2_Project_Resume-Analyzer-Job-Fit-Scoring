---
phase: testing
title: "Phân Tích CV + Chấm Điểm Độ Phù Hợp Công Việc — Chiến Lược Kiểm Thử"
description: Phương pháp kiểm thử, các kịch bản kiểm thử (test cases), và kế hoạch đảm bảo chất lượng phần mềm cho tính năng Resume Analyzer.
---

# Chiến Lược Kiểm Thử (Testing Strategy)

## Mục Tiêu Độ Phủ (Test Coverage Goals)
**Mức độ kiểm thử chúng ta muốn đạt được là gì?**

- Độ phủ Unit Test: đạt 90%+ cho logic xử lý của backend service và các endpoints (routes).
- Kiểm thử Tích hợp (Integration tests): Tất cả các API endpoints + luồng Webhook n8n kích hoạt.
- Kiểm thử Đầu-Cuối (End-to-End E2E): Chạy toàn bộ luồng pipeline (Tải lên → n8n → AI Mock → Lưu DB → Gọi kết quả API).
- Đảm bảo toàn bộ Hạng mục Tiêu chí Thành công trong tài liệu Yêu cầu (Requirements) phải có ít nhất một kịch bản test cover.

## Kiểm Thử Đơn Vị (Unit Tests)
**Các thành phần độc lập nào cần được kiểm tra?**

### Dịch vụ Tải CV (Upload Service)
- [ ] Test thành công với CV PDF — file đã tải và lưu R2 Cloudflare, tạo DB Record kèm `pending` status.
- [ ] Test tải DOCX thành công — pass quy trình validation duyệt.
- [ ] Test tải file sai định dạng (`.exe`, `.jpg`) — trả mã 400 Bad Request.
- [ ] Test vượt giới hạn dung lượng 10 MB — ném mã 413 Payload Too Large.
- [ ] Test tải thiếu file (Missing file) — trả mã 422 Unprocessable Entity.
- [ ] Test hàm tạo chuỗi ngẫu nhiên (UUID filename) — không bị trùng lặp ID.

### Dịch vụ Kết Qủa Phân Tích (CV Result Service)
- [ ] Lấy kết quả bằng ID hợp lệ chứa Token ID JWT Đăng Nhập — trả ra nguyên khối điểm phân tích chi tiết.
- [ ] Lấy điểm của một User ID lạ không cùng Profile Auth — Block mã 403 Forbidden Access.
- [ ] Query Result ID không tồn tại — trả mã 404 Not Found.
- [ ] Lấy Result khi status đang `pending` — ném 202 Accepted xử lí báo tin nhắn Web "processing".
- [ ] Lấy Result gặp lỗi hệ AI sập `failed` — chọc mã 500 báo System Pipeline lỗi.

### API Danh Sách Lịch Sử Hệ (History Service)
- [ ] Query lịch sử phân trang Auth đúng (page 1, page_size 10), trả 10 rows.
- [ ] Xem list lúc tài khoản chưa up file nào — List rỗng Array `[]`.
- [ ] Truy list sắp xếp List Order — Data CV mới chấm hiện lên đầu `created_at` DESC.

### Luồng Gọi API So Sánh Hệ CV (Compare)
- [ ] Ném 2 UUIDs Valid — Build JSON nối bảng Data Scores chéo đối.
- [ ] Ném Compare vô 1 List thiếu (chỉ rỗng hoặc có 1 Array ID) — Quăng 400 Bad Request Về Format.
- [ ] ID Compare Sai Missing Missing — Ném 404.

### Logic Tách Trích Xuất Dữ Liệu (Extraction N8N Mock Test Fallbacks)
- [ ] Code Read File Có Chữ Bôi Cứng Text Lấy PyMuPDF. Đọc Khớp Nghĩa Đúng.
- [ ] Bỏ File Text Ảnh PDF — Run Try OCR Tesseract Quét Dữ Liệu Data Text Text .
- [ ] Test Read Ném File Code Trống Text Nghĩa Đen (Null bytes) — Return Lỗi Cứng Cáo Report Lỗi File Hư N8n Break Data Trả DB Fail . 

## Kiểm Thử Liên Tích Hợp Flow Nối (Integration Tests)
**Kiểm tra giao tiếp sự bắt tay tương tác giữa Service DB & N8N Flow?**

- [ ] **Upload Call Webhook:** Up Endpoint Trả Lên FastAPI, Check Log Nhận Dữ Liệu Tín POST Đưa Sang HTTP N8N Endpoint. Gửi `user_id` CV ID R2 Đường 
- [ ] **n8n Sang Data SQL DB:** Test Ấn Bắn Data Text Json Gọi Bằng Tay Bảng Node Postgres Chèn Update Bảng Record CV Upload Table Thành Đạt Kết Completed Có Chứa Điểm Rate Rê Điểm Json Map Vô .
- [ ] **Luồng Pipeline Mock Chặn Toàn Băng AI:** Tránh Lãng Phí Tiền Rate Limit Khi Test Run Node Code MOCK GIẢ Giả Danh Hàm AI Trả Tín Hiệu Json Xong Push Data Database Nối FastAPI Lọc Giao.
- [ ] **Connection DB Pool Trống Hạn:** Chạy Nhịp Kéo 20 Người Up File Khung DB Pool Kín Băng Kết Lọc Lỗi.

## Test Tự Động Kịch Người Dùng (End-to-End Tests E2E User Luồng Flows)
**Góc độ Hành Trình người Khách End User:**

- [ ] **Luồng Kịch Bất Ngờ Happy Path:** Người Đăng Kí, Cấp Tín JWT. Tải File PDF. Chờ N8N Chạy . Dùng User Request `/cv/history` Thấy Load. Gọi Thẳng Load API Lên Điểm Mắt Suggestions .
- [ ] **Phân Matching Kéo JD:** Kịch Đăng Mô Công Job Mới Chèn Nội . Chọn Tải CV Map JD Đo Độ Fit Chấm Điểm Thấy Đổi Code Ngôn Phù Hợp Lạ Đo Cấu Trúc Text Match Bố 
- [ ] **Trải Sự Nâng Cảnh Xử Bug Dọc Đường Trơn:** Up File. Ép Đánh Sập Node Tắt N8N Network Fail Điểm Status Fail API Failed . User Xoá Và Restart Up Lại Xử Process Thành Ok Kệ . 

## Cấu File Mock Dữ Test Fake File (Test Data & Assets Test)
**Đầu Vào Tool Data?**
- `tests/fixtures/sample_resume.pdf` — Mẫu Resume Đẹp CV Chuẩn Lấy Dòng Test Data.
- `tests/fixtures/scanned_resume.pdf` — Máy Render Toàn Bộ Bản Hình Test AI Lỗi Fall Back Mạch Thư Chữa OCR.
- `tests/fixtures/sample_resume.docx` — CV Form Đứng Chuẩn Word Windows.
- `tests/fixtures/large_file.pdf` — Chặn File Nặng Test Lỗi Trên 10 MB Rỗng Kéo Gửi 11MB RAM 
- `tests/fixtures/not_a_resume.pdf` — Tool Fake Dữ Dán Đuôi Check Mã Lỗi Code Hình PNG Thay Type File. Nghĩa Kín Bẫy Tải.

## Báo Test Thông Giới Đo Mảng Unit (Test Reporting & Coverage Metrics)
**Nội Trú Report HTML Ra Màn Hệ Build Coverage Python**
- Pipeline Run Đọc Chạy Unit FastAPI Lệnh Scripts Test Lịch: `docker compose exec backend pytest --cov=app --cov-report=html`
- Rate Dốc Báo Mã Pass Code Fail CI Vượt Quá: Trượt Hư Tụt Cấp Thấp 90% Block Tool Test Nhánh Kéo .
- Logs Result Output: Sinh Tín Lệnh Text Nằm Ở Đuôi Path `backend/htmlcov/index.html` 

## Test Tay Kiểm Rê Form Bug Front Lỗi Web (Manual Test API & Workflow)
**User Vọc Tools Thủ Check Sức** 

### Tấn Các Ngả API Lên UI Cửa Đọc API FastAPI 
- Setup URL Bắn Link Web Gọi Ngay Chạy Môi Trướng Local Cấp Port Test Web Tải Bằng Postman Giao Client Check Bearer Token Auth 
- Nấn Đọc Cột Tín Quét Quãng `/api/v1/cv/{id}/status` 
- Đọc File List Lên Trả Dữ Data Array Có Ra Mắt List Lĩnh Score Lọc Đẹp Hay Json Xương Lòi Khóa Không Nhả Value 

### Bóp Chạy WorkFlow Kéo Giao Hình (n8n Workflow Testing)
- Gọi Trang Địa Flow Chữ Lịch Setup Chạy IP Dashboard Config `http://localhost:5678` . Bấm Pin Tải Load . Chờ Nút Nháy Xanh Khối Pass Vòng Run Request Code Python Tróc Test Try Khối Đọc Tĩnh Parse Check Bằng Manual Web Giao Click Mắt Nhìn . 

## Quản Hiệu Suất & Xử Load Balance Hiệu Suất  (Performance Trắc Testing Cấp Tính Tải Lớn Nhanh Nhạy Tốc) 
**Bắt Sự Liệu Quản Khí Hệ System Gãy Khi Nóng Đụng Lượng?**
- Code Tải End To Nhánh Run Data Request Chờ Output < 30 Giây 
- Khối Load Thử Database Tới Lần Lệnh Data `history` Endpoints (Chứa Tới Row 100 Array Chục Cũ Tức Page Cấu Lệnh Ngắn Rung List Database Trả Rất Dễ  < 200 ms  Phút).
- Bơm Sức Test Server Kéo Ngay 5 Người Chạy Up Nhánh Trùng N8N Node Pipeline Thread Treo Data Bể Lọc Memory Khủng Tải Song Vẫn Gồng Ram RAM Trầm . Chạy Cầm RAM Tốt Máy Mát Đo Docker Logs . 

## Trình Quản Sinh Report Kéo Mác Lỗi Sập Báo Dự Chấm Fix Bắt (Bug Report Kéo Tương GitHub Theo Dõi Tracker Issue)
- Bắn Bảng GitHub Issue Tag Tên Quản Issue Cho Developer Thêm Mác:
  - **Mác Mã Đỏ Kín (Critical Lỗi Đơ Core DB):** Pipeline N8n Lõi Database Ngắt Tắt Tín Sập Hư Cấu Trúc Toàn Không Kéo AI Chấm .
  - **Nhãn Gắt Báo Đỏ (High Lỗi Trật Trật Bảo Score):** AI Check Kéo Nối Lọc Thủng 401 JWT User Sai Profile Mở Tài Xem Lịch Lẫn Không Chữa Trật Mã Code Json Xô Toác Null 
  - **Tem Lỗi (Medium Lỗi Giật Dọn Đọng Sút Ram):** Giao Gấp API Kéo Đăng Time Mất Mấy Page Rate Ram Thủng Timeout Nặng Nhập Data Dùng Nhè .
  - **Nhãn Rác (Low Bug Nhẹ):**  Báo Không Format Header Dữ CSS Text Size 1 Byte Text Không Form Dư Format Khối Thường .
- Chiến Luật Sửa Bắn Update Fix Test Rào Kín Sửa Tức Mọi Test Unit Pass Tắt Git PR Lên Review Bàn Giao Hết Dính Regression Bể Code Đụng Ngầm Cho.
