# Archive Report: system-backups-s3

## Change Summary
- **Change Name:** `system-backups-s3`
- **Target Spec:** `openspec/specs/platform/spec.md` (created)
- **Archive Date:** 2026-09-14

## Delivered
1. Admin `/configuracion`: manual + scheduled `pg_dump -Fc` → S3-compatible storage.
2. Retention last 15; object `clinica_backup_YYYYMMDD_HHMMSS.dump`; dedicated clinica bucket.
3. Migration `0027_system_backups`; `postgresql-client` in backend image.
4. Restore documented as CLI `pg_restore` only (no UI restore/download).

## Specs synced
| Domain | Action | Details |
|--------|--------|---------|
| `platform` | Created | All ADDED backup requirements from delta |

## Verification
User-tested OK (2026-09-14).
