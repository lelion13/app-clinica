# Tasks: consultorios-ui

## Phase 1: Backend — schemas y batch

- [x] 1.1 Extender `AgendaLookupItem` con `current_room_id` / `current_room_code` (nullable) en `schemas/consulting_room.py`
- [x] 1.2 Agregar schemas batch: `RoomIdAgendaReplaceRequest`, `RoomHoursReplaceRequest` (lista `items`)
- [x] 1.3 Enriquecer `ocupacion_agenda_lookup` en `distribucion.py` (join mapeo room activo)
- [x] 1.4 Implementar `replace_room_id_agendas` en `room_agenda_map.py` (transacción, confirm_move, 409)
- [x] 1.5 Implementar `replace_room_hours` en `consulting_room_service.py` (transacción, validación tiempos)
- [x] 1.6 Exponer `PUT /{room_id}/id-agendas` y `PUT /{room_id}/hours` en `consulting_rooms.py`

## Phase 2: Backend — tests

- [x] 2.1 Tests lookup: ítem mapeado incluye `current_room_*`; no mapeado → null
- [x] 2.2 Tests PUT agendas: replace add/remove; move con confirm_move; 409 sin confirm y sin side effects
- [x] 2.3 Tests PUT hours: replace completo; validación start < end; room inexistente 404

## Phase 3: Frontend — grilla y nav

- [x] 3.1 Quitar ítem “Horarios consultorio” de `navigation.js`
- [x] 3.2 Quitar ruta `/horarios-consultorio` e import de `RoomHoursPage` en `main.jsx`
- [x] 3.3 Eliminar `RoomHoursPage.jsx` (huérfano)
- [x] 3.4 Reescribir `ConsultingRoomsPage.jsx`: load rooms/locations, grilla Ubicación|Nombre, filtro Todas, botón Agregar, Eliminar con confirm

## Phase 4: Frontend — modales

- [x] 4.1 Modal Agregar (ubicación + código, Aceptar POST / Cancelar)
- [x] 4.2 Modal Editar (PATCH, mismos campos)
- [x] 4.3 Modal Agendas (draft, typeahead + current_room confirm, quitar, PUT batch)
- [x] 4.4 Modal Horarios (draft franjas, PUT batch)
- [x] 4.5 Un solo modal abierto; errores de API visibles en el modal / página

## Phase 5: Docs y verificación

- [x] 5.1 Nota breve en `docs/runbook.md` si documenta menú Distribución / horarios
- [x] 5.2 Correr tests backend del área tocada
- [ ] 5.3 Smoke manual: grilla, filtro, 4 modales Aceptar/Cancelar, menú sin Horarios, ruta 404
