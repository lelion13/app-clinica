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

The system MUST provide ABM of **servicios** (id, nombre, activo, **valor_hora**, optional integer **concepto_liquidacion**) and **módulos** (id, descripción, comentario, valor ARS, **produccion** boolean, **sadofe** boolean) with **N:N** association to services. Admin and `rrhh` MUST manage them; `jefe_medico` MUST NOT.

Parametrización tabs MUST include **Producción** (tarifas de valor unitario por opción de bono importado) between **Módulos** and **Jefes ↔ servicios**, managed by `admin`/`rrhh` only. This tab MUST NOT be confused with the module boolean `produccion` (external production-check skip).

Servicios: `concepto_liquidacion` MUST be optional (empty or `0` → `NULL`); non-zero MUST be integer ≥ 1; negatives MUST be rejected (422); duplicates allowed. ABM MUST use modals like Módulos: grid, **Nuevo servicio** (always `activo=true`), edit modal (nombre, valor hora, concepto, **Activo** checkbox), confirm-delete modal; Escape cancels. No inline `valor_hora` edit. Grid shows `#id · nombre · activo · Concepto liquidación` (`NULL` → "—").

Modules: **sadofe** boolean (default false; off = Semana; `produccion` remains independent).

Modules MUST support:
- Create with optional `produccion` (default false) and at least one `servicio_id`, via Param UI modal **Nuevo módulo** (Cancelar / Cargar → `POST /modulos`)
- Update of data fields (descripción, comentario, valor, produccion) without changing associations (`PUT /modulos/{id}`)
- Replace of service associations (including empty set) via `PUT /modulos/{id}/servicios`
- Soft-delete only after confirmation modal showing module summary (Cancelar / Eliminar; Escape cancels)
- Param list buttons: `editar`, `servicios`, `eliminar`; no inline create form; no `produccion` badge on list rows

#### Scenario: Alta módulo asociado a servicios

- GIVEN `rrhh` autenticado en tab Módulos
- WHEN abre Nuevo módulo, completa descripción, valor y ≥1 servicio, y pulsa Cargar
- THEN queda disponible solo para cargas en esos servicios (o “sin asociar” si luego se vacían)

#### Scenario: Alta módulo con produccion

- GIVEN `rrhh` autenticado
- WHEN crea módulo con `produccion` desmarcado (default) y ≥1 servicio
- THEN el módulo se persiste con `produccion=false`

#### Scenario: Editar datos sin tocar servicios

- GIVEN módulo asociado a servicios S1,S2
- WHEN admin guarda el modal editar cambiando valor y `produccion`
- THEN descripción/comentario/valor/produccion se actualizan y las asociaciones permanecen

#### Scenario: Desasociar todos los servicios

- GIVEN módulo con servicios
- WHEN admin acepta el modal servicios con ningún checkbox
- THEN el módulo queda sin asociaciones activas (“sin asociar”)

#### Scenario: Confirmar eliminación de módulo

- GIVEN módulo en la lista
- WHEN pulsa eliminar y confirma en el modal
- THEN MUST soft-delete el módulo
- AND Cancelar o Escape MUST NOT eliminar

#### Scenario: Valor hora por servicio

- GIVEN servicio con `valor_hora = 1000`
- WHEN se carga una novedad de 3 horas en ese servicio
- THEN el valor calculado MUST ser 3000

#### Scenario: Orden de tabs Param

- GIVEN admin en Parametrización
- WHEN visualiza tabs
- THEN MUST ver **Producción** inmediatamente después de Módulos y antes de Jefes ↔ servicios

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
2. **Cargar novedad**: `tipo` ∈ {`hora_extra`, `hora_extra_por_ausencia`, `horas_a_descontar`} + `horas` entero ≥ 1; valor = horas × valor_hora del servicio (negative for `horas_a_descontar`). Negative values MUST enter Carga grid, XLS, and Capital Humano aggregates.

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

### Requirement: Filtro módulos por fecha y feriados

The Carga module select MUST list only modules valid for the selected `fecha_realizacion`:
- Semana (`sadofe=false`): Monday–Friday and the date is **not** a loaded holiday
- SADOFE (`sadofe=true`): Saturday, Sunday, **or** a loaded holiday

Validation is UI-only. Changing the date MUST clear a previously selected module if it is no longer valid.

#### Scenario: Combo filtra SADOFE

- GIVEN feriado 2026-05-25 y módulo SADOFE asociado al servicio
- WHEN fecha de realización es 2026-05-25
- THEN el combo MUST incluir el módulo SADOFE
- AND MUST NOT incluir módulos Semana de ese servicio

### Requirement: Feriados Novedades

The system MUST provide global holidays (`fecha` + `nombre` required). Admin/`rrhh` MUST manage them in Parametrización tab **Feriados** (next to Períodos): list grid, **Nuevo feriado** modal (Cancelar/Cargar), edit and confirm-delete modals like Módulos (Escape cancels). Duplicate active dates MUST be rejected (409). `jefe_medico` MUST be able to read holidays for Carga filtering but MUST NOT manage them.

#### Scenario: Alta feriado

- GIVEN `rrhh` autenticado
- WHEN crea feriado con fecha y nombre
- THEN aparece en la grilla y cuenta como SADOFE en Carga

