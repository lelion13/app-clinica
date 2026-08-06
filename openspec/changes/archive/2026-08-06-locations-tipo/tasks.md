# Tasks: locations-tipo (retroactivo)

## Phase 1: Datos

- [x] 1.1 Migración `0016_locations_tipo` (columna, placeholders, unique parcial)
- [x] 1.2 Model SQLAlchemy `Location.tipo`

## Phase 2: API

- [x] 2.1 Schemas create/update/response con `tipo` required
- [x] 2.2 Service unique dominio+tipo + create/update
- [x] 2.3 Router response incluye `tipo`

## Phase 3: Agenda + UI

- [x] 3.1 `agenda_ocupacion`: labels y filtro location por dominio+tipo
- [x] 3.2 `LocationsPage` campo tipo
- [x] 3.3 Tests + runbook

## Notes

Documentado tras implementar. Ver también `agenda-ocupacion-ui/implementation-notes.md` §A–B.
