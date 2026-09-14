# Delta Spec: novedades-modulos-tipo-dia

## ADDED Requirements

### Requirement: Tipo de día del módulo (`tipo_dia`)

Each módulo MUST have exactly one `tipo_dia` in `{semana, sadofe, valor_unico}`. Default on create MUST be `semana`.

API create/update/list MUST expose `tipo_dia` and MUST NOT expose `sadofe`.

Parametrización create/edit MUST show three mutually exclusive controls labeled **Semana**, **SADOFE**, **Valor único** (left→right). Exactly one MUST remain selected at all times (cannot clear all). Edit MUST preserve the module’s current `tipo_dia`.

Delete/summary UI MUST show `Tipo día: Semana | SADOFE | Valor único` (human labels).

#### Scenario: Alta default Semana

- GIVEN admin abre Nuevo módulo
- WHEN no cambia los checks de tipo día
- THEN Semana MUST estar tildado
- AND al guardar `tipo_dia` MUST ser `semana`

#### Scenario: Exclusividad UI

- GIVEN Semana tildado
- WHEN admin tilda Valor único
- THEN Semana MUST destildarse
- AND solo Valor único MUST quedar activo

#### Scenario: Migración datos

- GIVEN módulo histórico con `sadofe=false` y otro con `sadofe=true`
- WHEN aplica la migración
- THEN el primero MUST quedar `tipo_dia=semana`
- AND el segundo MUST quedar `tipo_dia=sadofe`

## MODIFIED Requirements

### Requirement: Catálogo de servicios y módulos

(Previously: módulos had boolean `sadofe`.)

Módulos MUST include **`tipo_dia`** (`semana` | `sadofe` | `valor_unico`) instead of boolean `sadofe`. Field `produccion` remains independent.

Modules MUST support create/update including `tipo_dia` (default `semana` on create).

### Requirement: Filtro módulos por fecha y feriados

(Previously: filtered only by `sadofe` true/false.)

The Carga module select MUST list only modules valid for the selected `fecha_realizacion`:
- `tipo_dia=semana`: Monday–Friday and the date is **not** a loaded holiday
- `tipo_dia=sadofe`: Saturday, Sunday, **or** a loaded holiday
- `tipo_dia=valor_unico`: **any** `fecha_realizacion` (no Semana/SADOFE restriction)

Validation remains UI-only. Changing the date MUST clear a previously selected module if it is no longer valid.

#### Scenario: Combo filtra SADOFE

- GIVEN feriado 2026-05-25, módulo `sadofe` y módulo `semana` asociados al servicio
- WHEN fecha de realización es 2026-05-25
- THEN el combo MUST incluir el módulo SADOFE
- AND MUST NOT incluir el módulo Semana

#### Scenario: Valor único en cualquier día

- GIVEN módulo `valor_unico` asociado al servicio
- WHEN fecha es un martes no feriado o un domingo
- THEN el combo MUST incluir ese módulo en ambos casos

### Requirement: Plantilla Excel import módulos

(Previously: Producción and SADOFE Sí/No.)

Plantilla MUST include column **`tipo_dia`** with dropdown values exactly `semana`, `sadofe`, `valor_unico` (replacing `sadofe` Sí/No). Producción remains Sí/No.

### Requirement: Carga masiva módulos

(Previously: used `sadofe` Sí/No.)

Import MUST read `tipo_dia`. Empty/missing `tipo_dia` MUST default to `semana`. Invalid `tipo_dia` MUST be a row error and, with any errors, MUST import **no** modules (all-or-nothing). Remaining import rules (servicio, descripción, valor vacío→0, etc.) MUST stay unchanged.
