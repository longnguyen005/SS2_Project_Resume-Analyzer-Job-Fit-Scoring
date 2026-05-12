# n8n Workflows

## Current status

Available workflow exports:

- `workflows/cv-analysis-http-pipeline-staged.json`

Source of truth:

- `cv-analysis-http-pipeline-staged.json` is the only canonical workflow export for the workerized pipeline.
- Historical skeleton/smoke-test exports were removed because they use the same webhook path and can be imported by mistake.
- The exported JSON is intentionally stored with `active: false`; after import, activate it inside n8n for the target environment.

Runtime contract assumptions:

- FastAPI triggers `POST /webhook/analyze-cv` on n8n after a successful upload.
- The active runtime uses the staged workerized flow, not the legacy `/prepare`-style exports.
- Default timeout and retry expectations are owned by `docker-compose.yml` + `backend/app/core/config.py`, not by ad-hoc edits in the n8n UI.
- Worker URLs in the export assume `API_V1_PREFIX=/api/v1`; update and re-export the workflow if that prefix changes.
- R2 is optional in the default contract; the staged workflow must still work with local uploads when `R2_ENABLED=false`.

## What it does

- `cv-analysis-http-pipeline-staged.json`
  - Current runtime workflow export
  - Starts with a `claim` step to make repeated webhook executions idempotent
  - Splits the worker path into `extract -> validate -> analyze -> complete/fail`
  - Uses the dedicated `file-worker` service for `extract/validate`
  - Uses the dedicated `ai-worker` service for `analyze`
  - Uses the dedicated `persistence-worker` service for `complete`
  - Uses backend helper endpoints for `claim` and `fail`
  - Adds per-stage timeout and retry policy for the HTTP worker nodes
  - Keeps validation failures mapped to the `extract` stage, so frontend progress stays consistent with the 3-step UI
  - Replaces the older `/prepare`-based pipeline exports, which have been removed

## Next step

For Week 11 and later, the intended runtime setup is:

- FastAPI upload route triggers n8n
- n8n orchestrates `claim -> extract -> validate -> analyze -> complete/fail`
- `file-worker` exposes the extraction and validation primitives
- `ai-worker` exposes the AI analysis primitive
- `persistence-worker` exposes the DB persistence primitive
- backend helper endpoints currently expose the claim and fail primitives

## Import checklist

1. Import `workflows/cv-analysis-http-pipeline-staged.json` into n8n.
2. Confirm the webhook path is still `analyze-cv`.
3. Activate the workflow after import.
4. If you change the workflow in the n8n UI, re-export it back to this same file before committing.

## Validation notes

- If runtime behavior drifts from this export, re-export the active workflow back into `workflows/cv-analysis-http-pipeline-staged.json`.
- Do not treat a manually edited UI-only workflow as the new source of truth unless it has been exported back into the repository.
- Do not commit local n8n database files or temporary active-workflow exports.
