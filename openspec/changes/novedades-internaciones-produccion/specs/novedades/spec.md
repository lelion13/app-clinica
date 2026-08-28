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

### Requirement: Valorización y regla de elegibilidad de Prácticas e Internaciones

In Capital Humano, imported prácticas and internaciones MUST be valorized as `cantidad × valor_unitario`.

**Eligibility rule:** The valorized prácticas and internaciones amounts MUST ONLY be added to the professional's total if:
1. The professional has at least one **módulo asignado** in the period, OR
2. The professional or the item's service belongs to `{DEA, DEP, CAP, CAI}`.

If the professional has only novedades (horas extras) and no special service association, prácticas and internaciones MUST NOT be valorized into their total.

The valorized amounts MUST be added to **Total producción** and **Total general** in the Capital Humano grid, and MUST be clearly itemized in the **Detalle** modal (secciones separadas para Cargas, Bonos, Prácticas, Internaciones y Ajustes) and in XLS exports.

#### Scenario: Profesional con módulo contabiliza ambas
- GIVEN profesional con 1 módulo asignado en el período, 10 prácticas y 2 internaciones
- WHEN se calcula la fila de Capital Humano
- THEN su Total producción incluye el monto de bonos + prácticas valorizadas + internaciones valorizadas

#### Scenario: Profesional sin módulos ni servicio especial
- GIVEN profesional solo con horas extras y sin servicios especiales
- WHEN se calcula la fila de Capital Humano
- THEN prácticas e internaciones no suman a su Total producción

#### Scenario: Servicio especial contabiliza sin módulos
- GIVEN profesional sin módulos pero con registros en servicio especial `CAP`
- WHEN se calcula Capital Humano
- THEN las prácticas e internaciones se contabilizan y el profesional aparece en la grilla principal
