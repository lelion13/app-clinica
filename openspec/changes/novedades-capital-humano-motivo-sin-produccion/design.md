# Design: novedades-capital-humano-motivo-sin-produccion

## Technical Approach

Surface existing `motivo_sin_produccion` / `observacion_sin_produccion` on grilla + export; derive per-professional motivo flags on capital-humano rows for highlight. UI: Motivo select + row color + **Con novedad** modal from `/grilla` filtered client-side.

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Highlight data | `motivos_sin_produccion: list[str]` on `CapitalHumanoRowResponse` | Compact; FE matches select |
| Modal data | Reuse `GET /grilla?periodo_id` + filter FE | No new endpoint |
| Labels XLS | Human labels Vacaciones/Enfermedad via `MOTIVO_SIN_PRODUCCION_LABELS` | Match Carga UI |
| Highlight color | One CSS/background token | Survey Q14 |

## Data Flow

```
cargas (asignacion|novedad with motivo)
  → GridRowResponse.motivo_* 
  → CH row.motivos_sin_produccion (unique)
  → FE: select → highlight if intersection; modal = grilla rows with motivo match
```

## File Changes

| File | Action |
|------|--------|
| `schemas/novedades.py` | `GridRowResponse` + `CapitalHumanoRowResponse` fields |
| `export_xls.py` | Map fields; XLS columns motivo/observacion |
| `capital_humano.py` | Collect motivos while aggregating cargas |
| `NovedadesXlsPage.jsx` | Select, highlight, modal, Detalle cols |
| tests + runbook | Cover + note |

## Testing Strategy

Unit: row builders include motivo; export headers; CH flags from stubbed grid rows. Manual: select/highlight/modal/Detalle.

## Migration

None — columns already exist.
