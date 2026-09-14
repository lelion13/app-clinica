# Tasks: system-backups-s3

## Phase 1: Infrastructure

- [x] 1.1 Add `boto3` + `apscheduler` to `backend/requirements.txt`
- [x] 1.2 `backend/Dockerfile`: apt install `postgresql-client` (for `pg_dump`)
- [x] 1.3 Alembic `0027_system_backups`: `system_backup_config` + `system_backup_logs`; seed config `id=1` disabled, retention 15, prefix `clinica-backups/`
- [x] 1.4 Models `backend/app/models/backup.py` (+ export if needed)

## Phase 2: Backend

- [x] 2.1 Schemas `backend/app/schemas/backup.py` (config response masks secret; `has_secret_access_key`)
- [x] 2.2 `backup_service.py`: dump from `DATABASE_URL`, S3 upload, prune N, asyncio lock, logs
- [x] 2.3 `scheduler_service.py`: AsyncIOScheduler TZ `America/Argentina/Buenos_Aires`; reload on config save
- [x] 2.4 Router `backup.py` with `require_admin`; wire in `main.py` under `/api/v1/backups`
- [x] 2.5 Lifespan in `main.py`: start/shutdown scheduler

## Phase 3: Frontend

- [x] 3.1 `SettingsBackupPage.jsx`: form S3/schedule/retention, “Realizar backup ahora”, history table
- [x] 3.2 `navigation.js` + `AppLayout.jsx`: link **Configuración** (admin)
- [x] 3.3 `main.jsx`: route `/configuracion` with `adminOnly`

## Phase 4: Tests + docs

- [x] 4.1 `backend/tests/test_backups.py`: schemas, retention, mocked run, non-admin 403, concurrent 409
- [x] 4.2 `docs/runbook.md`: config S3 + CLI `pg_restore`; `docs/go-live-checklist.md`: backup inicial
