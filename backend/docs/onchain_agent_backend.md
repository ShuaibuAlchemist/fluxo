# On-chain Analyst Agent — Backend Modules (source: data_pipeline/)

This document describes the backend modules used by the On-chain Analyst agent and clarifies the role of the `data_pipeline/` folder as the canonical source for precomputed pipeline outputs.

Summary (one-liner)
- The On-chain Analyst is using normalized, precomputed outputs from `data_pipeline/` which are save to the database and then pulled up by any related agents from the database

Why `data_pipeline/` is the source
- The `data_pipeline/` directory contains ingestion and transformation jobs that produce denormalized datasets (e.g., historical balances, aggregated transfers,) optimized for analysis and reports.
- Using `data_pipeline/` outputs gives deterministic, repeatable, and faster analyses because heavy aggregation and joins are done once at ingestion time.
- When data freshness is less critical (e.g., historical analysis, backtests, batch alerts), prefer `data_pipeline/` outputs.

Key modules & responsibilities

- `data_pipeline/`
  - Purpose: Ingestion and transformation. Example tasks: fetch historical transfers, enrich with token metadata, compute time-series of TVL for a wallet or protocol, aggregate transfers into flows.
  - Outputs: database/function call
  - Location: `fluxo/backend/data_pipeline/` (run these via scheduled jobs)

- `fluxo/backend/agents/`
  - Purpose: Implement analysis business logic. The On-chain agent orchestrates calls to either the pipeline outputs or services, computes signals/alerts, and returns typed JSON results.
  - Recommendation: some Agents should load data from database and not from the source

- `fluxo/backend/tasks/`
  - Purpose: Celery tasks that run agents asynchronously, persist results (Redis/DB), and update progress/state.
  - Pattern: Agents are side-effect free; Celery tasks call agents and handle persistence and failure-state reporting.

- `fluxo/backend/api/`
  - Purpose: FastAPI endpoints that enqueue tasks and expose task status/results.
  - Pattern: POST to enqueue (return `task_id`); GET to poll status and return stored result when ready.



Practical runbook
1.start the pipline with celery beat to run on schedule
2. Start the API server (from repo root) and a Celery worker. Example commands:

```bash
# in repo root
uvicorn main:app --reload --host 0.0.0.0 --port 8000
celery -A core.celery_app worker --loglevel=info
```

### Starting the pipeline celery beat
```bash
# In the repo root
celery -A core.celery_app beat --loglevel=info
```