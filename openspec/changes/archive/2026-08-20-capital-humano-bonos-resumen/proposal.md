# Proposal: Capital Humano — importar bonos resumen

## Intent

Desde Capital Humano, con **período obligatorio**, importar el resumen de bonos de producción (`/bonos/resumen?fecha_desde&fecha_hasta`), persistirlo por período, mostrar cantidades en **columnas dinámicas** (una fila por profesional que ya está en la grilla) y ofrecer un tercer XLS “con bonos”. Profesionales del catálogo con solo bonos (sin cargas/ajustes) se consultan en un modal aparte.

## Scope

### In Scope

- Botón **Importar bonos** (admin/rrhh); exige período seleccionado.
- Proxy backend: URL env + Bearer = `NOVEDADES_PROF_SYNC_TOKEN`; `fecha_desde`/`fecha_hasta` = inicio/fin del período.
- Match `profesional` API → `CODPROF` (trim/string).
- Columna dinámica = `centro|servicio|semana|horario`; sumar cantidades si hay duplicados.
- Persistencia DB por período; re-import con período **open** reemplaza snapshot; con período **closed** no se puede pisar.
- Grilla principal: columnas de bonos a la derecha para profesionales con cargas/ajustes; **no** filas solo-bonos.
- Modal “solo bonos” (catálogo matched, sin cargas/ajustes).
- Tercer download: XLS agregado + columnas bonos; XLS actuales sin cambio; descarga XLS siempre permitida (pruebas).
- Modal resumen post-import; errores sin tocar snapshot; 422 si faltan fechas del período.
- Migración, tests, runbook, delta specs.

### Out of Scope

- Restringir XLS solo a período cerrado (futuro).
- Match por LEGAJO.
- Cron automático de import.
- Roles distintos a admin/rrhh.
- Edición manual de cantidades de bonos.

## Approach

1. Alembic: tablas de snapshot bonos por `periodo_id` + professional + dimensión opción + cantidad.
2. Service: fetch HTTP → normalizar → match CODPROF → upsert replace si open → aggregate columns.
3. API: `POST .../capital-humano/bonos/import`, listado solo-bonos, export XLS con bonos; grilla Capital Humano incluye map de cantidades.
4. UI: botón import (disabled sin período), columnas dinámicas, modal solo-bonos, 3er XLS, AlertModal resumen/errores.

## Affected Areas

| Area | Impact |
|------|--------|
| models + alembic | New |
| services capital_humano / bonos_import | New/Modified |
| router novedades + config | Modified |
| NovedadesXlsPage | Modified |
| runbook + openspec | Modified |

## Risks

| Risk | Mitigation |
|------|------------|
| CODPROF no matchea | Contar ignorados en resumen; trim/string |
| Período cerrado re-import | 422 + UI deshabilita botón |
| API caído | No mutar snapshot (Q8) |
| Muchas columnas | scroll horizontal; headers compactos |

## Rollback Plan

Revert deploy + `alembic downgrade` de la rev de bonos; datos de snapshot se pierden en down.

## Dependencies

- Capital Humano archivado (`novedades-capital-humano-legajo`).
- Token sync profesionales ya configurado.
- API `https://api.cpmgsa.com.ar:8001/bonos/resumen` alcanzable desde el backend.

## Success Criteria

- Con período open y fechas: import llena columnas; re-import reemplaza.
- Con período closed: import bloqueado; datos previos visibles.
- Solo-bonos en modal; XLS con bonos descarga agregado+columnas.
- Sin período seleccionado: no ejecuta import.
