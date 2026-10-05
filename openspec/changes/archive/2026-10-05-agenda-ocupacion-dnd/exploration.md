# Exploration: agenda-ocupacion-dnd

## Current State

`AgendaOcupacionPage.jsx`:
- Grilla día × consultorios + columna **Sin consultorio** (`resource_id=unassigned`).
- Eventos materializados desde sync; click → modal detalle.
- Filtros una fila: ubicación, día, tipo, especialidad, médico.
- **Solo lectura** (spec estable). Sin drag/drop.

Mapeo persistente: `consulting_room_id_agenda` — `id_agenda` UNIQUE → un `room_id`.
- Gestión hoy: modal **Agendas** en Consultorios (`PUT …/id-agendas`, `confirm_move`, DELETE).
- Spec: asociación agenda↔room **MUST NOT** validar contra `room_operating_hours` (regla a **relajar solo** para el nuevo path DnD; Consultorios conserva Q10=A).

Events API: `resource_id` = room id o `unassigned` según mapa. Un drag que reasigna `id_agenda` mueve **todas** las ocurrencias de esa agenda.

## Affected Areas

- `frontend/src/pages/AgendaOcupacionPage.jsx` (+ posible helper DnD)
- `backend/app/services/room_agenda_map.py` (o servicio nuevo de reassign + validate)
- `backend/app/api/routers/distribucion.py` y/o `consulting_rooms.py`
- schemas/tests distribucion / consulting rooms
- `openspec/specs/distribucion/spec.md` (UI Agenda deja de ser solo lectura para mapeo vía DnD)
- `docs/runbook.md`

## Approaches

1. **Endpoint dedicado** `POST …/ocupacion/agenda/reassign` `{ id_agenda, target_room_id | null, confirm_move }` con validación horario+solape en todos los weekday del sync → UI HTML5/Pointer DnD — **elegido**.
2. Reusar solo PUT replace agendas del room destino — UI tendría que listar agendas actuales del room + merge; validación nueva igual necesaria; más frágil.
3. Override por fecha (no persistir en mapa global) — descartado (Q1=A).

## Recommendation

Approach 1. Validación server-side autoritativa; UI optimista con rollback + modal error (Q9). Confirm modals para robo (Q5) y unassign (Q7).

## Risks

- Validar “todos los weekdays” requiere cargar sync + hours + agendas del room destino; perf OK a escala actual.
- Consultorios Agendas sigue permitiendo asignaciones que el DnD rechazaría (aceptado Q10).
- Solape: definir intervalo half-open / inclusivo y múltiples franjas del mismo `id_agenda`.

## Ready for Proposal

Yes.
