# Tasks: agenda-ocupacion-dnd

## Phase 1: Backend — reassign + validación

- [x] 1.1 Schema request/response `AgendaReassign` (`id_agenda`, `target_room_id`, `confirm_move`, flag unassign si aplica)
- [x] 1.2 Servicio: cargar intervalos sync por `id_agenda` (todos weekdays)
- [x] 1.3 Validar cobertura `room_operating_hours` (unión franjas / contenido)
- [x] 1.4 Validar no solape con otras agendas del room (excluir propio `id_agenda`; half-open)
- [x] 1.5 Persist: assign/move con `confirm_move`; unassign = delete mapa
- [x] 1.6 Router `POST .../ocupacion/agenda/reassign` (JWT admin|operador)
- [x] 1.7 Tests: OK assign; fuera horario; solape; multi-weekday fail; 409 sin confirm; unassign

## Phase 2: Frontend — DnD Agenda ocupación

- [x] 2.1 Bloques draggables; drop zones columnas rooms + Sin consultorio
- [x] 2.2 Threshold drag vs click (detalle modal intacto)
- [x] 2.3 Confirm modal robo (`confirm_move`)
- [x] 2.4 Confirm modal desasignar
- [x] 2.5 Modal error detallado + revert visual
- [x] 2.6 Tras éxito: refrescar events; respetar filtros

## Phase 3: Docs y cierre

- [x] 3.1 Nota `docs/runbook.md` (DnD + divergencia vs modal Agendas Consultorios)
- [x] 3.2 Verify + archive (smoke: rechazo solape multi-día C5→C2)
