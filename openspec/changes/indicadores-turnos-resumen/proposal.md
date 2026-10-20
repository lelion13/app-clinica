# Proposal: indicadores-turnos-resumen

## Intent

Traer resumen de turnos (API externa) a Indicadores ocupación, asociado por `id` de horario de ocupación, sin demorar la carga principal de la pantalla.

## Scope

### In Scope (v1)
- Exponer/persistir y mostrar columna **`id`** en Ocupación (dato del sync Actualizar).
- Env `DISTRIBUCION_TURNOS_RESUMEN_URL` (+ timeout); Bearer = `NOVEDADES_PROF_SYNC_TOKEN`.
- Backend proxy: GET resumen con `fecha_desde`/`fecha_hasta` según Día|Mes.
- Indicadores: carga async del resumen; join `turno_horario_id` = `ocupacion.id`; filtros en memoria; bloque UI con todos los campos agregados.
- Fallo no bloqueante.

### Out of Scope
- Reemplazar CSV import (convive).
- Cache persistente / jobs / charts del resumen.
- Cambiar cálculo de torta/ocupados sync.

## Approach

1. Ocupación: asegurar `id` en response + columna en grilla.
2. BE: settings + service fetch externo + endpoint JWT bajo `/distribucion/ocupacion/indicadores/...`.
3. FE Indicadores: fetch al cambiar period/date|month; filtrar por ids del set actual; agregar métricas; loading/error local.
4. Runbook + `.env.prod.example`.

## Affected Areas

| Area | Impact |
|------|--------|
| `OccupancyPage`, schemas ocupación | Columna `id` |
| `config.py`, `.env.prod.example` | URL resumen |
| nuevo service + router distribucion | Proxy |
| `IndicadoresOcupacionPage` | UI async |
| specs/runbook | Sync |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Endpoint lento/grande | Med | Async; timeout; no bloquear |
| `id` ausente en filas viejas | Med | Re-Actualizar Ocupación; join skip null |
| Token/CORS | Low | Solo proxy BE |

## Rollback Plan

Revert PR; quitar env; UI sin bloque resumen.

## Dependencies

- Sync Ocupación con `id` en payload.
- Indicadores ocupación existente.

## Success Criteria

- [ ] Ocupación muestra columna `id` tras Actualizar.
- [ ] Indicadores carga torta sin esperar resumen; luego llena el bloque.
- [ ] Día/mes pasan fechas correctas; filtros recalculan en memoria.
- [ ] Fallo API → mensaje; resto intacto.
