# Design: locations.tipo (retroactivo)

## Technical Approach

Ampliar modelo Location con `tipo`; unique parcial PostgreSQL `(id_dominio, tipo) WHERE deleted_at IS NULL`. Agenda resuelve ubicación y filtra por par. Migración backfill placeholders.

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Unique `(id_dominio, tipo)` no solo dominio | Un dominio = muchas sedes/tipos en API ocupación |
| tipo required en API | Evitar filas sin vínculo usable |
| Placeholder `PENDIENTE-{id}` | Migra sin bloquear; editable en UI |
| Match agenda `casefold` | Datos externos inconsistentes en mayúsculas |
| Split nombre: `" - "` luego `-` | API mezcla formatos espaciados y compactos |

## File-Level Changes

Ver `proposal.md` Affected Areas. Tests: `test_location_tipo.py`, casos en `test_agenda_ocupacion.py`.
