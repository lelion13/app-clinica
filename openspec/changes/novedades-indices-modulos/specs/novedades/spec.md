# Delta Spec: novedades-indices-modulos

## ADDED Requirements

### Requirement: Navegación Índices (admin)

The Novedades Home menu MUST include **Índices** as the **last** item, visible only to role **`admin`**. The item MUST route to `/novedades/indices`.

Non-admin roles (`rrhh`, `jefe_medico`, `operador`, unauthenticated) MUST NOT see the item. Direct navigation to the route MUST be rejected or redirected the same way other admin-only Novedades screens are protected. Backend endpoints for Índices MUST require `admin` (MUST NOT accept `rrhh`).

#### Scenario: Admin ve Índices al final

- GIVEN usuario `admin` en Home
- WHEN mira el bloque Novedades
- THEN MUST ver Índices como último ítem
- AND al abrirlo MUST navegar a `/novedades/indices`

#### Scenario: RRHH no ve Índices

- GIVEN usuario `rrhh`
- WHEN mira Novedades
- THEN MUST NOT ver Índices

### Requirement: Pantalla Índices por período

Índices MUST require a selected **período** (open or closed). Without a period selected, metric grids MUST be empty or controls disabled (MUST NOT invent rows).

The page MUST show two stacked sections on the same screen:
1. **Por servicio**
2. **Por profesional**

Rows MUST appear only when the entity has **activity** in that period (see section requirements). Rows MUST be ordered by name A→Z. Soft-deleted cargas and adjustments MUST be excluded.

Export (Excel/CSV) is out of scope.

#### Scenario: Sin período

- GIVEN admin en Índices sin período seleccionado
- WHEN carga la pantalla
- THEN MUST NOT mostrar filas de métricas

#### Scenario: Período abierto o cerrado

- GIVEN período abierto o cerrado con actividad
- WHEN admin lo selecciona
- THEN MUST calcular métricas de ese período

### Requirement: Horas en catálogo de módulos

Each Novedades **módulo** MUST have an integer attribute **`horas`**: the number of hours the module includes.

Migration MUST add the column as **nullable** and leave existing modules with `horas=NULL` (empty).

**Create** (`POST /modulos` and Param **Nuevo módulo**) and **Update** (`PUT /modulos/{id}` and Param edit) MUST require `horas` as an integer **≥ 1**. Missing, non-integer, or &lt; 1 MUST be rejected (422). The Param UI MUST expose the field and MUST NOT allow save without a valid value on create or edit.

Bulk Excel import/template for modules is **out of scope** for this change (MUST NOT be required to add `horas` to import in this change).

#### Scenario: Migración deja vacíos

- GIVEN módulos existentes antes del change
- WHEN corre la migración
- THEN `horas` MUST ser NULL en esos registros

#### Scenario: Alta exige horas

- GIVEN `rrhh`/`admin` en Nuevo módulo
- WHEN intenta guardar sin `horas` o con 0
- THEN MUST rechazarse
- AND el módulo MUST NOT crearse

#### Scenario: Edición exige horas

- GIVEN módulo con `horas` NULL
- WHEN admin edita y guarda sin completar horas válidas
- THEN MUST rechazarse
- AND al guardar con horas=4 MUST persistirse 4

### Requirement: Índices por servicio

For the selected period, each service row with activity MUST expose:

| Column | Definition |
|--------|------------|
| Servicio | Service name |
| Horas | Sum of catalog `módulo.horas` for each module **assignment** in that service (`NULL` → 0) **plus** net sum of novedad `horas` in that service (`hora_extra` / `hora_extra_por_ausencia` add; `horas_a_descontar` subtracts). |
| Monto | Sum of carga `valor` (module assignments + novedades) for that `servicio_id` **plus** sum of Capital Humano adjustments with the same non-null `servicio_id`. MUST NOT include producción/bonos. MUST NOT include adjustments with `servicio_id` null. |
| Profesionales | Count of distinct professionals with ≥1 carga (módulo or novedad) in that service/period. |
| Módulos | Count of module **assignments** (carga rows) in that service/period. |

Producción MUST NOT be shown as a service metric (omit column or show — only; MUST NOT allocate professional producción to services).

A service has activity if it has ≥1 carga in the period (modules and/or novedades). Services with only null-service adjustments MUST NOT appear solely for that reason.

#### Scenario: Horas módulos + novedades

- GIVEN servicio con 2 asignaciones de un módulo con `horas=3`, y novedad 4h extra y 1h a descontar
- WHEN se calcula Índices
- THEN Horas MUST ser 3+3+4−1 = 9

#### Scenario: Módulo sin horas cuenta 0

- GIVEN asignación de módulo con `horas` NULL y novedad 2h extra
- WHEN se calcula Horas del servicio
- THEN MUST ser 2

#### Scenario: Monto sin producción ni ajuste global

- GIVEN servicio con cargas 1000, ajuste `servicio_id`=ese servicio −100, ajuste sin servicio −50, producción profesional 200
- WHEN se calcula monto del servicio
- THEN Monto MUST ser 900
- AND MUST NOT incluir 200 ni −50

#### Scenario: Profesionales y módulos

- GIVEN dos profesionales con módulos en el servicio (3 asignaciones en total) y uno solo con producción
- WHEN se lista el servicio
- THEN Profesionales MUST ser 2
- AND Módulos MUST ser 3

### Requirement: Índices por profesional

For the selected period, each professional row with activity MUST expose:

| Column | Definition |
|--------|------------|
| Profesional | Display name (and legajo MAY be shown) |
| Horas | Sum of catalog `módulo.horas` for that professional’s module assignments (`NULL` → 0) **plus** net sum of that professional’s novedad `horas` (same sign rules as por servicio). |
| Módulos | Count of module assignments for that professional in the period. |
| Producción (monto) | Same ARS total as Capital Humano producción for that professional/period (eligible bonos + prácticas + internaciones under existing CH eligibility rules). |
| Producción (cantidad) | Sum of quantities of those same eligible producción items. |

A professional has activity if they have ≥1 carga **or** non-zero eligible producción in the period.

Monto total CH and “profesionales” count are out of scope for this section.

#### Scenario: Profesional con producción sin cargas

- GIVEN profesional solo con producción elegible > 0 y sin cargas
- WHEN se lista por profesional
- THEN MUST aparecer con Módulos 0 y Horas 0
- AND Producción monto/cantidad MUST reflejar CH

#### Scenario: Producción alineada a CH

- GIVEN mismos snapshots/tarifas que Capital Humano para el período
- WHEN se muestra Producción (monto) en Índices
- THEN MUST coincidir con el monto de producción de la grilla CH para ese profesional

#### Scenario: Horas profesional con módulo

- GIVEN profesional con una asignación de módulo `horas=5` y novedad 2h a descontar
- WHEN se calcula Horas
- THEN MUST ser 5−2 = 3

## MODIFIED Requirements

### Requirement: Servicios y módulos

(Previously: módulos fields include descripción, comentario, valor, produccion, tipo_dia; create/update without `horas`.)

In addition to existing module fields, modules MUST expose **`horas`** as defined in Requirement “Horas en catálogo de módulos”. Create and update of modules MUST validate and persist `horas` (integer ≥ 1). List/detail API responses MUST include `horas` (nullable for legacy rows until edited).

#### Scenario: API expone horas

- GIVEN módulo creado con horas=8
- WHEN se lista módulos
- THEN la respuesta MUST incluir `horas: 8`
