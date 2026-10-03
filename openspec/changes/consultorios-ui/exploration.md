# Exploration: consultorios-ui

## Current State

`/consultorios` (`ConsultingRoomsPage.jsx`) hoy:
- Form inline superior: select ubicación + input código + Agregar (POST inmediato).
- Layout 2 columnas: lista de consultorios (click selecciona) + panel de agendas del seleccionado.
- Agendas: typeahead (`/distribucion/ocupacion/agenda-lookup`), POST/DELETE unitarios, `window.confirm` si 409 `requires_confirm_move`.
- Eliminar consultorio en cada ítem (DELETE inmediato, sin confirm).
- No hay modal de edición; no hay filtro por ubicación; no se gestionan horarios aquí.

`/horarios-consultorio` (`RoomHoursPage.jsx`):
- Select de consultorio + form día/desde/hasta + Agregar franja (POST `/consulting-rooms/hours`).
- Lista de franjas con eliminar (DELETE).
- Ítem de menú en `DISTRIBUTION_ITEMS` y ruta en `main.jsx`.

Backend (`consulting_rooms.py` + `room_agenda_map.py` + `consulting_room_service.py`):
- CRUD rooms: GET/POST/PATCH/DELETE.
- Agendas: GET/POST/DELETE por room; POST con `confirm_move`.
- Hours: GET por room; POST/PATCH/DELETE por hour id (create es `/hours` global con `room_id` en body).
- Lookup agendas: `GET /distribucion/ocupacion/agenda-lookup` → `AgendaLookupItem` sin info de mapeo actual a consultorio.
- Auth: JWT + `require_operator_or_admin`.

Spec estable `openspec/specs/distribucion/spec.md` no documenta aún la UI de ABM de consultorios/horarios (sí mapeo agenda↔consultorio en ocupación).

## Affected Areas

- `frontend/src/pages/ConsultingRoomsPage.jsx` — reescritura UI grilla + modales
- `frontend/src/pages/RoomHoursPage.jsx` — deja de ser entrada de menú/ruta (puede quedar archivo huérfano o borrarse)
- `frontend/src/config/navigation.js` — quitar ítem Horarios consultorio
- `frontend/src/main.jsx` — quitar ruta `/horarios-consultorio`
- `backend/app/api/routers/consulting_rooms.py` — PUT batch agendas/hours
- `backend/app/schemas/consulting_room.py` — payloads batch + lookup enrichment
- `backend/app/services/room_agenda_map.py` / `consulting_room_service.py` — replace atómico
- `backend/app/api/routers/distribucion.py` — enriquecer agenda-lookup
- `backend/tests/test_room_agenda_map.py` (+ tests hours batch)
- `docs/runbook.md` — nota de menú/ruta si aplica
- `openspec/specs/distribucion/spec.md` — merge en archive

## Approaches

1. **Modales + batch transaccional (elegido)** — Draft en UI; Aceptar llama PUT replace; Cancelar descarta.
   - Pros: Aceptar/Cancelar reales; sin estados a medias
   - Cons: Más backend; hay que enriquecer lookup para confirm en draft
   - Effort: Medium

2. **Modales + llamadas secuenciales** — Reusar POST/DELETE actuales en Aceptar.
   - Pros: Menos API nueva
   - Cons: Fallo parcial; contradice “seguro”
   - Effort: Low–Medium

3. **Efecto inmediato en modales** — Aceptar solo cierra.
   - Pros: Reuso total de APIs
   - Cons: Cancelar no deshace; contradice Q7
   - Effort: Low

## Recommendation

Approach 1. Encaja con Q7/Q11/Q12/Q13.

## Risks

- Race: entre confirm en draft y Accept otro usuario mueve el mismo `id_agenda` → batch MUST revalidar `confirm_move` y fallar 409 sin aplicar (todo-o-nada).
- Replace hours: franjas con ids existentes vs nuevas; diseño replace por lista desired sin exigir ids de cliente.
- Favoritos a `/horarios-consultorio` → 404 (aceptado Q3).

## Ready for Proposal

Yes — survey closed; proceed to proposal/spec/design/tasks.
