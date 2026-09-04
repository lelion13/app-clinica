# Design: novedades-capital-humano-importe-descontar

## Technical Approach

Reuse `NovedadesAjusteCapital` + soft-delete. Tag import rows with `descuento_lote_id` (UUID). Parse Excel like `modulos_import` (openpyxl, all-or-nothing HTTP 400 with `errors[]`). Allocate via waterfill against CH grid totals (cargas por servicio + producción valorizada).

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Persistence | `descuento_lote_id` UUID nullable on ajuste | Separate table / comment marker | Anular preciso; Detalle/grilla unchanged |
| Cap / totals | Reuse `build_capital_humano_rows(..., include_bonos=True)` + cargas from `build_grid_rows` | Recompute producción | Same numbers as UI |
| Active lot | Any non-deleted ajuste with non-null `descuento_lote_id` for período | Separate lot table | One query; Anular sets deleted_at |
| Liquidación | Apply ajuste to servicio’s `concepto_liquidacion` when `servicio_id` set; else equal split | Keep equal-only | Preserves waterfill |
| Errors | `HTTP 400` detail `{message, errors:[{row, reason}]}` | 422 mixed | Matches módulos import UX |

## Data Flow

```
UI file ─POST─→ /capital-humano/importe-descontar?periodo_id=
                      │
              validate closed + no active lot
                      │
              parse XLS → validate all rows
                      │
         fail? ──→ 400 + modal (no commit)
                      │
              waterfill → insert ajustes (same lote UUID)
                      │
UI Anular ─POST─→ soft_delete where descuento_lote_id IS NOT NULL
```

## API

- `GET /novedades/capital-humano/importe-descontar/status?periodo_id=` → `{has_descuento: bool}`
- `POST /novedades/capital-humano/importe-descontar?periodo_id=` multipart `file` → `{created: int, lote_id: uuid}`
- `POST /novedades/capital-humano/importe-descontar/anular?periodo_id=` → `{deleted: int}`
- Auth: `require_admin_or_rrhh`; período MUST be `closed`

## File Changes

| File | Action |
|------|--------|
| `alembic/versions/0025_ajuste_descuento_lote.py` | Create |
| `backend/app/models/novedades.py` | Add column |
| `backend/app/services/novedades/importe_descontar.py` | Create |
| `backend/app/services/novedades/liquidacion_export.py` | servicio_id mapping |
| `backend/app/schemas/novedades.py` | Response/error schemas |
| `backend/app/api/routers/novedades.py` | Endpoints |
| `frontend/.../NovedadesXlsPage.jsx` | Button + modal |
| `backend/tests/test_importe_descontar.py` | Create |
| `docs/runbook.md` | Document |

## Waterfill (service)

```
services = [(sid, cargas_sid)] sorted by cargas desc
remaining = abs_discount
for each except last: take min(remaining, cargas_sid); remaining -=
last gets remaining (may exceed its cargas if within prod headroom)
```

Projected total general = `monto_cargas + monto_ajustes_existentes + monto_bonos - abs_discount` (existentes exclude nothing special; new discount not yet in DB).

## Testing

| Layer | Focus |
|-------|--------|
| Unit | Headers, signo, waterfill, tope, duplicados, liquidación con servicio_id |
| API | Closed-only, active-lot block, anular leaves manual |

## Migration

Add nullable `descuento_lote_id` UUID (indexed). No backfill. Rollback: drop column.
