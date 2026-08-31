# Archive Report: novedades-internaciones-produccion

## Change Summary
- **Change Name:** `novedades-internaciones-produccion` (Prácticas traumatológicas e internaciones en Producción de Capital Humano)
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-08-28

## Delivered Capabilities
1. **Multi-API Sync atómico:**
   - Botón **Actualizar** en Capital Humano consulta en simultáneo/secuencia:
     - Bonos resumen (`NOVEDADES_BONOS_RESUMEN_URL`)
     - Prácticas traumatológicas (`NOVEDADES_BONOS_PRACTICAS_URL`)
     - Internaciones (`NOVEDADES_BONOS_INTERNACIONES_URL`)
   - Mismo token Bearer (`NOVEDADES_PROF_SYNC_TOKEN`) y rango `fecha_desde`/`fecha_fin` del período abierto.
   - Transaccionalidad fail-closed: ante error o timeout en cualquiera de las 3 APIs, se aborta sin tocar snapshots previos.
2. **Tablas de Snapshot y Migración:**
   - `novedades_practica_cantidad` (`periodo_id`, `professional_id`, `centro`, `servicio`, `cantidad`).
   - `novedades_internacion_cantidad` (`periodo_id`, `professional_id`, `sucursal`, `cantidad`).
   - Migración Alembic: `0024_practicas_internaciones.py`.
3. **Tarifas en Parametrización → Producción:**
   - Opciones garantizadas y protegidas de cleanup: "Práctica traumatológica" e "Internaciones".
   - Valor unitario configurable por `admin`/`rrhh`.
4. **Reglas de Elegibilidad y Valorización:**
   - Profesional **con módulos**: cuenta todos los bonos (todos los servicios), todas las prácticas y todas las internaciones.
   - Profesional **sin módulos**: cuenta únicamente bonos de servicios especiales (`DEA`, `DEP`, `CAP`, `CAI`); cuenta todas sus prácticas y todas sus internaciones. Bonos de otros servicios (ej. `GUA`) se omiten del total y de su desglose en Capital Humano.
5. **UI & Exportaciones:**
   - Modal Detalle con secciones específicas para Prácticas e Internaciones con cantidades, tarifas unitarias y subtotales.
   - Formulario de Carga ajustado con layout responsive para evitar superposición visual de Período, Servicio y Fecha.
   - Exportaciones XLS sincronizadas con el nuevo `monto_total` y columnas dinámicas.

## Test & Build Verification
- Backend tests: `143 passed` (`pytest`)
- Frontend build: `vite build` completado exitosamente sin errores.
