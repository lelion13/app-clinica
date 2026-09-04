# Tasks: novedades-capital-humano-export-liquidacion

## Phase 1: Backend builder
- [x] 1.1 Create `backend/app/services/novedades/liquidacion_export.py` with empresa helpers, fixed-concept map, `build_liquidacion_rows`, `export_liquidacion_xlsx_bytes`.
- [x] 1.2 Enforce closed period; fail-closed listing services missing `concepto_liquidacion`.
- [x] 1.3 Implement carga grouping, production allocation (same-empresa equal split + fallback), solo-special fixed concepts, ajustes equal split, row aggregation.

## Phase 2: API
- [x] 2.1 Add `GET /novedades/export-liquidacion.xlsx` in `novedades` router (`admin`/`rrhh`).

## Phase 3: Frontend
- [x] 3.1 Add **Descargar liquidación** button on `NovedadesXlsPage.jsx` without changing existing downloads.
- [x] 3.2 Enable only when selected period is `closed`; surface API errors (missing conceptos) via existing alert modal.

## Phase 4: Tests & docs
- [x] 4.1 Unit tests: multi-concepto split, fallback other-empresa, solo DEA, block missing concepto, open period rejected, ajustes prorrateo, aggregate unique rows.
- [x] 4.2 Update `docs/runbook.md`.
- [x] 4.3 Run pytest + frontend build; write `verify-report.md`.
