# Archive Report: limpiar-ui-obsoleta

## Change Summary
- **Change Name:** `limpiar-ui-obsoleta`
- **Target Spec:** `openspec/specs/distribucion/spec.md`
- **Archive Date:** 2026-10-19
- **Branch:** `agenda-ocupacion-segun-dia` (applied on current branch)
- **Revision:** `0033_drop_bookings_weekly`

## Delivered
1. Menú Distribución sin Ocupación semanal, Agenda (bookings) ni Estadística.
2. Páginas eliminadas; rutas legacy → Home.
3. APIs `/bookings`, `/weekly-assignments`, `/stats` desmontadas y código borrado.
4. Drop tablas `bookings` + `room_weekly_assignments`.
5. Profesionales / Ocupación / Agenda ocupación / Indicadores / Consultorios intactos.
6. Spec estable + runbook sincronizados.

## Specs synced
| Domain | Action | Details |
|--------|--------|---------|
| `distribucion` | Updated | REMOVED Estadística; MODIFIED menú Ocupación / Agenda ocupación / Indicadores; ADDED Retiro obsoletas. Traceability + README. |

## Verification
Usuario confirmó que el change quedó bien (2026-10-19).
