# Exploration: novedades-produccion-valor-bonos

## Topic

Valorizar en Capital Humano las cantidades importadas de bonos mediante un catálogo estable de tarifas en Parametrización, sin reconfigurar valores en cada importación.

## Current State

- **Import bonos** persiste snapshot por período: `novedades_bono_opcion` (dimensión `centro|servicio|semana|horario`) + `novedades_bono_cantidad` (cantidad por profesional/período/opción).
- Capital Humano muestra **columnas dinámicas de cantidad** por opción; `monto_total = monto_cargas + monto_ajustes` (bonos no monetizados).
- Change `capital-humano-bonos-servicios-especiales` promueve a grilla profesionales solo-bonos con servicios `DEA|DEP|CAP|CAI`.
- Param tabs actuales: Servicios, Módulos, Jefes ↔ servicios, Profesionales ↔ servicios, Períodos, Feriados. **No** hay tab Producción ni tabla de tarifas.
- El checkbox **`produccion`** en módulos significa “omitir check externo `tiene-produccion`” — concepto distinto al tab **Producción** propuesto.

## User Intent (resumido)

- Nuevo tab **Producción** en Param (entre Módulos y Jefes ↔ servicios).
- Grilla + **Nueva producción** con patrón ABM de Servicios.
- Cada fila matchea import de bonos por los **4 campos** y aplica `cantidad × valor_unitario`.
- Capital Humano: por opción, columnas **cantidad** + **subtotal**; sumar subtotales al total del profesional.
- Aviso (banner) si hay opciones importadas sin tarifa; no bloquear import ni grilla.

## Affected Areas (preliminar)

| Area | Impact |
|------|--------|
| `backend/app/models/novedades.py` | Nueva entidad tarifa (FK a `novedades_bono_opcion`) |
| `backend/alembic/versions/` | Migración `0021_*` |
| `backend/app/schemas/novedades.py` | Schemas tarifa + extensión grid CH |
| `backend/app/services/novedades/masters.py` (o nuevo `produccion_tarifas.py`) | CRUD tarifas |
| `backend/app/services/novedades/capital_humano.py` | Valorización + `monto_total` + exports |
| `backend/app/api/routers/novedades.py` | Rutas CRUD + listado opciones |
| `frontend/src/pages/novedades/NovedadesParamPage.jsx` | Tab Producción |
| `frontend/src/pages/novedades/NovedadesXlsPage.jsx` | Columnas subtotal + banner + total |
| `backend/tests/` | Tests valorización y ABM |
| `docs/runbook.md` | Documentar tab y fórmula |

## Riesgos

| Risk | Mitigation |
|------|------------|
| Confusión “Producción” vs flag módulo `produccion` | Texto de ayuda en tab y runbook |
| Opciones nuevas post-import sin tarifa | Banner en CH; subtotal 0 |
| Grilla muy ancha (2 columnas por opción) | Mismo patrón que hoy; scroll horizontal |
| Duplicar tarifa por misma opción | Unique en `opcion_id` |

## Ready for Proposal

Sí. Encuesta cerrada en `decisions.md` (2026-08-19).
