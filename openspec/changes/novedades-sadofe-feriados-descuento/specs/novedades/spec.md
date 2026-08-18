# Delta: novedades / SADOFE, feriados, horas a descontar, concepto liquidación

## MODIFIED Requirements

### Requirement: Servicios y módulos

Modules MUST include boolean **sadofe** (checkbox SADOFE; off = Semana). Existing `produccion` MUST remain independent. Existing rows MUST default `sadofe=false`.

Servicios MUST include optional integer **concepto_liquidacion** (label “Concepto liquidación”). Empty or `0` MUST persist as `NULL`. A non-zero value MUST be an integer ≥ 1 (no extra upper bound). Duplicate values across servicios MUST be allowed. Admin/`rrhh` MUST manage servicios in Parametrización like Módulos: grid, **Nuevo servicio** modal (Cancelar/Cargar; always `activo=true`), edit modal (nombre, valor hora, concepto, **Activo**), confirm-delete modal; Escape cancels. Inline `valor_hora` edit MUST be removed. The grid MUST keep `#id · nombre · activo` and show concepto (`NULL` → “—”).

#### Scenario: Alta módulo SADOFE

- GIVEN `rrhh` en Nuevo módulo
- WHEN marca SADOFE y carga
- THEN el módulo se persiste con `sadofe=true`

#### Scenario: Alta servicio con concepto

- GIVEN `rrhh` en Nuevo servicio
- WHEN carga nombre, valor hora y concepto `101`
- THEN el servicio queda activo con `concepto_liquidacion=101`

#### Scenario: Concepto vacío o cero

- GIVEN `rrhh` creando o editando un servicio
- WHEN deja concepto vacío o ingresa `0`
- THEN MUST persistirse `NULL`

### Requirement: Dos flujos de carga

**Cargar novedad** tipos MUST include `hora_extra`, `hora_extra_por_ausencia`, and `horas_a_descontar` (“Horas a descontar”). For `horas_a_descontar`, valor calculado MUST be `-(horas × valor_hora del servicio)`. Other tipos remain positive. Negative values MUST appear in Carga grid, XLS, and Capital Humano aggregates.

#### Scenario: Horas a descontar resta

- GIVEN servicio `valor_hora = 1000`
- WHEN se carga novedad tipo horas a descontar de 3 horas
- THEN valor calculado MUST ser -3000

### Requirement: Fecha de realización en cargas

The Carga module select MUST list only modules valid for the selected `fecha_realizacion`:
- Semana (`sadofe=false`): Monday–Friday and the date is **not** a loaded holiday
- SADOFE (`sadofe=true`): Saturday, Sunday, **or** a loaded holiday

Validation of this rule is UI-only for this change. Changing the date MUST clear a previously selected module if it is no longer valid.

#### Scenario: Combo filtra SADOFE

- GIVEN feriado 2026-05-25 y módulo SADOFE asociado al servicio
- WHEN fecha de realización es 2026-05-25
- THEN el combo MUST incluir el módulo SADOFE
- AND MUST NOT incluir módulos Semana de ese servicio

## ADDED Requirements

### Requirement: Feriados Novedades

The system MUST provide global holidays (`fecha` + `nombre` required). Admin/`rrhh` MUST manage them in Parametrización tab **Feriados** (next to Períodos): list grid, **Nuevo feriado** modal (Cancelar/Cargar), edit and confirm-delete modals like Módulos (Escape cancels). Duplicate active dates MUST be rejected. `jefe_medico` MUST be able to read holidays for Carga filtering but MUST NOT manage them.

#### Scenario: Alta feriado

- GIVEN `rrhh` autenticado
- WHEN crea feriado con fecha y nombre
- THEN aparece en la grilla y cuenta como SADOFE en Carga

#### Scenario: Fecha duplicada

- GIVEN feriado activo en 2026-12-25
- WHEN se intenta crear otro con la misma fecha
- THEN MUST fail (409)
