# Design: system-backups-s3

## Technical Approach

Port Almas backup subsystem into clinica: `pg_dump -Fc` → temp → boto3 S3 upload → prune last N → `system_backup_logs`. APScheduler in FastAPI lifespan; admin UI at `/configuracion`. Dedicated clinica bucket (UI-configured); default prefix `clinica-backups/`; object `clinica_backup_YYYYMMDD_HHMMSS.dump`.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Dump | `pg_dump -Fc` | `.sql.gz` | Same as Almas; `pg_restore` friendly |
| Storage | boto3 S3-compatible | Local volume | Survey Q4; R2/AWS/MinIO |
| Scheduler | APScheduler `AsyncIOScheduler` | Host cron | Survey Q1; no extra infra |
| Lock | `asyncio.Lock` + 409 | DB lock | Survey Q11; single backend |
| Auth | `require_admin` | admin+rrhh | Survey Q2 |
| Secrets | Mask; `has_secret_access_key` | Echo secret | Survey Q10 |
| Spec domain | New `platform` | Under novedades | Survey Q12 |

## Data Flow

```
Admin UI / APScheduler
        │
        ▼
BackupService.run_backup(trigger) ── lock
  → pg_dump -Fc → /tmp/clinica_backup_*.dump
  → S3 upload ({prefix}clinica_backup_YYYYMMDD_HHMMSS.dump)
  → prune to retention_count (default 15)
  → system_backup_logs + cleanup temp + unlock
```

## Schema (Alembic `0027_system_backups`)

**`system_backup_config`** (singleton `id=1`): `enabled` default false; `schedule_type` daily|weekly; `schedule_time`; `schedule_day_of_week` nullable; S3 endpoint/bucket/region/keys/prefix (default `clinica-backups/`); `retention_count` default 15.

**`system_backup_logs`**: UUID id; `trigger_type` manual|scheduled; `status` running|success|failed; file_name, size, storage_key, duration, error_message, started_at, completed_at.

## File Changes

| File | Action |
|------|--------|
| `backend/Dockerfile` | Add `postgresql-client` via apt |
| `backend/requirements.txt` | `boto3`, `apscheduler` |
| `backend/alembic/versions/0027_system_backups.py` | Create tables + seed config row |
| `backend/app/models/backup.py` | ORM |
| `backend/app/schemas/backup.py` | Pydantic |
| `backend/app/services/backup_service.py` | Dump/upload/prune/lock |
| `backend/app/services/scheduler_service.py` | CronTrigger, reload on save |
| `backend/app/api/routers/backup.py` | `/api/v1/backups/*` + `require_admin` |
| `backend/app/main.py` | Lifespan start/stop scheduler; include router |
| `frontend/src/pages/SettingsBackupPage.jsx` | Config + run + logs |
| `frontend/src/config/navigation.js` | `CONFIG_NAV_ITEM` admin |
| `frontend/src/layouts/AppLayout.jsx` | Link Configuración |
| `frontend/src/main.jsx` | Route `/configuracion` adminOnly |
| `backend/tests/test_backups.py` | Schemas, lock/retention mocks, 403 |
| `docs/runbook.md`, `docs/go-live-checklist.md` | Setup + `pg_restore` CLI |

## Interfaces

```
GET/PUT  /api/v1/backups/config
GET      /api/v1/backups/status
POST     /api/v1/backups/run
GET      /api/v1/backups/logs
```

Schedule TZ: `America/Argentina/Buenos_Aires`. Parse DB creds from `DATABASE_URL` for `PGPASSWORD` + `pg_dump`.

## Testing Strategy

| Layer | What |
|-------|------|
| Unit | Schemas, retention prune list, prefix/filename helpers |
| API | Admin OK; non-admin 403; concurrent 409 (mocked dump/S3) |
| Docs | Runbook restore steps |

## Migration / Rollout

1. Deploy BE image with `postgresql-client` + FE together.
2. `alembic upgrade head` (`0027`).
3. Admin creates clinica bucket in R2/S3, fills `/configuracion`, runs manual backup.
4. Enable schedule only after first success.

## Open Questions

None — survey closed.
