# Delta: novedades

## ADDED Requirements

### Requirement: Catálogo de profesionales Novedades

Novedades MUST use a **dedicated professionals catalog**, independent from Distribución (`professionals` / MySQL sync). Identity MUST be external code `CODPROF` stored as **string** preserving leading zeros. Stored fields MUST include display name from `NOMBRES` and `CODPROV` (persisted; MUST NOT be required in UI this change). Catalog MUST NOT support manual create/edit of professionals (sync-only).

#### Scenario: Distribución intacta

- GIVEN sync MySQL de Distribución operativo
- WHEN un usuario usa `/profesionales` de Distribución
- THEN el comportamiento MUST permanecer independiente del catálogo Novedades

### Requirement: Sincronización HTTP de profesionales

The system MUST expose a manual sync that fetches active professionals from the configured external HTTP API (Bearer token from environment; secrets MUST NOT be logged or returned). Sync MUST upsert by `CODPROF`, set inactive any catalog row whose `CODPROF` is absent from a **successful** response, and reactivate + refresh name/`CODPROV` when a previously inactive code reappears. If the external call fails, the system MUST NOT mass-inactivate locals and MUST surface a clear error.

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

### Requirement: Profesional inactivo no carga

Create of module assignment or novedad MUST require the professional to be **active** in the Novedades catalog and linked to the service. Inactive professionals MUST NOT appear as selectable for new associations or new cargas (except Mis profesionales linked roster showing inactive links per below).

#### Scenario: Carga con inactivo

- GIVEN profesional inactivo aún vinculado a S1
- WHEN se intenta crear carga para ese profesional
- THEN API MUST reject (422/403)

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

## MODIFIED Requirements

### Requirement: Profesional↔servicio

(Previously: listing/provider from existing `professionals`.)

Links and pickers for Novedades MUST use the **Novedades catalog** only. Association pickers MUST offer **active** Novedades professionals not yet linked to the service (typeahead). Distribución `professionals` MUST NOT be offered.

#### Scenario: Typeahead solo catálogo Novedades

- GIVEN un profesional solo en Distribución y otro solo en catálogo Novedades (activo)
- WHEN se abre el picker de asociación
- THEN MUST listar solo el del catálogo Novedades

### Requirement: Mis profesionales (ABM scoped)

(Previously: active catalog only; no sync; no inactive link UX.)

In addition to prior scoped associate/disassociate rules: the page MUST include sync (roles above). When a linked professional is inactive, the link MUST **remain** and MUST be shown as inactive so the user can manually disassociate. Disassociate remains always allowed (soft-delete link).

#### Scenario: Vínculo inactivo visible

- GIVEN P vinculado a S1 y luego inactivado por sync
- WHEN jefe abre Mis profesionales para S1
- THEN MUST ver P marcado inactivo
- AND MUST poder desasociarlo

### Requirement: Dos flujos de carga

(Previously: professionals from linked list without catalog split / active check explicit.)

Professional selection MUST be over **active** Novedades-catalog professionals linked to the service. Inactive linked professionals MUST NOT be selectable for create.

#### Scenario: Inactivo no en Carga

- GIVEN P inactivo vinculado a S1
- WHEN admin abre Carga para S1
- THEN P MUST NOT aparecer en el typeahead de profesional
