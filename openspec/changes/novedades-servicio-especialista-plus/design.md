# Design: novedades-servicio-especialista-plus

## Technical Approach

Add `novedades_servicio.especialista` (bool, default false). Gate `modulo_valor_para_profesional` with `servicio_especialista`. Create uses both flags; update stops applying plus. Grilla exposes `plus_especialista` bool for CH Detalle column (computed vs catalog×1.20).

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Column name | `especialista` | Matches UI label |
| Update valor | No plus; modulo change → catalog only | Survey Q3 |
| Detalle signal | `plus_especialista` on `GridRowResponse` | Avoid FE catalog lookup |
| Hist recalc | Out of scope | Survey Q1 |

## File Changes

| File | Action |
|------|--------|
| alembic `0028_servicio_especialista` | Create |
| model/schemas/masters/router response | Modified |
| `prof_sync.modulo_valor_para_profesional` | Modified signature |
| `cargas` create/update | Modified |
| `export_xls` asignacion row | Set `plus_especialista` |
| Param + Xls Detalle | Modified |
| tests + runbook | Modified |

## Testing

Unit: valor matrix (prof×servicio); update keeps valor; plus_especialista inference; servicio default false.
