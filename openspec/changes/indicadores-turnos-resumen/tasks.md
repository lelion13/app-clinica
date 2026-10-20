# Tasks: indicadores-turnos-resumen

## 1. Ocupación — exponer `id`
- [x] 1.1 Asegurar `id` en schema/response de ocupación activa (COLUMNS / serializers)
- [x] 1.2 Columna `id` en `OccupancyPage` (mobile-first)
- [x] 1.3 Smoke: tras Actualizar, filas muestran `id`

## 2. Config y proxy BE
- [x] 2.1 `DISTRIBUCION_TURNOS_RESUMEN_URL` en settings + `.env.prod.example`
- [x] 2.2 Service: GET externo + Bearer `NOVEDADES_PROF_SYNC_TOKEN` + timeout; errores genéricos
- [x] 2.3 Endpoint JWT `GET .../ocupacion/indicadores/turnos-resumen?fecha_desde&fecha_hasta`
- [x] 2.4 Tests con mock httpx (200 / timeout / 5xx)

## 3. Indicadores FE
- [x] 3.1 API client tipado para turnos-resumen
- [x] 3.2 Fetch solo al montar / cambiar Día|Mes (rango día = igual; mes = 1º–último)
- [x] 3.3 Join `turno_horario_id` ∈ ids del set filtrado; filtros solo re-agregan en memoria
- [x] 3.4 Agregación A (sumas, %, espera ponderada); UI todos los campos
- [x] 3.5 Bloque no bloqueante (loading/error local); debajo CSV si existe, si no debajo KPIs/torta

## 4. Docs y cierre
- [x] 4.1 Runbook: env, flujo Día/Mes vs filtros, re-Actualizar para ids
- [x] 4.2 Marcar tasks; listo para archive tras verify
