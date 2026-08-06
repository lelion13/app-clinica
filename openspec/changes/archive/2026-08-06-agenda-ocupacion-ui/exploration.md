# Exploration: agenda-ocupacion-ui

## Current State (post-implementación)

- Grilla CSS día × consultorios en `AgendaOcupacionPage.jsx`.
- Alineación: marcas de hora absolute + border-box (drift corregido).
- Layout: full-bleed + `100dvh` residual; scroll interno; sticky headers.
- Filtros: **una fila** de selects (ubicación, día, tipo, especialidad, médico).
- Modal detalle con overlay/Esc.
- Backend `filter-options` / `events` sin cambio de contrato.

## Affected Areas

- `frontend/src/pages/AgendaOcupacionPage.jsx`
- `backend/tests/test_agenda_ocupacion.py`
- `docs/runbook.md`
- Hermano: `locations-tipo`, parser sync en `horarios_activos.py`

## Approaches (histórico)

1. **Grilla CSS + wire filtros** (elegido) — Low–Med
2. FullCalendar resources — rechazado (look planilla)
3. Multi checkbox (Q3=A) — implementado luego **descartado** por altura

## Recommendation

Mantener approach 1 con selects compactos. Prioridad visual = grilla.

## Risks

- Selects con miles de médicos → UX nativa aceptable; typeahead futuro si molesta.
- GHCR package ACL independiente front/back.

## Ready for Proposal

Yes (cerrado; ver `implementation-notes.md`).
