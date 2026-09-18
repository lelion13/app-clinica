# Decisions: system-backups-s3

| # | Topic | Choice |
|---|--------|--------|
| Q1 | Alcance vs Almas | **A** — Paridad Almas (config DB, logs, scheduler, S3, UI; sin restore web) |
| Q2 | Quién puede usar | **A** — Solo `admin` |
| Q3 | UI | **A** — Nueva ruta `/configuracion` (solo admin) |
| Q4 | Destino storage | **A** — S3-compatible, credenciales en DB |
| Q5 | Bucket / prefix | **B** — Bucket nuevo dedicado a clinica (configurable en UI) |
| Q6 | Retención default | **A** — Últimos 15 dumps |
| Q7 | Schedule default | **A** — Deshabilitado hasta activación admin |
| Q8 | Nombre objetos | **A** — `clinica_backup_YYYYMMDD_HHMMSS.dump` |
| Q9 | Restore | **A** — Solo CLI/runbook; sin restore ni download en UI |
| Q10 | Secret S3 en API | **A** — No re-exponer; solo `has_secret_access_key` |
| Q11 | Concurrencia | **A** — `asyncio.Lock` + 409 si ya corre |
| Q12 | Change / dominio | **A** — `system-backups-s3` + dominio `platform` |
| Q13 | Deps backend | **A** — `boto3` + `apscheduler` + `postgresql-client` |
| Q14 | Tests / docs | **A** — Tests unitarios + runbook + go-live checklist |

## Survey status
CLOSED
