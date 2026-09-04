# Tasks: novedades-capital-humano-importe-descontar

## Phase 1: Datos

- [x] 1.1 Alembic `0025_ajuste_descuento_lote.py`: column `descuento_lote_id` UUID nullable + index on `novedades_ajuste_capital`
- [x] 1.2 Model `NovedadesAjusteCapital.descuento_lote_id` in `models/novedades.py`

## Phase 2: Backend core

- [x] 2.1 Schemas: status/import/anular responses + row error shape in `schemas/novedades.py`
- [x] 2.2 Service `importe_descontar.py`: parse exact headers, validate, waterfill, commit lote, status, anular
- [x] 2.3 Wire routes in `routers/novedades.py` (status GET, import POST, anular POST)
- [x] 2.4 Update `liquidacion_export.py` to map ajustes con `servicio_id` → concepto del servicio

## Phase 3: Frontend

- [x] 3.1 `NovedadesXlsPage.jsx`: botón Importe a descontar / Anular antes de liquidación; file input; load status
- [x] 3.2 Modal centrado listando todos los errores de import (patrón módulos)

## Phase 4: Tests + docs

- [x] 4.1 `test_importe_descontar.py`: waterfill, tope, duplicado, signo, solo-prod, headers
- [x] 4.2 Extend liquidación tests for ajuste con `servicio_id`
- [x] 4.3 Update `docs/runbook.md`
