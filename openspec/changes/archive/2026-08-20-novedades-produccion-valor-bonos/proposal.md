# Proposal: Novedades — tarifas Producción y valorización de bonos

## Intent

Permitir valorizar las cantidades de bonos importadas en Capital Humano mediante un catálogo estable de tarifas en Parametrización (tab **Producción**), sin reconfigurar valores en cada importación.

## Scope

### In Scope

- Tab **Producción** en Parametrización (entre Módulos y Jefes ↔ servicios), ABM estilo Servicios.
- Tabla de tarifas: una fila por `novedades_bono_opcion` con `valor_unitario` entero ≥ 0.
- Match exacto por `centro`, `servicio`, `semana`, `horario` (vía FK a opción).
- Capital Humano: por opción, columnas **cantidad** y **subtotal**; `monto_total` incluye suma de subtotales.
- Banner en Capital Humano si hay opciones del período sin tarifa (subtotal 0, no bloquea).
- Export **XLS con bonos**: cantidad + subtotal por opción; **XLS agregado**: total incluye bonos.
- API CRUD + listado de opciones de bono para selector de alta.
- Tests backend y actualización de runbook.

### Out of Scope

- Vigencia por fecha/período de tarifas (v2).
- Tarifas comodín (solo servicio, etc.).
- Valorización en modal Solo bonos como columnas extra (solo grilla principal / exports según alcance CH).
- Cambios al flujo de importación externa de bonos.
- Renombrar flag módulo `produccion`.

## Approach

- **Persistencia**: `novedades_produccion_tarifa` con `opcion_id` UNIQUE FK → `novedades_bono_opcion`, `valor_unitario` INTEGER NOT NULL CHECK ≥ 0, soft-delete vía `AuditMixin`.
- **Param UI**: tab Producción con grilla legible (4 campos + valor), modal Nueva/Editar con selector de opciones no tarifadas (o todas en editar), modal confirm delete.
- **Valorización**: al armar grid CH, cargar mapa `opcion_key → valor_unitario`; por celda `subtotal = cantidad × valor` (0 si sin tarifa); acumular por fila.
- **Respuesta API**: extender `CapitalHumanoGridResponse` con pares cantidad/subtotal en columnas y flag `opciones_sin_tarifa` para banner.

## Affected Areas

| Area | Impact |
|------|--------|
| `backend/app/models/novedades.py` | Add model |
| `backend/alembic/versions/0021_produccion_tarifa.py` | Add migration |
| `backend/app/schemas/novedades.py` | Add/modify schemas |
| `backend/app/services/novedades/` | CRUD + valorización |
| `backend/app/api/routers/novedades.py` | New routes |
| `frontend/src/pages/novedades/NovedadesParamPage.jsx` | Tab Producción |
| `frontend/src/pages/novedades/NovedadesXlsPage.jsx` | Subtotales + banner |
| `backend/tests/` | New/updated tests |
| `docs/runbook.md` | Modified |
| `openspec/specs/novedades/spec.md` | Modified (al archivar) |

## Risks

| Risk | Mitigation |
|------|------------|
| Confusión naming Producción vs `produccion` módulo | Help text + runbook |
| Opciones sin tarifa | Banner; subtotal 0 |
| Ancho de grilla | Scroll horizontal existente |

## Rollback Plan

Revert commit + `alembic downgrade` de revisión `0021`. Tarifas se pierden; snapshots de bonos intactos.

## Success Criteria

- [ ] admin/rrhh puede crear/editar/eliminar tarifa por opción de bono.
- [ ] Capital Humano muestra cantidad + subtotal por opción importada.
- [ ] `monto_total` = cargas + ajustes + suma subtotales bonos.
- [ ] Opción sin tarifa: cantidad visible, subtotal 0, banner visible.
- [ ] XLS con bonos y XLS agregado reflejan valorización.
- [ ] jefe_medico no accede al ABM Producción (403).
