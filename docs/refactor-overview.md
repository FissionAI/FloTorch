### FloTorch refactor – end‑to‑end overview (for any level)

This document explains what we changed, why we changed it, and how the pieces fit together so you can reason about the system and operate it confidently.

## 1) What we started with and the goals

The repo bundled “local core” code in folders like `core/`, `indexing/`, `retriever/`, `evaluation/`. This made it hard to:

- **swap storage engines**: DynamoDB vs PostgreSQL
- **reuse external services**
- **keep dependencies consistent**

Frontend and backend routing were misaligned (missing `/api` prefix). Startup assumptions about S3/OpenSearch could crash local dev.

You asked to:

- **remove local core** in favor of external packages/services
- **replace DynamoDB with PostgreSQL** (but still support migration/cutover)
- **support OpenSearch**
- **keep everything running on Windows/PowerShell** “from scratch”
- **do it carefully, incrementally, with rollback**

## 2) What we changed (the big pieces)

- **Removed active dependency on local `core/`** and replaced with:
  - `flotorch_core` (where generic storage clients exist)
  - thin app‑level adapters (where app specifics are needed)
  - HTTP adapters for external microservices (if used later)
- **Added full PostgreSQL integration** (app‑level schema + connection + migrations) and production‑style cutover controls:
  - backfill from DynamoDB
  - shadow reads
  - dual writes
  - full cutover / rollback
- **Reworked OpenSearch integration** to be reliable for Docker‑based local dev, removing brittle/local dependencies.
- **Hardened startup** (CSV/S3 fallbacks, guardrail fixes, `/api` route prefix).
- **Added optional docker‑compose** for Postgres and OpenSearch.
- **Left background sync/reindex as optional** (you can enable when needed).

## 3) Where the new code lives and why

### PostgreSQL schema and app glue

- `app/database/models.py`: defines your app’s tables (SQLAlchemy).
  - Experiment → `experiments`
  - Execution → `executions`
  - QuestionMetrics → `question_metrics`
  - ModelInvocations → `model_invocations`
  - Note: SQLAlchemy reserves `metadata`, so model field is `metadata_json` mapped to DB column `metadata`.
- `app/database/connection.py`: pooled DB engine + session management.
- `app/database/init_db.py`: simple create/drop helpers.
- `app/adapters/postgres_adapter.py`: app‑specific CRUD, maps logical table names to your models and returns dicts. This is glue that `flotorch_core` (a generic library) cannot provide because it doesn’t know your app schema.

### DB routing and lifecycle (one place to change behavior)

- `app/dependencies/database.py`:
  - `DBClientFactory` chooses the DB client per table:
    - If `ENABLE_DUAL_WRITES=true` → always `DualWriteAdapter` (Postgres primary + DynamoDB mirror).
    - Else if `DB_TYPE=POSTGRESDB` → use `flotorch_core`’s PostgresDB first; if that fails (e.g., config import), fall back to our `PostgresAdapter`.
    - Else if `DB_TYPE=DYNAMODB` → `flotorch_core`’s DynamoDB client.
  - Dependency generator `get_db_dependency(...)` yields a client per request and closes connections on exit.

### Migration + cutover (move safely from DynamoDB to Postgres)

- `app/migration/data_migrator.py`: scans DynamoDB (via boto3), transforms item shapes, inserts into Postgres models.
- `app/migration/migration_manager.py`: shadow reads (compare Postgres vs DynamoDB), basic counters, incremental hooks.
- `app/adapters/dual_write_adapter.py`: writes to Postgres and mirrors to DynamoDB using a minimal boto3 wrapper. Avoids the removed local core. Postgres remains the write “source of truth” in dual‑write mode.
- Routes to drive this:
  - `app/routes/migration.py`: run full migration; shadow reads; status.
  - `app/routes/cutover.py`: enable/disable dual writes; switch reads to Postgres; full cutover; rollback.

### OpenSearch (clean adapter for Docker dev)

- `app/adapters/opensearch_adapter.py`: now uses `opensearch-py` directly (no local core or forced `flotorch_core` dependency). Works with Docker OpenSearch at `http://localhost:9200` (no security).
- `app/routes/opensearch_admin.py`:
  - `GET /api/opensearch/health` → calls `client.info()` and returns OK.
  - `POST /api/opensearch/bootstrap` → currently validates connection; you can wire actual index creation later.
- `opensearch/opensearch_index_manager.py`: kept as a helper; if you use it, it already depends on the adapter.

### Orchestration and external services (flexible control)

- `app/adapters/orchestrator_adapter.py`: orchestrates via AWS Step Functions (default), or “direct” calls via adapters if you flip a flag.
- Service adapters (future‑proofing):
  - `RetrieverAdapter`, `IndexerAdapter`, `EvalAdapter` call either local implementations or external microservices via `HTTPServiceAdapter`.
  - This isolates your API from implementation (local vs external).

### Stability and developer experience hardening

- `/api` route prefix unified in `app/main.py`.
- S3 price CSV fallbacks so startup doesn’t crash without AWS.
- PyMuPDF (fitz) made optional (Windows DLL issues) with a `PyPDF2` fallback in `util/pdf_utils.py`.
- `docker-compose.yml` to run Postgres and OpenSearch locally:
  - Postgres published on 5432, OpenSearch on 9200.
  - `DISABLE_INSTALL_DEMO_CONFIG=true` prevents OpenSearch security init from blocking startup.

