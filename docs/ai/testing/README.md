---
phase: testing
title: Testing Strategy
description: Define testing approach, test cases, and quality assurance
---

# Testing Strategy

## Test Coverage Goals
**What level of testing do we aim for?**

- Unit test coverage target (default: 100% of new/changed code)
- Integration test scope (critical paths + error handling)
- End-to-end test scenarios (key user journeys)
- Alignment with requirements/design acceptance criteria

## Regression Checklist

### Backend
- [x] Worker routes compile after refactor.
- [x] File worker extract/validate integration tests pass.
- [x] AI worker success/503/422 integration tests pass.
- [x] Persistence worker complete/save-failure integration tests pass.
- [ ] Upload valid CV through the public API and verify status reaches `completed`.
- [ ] Upload a non-CV/invalid document and verify status reaches `failed` with `failed_stage=extract`.
- [ ] Request result before completion and verify HTTP 409.
- [ ] Request completed result and verify score/breakdown/suggestions are returned.

### Frontend
- [x] `npm run build` passes.
- [x] DashboardPage reads `/cv` instead of mock upload data.
- [x] ProcessingPage uses shared status polling for `pending`, `processing`, `completed`, `failed`.
- [x] ResultPageConnected links back to Processing when result is not ready (`409`).
- [x] HistoryPage and HistoryRow use the shared status model.
- [x] Legacy static ResultPage is removed from runtime source.
- [ ] Manual browser check: upload -> processing -> result.
- [ ] Manual browser check: processing failed state shows retry/upload/history actions.
- [ ] Manual browser check: dashboard loading/error/empty/recent uploads states.
- [ ] Manual browser check: history loading/error/empty/completed rows.

## Integration Tests
**How do we test component interactions?**

- [ ] Integration scenario 1
- [ ] Integration scenario 2
- [ ] API endpoint tests
- [ ] Integration scenario 3 (failure mode / rollback)

## End-to-End Tests
**What user flows need validation?**

- [ ] Register/login.
- [ ] Create optional job description.
- [ ] Upload CV.
- [ ] Poll status in ProcessingPage.
- [ ] Redirect to ResultPageConnected on completion.
- [ ] Confirm history/dashboard show the new upload.
- [ ] Confirm failed upload displays `failure_reason`.

## Test Data
**What data do we use for testing?**

- Test fixtures and mocks
- Seed data requirements
- Test database setup

## Test Reporting & Coverage
**How do we verify and communicate test results?**

- Coverage commands and thresholds (`npm run test -- --coverage`)
- Coverage gaps (files/functions below 100% and rationale)
- Links to test reports or dashboards
- Manual testing outcomes and sign-off

## Manual Testing
**What requires human validation?**

- Keyboard and focus behavior for upload, retry, and table actions.
- Desktop and mobile layout for Dashboard, Processing, Result, History.
- Smoke tests after deployment against the active n8n workflow.

## Performance Testing
**How do we validate performance?**

- Load testing scenarios
- Stress testing approach
- Performance benchmarks

## Bug Tracking
**How do we manage issues?**

- Issue tracking process
- Bug severity levels
- Regression testing strategy

