# Delta: novedades

## ADDED Requirements

### Requirement: Tarifas Producción (valor bonos)

The system MUST provide an ABM of **Producción** tariffs in Parametrización for `admin` and `rrhh` only. The tab MUST be labeled **Producción**, placed between **Módulos** and **Jefes ↔ servicios**. UI MUST clarify this is **not** the module checkbox `produccion` (external production check skip).

Each tariff MUST reference exactly one `novedades_bono_opcion` (unique among non-deleted rows) and store integer `valor_unitario` ≥ 0. Match semantics MUST be the option’s four fields: `centro`, `servicio`, `semana`, `horario`. To change a value, the user MUST edit the existing row (no duplicate tariff for the same option).

ABM MUST follow the Servicios pattern: grid listing, **Nueva producción** button, create/edit/delete via modals, delete confirmation modal, Escape cancels.

Create MUST allow selecting **one or more** bonus options that already exist in `novedades_bono_opcion` and share the same `valor_unitario`, via searchable multi-select (filter-as-you-type) and `POST /novedades/produccion-tarifas/bulk`. Single-create `POST /novedades/produccion-tarifas` MAY remain. Options that already have an active tariff MUST NOT be selectable on create.

#### Scenario: Alta tarifa admin

- GIVEN `rrhh` en tab Producción
- AND existe opción `CMG|CAP|LUNES_VIERNES|DIA` sin tarifa
- WHEN selecciona esa opción, ingresa `valor_unitario = 1500` y confirma
- THEN MUST persistirse una tarifa única para esa opción

#### Scenario: Alta múltiple mismo valor

- GIVEN dos opciones O1 y O2 sin tarifa
- WHEN admin las selecciona en el combobox, ingresa valor 2000 y confirma bulk
- THEN MUST persistirse una tarifa por opción con `valor_unitario = 2000`

#### Scenario: Duplicado rechazado

- GIVEN tarifa activa para opción O1
- WHEN admin intenta crear otra tarifa para O1
- THEN MUST rechazarse (422)

#### Scenario: Jefe sin ABM Producción

- GIVEN `jefe_medico` autenticado
- WHEN intenta `POST /novedades/produccion-tarifas`
- THEN MUST recibir 403

### Requirement: Limpieza de opciones de bono huérfanas

On successful **Importar bonos**, after replacing the period snapshot, the system MUST soft-delete `novedades_bono_opcion` rows that meet **all** of: (1) option key not present in the current import payload; (2) no active Producción tariff; (3) no `novedades_bono_cantidad` in **any** period. Options with tariff or historical quantities MUST be retained.

#### Scenario: Limpia huérfana sin tarifa

- GIVEN opción `…|DOMINGO|…` sin tarifa y sin cantidades en ningún período
- AND el nuevo import no la incluye
- WHEN termina Importar bonos
- THEN esa opción MUST soft-deletarse

#### Scenario: Conserva con tarifa

- GIVEN opción ausente del import pero con tarifa Producción activa
- WHEN termina Importar bonos
- THEN la opción MUST permanecer

### Requirement: Valorización de bonos en Capital Humano

For the selected period’s bonos snapshot, Capital Humano MUST show **two columns per imported option**: **cantidad** (from persisted snapshot) and **subtotal** = cantidad × `valor_unitario` from Producción tariff when present.

When no tariff exists for an imported option:
- cantidad MUST still display
- subtotal MUST be **0**
- the option MUST NOT block the grid or import
- the page MUST show a **banner** warning that some options lack tariffs in Producción

Per professional row, `monto_bonos` MUST be the sum of subtotals (missing tariff counts as 0). **`monto_total` MUST be** `monto_cargas + monto_ajustes + monto_bonos`.

Tariff lookup MUST use current Param catalog at read/export time (no re-import required after tariff changes).

#### Scenario: Subtotal con tarifa

- GIVEN opción O con cantidad 3 para profesional P
- AND tarifa `valor_unitario = 1000` para O
- WHEN admin lista Capital Humano del período
- THEN MUST ver cantidad 3 y subtotal 3000 para O en la fila de P
- AND `monto_total` MUST incluir 3000 además de cargas y ajustes

#### Scenario: Sin tarifa

- GIVEN opción O2 importada sin tarifa en Producción
- WHEN se lista Capital Humano
- THEN cantidad de O2 MUST mostrarse
- AND subtotal MUST ser 0
- AND MUST mostrarse banner de opciones sin tarifa

## MODIFIED Requirements

### Requirement: Columnas de bonos en grilla Capital Humano

The main Capital Humano grid MUST remain one row per professional, including the promotion rule for bonos-only professionals with special services `DEA|DEP|CAP|CAI` from change `capital-humano-bonos-servicios-especiales`.

For each bonos option column in the period snapshot, the grid MUST append a quantity column and an adjacent subtotal column as defined in Requirement “Valorización de bonos en Capital Humano”. **`monto_total` MUST include valorized bonos** (no longer limited to cargas ± ajustes).

#### Scenario: Total incluye bonos

- GIVEN profesional con monto_cargas 100, monto_ajustes 0, monto_bonos 50
- WHEN se muestra la grilla
- THEN `monto_total` MUST ser 150

### Requirement: XLS con bonos

Capital Humano MUST offer download **XLS con bonos** including, for each dynamic option, both **quantity** and **subtotal** columns, plus aggregated monetary columns consistent with the grid.

#### Scenario: XLS con subtotales

- GIVEN snapshot con opciones tarifadas y no tarifadas
- WHEN admin descarga XLS con bonos
- THEN MUST incluir columnas cantidad y subtotal por opción
- AND subtotal sin tarifa MUST exportarse como 0

### Requirement: Exportaciones XLS duales

The aggregated Capital Humano XLS (`export-capital.xlsx`) MUST reflect **`monto_total` including valorized bonos** for each professional row, consistent with the on-screen grid.

#### Scenario: XLS agregado con bonos en total

- GIVEN profesional con cargas 100, ajustes 0, monto_bonos 25
- WHEN descarga export-capital
- THEN `monto_total` en el XLS MUST ser 125

### Requirement: Servicios y módulos

Parametrización tabs MUST include **Producción** (tarifas bonos) between **Módulos** and **Jefes ↔ servicios**, managed by `admin`/`rrhh` only, in addition to existing tabs.

#### Scenario: Orden de tabs

- GIVEN admin en Parametrización
- WHEN visualiza tabs
- THEN MUST ver Producción inmediatamente después de Módulos y antes de Jefes ↔ servicios
