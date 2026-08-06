# Cierre — mapeo-agenda-consultorio

**Archivado:** 2026-08-06 → `openspec/changes/archive/2026-08-06-mapeo-agenda-consultorio/`

## Alcance final (implementado)

- Tabla/migración `0015_room_id_agenda` (`id_agenda` UNIQUE → room)
- ABM en ficha Consultorios + typeahead lookup + move con confirm
- Events con `resource_id` room | `unassigned`
- Agenda ocupación: columnas consultorios de la ubicación + Sin consultorio

## Relación con otros archives

| Tema | Archive |
|------|---------|
| Pulido UI (filtros fila, modal, viewport, alineación) | `agenda-ocupacion-ui` |
| Filtro ubicación dominio+tipo | `locations-tipo` |
| Sync / materialización base | `distribucion-ocupacion` / `agenda-ocupacion-sync` |

## Spec estable

`openspec/specs/distribucion/spec.md` — § Mapeo (+ UI compartida).
