# Delta Spec: novedades — descarga parcial de módulos

## ADDED Requirements

### Requirement: Descarga parcial de módulos (Capital Humano)

Capital Humano MUST show a control **Descarga parcial de módulos** immediately **after** **Descargar liquidación**, for `admin`/`rrhh` only. The control MUST be enabled only when the selected period is **closed** (same gate style as liquidación).

Activating it MUST open a modal with:
- Date inputs **desde** and **hasta**, initially empty
- UI constraints: `min`/`max` = period `fecha_inicio`/`fecha_fin`; require `desde ≤ hasta`
- No text filter and no footer totals in the modal grid

When both dates are valid, the modal MUST automatically load a grid with columns: **legajo**, **nombre**, **total cargas**, and action **Detalle**.  
**Total cargas** MUST be the sum of `valor` of matching carga items (módulos + novedades), same meaning as Capital Humano cargas total.  
Professionals with **no** matching cargas in the range MUST NOT appear.

Filter field MUST be **`fecha_realizacion`**, inclusive on both ends.

**Detalle** MUST expand **under** the selected row (indented), showing the same carga line columns as the Capital Humano Detalle “Cargas” section, limited to items in the date range. MUST NOT show producción or ajustes. Only **one** row MAY be expanded at a time.

Modal footer MUST provide **Cancelar** (close) and **Descargar**. **Descargar** MUST be enabled only when dates are valid and the grid has ≥1 row. Download MUST produce `descarga-parcial-modulos_{desde}_{hasta}.xlsx`.

#### Scenario: Botón solo período cerrado

- GIVEN período abierto seleccionado
- WHEN admin mira Capital Humano
- THEN **Descarga parcial de módulos** MUST estar deshabilitado o no operable
- AND con período cerrado MUST estar habilitado después de **Descargar liquidación**

#### Scenario: Grilla por rango

- GIVEN período cerrado y modal abierto
- WHEN admin elige desde/hasta válidos dentro del período
- THEN MUST cargarse la grilla automáticamente
- AND solo profesionales con cargas en ese rango MUST aparecer
- AND columnas MUST ser legajo · nombre · total cargas · Detalle

#### Scenario: Detalle indentado

- GIVEN grilla con filas
- WHEN admin pulsa Detalle en una fila
- THEN MUST expandirse debajo de esa fila el detalle de cargas del rango
- AND al expandir otra fila MUST cerrarse la anterior

#### Scenario: Descargar Excel

- GIVEN grilla con ≥1 fila
- WHEN admin pulsa Descargar
- THEN MUST descargar `descarga-parcial-modulos_{desde}_{hasta}.xlsx`
- AND el archivo MUST incluir hojas **Resumen** y **Detalle**

## MODIFIED Requirements

### Requirement: Grilla y XLS (detalle)

(Previously: filters período, servicio, texto, concepto — no date range on `fecha_realizacion`.)

`GET /novedades/grilla` and `GET /novedades/export.xlsx` MUST accept optional query params **`fecha_desde`** and **`fecha_hasta`**. When provided, results MUST include only rows whose **`fecha_realizacion`** satisfies `fecha_desde ≤ fecha_realizacion ≤ fecha_hasta`. The API MUST NOT require the period to be closed and MUST NOT reject dates outside the period bounds (period bounds are UI-only for this feature).

When **both** `fecha_desde` and `fecha_hasta` are provided on `export.xlsx`, the workbook MUST contain two sheets:
1. **Resumen** — one row per professional with loads in range: legajo, nombre, total cargas (sum of `valor`)
2. **Detalle** — same detail columns as the existing single-sheet export, filtered by the date range

When date params are omitted, export MUST keep the existing single-sheet detail behavior.

#### Scenario: Export con fechas → 2 hojas

- GIVEN cargas en el período
- WHEN `GET /novedades/export.xlsx` con `fecha_desde` y `fecha_hasta`
- THEN el XLS MUST tener hojas **Resumen** y **Detalle**
- AND Detalle MUST solo incluir filas con `fecha_realizacion` en el rango

#### Scenario: Export sin fechas → 1 hoja

- GIVEN el export detalle histórico
- WHEN se descarga sin `fecha_desde`/`fecha_hasta`
- THEN MUST comportarse como antes (una hoja de detalle)
