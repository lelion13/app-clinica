# Proposal: Mapeo id_agenda → consultorio + grilla Agenda ocupación

## Intent

Asociar agendas del sync a consultorios y mostrar Agenda ocupación como planilla (columnas = boxes).

## Scope

### In Scope
- Tabla `consulting_room_id_agenda` (`id_agenda` UNIQUE → `room_id`).
- ABM en ficha consultorio + typeahead médico→agenda.
- Move con confirmación si `id_agenda` ya mapeado.
- Agenda ocupación: día + ubicación; columnas rooms + “Sin consultorio”.
- Tests + runbook.

### Out of Scope
- Sync en Agenda ocupación; bookings `/agenda`; % ocupación Excel; campo consultorio en API externa.

## Approach

Mapeo administrable; events resuelven `room_id` vía join; UI grilla CSS día×consultorio (sin plugin premium FC).

## Affected Areas

| Area | Impact |
|------|--------|
| `backend/alembic/versions/0015_*` | New |
| `backend/app/models/`, services, routers | New/Mod |
| `frontend/.../ConsultingRoomsPage.jsx` | Mod |
| `frontend/.../AgendaOcupacionPage.jsx` | Mod |
| `docs/runbook.md` | Mod |

## Risks

| Risk | Mitigation |
|------|------------|
| id_agenda ausente en filas | Columna Sin consultorio |
| Muchas columnas | Filtro por ubicación |

## Rollback

Revert deploy + `alembic downgrade` 0015.

## Success Criteria

- [x] Asociar/quitar/mover id_agenda desde consultorio
- [x] Typeahead médico → label `id — nombre_agenda`
- [x] Agenda ocupación pinta por consultorio + Sin consultorio
- [x] Tests pasan

## Cierre

Archivado 2026-08-06 — ver `ARCHIVE.md`. UI posterior: `agenda-ocupacion-ui`.
