---
phase: requirements
title: "Phân Tích CV + Chấm Điểm Độ Phù Hợp Công Việc — Yêu Cầu"
description: Tải lên CV PDF → trích xuất nội dung → AI chấm điểm → gợi ý cải thiện → lưu kết quả → xem lịch sử phân tích.
---

# Yêu Cầu & Hiểu Bài Toán

## Phát Biểu Bài Toán
**Chúng ta đang giải quyết vấn đề gì?**

- Người tìm việc thiếu phản hồi khách quan, có cấu trúc về CV của họ trước khi ứng tuyển
- HR / nhà tuyển dụng mất quá nhiều thời gian để sàng lọc CV thủ công so với mô tả công việc (JD)
- Không có cách tự động để chấm điểm CV so với một JD cụ thể và nhận gợi ý cải thiện khả thi
- **Ai bị ảnh hưởng?** Người tìm việc, nhà tuyển dụng, đội ngũ HR, chuyên gia tư vấn nghề nghiệp
- **Giải pháp tạm thời hiện tại:** Đánh giá thủ công, các công cụ kiểm tra CV trực tuyến chung với khả năng AI hạn chế

## Mục Tiêu & Đối Tượng
**Chúng ta muốn đạt được gì?**

### Mục Tiêu Chính
- Cho phép người dùng tải lên CV dạng PDF/DOCX và nhận điểm do AI tạo (0–100)
- Cung cấp phân tích chi tiết theo tiêu chí: **Kỹ năng, Kinh nghiệm, Học vấn, Định dạng**
- Tạo gợi ý cải thiện khả thi cho từng hạng mục
- Lưu trữ kết quả phân tích và cho phép người dùng xem lịch sử

### Mục Tiêu Phụ
- Hỗ trợ so sánh nhiều CV với cùng một JD
- Hỗ trợ đầu vào Mô tả Công việc (JD) tùy chọn cho tính năng Chấm Điểm Độ Phù Hợp
- Cung cấp theo dõi xu hướng qua nhiều lần tải lên (sự cải thiện điểm theo thời gian)

### Không Nằm Trong Phạm Vi (ngoài phạm vi v1)
- Chỉnh sửa CV cộng tác theo thời gian thực
- Tích hợp ATS (Hệ thống Theo dõi Ứng viên)
- Tự động tạo / viết lại CV
- Đăng nhập mạng xã hội (Google, GitHub OAuth) — v1 chỉ dùng email/mật khẩu

## Câu Chuyện Người Dùng & Tình Huống Sử Dụng
**Người dùng sẽ tương tác với giải pháp như thế nào?**

1. **Với tư cách người tìm việc**, tôi muốn tải lên CV (PDF/DOCX) để nhận điểm AI khách quan và gợi ý cải thiện.
2. **Với tư cách người tìm việc**, tôi muốn xem phân tích điểm theo Kỹ năng, Kinh nghiệm, Học vấn, và Định dạng để biết chính xác cần cải thiện ở đâu.
3. **Với tư cách người tìm việc**, tôi muốn tùy chọn cung cấp Mô tả Công việc để AI có thể chấm điểm CV theo yêu cầu công việc cụ thể (Chấm Điểm Độ Phù Hợp).
4. **Với tư cách người dùng**, tôi muốn xem lịch sử phân tích để theo dõi sự cải thiện CV theo thời gian.
5. **Với tư cách người dùng**, tôi muốn so sánh nhiều CV cạnh nhau để chọn bản tốt nhất.
6. **Với tư cách nhà tuyển dụng**, tôi muốn tải lên hàng loạt nhiều CV và xem điểm xếp hạng so với một JD.

### Luồng Công Việc Chính
1. **Luồng Tải lên & Phân tích:** Tải PDF lên → Backend nhận file → Kích hoạt pipeline n8n → Trích xuất văn bản → Phân tích AI → Điểm + gợi ý lưu vào DB → Trả kết quả cho người dùng
2. **Luồng Xem Lịch sử:** Người dùng mở lịch sử → thấy danh sách các phân tích trước → nhấn vào một mục để xem chi tiết đầy đủ
3. **Luồng So sánh:** Người dùng chọn 2+ CV → hiển thị so sánh điểm cạnh nhau

### Trường Hợp Biên
- PDF bị hỏng hoặc có mật khẩu bảo vệ
- PDF chỉ có hình ảnh quét (cần OCR dự phòng)
- CV rất ngắn hoặc rỗng
- CV cực dài (>20 trang)
- Tài liệu không phải CV được tải lên nhầm
- Dịch vụ AI bị timeout hoặc giới hạn tốc độ

