# Proposal: novedades-modulos-tipo-dia

## Intent

Replace module boolean `sadofe` with exclusive `tipo_dia` (`semana` | `sadofe` | `valor_unico`) so Carga can show modules for Semana, SADOFE, or any day (valor único), without breaking existing modules/cargas.

## Scope

### In Scope
- DB: add `tipo_dia`, backfill from `sadofe`, drop `sadofe`.
- API/schemas: `tipo_dia` only; remove `sadofe`.
- Param UI: three exclusive checks (Semana · SADOFE · Valor único); default Semana; delete modal shows Tipo día.
- Carga: filter by `tipo_dia` + fecha (valor_unico always).
- Excel plantilla/import: `tipo_dia` column; empty→semana; invalid→error all-or-nothing.
- Specs + runbook + tests.

### Out of Scope
- Backend date vs tipo validation on assign (stays UI-only).
- Changing feriados / producción flags.
- Capital Humano.

## Approach

Alembic migrate → update model/schemas/masters/import → Param + Carga UI → tests.

## Risks

| Risk | Mitigation |
|------|------------|
| FE/BE deploy mismatch | Ship together; no dual `sadofe` |
| Old Excel with `sadofe` column | Document new plantilla; missing `tipo_dia`→semana |

## Success Criteria

- [x] Existing modules map correctly (false→semana, true→sadofe).
- [x] Carga shows valor_unico on any day; semana/sadofe as before.
- [x] Param exclusivity + import `tipo_dia` work.
- [x] No `sadofe` in API responses.
