# Delta Spec: platform — system-backups-s3

## ADDED Requirements

### Requirement: Database Backups to S3-Compatible Storage

The system MUST allow `admin` to generate PostgreSQL backups with `pg_dump -Fc` and upload them to an S3-compatible bucket. Non-admin roles MUST NOT access backup APIs or UI.

Object keys MUST use pattern `{prefix}clinica_backup_YYYYMMDD_HHMMSS.dump`. S3 settings MUST persist in `system_backup_config`. API MUST NOT re-expose `s3_secret_access_key`; responses MUST include `has_secret_access_key` instead.

While a backup is running, a second run MUST return **409**. Temp dump files MUST be deleted after success or failure.

#### Scenario: Manual backup OK

- GIVEN admin with valid S3 config
- WHEN `POST /api/v1/backups/run`
- THEN MUST dump with `pg_dump -Fc`, upload to bucket/prefix, log `success`, and remove temp file

#### Scenario: Manual backup failure

- GIVEN invalid S3 credentials
- WHEN backup runs
- THEN MUST log `failed` with error message and MUST NOT crash the API

#### Scenario: Concurrent run blocked

- GIVEN a backup already running
- WHEN admin triggers another
- THEN MUST respond 409

### Requirement: Scheduled Automated Backups

The system MUST support daily/weekly schedules via an in-process scheduler (APScheduler) in timezone `America/Argentina/Buenos_Aires`. Default MUST be **disabled** until an admin enables it. Scheduled runs MUST log `trigger_type=scheduled`.

#### Scenario: Scheduled run

- GIVEN enabled schedule at a configured time
- WHEN that time arrives
- THEN MUST run the same dump→upload→prune pipeline
- AND MUST record trigger `scheduled`

### Requirement: Backup Retention

After each successful upload, the system MUST keep only the last N backup objects under the configured prefix (default **N=15**, configurable). Oldest excess objects MUST be deleted from S3.

#### Scenario: Prune excess

- GIVEN more than N dumps under the prefix after a successful backup
- WHEN retention runs
- THEN MUST delete the oldest objects beyond N

### Requirement: Configuración UI (Backups)

The frontend MUST expose **Configuración** at `/configuracion` for `admin` only: manual “Realizar backup ahora”, editable schedule/S3/retention form, and backup history. Restore and dump download MUST NOT be offered in the UI.

#### Scenario: Admin opens Configuración

- GIVEN authenticated admin
- WHEN opens `/configuracion`
- THEN MUST see config (without secret value), status, and recent logs
- AND MAY save config and run a manual backup

#### Scenario: Non-admin denied

- GIVEN `rrhh` or `jefe_medico`
- WHEN navigates to `/configuracion` or calls backup APIs
- THEN MUST be denied (UI hidden / 403)

### Requirement: Ops restore documentation

Runbook MUST document restoring from a downloaded `.dump` via `pg_restore` on the VPS (CLI only). Go-live checklist MUST include validating an initial backup.
