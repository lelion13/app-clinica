# Delta Spec: novedades-param-recalculo

## ADDED Requirements

### Requirement: Pestaña Recálculo en Parametrización

Parametrización Novedades MUST include a tab **Recálculo** immediately **after** **Feriados**. The tab MUST be available to the same roles that access Parametrización (`admin` and `rrhh`). Other roles MUST NOT see or use Recálculo.

#### Scenario: Orden de tabs

- GIVEN `admin` o `rrhh` en Parametrización
- WHEN mira las tabs
- THEN MUST ver **Recálculo** inmediatamente después de **Feriados**

#### Scenario: Solo roles Param

- GIVEN usuario `jefe_medico`
- WHEN navega Novedades
- THEN MUST NOT acceder a Parametrización / Recálculo

### Requirement: Recálculo de importes de cargas por período

From the Recálculo tab, `admin`/`rrhh` MUST select:

1. **Período** — open or closed (required)
2. **Modo** — exactly one of: **solo horas** | **solo módulos** | **ambos**

The operation MUST consider all non-soft-deleted cargas of that period that match the mode:
- **Módulos**: asignaciones de módulo (`modulo_asignado`) del período
- **Horas**: novedades con tipo de horas (`hora_extra`, `hora_extra_por_ausencia`, `horas_a_descontar`) del período

Soft-deleted cargas MUST be excluded from preview and apply.

#### Scenario: Período cerrado permitido

- GIVEN período cerrado con cargas
- WHEN admin elige ese período y modo ambos
- THEN MUST poder pedir vista previa

#### Scenario: Soft-delete excluido

- GIVEN una asignación soft-deleted en el período
- WHEN corre preview de módulos
- THEN esa fila MUST NOT entrar en el resumen ni en el apply

### Requirement: Vista previa y confirmación de Recálculo

The UI MUST follow: filtros → **Vista previa** → resumen → **Confirmar actualización**.

The preview MUST show:

- **Por cada módulo de catálogo** involucrado: importe total actual vs importe total nuevo
- **Bloque horas** (si el modo incluye horas): importe total actual vs nuevo

A row “changes” when the recalculated importe differs from the persisted importe.

If the preview finds **zero** changing rows, **Confirmar actualización** MUST be blocked (or reject apply) with a clear message that there are no changes.

Confirm MUST persist the new importes only on rows that change.

#### Scenario: Preview con cambios

- GIVEN catálogo de módulo subió de 1000 a 1200 y hay 2 asignaciones de ese módulo en el período
- WHEN admin pide vista previa (modo módulos)
- THEN el resumen de ese módulo MUST mostrar actual 2000 vs nuevo 2400 (u equivalentes con plus si aplica)
- AND Confirmar MUST estar habilitado

#### Scenario: Sin cambios bloquea

- GIVEN ningún valor de catálogo/`valor_hora` difiere de lo persistido
- WHEN admin pide vista previa
- THEN MUST indicarse que no hay cambios
- AND Confirmar MUST NOT aplicar actualizaciones

#### Scenario: Flujo dos pasos

- GIVEN preview con cambios
- WHEN admin aún no confirma
- THEN MUST NOT haberse persistido ningún cambio
- AND al confirmar MUST persistirse los nuevos importes

### Requirement: Reglas de valor al recalcular

**Módulos:** the new persisted `valor` for each assignment MUST be computed with the **same rules as create carga** from the current module catalog value, including especialista plus (×1.20) when that rule applies for the professional/service at recalc time.

**Horas:** the quantity `horas` on each novedad row MUST NOT change. The new importe MUST be `novedad_valor_calculado(tipo, horas, valor_hora)` using the service’s **current** `valor_hora` (negative for `horas_a_descontar`).

#### Scenario: Plus especialista en módulo

- GIVEN asignación a profesional/servicio que aplica plus y catálogo módulo = 1000
- WHEN se recalcula
- THEN el nuevo valor MUST ser 1200 (misma regla que al cargar)

#### Scenario: Horas mantiene cantidad

- GIVEN novedad 3h extra en servicio con valor_hora que pasó de 1000 a 1100
- WHEN se recalcula horas
- THEN horas MUST seguir siendo 3
- AND el importe MUST pasar de 3000 a 3300

### Requirement: Valor persistido en novedades de horas

