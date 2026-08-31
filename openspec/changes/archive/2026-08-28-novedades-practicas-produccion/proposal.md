# Proposal: Integración de APIs Prácticas e Internaciones en Capital Humano

## Intent

Integrar dos APIs externas adicionales al presionar **Actualizar** en Capital Humano:
1. `NOVEDADES_BONOS_PRACTICAS_URL`: Prácticas traumatológicas (`centro`, `servicio`, `profesional`, `cantidad`).
2. `NOVEDADES_BONOS_INTERNACIONES_URL`: Internaciones (`profesional`, `sucursal`, `cantidad_internaciones`).

Permite sincronizar las cantidades por profesional en el período seleccionado, persistirlas en snapshots dedicados, valorizarlas mediante tarifas unitarias configurables en Parametrización → Producción ("Práctica traumatológica" e "Internaciones"), y sumarlas al Total Producción de cada profesional elegible.

## Scope

### In Scope
- Nuevas variables de entorno en `.env.prod`:
  - `NOVEDADES_BONOS_PRACTICAS_URL`
  - `NOVEDADES_BONOS_INTERNACIONES_URL`
  - Ambas usan el Bearer token existente `NOVEDADES_PROF_SYNC_TOKEN` y parámetros `fecha_desde` (inicio) / `fecha_hasta` (fin).
- Consulta atómica (todo o nada) en **Actualizar**: se consultan las 3 APIs (Bonos resumen, Prácticas, Internaciones). Si alguna falla, no se modifica el snapshot existente del período.
- Persistencia de snapshots por período para prácticas e internaciones asociadas a profesional y catálogo de opciones/sucursales.
- Configuración de tarifas unitarias en Parametrización → Producción para Prácticas e Internaciones.
- Criterio de elegibilidad unificado:
  - Profesional con módulos: contabiliza y valoriza todos los bonos (todos los servicios), prácticas e internaciones.
  - Profesional sin módulos: contabiliza únicamente bonos de servicios especiales (`DEA`, `DEP`, `CAP`, `CAI`), prácticas e internaciones.
- Sumatoria en **Total producción** y **Total general** de la grilla de Capital Humano.
- Desglose detallado de Bonos, Prácticas e Internaciones en el modal **Detalle** y en los reportes exportables XLS.
- Corrección de UI en formulario de Carga para evitar superposición entre Servicio y Fecha de realización.

### Out of Scope
- Carga manual de cantidades de prácticas e internaciones desde la UI (exclusivo vía sync).
- Modificación de snapshots cuando el período esté cerrado (`closed`).

## Approach

1. **Config & Settings**: Agregar `NOVEDADES_BONOS_PRACTICAS_URL` y `NOVEDADES_BONOS_INTERNACIONES_URL` con sus timeouts.
2. **Models & Migración**: Crear modelos de snapshot para cantidades de prácticas e internaciones por período, o unificar bajo la estructura de producción.
3. **Sync Service Atómico**: Al ejecutar `import_bonos_for_periodo`, realizar los 3 fetches antes de cualquier mutación DB. Si todos son válidos, reemplazar los snapshots en una única transacción.
4. **Valorización & Grilla**: En `build_capital_humano_rows`, calcular totales aplicando tarifas y reglas de elegibilidad.
5. **UI & Exportación**: Actualizar el modal Detalle con secciones claras (Cargas, Bonos, Prácticas, Internaciones, Ajustes) y las columnas correspondientes en exportaciones XLS.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/core/config.py` | Modified | Nuevas variables de entorno |
| `backend/app/models/novedades.py` | Modified | Modelos de persistencia para prácticas e internaciones |
| `backend/alembic/versions/` | New | Migración de base de datos |
| `backend/app/services/novedades/` | Modified | `bonos_import.py`, `capital_humano.py`, `produccion_tarifas.py`, `export_xls.py` |
| `frontend/src/pages/novedades/NovedadesXlsPage.jsx` | Modified | Modal Detalle y banner de actualización |
| `docs/runbook.md`, `.env*.example` | Modified | Documentación de nuevas variables |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Alguna API externa caída al actualizar | Low | Transacción atómica fail-closed que preserva el snapshot previo |
| Formato de clave o sucursal no reconocido | Low | Normalización defensiva con log y conteo en items ignorados |

## Rollback Plan

Revertir commit de backend/frontend y aplicar `alembic downgrade -1`.

## Success Criteria

- [ ] "Actualizar" consulta las 3 APIs bajo el mismo rango de fechas del período.
- [ ] Si falla cualquiera de las 3 APIs, no se altera ningún snapshot.
- [ ] Se configuran tarifas en Producción para prácticas e internaciones.
- [ ] Se respeta la regla de elegibilidad (módulos o DEA/DEP/CAP/CAI) para valorizar.
- [ ] El modal Detalle muestra el desglose completo de cargas, bonos, prácticas e internaciones.