#### Scenario: Fecha duplicada feriado

- GIVEN feriado activo en 2026-12-25
- WHEN se intenta crear otro con la misma fecha
- THEN MUST fail (409)

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

### Requirement: Verificación de producción al cargar

On the Carga page, before creating a module assignment and/or novedad, and before confirming an update of `fecha_realizacion`, the system MUST verify production for that professional and date via a **backend proxy** to the external `tiene-produccion` API (Bearer = Novedades professional sync token; URL from `NOVEDADES_BONOS_TIENE_PRODUCCION_URL`). The query MUST use `fecha` = selected realization date and `codprof` = catalog `CODPROF` (not internal id).

The check MUST run when the user confirms the action (submit Cargar / confirm fecha edit), for roles `admin` and `jefe_medico`.

If the proxy/external call **fails**, the UI MUST block the action (fail-closed) with an error modal and MUST NOT offer force-load.

If the external result is **false** on **create** (alta): see Requirement “Force-load sin producción”.

If the external result is **false** on **edit fecha**: the UI MUST block the update with a simple message and MUST NOT offer force-load. The create/update backend endpoints are NOT required to re-validate `tiene-produccion`.

**Exception (módulo flag):** When the create includes a selected módulo with `produccion=false`, the UI MUST NOT call the external check for that submit (see Requirement “Verificación de producción en Carga — flag módulo”). Solo-novedad and módulos with `produccion=true` MUST still check. Editing `fecha_realizacion` MUST always check.

#### Scenario: Con producción

- GIVEN proxy responde true
- WHEN pulsa Cargar con payload válido
- THEN MUST continuar el flujo de alta normal (sin motivo/obs)

#### Scenario: API caído

- GIVEN el proxy/externo falla
- WHEN pulsa Cargar
- THEN MUST bloquearse la carga con modal de error
- AND MUST NOT mostrar el flujo de force-load

#### Scenario: Editar fecha sin producción

- GIVEN carga existente
- WHEN confirma nueva fecha y el proxy responde false
- THEN MUST NO actualizar la fecha
- AND MUST NOT ofrecer force-load con motivo

### Requirement: Force-load sin producción

When create-submit receives `tiene_produccion: false`, the UI MUST show a modal containing: the message “El profesional no tiene producción en esa fecha. No se puede cargar módulo ni novedad para ese día.”; a motivo select defaulting to empty with options **Vacaciones** and **Enfermedad** only; a mandatory observation field; buttons **Cancelar** and **Cargar**.

- **Cancelar** MUST close the modal, MUST NOT create cargas, and MUST clear the carga form controls used for that attempt (profesional, módulo, novedad tipo/horas, fecha de realización); período and servicio MAY remain.
- **Cargar** MUST require a selected motivo and non-blank observation; then MUST create the intended module and/or novedad including the same `motivo_sin_produccion` and `observacion_sin_produccion` on each created row.
- Roles: `admin` and `jefe_medico`.

The system MUST persist those fields on `novedades_asignacion_modulo` and `novedades_novedad` and expose them on list responses for Carga. Backend MUST accept optional motivo/obs on create (validate enum + non-empty obs when provided) and MUST NOT require them on every create nor re-check production server-side.

#### Scenario: Cancelar force

- GIVEN modal force visible tras `false`
- WHEN pulsa Cancelar
- THEN MUST cerrarse el modal
- AND MUST NOT crearse módulo ni novedad
- AND MUST limpiarse profesional / módulo / novedad / fecha del form de carga

#### Scenario: Cargar force incompleto

- GIVEN modal force sin motivo o sin observación
- WHEN pulsa Cargar
- THEN MUST rechazar (validación UI)
- AND MUST NOT enviar POST

#### Scenario: Cargar force OK (módulo + novedad)

- GIVEN modal force con motivo Vacaciones y observación “texto”
- AND el form pedía módulo y novedad
- WHEN pulsa Cargar
- THEN MUST crearse ambas filas
- AND ambas MUST tener el mismo motivo y observación persistidos

### Requirement: Verificación de producción en Carga — flag módulo

When creating a carga that includes a **módulo** with `produccion=false`, the UI MUST NOT call the external `tiene-produccion` check for that submit. When the carga is only a novedad, or the selected módulo has `produccion=true`, Requirements “Verificación de producción al cargar” and “Force-load sin producción” MUST apply.

#### Scenario: Carga módulo sin producción propia

- GIVEN módulo M con `produccion=false`
- WHEN admin/jefe carga solo M (o M + novedad) en una fecha
- THEN MUST NOT llamar `GET .../bonos/tiene-produccion` y MUST permitir el POST

#### Scenario: Carga solo novedad

- GIVEN formulario sin módulo
- WHEN se carga solo novedad
- THEN MUST verificar producción externa

### Requirement: Listado de cargas en Carga

The Carga page MUST show a **unified grid** with columns at least: tipo, servicio, profesional, concepto, horas, valor, **fecha realización**, **Sin prod.** (motivo/obs when present), período, **fecha carga**. Filter/sort by column; default sort servicio → profesional.

Anular MUST use a confirmation modal (Cancelar / Confirmar). Editing fecha (period open) MAY use a dedicated modal.

