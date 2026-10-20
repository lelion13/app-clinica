# Implementation notes — agenda-ocupacion-dnd

Entregado y cerrado 2026-10-05. Rama: `agenda-ocupacion-dnd`.

## Comportamiento

- DnD horizontal en `/agenda-ocupacion`: reasigna **toda** la agenda (`id_agenda`).
- `POST /api/v1/distribucion/ocupacion/agenda/reassign`
- Assign/move: valida **todos** los weekdays del sync — horario box + sin solape (half-open).
- Confirm `confirm_move` (robo) y `confirm_unassign` (→ Sin consultorio).
- Rechazo: modal con lista de conflictos; no persiste.
- Modal Agendas en Consultorios **sin** estas reglas (Q10).

## Archivos clave

- `backend/app/services/distribucion/agenda_reassign.py`
- `backend/app/api/routers/distribucion.py`
- `backend/app/schemas/distribucion.py` (`AgendaReassignRequest/Response`)
- `frontend/src/pages/AgendaOcupacionPage.jsx`
- `backend/tests/test_agenda_reassign.py`

## Tests / smoke

- `pytest tests/test_agenda_reassign.py` → **7 passed** (2026-10-05).
- Smoke UI: usuario validó rechazo por solape multi-día (C5→C2; conflicto el **jueves** aunque la vista era lunes) — esperado Q6.

## Nota producto

El modal de error puede listar varios solapes (misma agenda destino con varias franjas sync). El día visible no basta: hay que revisar el resto de weekdays de esa agenda.
