# Week 12 Plan - Code Freeze and UI Polish (Updated)

## 1. Dinh huong Week 12

Week 12 la moc freeze:

- Khong them core feature moi
- Chot commitment features
- Tap trung bug fix, polish, reliability

## 2. Muc tieu chinh Week 12

- Freeze API contract cho flow core
- Dong P0/P1 con lai
- Chot loading/empty/error states tren tat ca man hinh chinh
- Tao release candidate on dinh

## 3. Scope Week 12

### Trong scope

- Bug fix P0/P1/P2
- UX consistency
- Regression full run
- Release notes noi bo

### Ngoai scope

- Kien truc moi
- Feature moi ngoai commitment

## 4. Task chi tiet

### 4.1 Backend

- Freeze shape response cho auth/jd/cv APIs
- Chot error code mapping
- Chot log keys can thiet de trace failure nhanh

File:

- `backend/app/api/routes/*.py`
- `backend/app/schemas/*.py`

### 4.2 Frontend

- Chot state handling:
- loading
- empty
- failed
- retry
- Chot copywriting thong nhat
- Chot navigation khong mat context

File:

- `frontend/src/pages/*.jsx`
- `frontend/src/styles.css`

### 4.3 QA

- Regression full run theo checklist Week 9-11
- Thu thap evidence (screens/logs/cases)
- Chot bug triage final

## 5. Deliverable cuoi Week 12

- Release candidate co the demo on dinh
- Checklist freeze da sign-off
- Bug backlog chi con minor/P3

## 6. Definition of Done

- Khong con blocker core flow
- API contract on dinh
- UI state handling day du
- Regression pass cho bo case chinh