#### Scenario: Modal anular

- GIVEN fila visible en la grilla
- WHEN el usuario pulsa anular
- THEN MUST ver modal con resumen
- AND Cancelar MUST no borrar
- AND Confirmar MUST anular y refrescar el listado

### Requirement: Período

A period MUST have optional name, start date, end date, and status open/closed. At most ONE open period MUST exist. Admin/`rrhh` MUST manage periods using modal-based interactions:
1. **Creación con modal:** Botón superior **"Nuevo período"** que abre modal con campos `nombre` (opcional), `fecha_inicio` y `fecha_fin`.
2. **Edición con modal (`PUT /novedades/periodos/{id}`):**
   - Permitida únicamente cuando el período está en estado **`open`** (`closed` retorna 409).
   - Permite modificar `nombre`, `fecha_inicio` y `fecha_fin`.
   - `fecha_fin` MUST ser posterior o igual a `fecha_inicio`.
   - Validación de cargas: Si el período contiene cargas existentes (`novedades_asignacion_modulo` o `novedades_novedad`), ninguna de sus fechas de realización puede quedar fuera del nuevo rango `[fecha_inicio, fecha_fin]`. En caso de conflicto, la API MUST responder 422 detallando el conflicto.
3. **Eliminación soft-delete (`DELETE /novedades/periodos/{id}`):**
   - Permitida únicamente si el período NO tiene cargas asociadas (módulos, novedades, bonos, prácticas, internaciones, ajustes).
   - Si tiene cargas asociadas, la API MUST responder 409 impidiendo la eliminación.
   - En la UI, la acción MUST requerir confirmación en modal ("Eliminar período").
4. **Cierre y reapertura:**
   - Admin/`rrhh` MUST close and reopen (`POST /periodos/{id}/cerrar` y `POST /periodos/{id}/reabrir`). While closed, ANY role MUST NOT create/edit/delete module assignments or novedades in that period.

#### Scenario: Segundo período abierto

- GIVEN ya hay un período abierto
- WHEN se intenta abrir otro
- THEN MUST fail

#### Scenario: Carga en cerrado

- GIVEN período cerrado
- WHEN jefe intenta cargar novedad
- THEN MUST be rejected

#### Scenario: Edición exitosa de período abierto sin conflicto

- GIVEN un período en estado `open` con rango `2026-08-01` a `2026-08-31`
- AND sus cargas existentes tienen `fecha_realizacion` entre `2026-08-05` y `2026-08-20`
- WHEN admin/rrhh actualiza el período con nuevo rango `2026-08-01` a `2026-08-25`
- THEN el período se actualiza correctamente y se persiste en base de datos

#### Scenario: Rechazo de edición por cargas fuera de nuevo rango

- GIVEN un período en estado `open` con una carga registrada el `2026-08-28`
- WHEN admin/rrhh intenta achicar el período a `2026-08-01` hasta `2026-08-20`
- THEN la API rechaza la actualización con error 422 indicando que existen cargas fuera del rango propuesto
- AND las fechas del período permanecen sin cambios

#### Scenario: Rechazo de edición en período cerrado

- GIVEN un período en estado `closed`
- WHEN se intenta invocar `PUT /novedades/periodos/{id}`
- THEN la API rechaza la solicitud con error 409

#### Scenario: Eliminación de período sin cargas

- GIVEN un período recién creado sin ninguna asignación de módulo ni novedad
- WHEN admin pulsa "eliminar" y confirma en el modal
- THEN el período es marcado como soft-deleted (`deleted_at != null`)
- AND deja de aparecer en el listado y selectores

#### Scenario: Rechazo de eliminación de período con cargas

- GIVEN un período que tiene al menos una carga registrada
- WHEN se intenta eliminar el período
- THEN la API rechaza la eliminación con error 409
- AND el período se mantiene activo en el sistema

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

Novedades MUST use a **dedicated professionals catalog**, independent from Distribución (`professionals` / MySQL sync). Identity MUST be external code `CODPROF` stored as **string** preserving leading zeros. Stored fields MUST include display name from `NOMBRES`, `CODPROV` (persisted; MUST NOT be required in UI), optional `LEGAJO`/`legajo` (string, trim, leading zeros preserved; null if absent), and boolean **`es_especialista`** (default false; set by specialists sync). Catalog MUST NOT support manual create/edit of professionals (sync-only).

#### Scenario: Distribución intacta

- GIVEN sync MySQL de Distribución operativo
- WHEN un usuario usa `/profesionales` de Distribución
- THEN el comportamiento MUST permanecer independiente del catálogo Novedades

### Requirement: Sincronización HTTP de profesionales

The system MUST expose a manual sync that fetches active professionals from the configured external HTTP API (Bearer token from environment; secrets MUST NOT be logged or returned). Sync MUST upsert by `CODPROF`, set inactive any catalog row whose `CODPROF` is absent from a **successful** response, and reactivate + refresh name/`CODPROV`/`legajo` when a previously inactive code reappears. Each upsert MUST refresh `legajo` from remote `LEGAJO` when present (string trim, leading zeros preserved, max 40). Absence of LEGAJO MUST store null and MUST NOT fail the sync row. If the external call fails, the system MUST NOT mass-inactivate locals and MUST surface a clear error.

