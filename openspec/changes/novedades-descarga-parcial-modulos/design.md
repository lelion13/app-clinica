# Design: novedades-descarga-parcial-modulos

## Technical Approach

Extend existing `build_grid_rows` / `export.xlsx` with optional `fecha_desde`/`fecha_hasta` on `fecha_realizacion`. Capital Humano modal aggregates `/grilla` by professional for preview; download calls export with both dates → sheets **Resumen** + **Detalle**. Closed-period gate and date min/max stay UI-only.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| API | Extend grilla + export | New endpoints | Survey Q15=B |
| 2 sheets | Only when both date params set | Always 2 sheets | Preserve current export (Q16) |
| Preview aggregate | Client-side from `/grilla` | New summary API | Reuse; small payload per period |
| Legajo | Add `legajo` on `GridRowResponse` from `NovedadesProfesional` | Join only in export | Modal + Resumen need it |
| Closed period | UI only | API 422 | Survey Q17/Q20 |

## Data Flow

```
[CH closed] → Modal fechas (min/max período)
       → GET /grilla?periodo_id&fecha_desde&fecha_hasta
       → FE groupBy professional_id → {legajo, name, sum(valor), items[]}
       → Detalle expand = items of one row
       → GET /export.xlsx?...&fecha_desde&fecha_hasta
            → sheet Resumen + sheet Detalle
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/schemas/novedades.py` | Modify | `GridRowResponse.legajo` optional |
| `backend/app/services/novedades/export_xls.py` | Modify | Date filter in `_matches`; legajo on rows; 2-sheet export |
| `backend/app/api/routers/novedades.py` | Modify | Query `fecha_desde`/`fecha_hasta` on grilla + export |
| `frontend/.../NovedadesXlsPage.jsx` | Modify | Button, modal, accordion, download filename |
| `backend/tests/test_novedades_domain.py` (or new) | Modify/Create | Date filter + 2-sheet vs 1-sheet |
| `docs/runbook.md` | Modify | Brief CH note |

## Interfaces

```
GET /novedades/grilla?periodo_id&fecha_desde&fecha_hasta&...
GET /novedades/export.xlsx?periodo_id&fecha_desde&fecha_hasta&...
# Both dates → Content-Disposition may stay generic; FE saves as
# descarga-parcial-modulos_{desde}_{hasta}.xlsx
```

Resumen columns: `legajo`, `nombre`, `total_cargas`.  
Detalle: existing detail headers unchanged.

## Testing Strategy

| Layer | What |
|-------|------|
| Unit | `_matches` date inclusive; export 1 sheet without dates; 2 sheets with dates; empty range |
| Manual | Closed-only button; accordion; download filename |

## Migration / Rollout

No DB migration. Deploy FE+BE together so date params are understood.

## Open Questions

None — survey closed.
