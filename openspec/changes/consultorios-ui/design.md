# Design: consultorios-ui

## Technical Approach

Reescribir la UI de Consultorios como grilla + modales draft; persistir Agendas/Horarios con PUT replace transaccional; enriquecer agenda-lookup para confirm de move en draft; retirar nav/ruta de Horarios.

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| PUT replace agendas/hours (no PATCH parcial) | Draft = desired set; un request = estado final; fácil transacción |
| Lookup enrichment vs endpoint check aparte | Un round-trip al elegir; reutiliza typeahead existente |
| Mantener POST/DELETE unitarios | Compat tests/clientes; UI nueva no los usa en Aceptar |
| `window.confirm` delete + move | Consistente con UX actual de move; bajo costo v1 |
| No migración Alembic | Solo API/UI sobre tablas existentes |

## Data Flow

```
Open /consultorios
  → GET /locations + GET /consulting-rooms
  → filter client-side by location_id (Todas = all)

Agregar/Editar Accept
  → POST or PATCH /consulting-rooms
  → reload rooms

Agendas open
  → GET /consulting-rooms/{id}/id-agendas → draft
  → typeahead GET agenda-lookup (items + current_room_*)
  → if other room: confirm → draft item {id_agenda, confirm_move, label}
Accept → PUT .../id-agendas { items: [...] } in one DB transaction
Cancel → discard draft

Horarios open
  → GET .../hours → draft franjas
  → add/remove in draft
Accept → PUT .../hours { items: [{weekday, start_time, end_time}, ...] }
Cancel → discard
```

## API Shape (proposed)

### `PUT /consulting-rooms/{room_id}/id-agendas`

Request:
```json
{ "items": [ { "id_agenda": 100, "confirm_move": true } ] }
```

Behavior:
- Desired set for this room = `items`.
- Remove mappings on this room not in set.
- For each item: if mapped elsewhere and `confirm_move` false → 409 `{ requires_confirm_move, current_room_id, current_room_code }` and rollback all.
- If mapped elsewhere and `confirm_move` true → move to this room.
- If already on this room → no-op keep.
- Response: `RoomIdAgendaListResponse` post-state.

### `PUT /consulting-rooms/{room_id}/hours`

Request:
```json
{ "items": [ { "weekday": 1, "start_time": "08:00", "end_time": "12:00" } ] }
```

Behavior:
- Validate each franja; on any invalid → 422, no write.
- Replace all hours for room to match `items` (delete removed, insert new; no client ids required).
- Response: list of `RoomOperatingHourResponse`.

### Agenda lookup enrichment

Extend `AgendaLookupItem` with optional `current_room_id: int | null`, `current_room_code: str | null` from room_agenda map join.

## File Changes

| File | Change |
|------|--------|
| `frontend/src/pages/ConsultingRoomsPage.jsx` | Grilla, filtro, 4 modales draft |
| `frontend/src/config/navigation.js` | Quitar Horarios consultorio |
| `frontend/src/main.jsx` | Quitar route + import RoomHoursPage |
| `frontend/src/pages/RoomHoursPage.jsx` | Delete file (orphan) |
| `backend/app/schemas/consulting_room.py` | Batch request schemas + lookup fields |
| `backend/app/services/room_agenda_map.py` | `replace_room_id_agendas` |
| `backend/app/services/consulting_room_service.py` | `replace_room_hours` |
| `backend/app/api/routers/consulting_rooms.py` | PUT routes |
| `backend/app/api/routers/distribucion.py` | Enrich lookup |
| `backend/tests/test_room_agenda_map.py` (+ hours tests) | Batch + conflict |
| `docs/runbook.md` | Brief note if nav/ops change documented |

## UI Notes

- Modal state: `null | 'add' | 'edit' | 'agendas' | 'hours'` + `activeRoomId`.
- Labels fila: Editar / Agendas / Horarios / eliminar.
- Columna Nombre = `code`; no rename DB field.
- Theme: reuse `uiStyles` / `uiTheme` (no redesign system).

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Stale confirm_move between draft and Accept | Re-check in PUT; 409 + rollback; UI muestra error y puede reabrir |
| Duplicate franjas overlapping | Keep existing create validation rules; document if overlap allowed today |
| Large draft lists | Unlikely; same scale as current UI |

## Open Questions

None — survey Q1–Q13 closed in `decisions.md`.