Sync UI buttons MUST appear on **Parametrización** for `admin`/`rrhh` and on **Mis profesionales** for `admin`/`rrhh`/`jefe_medico`. After success, UI MUST show a modal summary: created / updated / inactivated / errors, dismissible with OK.

**Parametrización** sync MUST also run the specialists sync (see Requirement “Profesionales especialistas”) when configured. **Mis profesionales** sync MUST NOT call the specialists endpoint.

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

### Requirement: Profesionales especialistas

The system MUST support marking Novedades catalog professionals as specialists using an external list. Configuration MUST use `NOVEDADES_PROF_ESPECIALISTAS_URL` and the same Bearer token as professional sync (`NOVEDADES_PROF_SYNC_TOKEN`).

Each remote item MUST provide `profesional` (matched to `codprof`, string/trim) and `descripcion`. On a successful specialists fetch during **Parametrización** professional sync, the system MUST set `es_especialista=true` for matched professionals and `es_especialista=false` for other active catalog professionals not in the list. Professionals present in the specialists API but absent from the catalog MUST be returned to the UI for a post-sync modal (`profesional` + `descripcion`) and MUST NOT create catalog rows.

If the specialists API fails after a successful catalog sync, the catalog sync MUST remain committed, existing `es_especialista` flags MUST remain unchanged, and the UI MUST show a warning.

**Mis profesionales** sync MUST NOT call the specialists endpoint.

#### Scenario: Match y flag

- GIVEN catálogo con CODPROF `1099`
- AND especialistas API incluye `profesional: "1099"`
- WHEN admin sincroniza profesionales desde Parametrización
- THEN `es_especialista` MUST ser true para ese profesional

#### Scenario: Unmatched modal

- GIVEN especialistas API incluye `profesional: "9999"` no presente en catálogo
- WHEN sync Param termina
- THEN la UI MUST mostrar modal con ese profesional y su descripcion

#### Scenario: Fallo parcial

- GIVEN catálogo sync OK
- AND especialistas API falla
- WHEN termina el flujo
- THEN flags `es_especialista` MUST permanecer como estaban
- AND MUST mostrarse aviso de error de especialistas

### Requirement: Plus 20% en módulos de especialistas

When creating a **module assignment** (not a novedad) for a professional with `es_especialista=true`, the persisted assignment `valor` MUST be the module catalog value multiplied by **1.20**. Historical assignments keep their stored `valor`. Novedades MUST NOT receive this factor. Capital Humano and exports MUST use the assignment’s persisted `valor` for modules (no second multiplication).

#### Scenario: Carga módulo especialista

- GIVEN profesional especialista y módulo con valor catálogo 1000
- WHEN se carga el módulo
- THEN el valor persistido MUST ser 1200

#### Scenario: Novedad sin plus

- GIVEN profesional especialista
- WHEN se carga una novedad
- THEN el valor MUST calcularse como hoy (horas × valor_hora), sin ×1.20 por especialista

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

The former **Generación archivo XLS** nav entry MUST be labeled **Capital Humano** and remain restricted to `admin`/`rrhh`. The page MUST present a **period selector** that defaults to the **open** period when one exists, and an **Actualizar** button.

**Actualizar** MUST run the bonos import for the selected period (same persistence rules as Importar bonos: replace when open; reject when closed) and then refresh the grid. There MUST NOT be a separate **Importar bonos** button. **Solo bonos** MUST remain.

On entry, the grid MUST show **already persisted** data for the selected period. **Actualizar** MUST be disabled when the selected period is **closed** (persisted data still visible).

The main grid MUST show **one row per professional** with fixed columns: legajo, name, total cargas (modules/novedades), ajustes, total producción (valorized imported bonos), total general (`cargas + ajustes + producción`), plus actions. Dynamic per-option bonos columns MUST NOT appear on the main grid. The Capital Humano UI MUST NOT show a service selector. Text filter (legajo/name) and banner for options missing Producción tariffs MUST remain.

Row eligibility MUST remain: professionals with cargas and/or adjustments, or bonos-only with option `servicio` in `DEA|DEP|CAP|CAI`. Others with only non-special bonos MUST appear only in Solo bonos.

Grouping/ordering by `concepto_liquidacion` is out of scope for the on-screen Capital Humano grid. Liquidación export uses `concepto_liquidacion` as defined in Requirement “Export liquidación XLS (Capital Humano)”.

#### Scenario: Default período abierto

- GIVEN existe un período open
- WHEN admin entra a Capital Humano
- THEN el selector MUST tener ese período seleccionado
- AND la grilla MUST cargar datos persistidos de ese período

#### Scenario: Actualizar importa bonos

- GIVEN período open seleccionado
- WHEN pulsa Actualizar
- THEN MUST ejecutarse el import de bonos del período
- AND MUST refrescarse la grilla

#### Scenario: Actualizar en closed

- GIVEN período closed seleccionado
- WHEN visualiza la toolbar
- THEN Actualizar MUST estar disabled

#### Scenario: Columnas fijas

