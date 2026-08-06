# Design: mapeo-agenda-consultorio

## Decisions

| Decisión | Rationale |
|----------|-----------|
| Tabla `consulting_room_id_agenda` | N:1 estable; UNIQUE id_agenda |
| POST con `confirm_move` | Q2 |
| Lookup desde snapshot ocupacion | Q3 sin API externo |
| Grilla CSS día×room | Evita FC Resource premium |
| Events con `resource_id` | room id o `unassigned` |

## API

- `GET /consulting-rooms/{id}/id-agendas`
- `POST /consulting-rooms/{id}/id-agendas` `{ id_agenda, confirm_move? }` → 409 si conflicto sin confirm
- `DELETE /consulting-rooms/{id}/id-agendas/{id_agenda}`
- `GET /distribucion/ocupacion/agenda-lookup?q=`
- `GET /distribucion/ocupacion/agenda/events` (+ `location_id`, `day=YYYY-MM-DD`) → events con `resource_id`

## Files

- `backend/app/models/consulting_room.py` (+ map model)
- `backend/app/services/room_agenda_map.py`, `agenda_ocupacion.py`
- `frontend/src/pages/ConsultingRoomsPage.jsx`, `AgendaOcupacionPage.jsx`
