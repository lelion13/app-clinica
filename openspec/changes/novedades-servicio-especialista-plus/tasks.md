# Tasks: novedades-servicio-especialista-plus

## Phase 1: Data + backend

- [x] 1.1 Alembic `0028_servicio_especialista`: column `especialista` bool NOT NULL default false
- [x] 1.2 Model + Servicio schemas/create/update/response + masters
- [x] 1.3 `modulo_valor_para_profesional(..., servicio_especialista=)` ; create_asignacion uses both; update_asignacion no plus
- [x] 1.4 `GridRowResponse.plus_especialista`; set in `_asignacion_row`

## Phase 2: Frontend

- [x] 2.1 Param Servicios: checkbox Especialista (alta/edición/listado hint)
- [x] 2.2 CH Detalle Cargas: column Plus esp.

## Phase 3: Verify

- [x] 3.1 Tests create/update/inference/default
- [x] 3.2 Runbook note
