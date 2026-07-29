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

The system MUST support roles `admin`, `operador`, `jefe_medico`, `rrhh`. Users ABM MUST allow assigning the new roles. API authorization MUST enforce the matrix in the archived change `novedades-modulos` decisions (admin/jefe carga; rrhh param+XLS; operador sin Novedades).

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

A professional MUST be linkable to many services via ABM in Parametrización. Listing professionals for carga MUST come from a swappable provider (v1: existing `professionals`) **filtered by servicio**. Carga MUST reject professionals not associated to the selected service.

#### Scenario: Carga sin asociación profesional↔servicio

- GIVEN período abierto y profesional no asociado al servicio
- WHEN se intenta asignar módulo o novedad
- THEN MUST fail validation (422)

### Requirement: Dos flujos de carga

The system MUST support in one form (módulo opcional y/o novedad opcional, al menos uno):

1. **Asignar módulo de catálogo** al profesional: `modulo_id` FK; valor mostrado solo lectura desde catálogo.
2. **Cargar novedad**: `tipo` ∈ {`hora_extra`, `hora_extra_por_ausencia`} + `horas` entero ≥ 1; valor = horas × valor_hora del servicio.

Only `admin` and `jefe_medico` (scoped) MUST create/edit/soft-delete while period is open.

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

### Requirement: Listado de cargas en Carga

The Carga page MUST show a **unified grid** of module assignments and novedades with columns at least: tipo, servicio, profesional, concepto, horas, valor, período, fecha. The grid MUST support text filter, tipo filter, servicio filter, and column sort. Default sort MUST be servicio → profesional.

Anular MUST open a **confirmation modal** with a summary of the row; **Cancelar** closes without delete; **Confirmar** soft-deletes the record.

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

Admin/`rrhh` MUST view a searchable grid and download XLS with columns including: período, servicio, profesional, tipo (módulo/novedad), concepto, horas (si aplica), valor hora, valor, cargado por, fecha carga. Filters MUST include período, servicio, texto profesional/servicio, concepto. Download MUST succeed only with valid auth; period-close rules MUST still apply to writes (not to read/export).

#### Scenario: RRHH exporta XLS

- GIVEN `rrhh` con cargas existentes
- WHEN aplica filtros y descarga XLS
- THEN receives a file with the agreed columns

#### Scenario: Jefe sin grilla XLS

- GIVEN `jefe_medico`
- WHEN navega a Generación XLS
- THEN MUST be denied (UI + API)
