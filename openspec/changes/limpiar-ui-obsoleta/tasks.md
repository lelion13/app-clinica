# Tasks: limpiar-ui-obsoleta

## Phase 0: Inventario (no romper)

- [x] 0.1 Grep FE/BE: `bookings`, `weekly-assignments`, `stats/summary`, `WeeklyOccupancy`, `AgendaPage`, `Estadisticas`
- [x] 0.2 Confirmar que `/professionals`, rooms, hours, `distribucion/ocupacion/*` no dependen de lo a borrar

## Phase 1: Frontend

- [x] 1.1 Quitar ítems de `navigation.js`
- [x] 1.2 Routes: delete pages; redirect legacy → `/`
- [x] 1.3 Borrar páginas y dead imports (+ fullcalendar deps)

## Phase 2: Backend

- [x] 2.1 Desregistrar routers bookings / weekly-assignments / stats
- [x] 2.2 Borrar modules (api/services/schemas/models/tests) exclusivos
- [x] 2.3 Alembic drop `bookings` + `room_weekly_assignments` (`0033_drop_bookings_weekly`)
- [x] 2.4 Limpiar `main.py`, `models/__init__`, `alembic/env.py`, `services/__init__`, `schemas/__init__`

## Phase 3: Docs / verify

- [x] 3.1 Sync delta a spec estable + runbook (backup pre-deploy)
- [ ] 3.2 Smoke: Ocupación, Agenda ocupación, Indicadores, Profesionales, Consultorios; redirects; 404 APIs
