# Cierre — dashboard-estadisticas

**Archivado:** 2026-10-03 → `openspec/changes/archive/2026-10-03-dashboard-estadisticas/`

## Alcance final (as-built)

- Menú **Estadística** → `/estadisticas` (`admin`/`operador`)
- `GET /api/v1/stats/summary` (rango fechas + filtros)
- % ocupación = horas de **asignaciones semanales** proyectadas al período ÷ `room_operating_hours`
- UI: torta, barras por día de semana, rankings; filtros ubicación/profesional/consultorio/especialidad

## Corrección vs proposal inicial

La proposal v1 hablaba de **bookings**. La implementación usa **`room_weekly_assignments`** (Ocupación semanal). Prevalece el as-built y la spec estable.

## Relación

- Distinto de **Indicadores ocupación** (sync externo, un día).
- No se modifica al archivar `indicadores-ocupacion`.

## Spec estable

`openspec/specs/distribucion/spec.md` — § Estadística (asignaciones semanales)
