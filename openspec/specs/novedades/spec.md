# Novedades Specification

## Purpose

Dominio de carga de módulos/novedades por servicio, parametrización, Capital Humano (agregados + ajustes) y export XLS con control de período.

## Requirements

### Requirement: Navegación Novedades

The system MUST show a top-level **Novedades** dropdown with at least: Carga módulos, Mis profesionales, Capital Humano, Parametrización. Visibility MUST follow RBAC. `operador` MUST NOT see Novedades.

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

A professional from the **Novedades catalog** (`novedades_profesional`, sync HTTP) MUST be linkable to many services. Listing for carga MUST use that catalog only (**not** Distribución `professionals`), filtered by servicio and **active**. Carga MUST reject professionals not associated to the selected service or inactive.

#### Scenario: Carga sin asociación profesional↔servicio

- GIVEN período abierto y profesional no asociado al servicio
- WHEN se intenta asignar módulo o novedad
- THEN MUST fail validation (422)

#### Scenario: Typeahead solo catálogo Novedades

- GIVEN un profesional solo en Distribución y otro solo en catálogo Novedades (activo)
- WHEN se abre el picker de asociación
- THEN MUST listar solo el del catálogo Novedades

### Requirement: Mis profesionales (ABM scoped)

The system MUST provide a Novedades menu entry **Mis profesionales** visible to `admin`, `rrhh`, and `jefe_medico`:

- `jefe_medico`: ONLY services linked to that jefe.
- `admin` / `rrhh`: all services.

Associating MUST offer **active** professionals from the **Novedades catalog** with **typeahead** (`ProfessionalCombobox`; match name/`codprof`), excluding those already linked. Disassociating MUST always be allowed (soft-delete of the link) even if cargas exist; historical cargas MUST remain; the professional MUST no longer appear for new cargas on that service.

When a linked professional is inactive after sync, the link MUST **remain** and MUST be shown as inactive so the user can manually disassociate.

The page MUST expose a sync button for `admin`/`rrhh`/`jefe_medico` (full catalog sync, not scoped to the jefe’s services).

Parametrización MAY keep its profesional↔servicio tab for admin/rrhh with the same typeahead (Novedades catalog only).

API writes for profesional↔servicio MUST use a roster guard that allows admin/rrhh globally and jefe only on scoped services (`assert_can_manage_profesional_servicio`). Do NOT reuse the carga-only `assert_can_load_servicio` for RRHH roster writes.

#### Scenario: Jefe asocia profesional a su servicio

- GIVEN `jefe_medico` asociado a S1
- AND profesional P activo del catálogo Novedades no asociado a S1
- WHEN asocia P a S1 desde Mis profesionales
- THEN P aparece en el listado de Carga para S1

#### Scenario: Typeahead filtra al tipear

- GIVEN catálogo Novedades con varios profesionales activos no vinculados al servicio elegido
- WHEN el usuario escribe parte del nombre o `codprof`
- THEN la lista MUST mostrar solo los que matchean
- AND MUST actualizarse al tipificar (sin botón “Buscar”)

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

#### Scenario: Vínculo inactivo visible

- GIVEN P vinculado a S1 y luego inactivado por sync
- WHEN jefe abre Mis profesionales para S1
- THEN MUST ver P marcado inactivo
- AND MUST poder desasociarlo

### Requirement: Dos flujos de carga

The system MUST support in one form (módulo opcional y/o novedad opcional, al menos uno):

1. **Asignar módulo de catálogo** al profesional: `modulo_id` FK; valor mostrado solo lectura desde catálogo.
2. **Cargar novedad**: `tipo` ∈ {`hora_extra`, `hora_extra_por_ausencia`} + `horas` entero ≥ 1; valor = horas × valor_hora del servicio.

Create payloads MUST include required `fecha_realizacion` under the fecha rules below. Professional selection on Carga MUST use typeahead over **active** Novedades-catalog professionals linked to the service. Inactive linked professionals MUST NOT be selectable. Submit MUST clear profesional/módulo/horas/fecha (MAY keep período/servicio; MAY reset fecha to today if still valid).

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

#### Scenario: Inactivo no en Carga

- GIVEN P inactivo vinculado a S1
- WHEN admin abre Carga para S1
- THEN P MUST NOT aparecer en el typeahead de profesional

#### Scenario: Carga con inactivo

