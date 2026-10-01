# Tasks: novedades-capital-humano-motivo-sin-produccion

## Phase 1: Backend

- [x] 1.1 Add `motivo_sin_produccion` + `observacion_sin_produccion` to `GridRowResponse`; set in `_asignacion_row` / `_novedad_row`
- [x] 1.2 Add columns `motivo` / `observacion` to detail XLS (label + text)
- [x] 1.3 Add `motivos_sin_produccion: list[str]` on `CapitalHumanoRowResponse`; fill from cargas in `build_capital_humano_rows`

## Phase 2: Frontend

- [x] 2.1 Motivo select (Todos / Vacaciones / Enfermedad) + row highlight (one color)
- [x] 2.2 Button **Con novedad** → modal flat list of matching cargas from `/grilla`
- [x] 2.3 Detalle Cargas: columns Motivo + Observación

## Phase 3: Verify

- [x] 3.1 Tests for grilla fields / export columns / CH flags
- [x] 3.2 Runbook short note
