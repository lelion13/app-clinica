# Delta Spec: novedades-param-recalculo

## ADDED Requirements

### Requirement: Pestaña Recálculo en Parametrización

Parametrización Novedades MUST include a tab **Recálculo** immediately **after** **Feriados**. The tab MUST be available to the same roles that access Parametrización (`admin` and `rrhh`). Other roles MUST NOT see or use Recálculo.

#### Scenario: Orden de tabs

- GIVEN `admin` o `rrhh` en Parametrización
- WHEN mira las tabs
- THEN MUST ver **Recálculo** inmediatamente después de **Feriados**

#### Scenario: Solo roles Param

- GIVEN usuario `jefe_medico`
- WHEN navega Novedades
- THEN MUST NOT acceder a Parametrización / Recálculo

### Requirement: Recálculo de importes de cargas por período

From the Recálculo tab, `admin`/`rrhh` MUST select:

1. **Período** — open or closed (required)
2. **Modo** — exactly one of: **solo horas** | **solo módulos** | **ambos**

The operation MUST consider all non-soft-deleted cargas of that period that match the mode:
- **Módulos**: asignaciones de módulo (`modulo_asignado`) del período
- **Horas**: novedades con tipo de horas (`hora_extra`, `hora_extra_por_ausencia`, `horas_a_descontar`) del período

Soft-deleted cargas MUST be excluded from preview and apply.

#### Scenario: Período cerrado permitido

- GIVEN período cerrado con cargas
- WHEN admin elige ese período y modo ambos
- THEN MUST poder pedir vista previa

#### Scenario: Soft-delete excluido

- GIVEN una asignación soft-deleted en el período
- WHEN corre preview de módulos
- THEN esa fila MUST NOT entrar en el resumen ni en el apply

### Requirement: Vista previa y confirmación de Recálculo

The UI MUST follow: filtros → **Vista previa** → resumen → **Confirmar actualización**.

The preview MUST show:

- **Por cada módulo de catálogo** involucrado: importe total actual (suma de valores persistidos de asignaciones de ese módulo) vs importe total nuevo (suma de valores recalculados)
- **Bloque horas** (si el modo incluye horas): importe total actual vs importe total nuevo de todas las novedades de horas del período

A row “changes” when the recalculated importe differs from the persisted importe.

If the preview finds **zero** changing rows, **Confirmar actualización** MUST be blocked (or reject apply) with a clear message that there are no changes.

Confirm MUST persist the new importes only on rows that change. Rows already equal to the recalculated value MUST NOT be rewritten unnecessarily (MAY no-op).

#### Scenario: Preview con cambios

- GIVEN catálogo de módulo subió de 1000 a 1200 y hay 2 asignaciones de ese módulo en el período
- WHEN admin pide vista previa (modo módulos)
- THEN el resumen de ese módulo MUST mostrar actual 2000 vs nuevo 2400 (u equivalentes con plus si aplica)
- AND Confirmar MUST estar habilitado

#### Scenario: Sin cambios bloquea

- GIVEN ningún valor de catálogo/`valor_hora` difiere de lo persistido
- WHEN admin pide vista previa
- THEN MUST indicarse que no hay cambios
- AND Confirmar MUST NOT aplicar actualizaciones

#### Scenario: Flujo dos pasos

- GIVEN preview con cambios
- WHEN admin aún no confirma
- THEN MUST NOT haberse persistido ningún cambio
- AND al confirmar MUST persistirse los nuevos importes

### Requirement: Reglas de valor al recalcular

**Módulos:** the new persisted `valor` for each assignment MUST be computed with the **same rules as create carga** from the current module catalog value, including especialista plus (×1.20) when that rule applies for the professional/service at recalc time.

**Horas:** the quantity `horas` on each novedad row MUST NOT change. The new importe MUST be `novedad_valor_calculado(tipo, horas, valor_hora)` using the service’s **current** `valor_hora` (negative for `horas_a_descontar`).

#### Scenario: Plus especialista en módulo

- GIVEN asignación a profesional/servicio que aplica plus y catálogo módulo = 1000
- WHEN se recalcula
- THEN el nuevo valor MUST ser 1200 (misma regla que al cargar)

#### Scenario: Horas mantiene cantidad

- GIVEN novedad 3h extra en servicio con valor_hora que pasó de 1000 a 1100
- WHEN se recalcula horas
- THEN horas MUST seguir siendo 3
- AND el importe MUST pasar de 3000 a 3300

## MODIFIED Requirements

### Requirement: Servicios y módulos (Param tabs)

(Previously: Param tabs include Producción between Módulos and Jefes; no Recálculo tab.)

In addition to existing Parametrización tabs, the tab list MUST include **Recálculo** immediately after **Feriados**, as defined in Requirement “Pestaña Recálculo en Parametrización”.

#### Scenario: Recálculo en el listado de tabs

- GIVEN admin en Parametrización
- WHEN lista tabs
- THEN MUST incluir Recálculo después de Feriados
