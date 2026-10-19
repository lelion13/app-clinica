# Archive Report: agenda-ocupacion-segun-dia

## Change Summary
- **Change Name:** `agenda-ocupacion-segun-dia`
- **Target Spec:** `openspec/specs/distribucion/spec.md`
- **Archive Date:** 2026-10-19
- **Branch:** `agenda-ocupacion-segun-dia`
- **Revision:** `0032_agenda_map_weekday`

## Delivered
1. Mapa persistente `(id_agenda, weekday)` → `room_id`; migración expand desde 1:1.
2. Agenda ocupación: DnD / unassign solo weekday del calendario; validación ese día; orden numérico; scroll H + auto-scroll; Sin consultorio sticky condicional.
3. Consultorios → Agendas: solo días pendientes; todo-o-nada + conflicto; labels full vs `nombre - día`.
4. Events e indicadores resuelven room por weekday del bloque.
5. Tests unitarios reassign / room_agenda_map / indicadores; runbook.
6. Fix migración prod: drop PK antes de expand (UniqueViolation en VPS 2026-10-18).

## Specs synced
| Domain | Action | Details |
|--------|--------|---------|
| `distribucion` | Updated | MODIFIED: Mapeo; UI Consultorios; UI Agenda; Reassign; Validación; Confirmaciones. Traceability + README. |

## Learned
Al expandir 1→N filas bajo la misma clave lógica, dropear la PK/unique vieja **antes** de los INSERT; documentado en `design.md` y `docs/runbook.md`.

## Verification
- Unit tests OK en apply.
- Usuario: `alembic upgrade head` OK en VPS tras fix PK (2026-10-19).
