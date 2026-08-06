# Cierre — agenda-ocupacion-sync

**Archivado:** 2026-08-06 → `openspec/changes/archive/2026-08-06-agenda-ocupacion-sync/`

## Alcance final (implementado)

- `GET .../ocupacion/agenda/events` + `filter-options`
- Materialización por ventana `[start,end)`, dia ES, solape fechas, filtros query
- Menú `/agenda-ocupacion` (solo lectura; sync NO aquí)

## Superseded (UI)

El delta original pedía FullCalendar + popover + filtros multi genéricos. **UI final** la definen:

1. `mapeo-agenda-consultorio` — grilla día × consultorio + Sin consultorio  
2. `agenda-ocupacion-ui` — viewport, alineación, selects una fila, modal Esc/overlay  

**API de events/filter-options de este change sigue vigente.**

## Spec estable

`openspec/specs/distribucion/spec.md` — § Agenda API (+ UI apuntando a archives posteriores).
