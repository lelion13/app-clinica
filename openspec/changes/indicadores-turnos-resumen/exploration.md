# Exploration: indicadores-turnos-resumen

## Goal (v1)

Integrar estadísticas de turnos desde API externa en **Indicadores ocupación**, joineando por `turno_horario_id` = `id` de ocupación. Async, sin bloquear la carga principal.

## Env

- URL: `DISTRIBUCION_TURNOS_RESUMEN_URL` (ej. `https://api.cpmgsa.com.ar:8001/is/turnos/resumen`)
- Token: `NOVEDADES_PROF_SYNC_TOKEN` (mismo Bearer)
- Timeout: `DISTRIBUCION_TURNOS_RESUMEN_TIMEOUT` (default razonable, ej. 60s)

## Q&A

| Q | Decisión |
|---|----------|
| Q1 | Mes: `fecha_desde`/`fecha_hasta` = 1º y último día del mes; **una** llamada |
| Q2 | Día: ambos = fecha del selector |
| Q3 | Agregación respeta filtros actuales de Indicadores (join en memoria) |
| Q4 | Mostrar **todos** los campos del JSON agregados |
| Q5 | Contadores = suma; `%` recalculados; `espera_promedio_dias` ponderado por `total_turnos` |
| Q6 | Columna `id` visible en grilla Ocupación |
| Q7 | Fallo resumen → aviso no bloqueante; torta/KPIs siguen |
| Q8 | Change name = `indicadores-turnos-resumen` |
| Q9 | Fetch solo al cambiar día/mes; filtros reclasifican en memoria |

## Notes

- Backend MUST proxy (no exponer token al browser).
- Payload ocupación ya incluye `id`; asegurar mapeo a item + columna UI.
- UI: bloque debajo de “turnos importados” si existe; si no, debajo de KPIs/torta principales.
