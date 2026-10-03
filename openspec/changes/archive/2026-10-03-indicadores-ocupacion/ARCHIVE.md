# Cierre — indicadores-ocupacion

**Archivado:** 2026-10-03 → `openspec/changes/archive/2026-10-03-indicadores-ocupacion/`

## Alcance final (implementado)

- Menú **Indicadores ocupación** → `/indicadores-ocupacion` (`admin`/`operador`)
- `GET /api/v1/distribucion/ocupacion/indicadores`
- % = horas sync (agendas mapeadas) ÷ `room_operating_hours` del día
- Torta global; % puede >100%; rooms sin horario fuera de torta
- Convive con **Estadística** (cálculo distinto)

## Spec estable

`openspec/specs/distribucion/spec.md` — § Indicadores ocupación (sync)
