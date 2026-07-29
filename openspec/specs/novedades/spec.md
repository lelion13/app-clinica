# Novedades Specification

## Purpose

Dominio de carga de módulos/novedades por servicio, parametrización y export XLS con control de período.

## Requirements

### Requirement: Navegación Novedades

The system MUST show a top-level **Novedades** dropdown with at least: Carga módulos, Mis profesionales, Generación archivo XLS, Parametrización. Visibility MUST follow RBAC. `operador` MUST NOT see Novedades.

#### Scenario: Admin ve Novedades

- GIVEN usuario `admin` autenticado
- WHEN abre el panel
- THEN ve Novedades con las subopciones permitidas a admin

#### Scenario: Operador sin Novedades

- GIVEN usuario `operador`
- WHEN abre el panel
- THEN NO ve Novedades
- AND rutas `/novedades/*` MUST bloquearse (UI + API 403)

### Requirement: Roles

The system MUST support roles `admin`, `operador`, `jefe_medico`, `rrhh`. Users ABM MUST allow assigning the new roles. API authorization MUST enforce the Novedades RBAC matrix (admin/jefe carga; jefe+admin+rrhh Mis profesionales; rrhh/admin param+XLS; operador sin Novedades).

#### Scenario: Jefe solo sus servicios (escritura)

- GIVEN `jefe_medico` asociado al servicio S1 (no S2)
- WHEN intenta cargar novedad en profesional de S2
- THEN la API MUST reject (403/422)

#### Scenario: Jefe solo sus servicios (listado)

- GIVEN `jefe_medico` asociado solo a S1
- AND existen cargas en S1 y S2
- WHEN lista asignaciones o novedades
- THEN MUST ver solo las de S1
- AND el orden por defecto MUST ser servicio → profesional

### Requirement: Servicios y módulos

The system MUST provide ABM of **servicios** (id, nombre, activo, **valor_hora**) and **módulos** (id, descripción, comentario, valor ARS) with **N:N** association to services. Admin and `rrhh` MUST manage them; `jefe_medico` MUST NOT.

#### Scenario: Alta módulo asociado a servicios

- GIVEN `rrhh` autenticado
- WHEN crea módulo con descripción, valor y uno o más `servicio_ids`
- THEN queda disponible solo para cargas en esos servicios

#### Scenario: Valor hora por servicio

- GIVEN servicio con `valor_hora = 1000`
- WHEN se carga una novedad de 3 horas en ese servicio
- THEN el valor calculado MUST ser 3000

### Requirement: Asociación jefe↔servicio

The system MUST support many-to-many jefe_medico↔servicio. Admin/`rrhh` MUST manage associations.

#### Scenario: Varios jefes en un servicio

- GIVEN servicio S1
- WHEN se asocian dos jefes
- THEN ambos MAY cargar en profesionales de S1

### Requirement: Profesional↔servicio

A professional MUST be linkable to many services. Listing professionals for carga MUST come from a swappable provider (v1: existing `professionals`) **filtered by servicio**. Carga MUST reject professionals not associated to the selected service.

#### Scenario: Carga sin asociación profesional↔servicio

- GIVEN período abierto y profesional no asociado al servicio
- WHEN se intenta asignar módulo o novedad
- THEN MUST fail validation (422)

### Requirement: Mis profesionales (ABM scoped)

The system MUST provide a Novedades menu entry **Mis profesionales** visible to `admin`, `rrhh`, and `jefe_medico`:

- `jefe_medico`: ONLY services linked to that jefe.
- `admin` / `rrhh`: all services.

Associating MUST offer active professionals from the local catalog with **typeahead** (`ProfessionalCombobox` pattern), excluding those already linked to the selected service. Disassociating MUST always be allowed (soft-delete of the link) even if cargas exist; historical cargas MUST remain; the professional MUST no longer appear for new cargas on that service.

Parametrización MAY keep its profesional↔servicio tab for admin/rrhh with the same typeahead.

API writes for profesional↔servicio MUST use a roster guard that allows admin/rrhh globally and jefe only on scoped services (`assert_can_manage_profesional_servicio`). Do NOT reuse the carga-only `assert_can_load_servicio` for RRHH roster writes.

#### Scenario: Jefe asocia profesional a su servicio

- GIVEN `jefe_medico` asociado a S1
- AND profesional P activo no asociado a S1
- WHEN asocia P a S1 desde Mis profesionales
- THEN P aparece en el listado de Carga para S1

#### Scenario: Typeahead filtra al tipear

- GIVEN catálogo con varios profesionales activos no vinculados al servicio elegido
- WHEN el usuario escribe parte del nombre (o identificador) en el buscador
- THEN la lista MUST mostrar solo los que matchean el texto
- AND MUST actualizarse a medida que tipifica (sin requerir botón “Buscar”)

#### Scenario: Jefe no toca servicio ajeno

- GIVEN `jefe_medico` no asociado a S2
- WHEN intenta asociar o desasociar en S2
- THEN API MUST return 403

#### Scenario: Desasociar con cargas existentes

- GIVEN profesional P con cargas en S1
- WHEN se desasocia P de S1
- THEN el vínculo se soft-deletea
- AND las cargas existentes permanecen
- AND P ya no se ofrece para nuevas cargas en S1

### Requirement: Dos flujos de carga

The system MUST support in one form (módulo opcional y/o novedad opcional, al menos uno):

