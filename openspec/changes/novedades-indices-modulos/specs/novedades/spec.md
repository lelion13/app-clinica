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

### Requirement: Índices por servicio

For the selected period, each service row with activity MUST expose:

| Column | Definition |
|--------|------------|
| Servicio | Service name |
| Horas | Net sum of novedad `horas` in that service: types `hora_extra` and `hora_extra_por_ausencia` add; `horas_a_descontar` subtracts. Module assignments MUST NOT contribute hours. |
| Monto | Sum of carga `valor` (module assignments + novedades) for that `servicio_id` **plus** sum of Capital Humano adjustments with the same non-null `servicio_id`. MUST NOT include producción/bonos. MUST NOT include adjustments with `servicio_id` null. |
| Profesionales | Count of distinct professionals with ≥1 carga (módulo or novedad) in that service/period. |
| Módulos | Count of module **assignments** (carga rows) in that service/period. |

Producción MUST NOT be shown as a service metric (omit column or show — only; MUST NOT allocate professional producción to services).

A service has activity if it has ≥1 carga in the period (modules and/or novedades). Services with only null-service adjustments MUST NOT appear solely for that reason.

#### Scenario: Horas netas novedades

- GIVEN servicio con novedad 4h extra y 1h a descontar en el período
- WHEN se calcula Índices
- THEN Horas MUST ser 3

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
| Horas | Net sum of that professional’s novedad `horas` across services (same sign rules as por servicio). |
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