- GIVEN profesionales en grilla con bonos valorizados
- WHEN se lista Capital Humano
- THEN MUST ver Total cargas, Ajustes, Total producción, Total general
- AND MUST NOT ver columnas dinámicas por opción de bono en la grilla principal

#### Scenario: UI sin filtro por servicio

- GIVEN usuario admin/rrhh en Capital Humano
- WHEN visualiza filtros
- THEN MUST ver selector de período y búsqueda de texto
- AND MUST NOT ver selector de servicio

#### Scenario: Solo admin/rrhh

- GIVEN `jefe_medico` autenticado
- WHEN intenta `GET /novedades/capital-humano`
- THEN MUST recibir 403

### Requirement: Detalle unificado Capital Humano

The **Detalle** action MUST open a modal showing, for the selected professional and period: (1) carga items (módulos/novedades), (2) producción/bonos breakdown (quantities and subtotales), and (3) adjustment history. Detalle MUST indicate whether the professional is marked `es_especialista`. Adding a new adjustment MUST remain available from the main grid (**Agregar importe**) and MAY omit create-from-Detalle.

#### Scenario: Detalle completo

- GIVEN profesional con cargas, bonos y ajustes en el período
- WHEN admin abre Detalle
- THEN MUST ver las tres secciones (cargas, producción, historial de ajustes)

#### Scenario: Detalle muestra especialista

- GIVEN profesional con `es_especialista=true`
- WHEN admin abre Detalle en Capital Humano
- THEN MUST indicarse que es especialista

### Requirement: Ajustes de Capital Humano

The system MUST persist create-only signed adjustments (`novedades_ajuste_capital`) with non-zero `importe` and required non-blank `comentario`. Creating an adjustment MUST be available from the **main grid** action without requiring opening Detalle. The Detalle modal MUST show the adjustment **history** for that professional/period. Edit/delete of adjustments MUST NOT be offered unless a later change adds them.

#### Scenario: Alta desde grilla

- GIVEN profesional en grilla y período seleccionado
- WHEN admin agrega un ajuste desde la acción de grilla
- THEN MUST persistirse
- AND montos de la fila MUST actualizarse

#### Scenario: Importe cero rechazado

- GIVEN payload con importe 0
- WHEN POST `/novedades/capital-humano/ajustes`
- THEN MUST rechazar 422

### Requirement: Exportaciones XLS duales

Capital Humano MUST offer the aggregated Capital Humano XLS (`GET /novedades/export-capital.xlsx`) and the detail XLS (`GET /novedades/export.xlsx`). Both MUST honor the same filters as the grid and require `admin`/`rrhh`. The aggregated XLS MUST reflect **`monto_total` including valorized bonos** for each professional row, consistent with the on-screen grid.

#### Scenario: Export agregada

- GIVEN filas visibles en Capital Humano
- WHEN descarga export-capital
- THEN el XLS MUST contener una fila por profesional con legajo, nombre y montos

#### Scenario: XLS agregado con bonos en total

- GIVEN profesional con cargas 100, ajustes 0, monto_bonos 25
- WHEN descarga export-capital
- THEN `monto_total` en el XLS MUST ser 125

### Requirement: Export liquidación XLS (Capital Humano)

Capital Humano MUST offer a **Descargar liquidación** control for `admin`/`rrhh` that downloads an `.xlsx` via `GET /novedades/export-liquidacion.xlsx?periodo_id=…` with exactly these columns, in order: **empresa**, **legajo**, **monto**, **concepto**.

The download MUST NOT replace existing Capital Humano exports (`export-capital.xlsx`, `export-capital-bonos.xlsx`, `export.xlsx`).

Export MUST be allowed **only for a closed period**. If the period is missing, open, or not found, the API MUST reject (422/409) and the UI MUST keep the button disabled or show the error.

#### Scenario: Período abierto rechazado

- GIVEN período en estado `open`
- WHEN admin solicita Descargar liquidación
- THEN MUST rechazarse
- AND no se genera archivo

#### Scenario: Período cerrado OK

- GIVEN período `closed` con cargas válidas
- WHEN admin pulsa Descargar liquidación
- THEN MUST descargar un `.xlsx` con columnas empresa, legajo, monto, concepto

### Requirement: Filas de liquidación desde cargas

For each professional in the selected closed period, **carga** items (module assignments and novedades) MUST be grouped by the associated service’s `concepto_liquidacion`.

Each distinct `(legajo, concepto)` from cargas MUST produce (after merges) one output row with:
- `concepto` = that `concepto_liquidacion`
- `empresa` = `CHI` if `concepto > 100`, else `CMG`
- `legajo` = professional legajo (string as stored)
- `monto` = sum of carga values for that concepto, plus allocated production and ajustes, preserving system decimal precision

If the professional has cargas in **more than one** servicio/concepto, they MUST appear **more than once** (one row per concepto).

If any carga’s service has `concepto_liquidacion` null/empty, the **entire export MUST fail** with an error listing the service name(s) missing the concept.

#### Scenario: Profesional multi-servicio

- GIVEN profesional con cargas en servicio concepto 50 y servicio concepto 150
- WHEN exporta liquidación
- THEN MUST haber dos filas (CMG/50 y CHI/150) con montos de cargas respectivos

#### Scenario: Servicio sin concepto bloquea

