# Exploration: system-backups-s3 (app-clinica)

## Intent

Replicate app-Almas archived change `system-backups-s3` (2026-08-30): admin-triggered + scheduled `pg_dump -Fc` → S3-compatible storage with retention and logs.

## Current State (clinica)

- Prod DB: `app-clinica-db` (`postgres:16`), volume `pgdata`, no host port.
- No backup scripts, cron, S3 config, or openspec backup domain.
- Backend image likely lacks `postgresql-client` (Almas added it for `pg_dump` in API container).
- Roles: `admin`, `rrhh`, `jefe_medico` (Almas was admin-only for backups).
- No `/configuracion` page yet.

## Reference (app-Almas)

- Archive: `app-Almas/openspec/changes/archive/2026-08-30-system-backups-s3/`
- Pipeline: `pg_dump -Fc` → temp → boto3 upload → prune last N → `system_backup_logs`
- Scheduler: APScheduler in FastAPI lifespan (daily/weekly)
- Config in DB singleton `system_backup_config` (not env)
- UI: `/configuracion` “Realizar backup ahora” + form + history
- Out of scope there: restore via UI

## Approaches

1. **Clone Almas pattern** — same tables/API/UI/scheduler/S3 — Pros: proven; Cons: need clinica nav/roles fit
2. **Host cron + volume only** — Pros: simple; Cons: diverges from Almas; no UI/history
3. **Env-only S3 + script** — Pros: no DB secrets; Cons: no Almas parity

**Recommendation:** Approach 1, with survey below for clinica-specific deltas.

## Risks

- Backend without `pg_dump` until Dockerfile change
- S3 secrets in DB (same as Almas)
- Multi-replica lock is in-memory only (clinica is single backend today)
- Restore undocumented beyond CLI (acceptable if same as Almas)

## Survey status

CLOSED (Q1–Q14). Proposal + delta `platform` written. Ready for design/tasks.
