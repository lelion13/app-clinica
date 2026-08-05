# Tasks: agenda-ocupacion-sync

## Phase 1 — Backend

- [x] 1.1 Schemas eventos + filter-options en `schemas/distribucion.py`
- [x] 1.2 Service `agenda_ocupacion.py`: parse fechas/horas, map dia ES, solape, expand, filtros, location label
- [x] 1.3 Router GET `.../agenda/events` y `.../agenda/filter-options` (JWT admin|operador)
- [x] 1.4 Tests unitarios materialización + filtros + exclusiones

## Phase 2 — Frontend

- [x] 2.1 Nav + ruta `/agenda-ocupacion`
- [x] 2.2 `AgendaOcupacionPage.jsx`: FullCalendar, datesSet→events, filtros multi, popover detalle, solo lectura
- [x] 2.3 Labels dominio desde filter-options (nombre o id)

## Phase 3 — Docs / verify

- [x] 3.1 Nota en `docs/runbook.md`
- [x] 3.2 Correr tests backend del área (`tests/test_agenda_ocupacion.py` — 7 passed)