- GIVEN al menos una carga en servicio sin `concepto_liquidacion`
- WHEN exporta liquidación
- THEN MUST fallar
- AND el mensaje MUST indicar el/los nombre(s) de servicio sin concepto

### Requirement: Sumar producción a filas de carga

Valorized **bonos**, **prácticas traumatológicas**, and **internaciones** for the period MUST use the same eligibility and valorization rules as Capital Humano grid.

Production amounts MUST be bucketed by source empresa:
- `centro`/`sucursal` starting with `SC` (case-insensitive) → CHI
- otherwise → CMG

Allocation onto carga conceptos:
1. If the professional has one or more carga conceptos whose empresa matches the production bucket, split that bucket’s monto **equally** across those matching conceptos.
2. Else (no matching empresa among cargas), split equally across **all** of the professional’s carga conceptos.

After allocation, rows MUST be aggregated to a single row per `(empresa, legajo, concepto)`.

#### Scenario: Producción repartida en dos conceptos misma empresa

- GIVEN profesional con dos conceptos CMG (50 y 60) y producción CMG valorizada 1000
- WHEN exporta
- THEN cada fila CMG recibe +500 además de sus cargas

### Requirement: Solo producción sin cargas

If a professional has **no cargas** in the period:
- MUST export only if they have eligible **special bonos** with servicio in `{DEA, DEP, CAP, CAI}`.
- Fixed conceptos:
  - CMG + DEA/CAI → 90
  - CMG + DEP/CAP → 91
  - CHI + DEA/CAI → 123
  - CHI + DEP/CAP → 122
- Create one row per fixed concepto present; production for that empresa (including prácticas/internaciones attributed to that empresa) MUST split equally across those conceptos.
- If no special bonos and no cargas → MUST NOT appear in the file.
- Ajustes for such professionals MUST split equally across the generated fixed conceptos; if none generated, ajustes are omitted.

#### Scenario: Solo DEA CMG

- GIVEN profesional sin cargas con bono DEA en centro CMG y producción valorizada
- WHEN exporta
- THEN MUST existir fila empresa=CMG, concepto=90 con el monto correspondiente

### Requirement: Ajustes en liquidación

Importe adjustments (“Agregar importe”) for the period MUST be split **equally** across the professional’s liquidación conceptos (carga-derived, or fixed conceptos when no cargas). They MUST NOT create a separate concepto by themselves.

#### Scenario: Ajuste con dos conceptos

- GIVEN profesional con conceptos 50 y 150 y ajuste +200
- WHEN exporta
- THEN cada fila recibe +100

### Requirement: UI Descargar liquidación

On Capital Humano, next to existing download buttons, the system MUST show **Descargar liquidación**. It MUST require a selected closed period. Existing download buttons MUST remain unchanged in behavior.

### Requirement: Importar bonos resumen en Capital Humano

Capital Humano MUST support importing bonos for `admin`/`rrhh` via the **Actualizar** button (no separate Importar bonos control). The user MUST select a **single period** before import. The backend MUST call the configured external resumen API with `fecha_desde` = period `fecha_inicio` and `fecha_hasta` = period `fecha_fin`, using the same Bearer token as Novedades professional sync (`NOVEDADES_BONOS_RESUMEN_URL` + `NOVEDADES_PROF_SYNC_TOKEN`). Results MUST be persisted per period. Match MUST be by API `profesional` → catalog `CODPROF` (string/trim). Each option MUST be the full key `centro|servicio|semana|horario`. Duplicate rows for the same professional+option MUST sum `cantidad`. Unknown CODPROF MUST be ignored and counted in the summary. On success the UI MUST show a summary modal and refresh the grid.

While the period is **open**, re-import MUST **replace** the period’s bonos quantity snapshot. While the period is **closed**, import MUST be rejected (frozen). If the period lacks valid start/end dates, the API MUST return 422 without calling the external service. If the external call fails, the system MUST NOT modify the existing snapshot and MUST surface an error modal.

After a successful import, orphan option cleanup MAY run as defined in Requirement “Limpieza de opciones de bono huérfanas”.

#### Scenario: Entry point Actualizar

- GIVEN período open
- WHEN admin pulsa Actualizar
- THEN MUST ejecutarse el import de bonos del período

#### Scenario: Re-import reemplaza

- GIVEN período open con snapshot previo
- WHEN se importa de nuevo con éxito
- THEN el snapshot de cantidades del período MUST ser reemplazado

#### Scenario: Período cerrado congela

- GIVEN período closed con snapshot
- WHEN se intenta Actualizar / import
- THEN MUST rechazarse
- AND el snapshot MUST permanecer intacto

#### Scenario: Sin período

- GIVEN Capital Humano sin período seleccionado
- WHEN se intenta importar
- THEN MUST NO ejecutarse (UI y/o 422)

#### Scenario: API externo falla

- GIVEN período open y snapshot existente
- WHEN el GET externo falla
- THEN MUST mostrarse error
- AND el snapshot MUST no modificarse

### Requirement: Columnas de bonos en grilla Capital Humano