Each `novedades_novedad` row MUST persist a numeric **`valor`** (importe snapshot) set on create/update and used by grid/export/CH/recalc. Migration `0035_novedad_valor` MUST backfill existing rows from the then-current formula and enforce NOT NULL thereafter.

#### Scenario: Alta setea valor

- GIVEN create de novedad hora_extra 2h con valor_hora 1000
- WHEN se persiste
- THEN `valor` MUST ser 2000 (o el signo/regla del tipo)

### Requirement: Valores Extras en Índices

The Índices screen (`admin` only) MUST expose a **Valores Extras** button that is **disabled** until a período is selected. The button MUST open a modal scoped to that selected period.

The modal MUST allow:

1. **Filtro tipo**: `ambos` (default) | `modulos` | `novedades` | `novedad_extra`
2. **Búsqueda** por nombre o legajo de profesional
3. A **grid** with one row per professional that has matching cargas, showing: cant. módulos, cant. novedades, importe módulos, importe novedades, importe total
4. **Expand** a professional row to show detalle columns: fecha, tipo, concepto, cant/horas, valor, importe, motivo, observación(es), servicio
5. **Checkboxes** per professional plus select-all in the header
6. Buttons **Exportar** (left of **Cerrar**)

Universe: all non-soft-deleted module assignments and hour novedades of the period; filters only narrow. Filter **novedad_extra** MUST include rows that have **any non-empty observation field** (currently `observacion_sin_produccion`); motivo alone without observation MUST NOT qualify.

Backend: `GET /novedades/indices/valores-extras` MUST require `admin`.

#### Scenario: Botón sin período

- GIVEN admin en Índices sin período
- THEN Valores Extras MUST estar deshabilitado

#### Scenario: Filtro novedad extra

- GIVEN carga con observación y carga solo con motivo sin observación
- WHEN filtro = novedad_extra
- THEN MUST incluir solo la que tiene observación

#### Scenario: Expand detalle

- GIVEN profesional con módulo y novedad en el período (filtro ambos)
- WHEN admin expande la fila
- THEN MUST ver el detalle de ambas cargas con las columnas definidas

### Requirement: Export PDF Valores Extras

From the Valores Extras modal, **Exportar** MUST download **one** PDF containing the detalle of **selected** professionals (at least one required). Multiple professionals MUST appear as separate pages/sections in the same PDF (page break between professionals).

The PDF visual chrome MUST match Clínica Monte Grande / app-recepcion signature PDFs: navy header band asset, gray title band with document title **Valores Extras**, footer label + page number.

Export MUST respect the current filtro (and applied search) and the selected `professional_ids`. Endpoint: `POST /novedades/indices/valores-extras/pdf` (`admin` only). If none of the selected professionals have cargas under the filter, the API MUST reject with a clear error (no empty fake PDF of “success”).

#### Scenario: Export selección

- GIVEN dos profesionales visibles y solo uno tildado
- WHEN Exportar
- THEN el PDF MUST incluir solo el seleccionado

#### Scenario: Sin selección

- GIVEN modal abierto sin checkboxes
- WHEN Exportar
- THEN MUST NOT descargar (UI o API bloquea)

## MODIFIED Requirements

### Requirement: Servicios y módulos (Param tabs)

(Previously: Param tabs include Producción between Módulos and Jefes; no Recálculo tab.)

In addition to existing Parametrización tabs, the tab list MUST include **Recálculo** immediately after **Feriados**, as defined in Requirement “Pestaña Recálculo en Parametrización”.

#### Scenario: Recálculo en el listado de tabs

- GIVEN admin en Parametrización
- WHEN lista tabs
- THEN MUST incluir Recálculo después de Feriados

### Requirement: Pantalla Índices por período

(Previously: two stacked sections; export out of scope.)

In addition to **Por servicio** and **Por profesional**, the screen MUST provide **Valores Extras** (modal) as defined in Requirements “Valores Extras en Índices” and “Export PDF Valores Extras”. Metric grids remain unchanged. Excel/CSV export of Índices metrics remains out of scope; PDF export applies only to Valores Extras.

#### Scenario: Valores Extras disponible con período

- GIVEN admin con período seleccionado en Índices
- WHEN pulsa Valores Extras
- THEN MUST abrirse el modal del período seleccionado
