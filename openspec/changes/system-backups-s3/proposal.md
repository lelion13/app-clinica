# Proposal: system-backups-s3

## Intent

Add admin database backups for app-clinica, replicating app-Almas `system-backups-s3`: manual + scheduled `pg_dump -Fc` uploads to S3-compatible storage with retention and execution history. Clinica today has no automated backup path.

## Scope

### In Scope
- Backend: `boto3`, APScheduler, `postgresql-client` in backend image; tables `system_backup_config` + `system_backup_logs`.
- Pipeline: `pg_dump -Fc` → temp → S3 upload → prune last N → log → delete temp; in-memory lock (409 if busy).
- API admin-only: `GET/PUT /backups/config`, `POST /backups/run`, `GET /backups/status`, `GET /backups/logs`.
- UI `/configuracion` (admin): run now, schedule/S3 form, history; secret never re-echoed (`has_secret_access_key`).
- Defaults: schedule **disabled**; retention **15**; object name `clinica_backup_YYYYMMDD_HHMMSS.dump`; dedicated clinica bucket (UI-configured).
- Docs: runbook restore CLI + go-live checklist; unit tests.
- OpenSpec domain **`platform`** (new).

### Out of Scope
- Restore or download via UI.
- Hostinger/OS cron (scheduler is in-process).
- Sharing Almas bucket (dedicated clinica bucket).
- Non-admin roles (`rrhh` / `jefe_medico`).

## Approach

Port Almas design adapted to clinica stack (JSX nav, roles, alembic rev next). Config singleton in DB; scheduler starts on FastAPI lifespan and reschedules on config save. TZ schedule: `America/Argentina/Buenos_Aires`.

## Risks

| Risk | Mitigation |
|------|------------|
| Backend image lacks `pg_dump` | Install `postgresql-client` in Dockerfile |
| Wrong S3 config | Failed run logged; no crash |
| Multi-replica lock | In-memory OK for current single backend |

## Success Criteria

- [x] Admin can configure S3 + run manual backup successfully. *(code ready; validate on VPS after bucket)*
- [x] Scheduled backups run when enabled; default off.
- [x] Retention keeps last 15 objects under prefix.
- [x] Non-admin cannot access APIs/UI.
- [x] Runbook documents `pg_restore` CLI path.
