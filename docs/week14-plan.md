# Week 14 Plan - Documentation, Evidence and Packaging (Updated)

## 1. Cap nhat hien tai

Sau Week 13 hardening, Week 14 la tuan dong goi va chuan hoa tai lieu:

- Chot tai lieu dung voi implementation thuc te
- Gom du bang chung test/deployment cho bao cao
- Chuan bi bo artifact de vao Week 15 chi con rehearsal

## 2. Muc tieu chinh Week 14

- README va runbook du de 1 nguoi moi clone va chay duoc
- Bao cao project draft gan final, co evidence ro rang
- Tai lieu kien truc/API/workflow dong bo voi code hien tai
- Submission package checklist co owner va due date

## 3. Scope Week 14

### Trong scope

- Documentation freeze (README, architecture, API contract)
- Evidence collection (screens, logs, benchmark, bug closure)
- Packaging checklist va dry-run nop bai

### Ngoai scope

- Phat trien feature moi
- Refactor lon sau freeze (chi sua loi nho neu bat buoc)

## 4. Task chi tiet theo nhom

## 4.1 Documentation

### D1. README and runbook final

- Yeu cau he thong, setup local/docker, env variables
- Huong dan chay backend/frontend/n8n
- Troubleshooting cho cac loi pho bien (AI provider, DB, webhook)

File:

- `README.md`
- `docs/run-guide-week6.md`

### D2. Architecture and flow docs

- Cap nhat so do E2E theo flow that: UI -> API -> R2 -> n8n -> AI -> DB
- Chot data flow upload -> processing -> result -> history
- Them note ve OCR fallback va failure_reason strategy

File:

- `docs/ai/design/feature-resume-analyzer.md`
- `docs/week9-15-roadmap.md`

### D3. API and error contract

- Chot endpoint final va response schema
- Chot ma loi va thong diep cho frontend
- Them vi du request/response quan trong

File:

- `docs/ai/implementation/feature-resume-analyzer.md`

## 4.2 Report and evidence

### R1. Report draft final

- Problem statement, scope, architecture, implementation, testing, limitation
- Co hinh anh/so lieu benchmark va case loi tieu bieu

### R2. Evidence package

- Screenshots flow chinh
- Log mau cho case success/failure
- Bang bug fix timeline va ket qua regression

## 4.3 Packaging

### P1. Submission checklist

- Source code, migration, workflow export, README, report, slides
- Validate lai ten file va cau truc thu muc theo yeu cau mon

### P2. Dry-run handover

- Team khac clone repo va run theo README
- Ghi lai cac diem vuong va fix truoc Week 15

## 5. Deliverable cuoi Week 14

- README/runbook final
- Report draft final (co evidence day du)
- Architecture/API docs da dong bo
- Submission checklist da sign-off

## 6. Definition of Done

- Nguoi moi setup du an thanh cong theo docs trong 1 lan
- Tai lieu khop voi implementation thuc te
- Artifact nop bai du va de truy vet
- Week 15 chi con tap trung presentation va demo