## Tiêu Chí Thành Công
**Làm sao biết khi nào đã hoàn thành?**

- [ ] Người dùng có thể tải lên file PDF và DOCX thành công
- [ ] Đăng ký và đăng nhập người dùng với xác thực JWT hoạt động chính xác
- [ ] Văn bản được trích xuất chính xác từ tài liệu đã tải lên (bao gồm OCR cho PDF quét)
- [ ] AI trả về điểm (0–100) với phân tích chi tiết theo 4 hạng mục
- [ ] Phân tích AI hỗ trợ CV cả Tiếng Anh và Tiếng Việt
- [ ] Gợi ý cải thiện cụ thể và khả thi theo từng hạng mục
- [ ] Kết quả được lưu trữ trong PostgreSQL và có thể truy xuất qua endpoint lịch sử
- [ ] Người dùng chỉ có thể truy cập CV và kết quả phân tích của chính mình
- [ ] Mô tả công việc có thể được lưu và tái sử dụng cho nhiều lần phân tích
- [ ] File được lưu trữ trên Cloudflare R2
- [ ] Pipeline đầu-cuối (tải lên → chấm điểm → hiển thị) hoàn thành trong < 30 giây
- [ ] Workflow n8n kích hoạt đáng tin cậy từ webhook backend
- [ ] Docker Compose khởi chạy tất cả dịch vụ (FastAPI, PostgreSQL, n8n) bằng một lệnh duy nhất

## Ràng Buộc & Giả Định
**Chúng ta cần làm việc trong những giới hạn nào?**

### Ràng Buộc Kỹ Thuật
- **Stack cố định:** FastAPI + PostgreSQL + n8n + Docker Compose
- Nhà cung cấp AI: OpenAI hoặc Gemini (cần API key, áp dụng giới hạn tốc độ)
- Trích xuất văn bản PDF: PyMuPDF cho PDF gốc, OCR (Tesseract) cho PDF quét
- Giới hạn kích thước file: tối đa 10 MB mỗi lần tải
- Định dạng hỗ trợ: chỉ PDF, DOCX
- Lưu trữ file: Cloudflare R2 (tương thích S3)
- Xác thực: JWT (email/mật khẩu)
- Đa ngôn ngữ: hỗ trợ CV Tiếng Anh + Tiếng Việt

### Ràng Buộc Nghiệp Vụ
- Xác thực JWT bắt buộc (đăng ký email/mật khẩu)
- Chi phí API AI phải được giám sát (theo dõi lượng token sử dụng)

### Giả Định
- Người dùng chủ yếu tải lên CV từ 1 đến 5 trang
- Phản hồi AI (OpenAI/Gemini) sẽ tuân thủ JSON schema được yêu cầu trong prompt một cách nhất quán
- Bản n8n community edition là đủ (không cần tính năng enterprise)
- PostgreSQL chạy trong Docker container (không dùng managed cloud DB cho v1)
- Người dùng có tài khoản Cloudflare với R2 storage đã được cấu hình

## Câu Hỏi & Hạng Mục Mở
**Chúng ta còn cần làm rõ điều gì?**

1. ~~**Nhà cung cấp AI:** Nên mặc định dùng OpenAI (GPT-4) hay Google Gemini? Hay để cấu hình được?~~ → **Đã giải quyết:** Không cấu hình được, dùng nhà cung cấp cố định
2. ~~**Đầu vào JD:** Mô tả Công việc là bắt buộc hay tùy chọn cho v1?~~ → **Đã giải quyết:** Tùy chọn, với quản lý JD riêng (lưu & tái sử dụng)
3. ~~**Xác thực:** Có nên thêm xác thực cơ bản (API key hoặc đăng nhập đơn giản) cho v1?~~ → **Đã giải quyết:** Có, xác thực JWT với email/mật khẩu
4. ~~**Lưu trữ File:** Giữ file đã tải lên vĩnh viễn hay xóa sau khi trích xuất?~~ → **Đã giải quyết:** Lưu trữ vĩnh viễn trên Cloudflare R2
5. ~~**Frontend:** Giao diện frontend có trong phạm vi không, hay chỉ API cho v1?~~ → **Đã giải quyết:** Có, giao diện frontend nằm trong phạm vi
6. ~~**Trọng số điểm:** 4 hạng mục có trọng số bằng nhau hay nên tùy chỉnh được?~~ → **Đã giải quyết:** Không tùy chỉnh được, trọng số bằng nhau
7. ~~**Đa ngôn ngữ:** Phân tích AI có nên hỗ trợ CV Tiếng Việt trong v1?~~ → **Đã giải quyết:** Có, hỗ trợ Tiếng Anh + Tiếng Việt
