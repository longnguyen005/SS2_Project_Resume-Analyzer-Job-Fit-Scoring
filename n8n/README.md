# n8n Workflows

## Current status

Available workflow exports:

- `workflows/cv-analysis-skeleton.json`
- `workflows/cv-analysis-http-pipeline-staged.json`

Source of truth:

- `cv-analysis-http-pipeline-staged.json` is the canonical workflow export for the workerized pipeline.
- `cv-analysis-skeleton.json` is only for webhook smoke-testing and should not be treated as the production pipeline.
- The exported JSON is intentionally stored with `active: false`; after import, activate it inside n8n for the target environment.

Runtime contract assumptions:

- FastAPI triggers `POST /webhook/analyze-cv` on n8n after a successful upload.
- The active runtime uses the staged workerized flow, not the legacy `/prepare`-style exports.
- Default timeout and retry expectations are owned by `docker-compose.yml` + `backend/app/core/config.py`, not by ad-hoc edits in the n8n UI.
- R2 is optional in the default contract; the staged workflow must still work with local uploads when `R2_ENABLED=false`.

## What it does

- `cv-analysis-skeleton.json`
  - Receives `POST /webhook/analyze-cv`
  - Normalizes the incoming payload from FastAPI
  - Returns a simple JSON acknowledgement so backend integration can be tested

- `cv-analysis-http-pipeline-staged.json`
  - Current recommended workflow export
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
4. Keep the skeleton workflow disabled unless you are doing a webhook-only smoke test.

## Validation notes

- If runtime behavior drifts from this export, re-export the active workflow back into `workflows/cv-analysis-http-pipeline-staged.json`.
- Do not treat a manually edited UI-only workflow as the new source of truth unless it has been exported back into the repository.