- GIVEN profesional inactivo aún vinculado a S1
- WHEN se intenta crear carga para ese profesional
- THEN API MUST reject (422)

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

### Requirement: Grilla y XLS (detalle)

Admin/`rrhh` MUST be able to download a detail XLS (`GET /novedades/export.xlsx`) with columns including: período, servicio, profesional, tipo, concepto, horas, valor hora, valor, cargado por, **fecha realización**, **fecha carga**. Filters: período, servicio, texto, concepto. The same detail rows MUST be available via `GET /novedades/grilla` (including optional `professional_id` for Capital Humano Detalle).

#### Scenario: RRHH exporta XLS detalle

- GIVEN `rrhh` con cargas existentes
- WHEN aplica filtros y descarga XLS detalle
- THEN receives a file with the agreed columns

#### Scenario: Jefe sin Capital Humano / XLS

- GIVEN `jefe_medico`
- WHEN navega a Capital Humano o intenta export XLS
- THEN MUST be denied (UI + API)

### Requirement: Alertas UI Novedades

Validation and API error messages on Novedades screens (Carga, Mis profesionales, Parametrización, Capital Humano) MUST be presented in a modal dialog with an explicit **OK** action to dismiss. Inline red labels alone MUST NOT be the primary error presentation for those actions.

#### Scenario: Error de validación en Carga

- GIVEN usuario en Carga con payload inválido (p. ej. fecha fuera de rango)
- WHEN intenta guardar
- THEN MUST ver un modal con el mensaje de error
- AND MUST poder cerrarlo con OK

### Requirement: Catálogo de profesionales Novedades

Novedades MUST use a **dedicated professionals catalog**, independent from Distribución (`professionals` / MySQL sync). Identity MUST be external code `CODPROF` stored as **string** preserving leading zeros. Stored fields MUST include display name from `NOMBRES`, `CODPROV` (persisted; MUST NOT be required in UI), and optional `LEGAJO`/`legajo` (string, trim, leading zeros preserved; null if absent). Catalog MUST NOT support manual create/edit of professionals (sync-only).

#### Scenario: Distribución intacta

- GIVEN sync MySQL de Distribución operativo
- WHEN un usuario usa `/profesionales` de Distribución
- THEN el comportamiento MUST permanecer independiente del catálogo Novedades

### Requirement: Sincronización HTTP de profesionales

The system MUST expose a manual sync that fetches active professionals from the configured external HTTP API (Bearer token from environment; secrets MUST NOT be logged or returned). Sync MUST upsert by `CODPROF`, set inactive any catalog row whose `CODPROF` is absent from a **successful** response, and reactivate + refresh name/`CODPROV`/`legajo` when a previously inactive code reappears. Each upsert MUST refresh `legajo` from remote `LEGAJO` when present (string trim, leading zeros preserved, max 40). Absence of LEGAJO MUST store null and MUST NOT fail the sync row. If the external call fails, the system MUST NOT mass-inactivate locals and MUST surface a clear error.

Sync UI buttons MUST appear on **Parametrización** for `admin`/`rrhh` and on **Mis profesionales** for `admin`/`rrhh`/`jefe_medico`. After success, UI MUST show a modal summary: created / updated / inactivated / errors, dismissible with OK.

#### Scenario: Sync inactiva ausente

- GIVEN catálogo local con `CODPROF` "001" activo
- AND response exitoso sin "001"
- WHEN corre sync
- THEN "001" MUST quedar inactivo
- AND el resumen MUST reflejar inactivados ≥ 1

#### Scenario: Sync no inactiva si API falla

- GIVEN catálogo con profesionales activos
- WHEN el GET externo falla (red/401/timeout)
- THEN ningún profesional MUST ser inactivado por esa corrida
- AND el usuario MUST ver error en modal

#### Scenario: Reactivación

- GIVEN `CODPROF` "001" inactivo
- AND response exitoso incluye "001" con nuevo nombre
- WHEN corre sync
- THEN MUST quedar activo con el nombre actualizado

#### Scenario: Jefe puede sync desde Mis profesionales

- GIVEN `jefe_medico` autenticado
- WHEN pulsa sincronizar en Mis profesionales
- THEN MUST ejecutarse el mismo sync de catálogo (no limitado a sus servicios)

#### Scenario: LEGAJO con ceros a la izquierda

