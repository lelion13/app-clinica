# Novedades Specification

## Purpose

Dominio de carga de módulos/novedades por servicio, parametrización y export XLS con control de período.

## Requirements

### Requirement: Navegación Novedades

The system MUST show a top-level **Novedades** dropdown (like Distribución) with: Carga módulos, Generación archivo XLS, Parametrización. Visibility MUST follow RBAC. `operador` MUST NOT see Novedades.

#### Scenario: Admin ve Novedades

- GIVEN usuario `admin` autenticado
- WHEN abre el panel
- THEN ve Novedades con las tres subopciones

#### Scenario: Operador sin Novedades

- GIVEN usuario `operador`
- WHEN abre el panel
- THEN NO ve Novedades
- AND rutas `/novedades/*` MUST bloquearse (UI + API 403)

### Requirement: Roles

The system MUST support roles `admin`, `operador`, `jefe_medico`, `rrhh`. Users ABM MUST allow assigning the new roles. API authorization MUST enforce the matrix in `decisions.md`.

#### Scenario: Jefe solo sus servicios

- GIVEN `jefe_medico` asociado al servicio S1 (no S2)
- WHEN intenta cargar novedad en profesional de S2
- THEN la API MUST reject (403/422)

### Requirement: Servicios y módulos

The system MUST provide ABM of **servicios** (id, nombre, activo) and **módulos** (id, descripción, comentario, valor ARS). Admin and `rrhh` MUST manage them; `jefe_medico` MUST NOT.

#### Scenario: Alta módulo

- GIVEN `rrhh` autenticado
- WHEN crea módulo con descripción y valor
- THEN queda disponible como concepto de novedad

### Requirement: Asociación jefe↔servicio

The system MUST support many-to-many jefe_medico↔servicio. Admin/`rrhh` MUST manage associations.

#### Scenario: Varios jefes en un servicio

- GIVEN servicio S1
- WHEN se asocian dos jefes
- THEN ambos MAY cargar en profesionales de S1

### Requirement: Profesional↔servicio

A professional MUST be linkable to many services (for Novedades scope). Listing professionals for carga MUST come from a swappable provider (v1: existing `professionals`).

### Requirement: Dos flujos de carga

The system MUST support separately: (1) assign catalog modules to a professional; (2) create a novedad with concept=module FK, valor ARS, required justification. Only `admin` and `jefe_medico` (scoped) MUST create/edit/soft-delete while period is open.

#### Scenario: Novedad sin justificación

- GIVEN período abierto y módulo válido
- WHEN se intenta guardar novedad sin justificación
- THEN MUST fail validation

#### Scenario: Concepto fuera de catálogo

- GIVEN request con module_id inexistente
- WHEN se crea novedad
- THEN MUST fail validation

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

### Requirement: Grilla y XLS

Admin/`rrhh` MUST view a searchable grid and download XLS with columns: período, servicio, profesional, tipo (módulo asignado/novedad), módulo/concepto, valor, justificación, cargado por, fecha carga. Filters MUST include período, servicio, profesional text, módulo/concepto. Download MUST succeed only with valid auth; period-close rules MUST still apply to writes (not to read/export).

#### Scenario: RRHH exporta XLS

- GIVEN `rrhh` con cargas existentes
- WHEN aplica filtros y descarga XLS
- THEN receives a file with the agreed columns

#### Scenario: Jefe sin grilla

- GIVEN `jefe_medico`
- WHEN navega a Generación XLS
- THEN MUST be denied (UI + API)