The main Capital Humano grid MUST remain one row per professional. In addition to professionals with cargas/ajustes, it MUST include professionals with bonos-only when, for the selected period, they have at least one bonos option whose `servicio` value is exactly one of: `DEA`, `DEP`, `CAP`, `CAI`.

For each bonos option in the period snapshot, the grid MUST append a **cantidad** column and an adjacent **subtotal** column (cantidad × Producción `valor_unitario`, or 0 if no tariff). **`monto_total` MUST include valorized bonos**.

#### Scenario: Solo bonos CAP entra a grilla

- GIVEN profesional P con bonos en período y opción con `servicio = CAP`
- AND P no tiene cargas ni ajustes
- WHEN se lista Capital Humano
- THEN P MUST aparecer en la grilla principal

#### Scenario: Solo bonos servicio no especial no entra

- GIVEN profesional Q con bonos en período y opciones sin `DEA|DEP|CAP|CAI`
- AND Q no tiene cargas ni ajustes
- WHEN se lista Capital Humano
- THEN Q MUST NOT aparecer en la grilla principal

#### Scenario: Total incluye bonos

- GIVEN profesional con monto_cargas 100, monto_ajustes 0, monto_bonos 50
- WHEN se muestra la grilla
- THEN `monto_total` MUST ser 150

### Requirement: Modal solo bonos

The Solo bonos modal MUST list only professionals with bonos persisted for the period that are not present in the main grid after applying the special-service promotion rule.

#### Scenario: Promovido excluido de Solo bonos

- GIVEN profesional P con bonos-only y opción `servicio = DEA`
- WHEN se abre modal Solo bonos
- THEN P MUST NOT aparecer en el modal

### Requirement: XLS con bonos

Capital Humano MUST offer download **XLS con bonos** including, for each dynamic option, both **quantity** and **subtotal** columns, plus aggregated monetary columns consistent with the grid.

#### Scenario: XLS con subtotales

- GIVEN snapshot con opciones tarifadas y no tarifadas
- WHEN admin descarga XLS con bonos
- THEN MUST incluir columnas cantidad y subtotal por opción
- AND subtotal sin tarifa MUST exportarse como 0

### Requirement: Tarifas Producción (valor bonos)

The system MUST provide an ABM of **Producción** tariffs in Parametrización for `admin` and `rrhh` only. Each tariff MUST reference exactly one `novedades_bono_opcion` (unique among non-deleted rows) and store integer `valor_unitario` ≥ 0.

ABM MUST follow the Servicios pattern (grid, modals, Escape cancels). Create MUST support searchable multi-select of options without an active tariff and shared `valor_unitario` via bulk create. Options with an active tariff MUST NOT be selectable on create.

#### Scenario: Alta tarifa admin

- GIVEN `rrhh` en tab Producción
- AND existe opción sin tarifa
- WHEN selecciona esa opción, ingresa `valor_unitario = 1500` y confirma
- THEN MUST persistirse una tarifa única para esa opción

#### Scenario: Duplicado rechazado

- GIVEN tarifa activa para opción O1
- WHEN admin intenta crear otra tarifa para O1
- THEN MUST rechazarse (422)

#### Scenario: Jefe sin ABM Producción

- GIVEN `jefe_medico` autenticado
- WHEN intenta `POST /novedades/produccion-tarifas`
- THEN MUST recibir 403

### Requirement: Valorización de bonos en Capital Humano

For the selected period’s bonos snapshot, Capital Humano MUST show **cantidad** and **subtotal** per option. Missing tariff → cantidad visible, subtotal **0**, banner `opciones_sin_tarifa`. Tariff lookup MUST use current Param catalog at read/export time (no re-import required after tariff changes). Per row, `monto_bonos` MUST be the sum of subtotals.

#### Scenario: Subtotal con tarifa

- GIVEN opción O con cantidad 3 para profesional P
- AND tarifa `valor_unitario = 1000` para O
- WHEN admin lista Capital Humano del período
- THEN MUST ver cantidad 3 y subtotal 3000 para O en la fila de P

#### Scenario: Sin tarifa

- GIVEN opción O2 importada sin tarifa en Producción
- WHEN se lista Capital Humano
- THEN cantidad de O2 MUST mostrarse
- AND subtotal MUST ser 0
- AND MUST mostrarse banner de opciones sin tarifa

### Requirement: Limpieza de opciones de bono huérfanas

On successful Importar bonos, the system MUST soft-delete `novedades_bono_opcion` rows that meet all of: (1) not in the current import; (2) no active Producción tariff; (3) no `novedades_bono_cantidad` in any period.

#### Scenario: Limpia huérfana sin tarifa

- GIVEN opción ausente del import, sin tarifa y sin cantidades en ningún período
- WHEN termina Importar bonos
- THEN esa opción MUST soft-deletarse

#### Scenario: Conserva con tarifa

- GIVEN opción ausente del import pero con tarifa Producción activa
- WHEN termina Importar bonos
- THEN la opción MUST permanecer

### Requirement: Plantilla Excel import módulos

Parametrización tab **Módulos** MUST offer **Plantilla de importación** for `admin`/`rrhh`. Download MUST be an `.xlsx` with headers for module fields and a **dropdown of existing active service names** on the service column. Producción and SADOFE MUST use Sí/No dropdowns.

#### Scenario: Descargar plantilla