- GIVEN response remoto con `CODPROF` "032" y `LEGAJO` " 05100"
- WHEN corre sync
- THEN el profesional MUST persistir `legajo` = "05100"

#### Scenario: LEGAJO ausente

- GIVEN fila remota sin `LEGAJO`
- WHEN corre sync
- THEN el upsert MUST completar con `legajo` null
- AND el resto de campos MUST actualizarse normalmente

#### Scenario: Actualiza legajo en re-sync

- GIVEN profesional local con `legajo` null
- AND response exitoso incluye LEGAJO "05100"
- WHEN corre sync
- THEN `legajo` MUST quedar "05100"

### Requirement: Limpieza transaccional Novedades

Parametrización MUST offer **Limpiar cargas** to `admin`/`rrhh` only. After mandatory confirmation modal, the system MUST **hard-delete** module assignments, novedades, and profesional↔servicio links. It MUST NOT delete servicios, módulos catalog, períodos, or jefe↔servicio. Mis profesionales MUST NOT show this control.

#### Scenario: Limpiar conserva param

- GIVEN existen cargas, vínculos, servicios y un período
- WHEN admin confirma Limpiar cargas
- THEN cargas y vínculos MUST desaparecer
- AND servicios/período/módulos/jefes MUST permanecer

#### Scenario: Jefe sin limpiar

- GIVEN `jefe_medico`
- WHEN abre Mis profesionales o Parametrización
- THEN MUST NOT ver ni invocar Limpiar cargas

### Requirement: Pantalla Capital Humano

The former **Generación archivo XLS** nav entry MUST be labeled **Capital Humano** and remain restricted to `admin`/`rrhh`. The page MUST show **one row per professional** with columns: legajo, name, monto cargas, monto ajustes, monto total. Rows MUST appear only when the professional has cargas and/or adjustments in the active filter scope (period ± optional service). Filter/sort MUST follow the same UX patterns as the Carga grid (period, service, text search including legajo/name).

Total cargas MUST be the sum of module + novedad valores in the filtered period (and only that service when filtered). Total = cargas ± persisted adjustments. Adjustments MUST be allowed when the period is **closed**.

Each row MUST offer **Detalle**, which opens a modal with the grid of that professional’s carga items (módulos/novedades) in the current filter scope.

#### Scenario: Agregación por profesional

- GIVEN profesional P con dos cargas (100 y 50) y un ajuste −10 en período abierto o cerrado
- WHEN admin abre Capital Humano filtrado por ese período
- THEN MUST ver una fila con monto_cargas 150, monto_ajustes −10, monto_total 140

#### Scenario: Solo admin/rrhh

- GIVEN `jefe_medico` autenticado
- WHEN intenta `GET /novedades/capital-humano`
- THEN MUST recibir 403

#### Scenario: Detalle por profesional

- GIVEN profesional P con cargas en el filtro actual
- WHEN admin pulsa **Detalle** en la fila de P
- THEN MUST abrirse un modal con la grilla de ítems (módulos/novedades) de P en ese alcance

### Requirement: Ajustes de Capital Humano

The system MUST persist create-only signed adjustments (`novedades_ajuste_capital`) with non-zero `importe` and required non-blank `comentario`. UI MUST open a modal from the ajustes column showing history and a create form. Edit/delete of adjustments MUST NOT be offered unless a later change adds them. Scope of listed/created adjustments MUST match the current period filter and optional service filter.

#### Scenario: Alta con comentario

- GIVEN período seleccionado y profesional en grilla
- WHEN admin crea ajuste importe −25 con comentario "descuento guardia"
- THEN MUST persistirse
- AND la grilla MUST reflejar el nuevo monto_ajustes / monto_total

#### Scenario: Importe cero rechazado

- GIVEN payload con importe 0
- WHEN POST `/novedades/capital-humano/ajustes`
- THEN MUST rechazar 422

### Requirement: Exportaciones XLS duales

Capital Humano MUST offer **two** downloads: aggregated Capital Humano XLS (`GET /novedades/export-capital.xlsx`) and the detail XLS (`GET /novedades/export.xlsx`). Both MUST honor the same filters as the grid and require `admin`/`rrhh`.

#### Scenario: Export agregada

- GIVEN filas visibles en Capital Humano
- WHEN descarga export-capital
- THEN el XLS MUST contener una fila por profesional con legajo, nombre y montos
