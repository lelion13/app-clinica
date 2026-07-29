# Delta: novedades

## ADDED Requirements

### Requirement: Mis profesionales (ABM scoped)

The system MUST provide a Novedades menu entry (e.g. “Mis profesionales”) visible to `admin`, `rrhh`, and `jefe_medico`. Users MUST be able to associate and disassociate active professionals to services:

- `jefe_medico`: ONLY services linked to that jefe.
- `admin` / `rrhh`: all services.

Associating MUST offer active professionals from the local catalog with **typeahead search** (filter as the user types; show matching results), excluding those already linked to the selected service. The UX MUST follow the existing clinic pattern (`ProfessionalCombobox`: match on name and related identifiers such as document/license when present). Disassociating MUST always be allowed (soft-delete of the link) even if cargas exist; historical cargas MUST remain; the professional MUST no longer appear for new cargas on that service.

Parametrización MAY keep its existing profesional↔servicio tab for admin/rrhh; if that tab retains a professional picker, it SHOULD use the same typeahead behavior.

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
- AND las cargas existentes permanecen visibles según reglas de listado
- AND P ya no se ofrece para nuevas cargas en S1

### Requirement: Fecha de realización en cargas

Module assignments and novedades MUST require `fecha_realizacion` (calendar date): the day the module/novedad occurred. On create and update (while period open), the date MUST satisfy:

1. `periodo.fecha_inicio` ≤ `fecha_realizacion` ≤ `periodo.fecha_fin`
2. `fecha_realizacion` ≤ today (load day; no future dates)

Carga UI MUST use a date control (calendar/date picker). While the period is open, `admin` and scoped `jefe_medico` MUST be able to update `fecha_realizacion`. While closed, updates MUST be rejected.

Grilla Carga and XLS/export MUST include **both** “Fecha realización” and “Fecha carga” (`created_at`).

#### Scenario: Fecha fuera del período

- GIVEN período abierto 2026-07-01..2026-07-31
- WHEN se carga con `fecha_realizacion` = 2026-06-15
- THEN MUST fail validation

#### Scenario: Fecha futura

- GIVEN hoy = 2026-07-29 y período que incluye 2026-07-30
- WHEN se carga con `fecha_realizacion` = 2026-07-30
- THEN MUST fail validation

#### Scenario: Editar fecha con período abierto

- GIVEN carga existente en período abierto y usuario admin o jefe con alcance
- WHEN actualiza `fecha_realizacion` a una fecha válida
- THEN MUST succeed

#### Scenario: Editar fecha con período cerrado

- GIVEN carga en período cerrado
- WHEN se intenta actualizar `fecha_realizacion`
- THEN MUST be rejected

## MODIFIED Requirements

### Requirement: Dos flujos de carga

(Previously: módulo and/or novedad without realization date.)

Create payloads for module assignment and novedad MUST include required `fecha_realizacion` under the validation rules above. Submit UX (clear form fields after success) MUST also clear or reset the date control per product UX (MAY default to today if still valid).

When selecting the professional on the Carga form, the UI SHOULD use the same typeahead pattern as Mis profesionales / `ProfessionalCombobox` (filter matches while typing) over the professionals already linked to the selected service — not a plain unfiltered `<select>` when the list is long.

### Requirement: Listado de cargas en Carga

The unified grid MUST include a **Fecha realización** column in addition to fecha de carga / created_at, with filter/sort support consistent with other columns.

### Requirement: Grilla y XLS (Generación)

Export and RRHH grid MUST add column **Fecha realización** alongside existing **Fecha carga**.
