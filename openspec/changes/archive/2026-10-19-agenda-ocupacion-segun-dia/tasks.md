# Tasks: agenda-ocupacion-segun-dia

## Phase 1: Datos / migración

- [x] 1.1 Alembic: `weekday` + PK `(id_agenda, weekday)`; expandir mapas legados a weekdays sync
- [x] 1.2 Modelo `ConsultingRoomIdAgenda` + índices

## Phase 2: Backend

- [x] 2.1 Reassign/unassign con `weekday`; validación solo ese día
- [x] 2.2 `agenda/events` (e indicadores si aplica): `resource_id` por weekday del evento
- [x] 2.3 Consultorios id-agendas: list con weekdays; assign solo pendientes todo-o-nada; delete por día o full-en-room
- [x] 2.4 Schemas Pydantic + tests unitarios/API

## Phase 3: Frontend Agenda ocupación

- [x] 3.1 Filtrar/mostrar solo agendas del weekday del calendario
- [x] 3.2 DnD envía weekday; unassign/assign día
- [x] 3.3 Orden numérico columnas; scroll H; auto-scroll en drag
- [x] 3.4 Sin consultorio sticky condicional

## Phase 4: Frontend Consultorios

- [x] 4.1 Labels full vs parcial (`nombre - día`)
- [x] 4.2 Assign pendientes + modal conflicto todo-o-nada
- [x] 4.3 Unassign un día vs todos los del room

## Phase 5: Docs / verify

- [x] 5.1 Nota `docs/runbook.md` (mapa por día; divergencia AO vs Consultorios)
- [x] 5.2 Smoke: migración VPS OK tras fix PK; feature en prod (usuario 2026-10-19)