- GIVEN admin en tab Módulos con servicios activos S1, S2
- WHEN pulsa Plantilla de importación
- THEN descarga un Excel con columnas de módulo
- AND la columna servicio ofrece S1 y S2 en lista desplegable

### Requirement: Importación múltiple de producción externa (Bonos, Prácticas e Internaciones)

When the user clicks **Actualizar** in **Capital Humano** (`admin`/`rrhh`), the system MUST fetch from 3 external APIs:
1. `NOVEDADES_BONOS_RESUMEN_URL`: Bonos resumen.
2. `NOVEDADES_BONOS_PRACTICAS_URL`: Prácticas traumatológicas (`centro`, `servicio`, `profesional`, `cantidad`).
3. `NOVEDADES_BONOS_INTERNACIONES_URL`: Internaciones (`profesional`, `sucursal`, `cantidad_internaciones`).

All calls MUST use the same Bearer token `NOVEDADES_PROF_SYNC_TOKEN` and period date parameters (`fecha_desde` = `fecha_inicio`, `fecha_hasta` = `fecha_fin`).

The sync MUST be **atomic (all-or-nothing)**: if any of the three APIs fails (HTTP error, timeout, malformed payload), the existing period snapshots MUST NOT be modified, and an error MUST be presented to the user.

Imported items MUST be matched to the catalog by `profesional` → `CODPROF`. Duplicates for the same professional and option key MUST sum quantities. Unknown `CODPROF` MUST be ignored and counted in summary.

#### Scenario: Actualización atómica exitosa
- GIVEN período abierto seleccionado en Capital Humano
- WHEN admin pulsa Actualizar
- THEN el sistema consulta las 3 APIs externas (bonos, prácticas, internaciones)
- AND si las 3 responden OK, reemplaza los snapshots del período de forma transaccional
- AND refresca la grilla de Capital Humano con el resumen consolidado

#### Scenario: Fallo de una de las APIs externas
- GIVEN período abierto y snapshots previos en base de datos
- WHEN la API de internaciones falla (o cualquiera de las 3)
- THEN ningún snapshot del período es modificado
- AND la UI muestra un modal de error

### Requirement: Tarifas de Prácticas e Internaciones en Producción

Parametrización tab **Producción** MUST support configuring unit tariffs for:
- Prácticas traumatológicas (`GLOBAL|PRACTICA_TRAUMATOLOGICA|—|—`).
- Internaciones (`GLOBAL|INTERNACIONES|—|—`).

These special options MUST be automatically ensured in the catalog and MUST be protected against orphan cleanup. Tariffs MUST be integers ≥ 0, editable by `admin`/`rrhh` only.

#### Scenario: Configurar tarifa de prácticas e internaciones
- GIVEN `rrhh` en Parametrización tab Producción
- WHEN asigna valor unitario a la práctica traumatológica y a las internaciones
- THEN Capital Humano valoriza las cantidades correspondientes con esos valores unitarios

### Requirement: Valorización y regla de elegibilidad de Producción (Bonos, Prácticas e Internaciones)

In Capital Humano, imported bonos, prácticas and internaciones MUST be valorized as `cantidad × valor_unitario`.

**Eligibility rules:**
1. If the professional has at least one **módulo asignado** in the period:
   - ALL bonos (all services), ALL prácticas and ALL internaciones are counted and valorized in their total.
2. If the professional does NOT have any **módulo asignado** in the period:
   - Bonos: ONLY options belonging to `{DEA, DEP, CAP, CAI}` are counted and valorized (bonos of other services like `GUA` are omitted from the valorized total and from the professional's table in Capital Humano).
   - Prácticas: ALL prácticas are counted and valorized.
   - Internaciones: ALL internaciones are counted and valorized.

If the professional has only novedades (horas extras) and no special service association, bonos, prácticas and internaciones MUST NOT be valorized into their total.

The valorized amounts MUST be added to **Total producción** and **Total general** in the Capital Humano grid, and MUST be clearly itemized in the **Detalle** modal (secciones separadas para Cargas, Bonos, Prácticas, Internaciones y Ajustes) and in XLS exports.

#### Scenario: Profesional con módulo contabiliza todos los servicios
- GIVEN profesional con 1 módulo asignado en el período, bonos en GUA y CAP, 10 prácticas y 2 internaciones
- WHEN se calcula la fila de Capital Humano
- THEN su Total producción incluye todos los bonos (GUA y CAP) + prácticas valorizadas + internaciones valorizadas

#### Scenario: Profesional sin módulos filtra bonos no especiales
- GIVEN profesional sin módulos asignados, con 1 bono en CAP, 193 bonos en GUA y 3 internaciones
- WHEN se calcula la fila de Capital Humano
- THEN solo se valoriza el bono de CAP ($6.000) y las 3 internaciones ($15.000)
- AND los 193 bonos de GUA no se contabilizan ni valorizan en la grilla principal de Capital Humano
- AND su Total producción resulta en $21.000

#### Scenario: Profesional sin módulos ni servicio especial
- GIVEN profesional solo con horas extras y sin servicios especiales
- WHEN se calcula la fila de Capital Humano
- THEN prácticas e internaciones no suman a su Total producción


