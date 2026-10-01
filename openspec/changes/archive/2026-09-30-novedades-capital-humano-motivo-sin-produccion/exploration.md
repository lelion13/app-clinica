# Exploration: novedades-capital-humano-motivo-sin-produccion

## Intent
Capital Humano must easily spot cargas tagged with `motivo_sin_produccion` (Vacaciones / Enfermedad) — the “novedad extra” / sin-producción path from Carga.

## Existing signals
- DB already has `motivo_sin_produccion` + `observacion_sin_produccion` on asignaciones and novedades
- Carga list shows them; CH Detalle Cargas and `GridRowResponse` / `export.xlsx` do **not** yet

## Closed decisions (see decisions.md)
- Select Motivo: Todos · Vacaciones · Enfermedad + button **Con novedad** → flat modal of matching cargas
- Grid: highlight matching professionals with one color (no hide rows; no motivo text on main grid)
- Detalle + export.xlsx: Motivo + Observación columns
- Modal follows Motivo select (Todos = any motivo)

## Likely touchpoints
- `GridRowResponse` + `export_xls` row builders / XLS headers
- `capital_humano` grid payload: flags for highlight (e.g. motivos present per professional)
- `NovedadesXlsPage.jsx`: select, highlight styles, modal, Detalle columns

## Survey
CLOSED