## 4) How the pieces link together (logical flow)

### Backend request flow (DB)

Your API route uses a dependency like `get_execution_db()`.

That dependency calls `DBClientFactory` with `DB_TYPE` + flags and builds:

- `DualWriteAdapter` (if dual writes on), or
- `flotorch_core` client for `POSTGRESDB`/`DYNAMODB`, or fallback to
- `PostgresAdapter` (app‑specific).

The route uses the returned client (same interface) to CRUD data.

### Migration/cutover

1. Start with DynamoDB as “old” store (if you have data there).
2. Run backfill (`/api/migration/run`) to Postgres.
3. Use shadow reads to compare results.
4. Enable dual writes (`/api/cutover/enable-dual-writes`) to keep both in sync.
5. Move reads to Postgres (`/api/cutover/enable-postgres-reads`).
6. When confident, disable dual writes and set `DB_TYPE=POSTGRESDB`.

### Search (OpenSearch)

Adapter connects to Docker OpenSearch on `localhost:9200`.

- Health route verifies connectivity.
- When ready, wire bootstrap to create indices (either from experiments configs or a known schema), then index your content.

### Orchestration

By default, Step Functions run experiments (region, ARN from config).

If needed, orchestrator can call local/external services via adapters instead.

## 5) Environments and variables (the minimum to run locally)

### Backend (PowerShell)

Activate venv:

```powershell
..\.venv\Scripts\Activate.ps1
```

Basic envs:

- **AWS**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` (valid session).
- **DB**: `DB_TYPE=POSTGRESDB`, plus:
  - `POSTGRES_HOST=localhost`, `POSTGRES_PORT=5432`, `POSTGRES_DB=flotorch`, `POSTGRES_USER=flotorch`, `POSTGRES_PASSWORD=flotorch`
- **S3**: `s3_bucket=flotorch-bucket` (or a known bucket; CSV fallbacks prevent crashes)
- **OpenSearch**:
  - `opensearch_host=localhost`, `opensearch_serverless=false` (Docker), no credentials by default because we disabled security.

Start:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker local services (in repo root)

```powershell
docker compose up -d
```

- Postgres: `localhost:5432`
- OpenSearch: `http://localhost:9200` (no auth)

### Frontend

Set `ui/.env`:

```
NUXT_API_ENDPOINT=http://localhost:8000/api
```

Run:

```powershell
cd ui
npx --yes pnpm@9.14.4 install
npx --yes pnpm@9.14.4 dev --port 3000
```

## 6) What we removed and why

We removed runtime usage of local `core/` code because:

- It conflicted with external packages and made refactor brittle.
- It blocked swapping to Postgres and to Docker OpenSearch cleanly.

We kept a backup of the legacy folders and added cleanup routes (backup/restore/remove) so you had a reversible path.

## 7) How this improves things

- **Clear boundaries**: App schema and CRUD (your models) vs. generic storage engines (`flotorch_core`) vs. adapters/public APIs (your FastAPI routes).
- **Maintainability**: All DB switching logic centralized in `DBClientFactory`.
- **Feature flags**: Isolate risky behaviors (dual writes, direct orchestration).
- **Developer experience**: Docker services predictable, optional security complications removed for local. S3 and PyMuPDF fallbacks prevent “works on my machine” blockers.

## 8) Current “truth” and what’s optional

**Current truth:**

- Postgres is the primary store (`DB_TYPE=POSTGRESDB`).
- Dual writes off (simpler). You can turn it on to mirror to DynamoDB.
- OpenSearch adapter uses `opensearch-py` directly; Docker OpenSearch health is green.
- Frontend and backend are aligned on `/api`.

**Optional next:**

- Index bootstrap/reindex endpoints (build indices from configs or DB).
- Background sync job from Postgres to OpenSearch.
- CI/dev docker-compose smoke tests.
- Documentation/runbooks (cutover/rollback steps curated for the team).

## 9) How to reason about it in one picture (textual)

```
API routes → dependencies in app/dependencies/database.py → client chosen by DBClientFactory:
  Dual writes on? → DualWriteAdapter (Postgres + DynamoDB via boto3 wrapper).
  Else DB_TYPE=POSTGRESDB? → flotorch_core PostgresDB or fallback PostgresAdapter.
  Else DB_TYPE=DYNAMODB? → flotorch_core DynamoDB.

Search routes → OpenSearchAdapter → opensearch-py → Docker OpenSearch.
Orchestrator → Step Functions (default) or direct adapters (optional).
```

## 10) If something goes wrong (quick playbook)

- **“No module named core”** → means some path still tries to import removed local core. We eliminated these in adapters and routes. If you see it again, confirm:
  - Restart backend after changes,
  - Ensure env `USE_FLOTORCH_CORE` is not forcing a path, and
  - The adapter is the new version (it now uses opensearch-py only).
- **“OpenSearch not reachable”** → Docker OpenSearch not up:
  - `docker ps`, `docker logs flotorch-opensearch`, confirm `http://localhost:9200` responds.
  - We disabled demo security and bound port 9200.
- **“PyMuPDF DLL” on Windows** → we auto‑fallback to PyPDF2. Nothing to fix unless you want PyMuPDF.
- **“DB connection error”** → verify envs for Postgres; check container health.