1. **Asignar módulo de catálogo** al profesional: `modulo_id` FK; valor mostrado solo lectura desde catálogo.
2. **Cargar novedad**: `tipo` ∈ {`hora_extra`, `hora_extra_por_ausencia`} + `horas` entero ≥ 1; valor = horas × valor_hora del servicio.

Create payloads MUST include required `fecha_realizacion` under the fecha rules below. Professional selection on Carga SHOULD use typeahead over linked professionals. Submit MUST clear profesional/módulo/horas/fecha (MAY keep período/servicio; MAY reset fecha to today if still valid).

Only `admin` and `jefe_medico` (scoped) MUST create/edit/soft-delete while period is open.

Validation/API error messages on Novedades screens MUST be shown in an **alert modal** with an **OK** button (not only a red inline label).

#### Scenario: Novedad sin horas válidas

- GIVEN período abierto
- WHEN se intenta guardar novedad con horas no enteras o &lt; 1
- THEN MUST fail validation (UI y/o API)

#### Scenario: Módulo fuera del servicio

- GIVEN módulo no asociado al servicio elegido
- WHEN se asigna ese módulo
- THEN MUST fail validation

#### Scenario: Submit limpia formulario

- GIVEN carga exitosa
- WHEN vuelve la UI
- THEN MUST limpiar profesional, módulo y horas
- AND MAY conservar período y servicio seleccionados

### Requirement: Fecha de realización en cargas

Module assignments and novedades MUST require `fecha_realizacion` (calendar date): the day the fact occurred. On create and update (while period open):

1. `periodo.fecha_inicio` ≤ `fecha_realizacion` ≤ `periodo.fecha_fin`
2. `fecha_realizacion` ≤ today (`BUSINESS_TIMEZONE` calendar day)

Carga UI MUST label Período, Servicio and Fecha realización consistently (aligned controls). Selectable days MUST be `[fecha_inicio, min(fecha_fin, today)]`. If that range is empty (period not started yet), the UI MUST disable/clear the date control and explain; it MUST NOT set HTML `min` &gt; `max`.

While period open, admin/jefe scoped MUST be able to update `fecha_realizacion`. While closed, updates MUST be rejected.

#### Scenario: Fecha fuera del período

- GIVEN período abierto 2026-07-01..2026-07-31
- WHEN se carga con `fecha_realizacion` = 2026-06-15
- THEN MUST fail validation

#### Scenario: Fecha futura

- GIVEN hoy = 2026-07-29 y período que incluye 2026-07-30
- WHEN se carga con `fecha_realizacion` = 2026-07-30
- THEN MUST fail validation

#### Scenario: Período aún no iniciado

- GIVEN hoy = 2026-07-29 y período abierto 2026-08-01..2026-08-31
- WHEN se muestra el date picker
- THEN no MUST haber días seleccionables
- AND la UI MUST explicar que el período aún no está en curso

#### Scenario: Editar fecha con período abierto

- GIVEN carga existente en período abierto y usuario admin o jefe con alcance
- WHEN actualiza `fecha_realizacion` a una fecha válida
- THEN MUST succeed

#### Scenario: Editar fecha con período cerrado

- GIVEN carga en período cerrado
- WHEN se intenta actualizar `fecha_realizacion`
- THEN MUST be rejected

### Requirement: Listado de cargas en Carga

The Carga page MUST show a **unified grid** with columns at least: tipo, servicio, profesional, concepto, horas, valor, **fecha realización**, período, **fecha carga**. Filter/sort by column; default sort servicio → profesional.

Anular MUST use a confirmation modal (Cancelar / Confirmar). Editing fecha (period open) MAY use a dedicated modal.

#### Scenario: Modal anular

- GIVEN fila visible en la grilla
- WHEN el usuario pulsa anular
- THEN MUST ver modal con resumen
- AND Cancelar MUST no borrar
- AND Confirmar MUST anular y refrescar el listado

### Requirement: Período

A period MUST have optional name, start date, end date, and status open/closed. At most ONE open period MUST exist. Admin/`rrhh` MUST close and reopen. While closed, ANY role MUST NOT create/edit/delete module assignments or novedades in that period.

#### Scenario: Segundo período abierto

- GIVEN ya hay un período abierto
- WHEN se intenta abrir otro
- THEN MUST fail

#### Scenario: Carga en cerrado

- GIVEN período cerrado
- WHEN jefe intenta cargar novedad
- THEN MUST be rejected

### Requirement: Grilla y XLS (Generación)

Admin/`rrhh` MUST view a searchable grid and download XLS with columns including: período, servicio, profesional, tipo, concepto, horas, valor hora, valor, cargado por, **fecha realización**, **fecha carga**. Filters: período, servicio, texto, concepto.

#### Scenario: RRHH exporta XLS

- GIVEN `rrhh` con cargas existentes
- WHEN aplica filtros y descarga XLS
- THEN receives a file with the agreed columns

#### Scenario: Jefe sin grilla XLS

- GIVEN `jefe_medico`
- WHEN navega a Generación XLS
- THEN MUST be denied (UI + API)

### Requirement: Alertas UI Novedades

Validation and API error messages on Novedades screens (Carga, Mis profesionales, Parametrización, XLS) MUST be presented in a modal dialog with an explicit **OK** action to dismiss. Inline red labels alone MUST NOT be the primary error presentation for those actions.

#### Scenario: Error de validación en Carga

- GIVEN usuario en Carga con payload inválido (p. ej. fecha fuera de rango)
- WHEN intenta guardar
- THEN MUST ver un modal con el mensaje de error
- AND MUST poder cerrarlo con OK
