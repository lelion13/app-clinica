# Delta for novedades

## ADDED Requirements

### Requirement: Importación múltiple de producción externa (Bonos, Prácticas e Internaciones)

When the user clicks **Actualizar** in **Capital Humano** (`admin`/`rrhh`), the system MUST fetch from 3 external APIs:
1. `NOVEDADES_BONOS_RESUMEN_URL`: Bonos resumen.
2. `NOVEDADES_BONOS_PRACTICAS_URL`: Prácticas traumatológicas (`centro`, `servicio`, `profesional`, `cantidad`).
3. `NOVEDADES_BONOS_INTERNACIONES_URL`: Internaciones (`profesional`, `sucursal`, `cantidad_internaciones`).

All calls MUST use the same Bearer token `NOVEDADES_PROF_SYNC_TOKEN` and period date parameters (`fecha_desde` = `fecha_inicio`, `fecha_hasta` = `fecha_fin`).

The sync MUST be **atomic (all-or-nothing)**: if any of the three APIs fails (HTTP error, timeout, malformed payload), the existing period snapshots MUST NOT be modified, and an error MUST be presented to the user.

Imported items MUST be matched to the catalog by `profesional` → `CODPROF`. Duplicates for the same professional and option key MUST sum quantities. Unknown `CODPROF` MUST be ignored and counted in summary.

#### Scenario: Actualización atómica exitosa
- GIVEN período abierto seleccionado en Capital Humano
- WHEN admin pulsa Actualizar
- THEN el sistema consulta las 3 APIs externas (bonos, prácticas, internaciones)
- AND si las 3 responden OK, reemplaza los snapshots del período de forma transaccional
- AND refresca la grilla de Capital Humano con el resumen consolidado

#### Scenario: Fallo de una de las APIs externas
- GIVEN período abierto y snapshots previos en base de datos
- WHEN la API de internaciones falla (o cualquiera de las 3)
- THEN ningún snapshot del período es modificado
- AND la UI muestra un modal de error

### Requirement: Tarifas de Prácticas e Internaciones en Producción

Parametrización tab **Producción** MUST support configuring unit tariffs for:
- Prácticas traumatológicas (opción de catálogo con su tarifa unitaria).
- Internaciones (opción de catálogo con su tarifa unitaria).

Tariffs MUST be integers ≥ 0, editable by `admin`/`rrhh` only.

#### Scenario: Configurar tarifa de prácticas e internaciones
- GIVEN `rrhh` en Parametrización tab Producción
- WHEN asigna valor unitario a la práctica traumatológica y a las internaciones
- THEN Capital Humano valoriza las cantidades correspondientes con esos valores unitarios

### Requirement: Valorización y regla de elegibilidad de Producción (Bonos, Prácticas e Internaciones)

In Capital Humano, imported bonos, prácticas and internaciones MUST be valorized as `cantidad × valor_unitario`.

**Eligibility rules:**
1. If the professional has at least one **módulo asignado** in the period: ALL bonos, prácticas, and internaciones are counted and valorized in their total.
2. If the professional does NOT have any **módulo asignado** in the period:
   - Bonos: ONLY options belonging to `{DEA, DEP, CAP, CAI}` are counted and valorized (bonos of other services like `GUA` are omitted from the valorized total and from the professional's table in Capital Humano).
   - Prácticas: ONLY items belonging to `{DEA, DEP, CAP, CAI}` are counted and valorized.
   - Internaciones: Counted and valorized if the professional has at least one eligible bono or práctica in `{DEA, DEP, CAP, CAI}`.

If the professional has only novedades (horas extras) and no special service association, bonos, prácticas and internaciones MUST NOT be valorized into their total.

The valorized amounts MUST be added to **Total producción** and **Total general** in the Capital Humano grid, and MUST be clearly itemized in the **Detalle** modal (secciones separadas para Cargas, Bonos, Prácticas, Internaciones y Ajustes) and in XLS exports.

#### Scenario: Profesional con módulo contabiliza todos los servicios
- GIVEN profesional con 1 módulo asignado en el período, bonos en GUA y CAP, 10 prácticas y 2 internaciones
- WHEN se calcula la fila de Capital Humano
- THEN su Total producción incluye todos los bonos (GUA y CAP) + prácticas valorizadas + internaciones valorizadas

#### Scenario: Profesional sin módulos solo contabiliza servicios especiales
- GIVEN profesional sin módulos asignados, con 1 bono en CAP, 193 bonos en GUA y 3 internaciones
- WHEN se calcula la fila de Capital Humano
- THEN solo se valoriza el bono de CAP ($6.000) y las 3 internaciones ($15.000)
- AND los 193 bonos de GUA no se contabilizan ni valorizan en la grilla principal de Capital Humano

#### Scenario: Profesional sin módulos ni servicio especial
- GIVEN profesional solo con horas extras y sin servicios especiales
- WHEN se calcula la fila de Capital Humano
- THEN prácticas e internaciones no suman a su Total producción
