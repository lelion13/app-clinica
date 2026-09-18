# Tasks: novedades-descarga-parcial-modulos

## Phase 1: Backend filters + export

- [x] 1.1 Add optional `legajo` to `GridRowResponse`; set it in `_asignacion_row` / `_novedad_row` from `NovedadesProfesional`
- [x] 1.2 `build_grid_rows` + `_matches`: optional `fecha_desde`/`fecha_hasta` on `fecha_realizacion` (inclusive); wire query params on `GET /grilla`
- [x] 1.3 `export_xlsx_bytes` + `GET /export.xlsx`: same date params; if both set → sheets `Resumen` + `Detalle`; else single sheet as today

## Phase 2: Capital Humano UI

- [x] 2.1 Button **Descarga parcial de módulos** after liquidación; disabled unless closed period
- [x] 2.2 Modal: empty desde/hasta, `min`/`max` = period bounds, require desde ≤ hasta; auto-fetch `/grilla` when valid
- [x] 2.3 Aggregate rows (legajo · nombre · total cargas); Detalle accordion one-at-a-time with carga columns; Cancelar
- [x] 2.4 Descargar enabled only if ≥1 row; call export with dates; save as `descarga-parcial-modulos_{desde}_{hasta}.xlsx`

## Phase 3: Tests + docs

- [x] 3.1 Tests: date filter inclusive; export 1 vs 2 sheets; resumen totals
- [x] 3.2 Runbook: short note on Descarga parcial de módulos
