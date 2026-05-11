# Roadmap Week 9 -> Week 15 (Updated)

## 1. Muc tieu roadmap

Roadmap nay chot huong di cho giai doan cuoi du an:

- Week 9: chot full business flow end-to-end va bo mock user-facing
- Week 10: dua file storage len Cloudflare R2 + webhook n8n skeleton
- Week 11: hoan thien n8n processing pipeline that
- Week 12: code freeze + UI state polish + regression
- Week 13: hardening + performance + scoring consistency
- Week 14: documentation + evidence + packaging
- Week 15: final demo rehearsal + submission

## 2. Trang thai hien tai

Da hoan thanh:

- Core flow `login -> jd -> upload -> processing -> result -> history`
- Loai bo hien thi mock-ai/mock-ai-fallback cho user
- Co `failure_reason` de frontend hien message loi ro rang
- Co OCR fallback o backend parser
- Da chuyen processing chinh sang n8n workerized pipeline `claim -> extract -> validate -> analyze -> complete/fail`
- Da tach worker runtime thanh `file-worker`, `ai-worker`, `persistence-worker`

Can tiep tuc:

- Chuyen storage sang R2 (neu chua done production)
- Chot benchmark/stability report va bo tai lieu final
- Freeze runtime contract va cleanup config/docs drift truoc khi sang hardening

## 3. Milestone den cuoi ky

- M1 (W9): Core flow on dinh, error handling ro rang
- M2 (W10): Upload moi qua R2 + backend trigger webhook n8n
- M3 (W11): n8n pipeline xu ly that (extract/OCR/analyze/save)
- M4 (W12): Code freeze, regression pass, release candidate
- M5 (W13): Hardening report + performance/scoring consistency
- M6 (W14): README/report/docs final + submission checklist sign-off
- M7 (W15): Demo ready + backup ready + nop bai day du

## 4. Thu tu uu tien xu ly

1. Reliability core flow
2. Cloud storage R2
3. Workflow orchestration n8n
4. Hardening + observability + consistency
5. Documentation + report + packaging
6. Presentation + final rehearsal

## 5. Dependency chinh

- R2 la nen tang de n8n xu ly file cloud-native on dinh
- n8n pipeline phai on dinh truoc khi chot freeze Week 12
- Hardening Week 13 phu thuoc vao metric/log thu duoc tu Week 11-12
- Week 14-15 phu thuoc vao artifact test va benchmark da chot

## 6. Risk can quan tri

- AI provider 503/429 gay fail batch processing
- R2 permission/CORS sai cau hinh lam upload loi
- n8n workflow timeout hoac retry loop khong dung
- Ket qua cham dao dong neu tham so model khong duoc co dinh
- Cham tai lieu se anh huong chat luong demo va nop bai

## 7. KPI theo tuan

- Week 9: ty le flow end-to-end thanh cong >= 90% (manual smoke set)
- Week 10: >= 95% upload moi luu thanh cong len R2
- Week 11: n8n pipeline success rate >= 85% tren bo test noi bo
- Week 12: 0 bug blocker/P0 tren core flow
- Week 13: latency trung binh upload->result giam it nhat 15%
- Week 14: README/report/docs dat full checklist
- Week 15: rehearsal tron ven trong <= 12 phut, co backup demo

## 8. Tai lieu chi tiet tung tuan

- `docs/week9-plan.md`
- `docs/week10-plan.md`
- `docs/week11-plan.md`
- `docs/week12-plan.md`
- `docs/week13-plan.md`
- `docs/week14-plan.md`
- `docs/week15-plan.md`
