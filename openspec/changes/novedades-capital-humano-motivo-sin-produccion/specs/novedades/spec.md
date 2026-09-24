# Delta Spec: novedades — Capital Humano motivos sin producción

## ADDED Requirements

### Requirement: Motivos sin producción en Capital Humano

Capital Humano (`admin`/`rrhh`) MUST provide:

1. A **Motivo** select with options **Todos**, **Vacaciones**, **Enfermedad** (default **Todos**). The existing text filter MUST remain legajo/nombre only.
2. A button **Con novedad** that opens a modal listing **carga rows** (módulos and novedades) that have `motivo_sin_produccion` set, scoped to the selected period, and filtered by the Motivo select:
   - **Todos** → any motivo (`vacaciones` or `enfermedad`)
   - **Vacaciones** / **Enfermedad** → only that motivo
3. Main-grid row **highlight** (single shared background/border color; no motivo text on the main grid):
   - **Todos** → professionals with ≥1 matching carga with any motivo
   - **Vacaciones** / **Enfermedad** → professionals with ≥1 carga of that motivo
   - The select MUST NOT hide rows or change footer/totals logic

The modal MUST be a **flat table** of cargas (not accordion). Columns MUST include at least: legajo, nombre, tipo, servicio, concepto, valor, fecha realización, **Motivo**, **Observación** (and MAY include other carga columns already used in Detalle). Empty result MUST show a clear empty state.

“Matching carga” MUST mean rows from `/novedades/grilla` (or equivalent) for the period where `motivo_sin_produccion` is non-null and matches the select rule above. Professionals who only appear for producción/bonos without such cargas MUST NOT be highlighted.

#### Scenario: Highlight con Todos

- GIVEN período con profesionales A (carga Vacaciones) y B (sin motivo)
- WHEN Motivo = Todos
- THEN la fila de A MUST resaltarse
- AND la fila de B MUST NOT resaltarse
- AND ambas filas MUST seguir visibles

#### Scenario: Select Vacaciones

- GIVEN A con solo Enfermedad y C con Vacaciones
- WHEN Motivo = Vacaciones
- THEN solo C MUST resaltarse
- AND el modal **Con novedad** MUST listar solo cargas con motivo Vacaciones

#### Scenario: Modal vacío

- GIVEN Motivo = Enfermedad y ninguna carga con ese motivo
- WHEN admin abre **Con novedad**
- THEN MUST ver estado vacío (sin filas)

### Requirement: Motivo y observación en Detalle Cargas

In Capital Humano **Detalle**, the Cargas table MUST include columns **Motivo** and **Observación** for each carga row. When the carga has no `motivo_sin_produccion`, those cells MUST be empty or “—”. Labels MUST use human-readable Motivo (Vacaciones / Enfermedad).

#### Scenario: Detalle con motivo

- GIVEN carga con motivo Vacaciones y observación “viaje”
- WHEN admin abre Detalle
- THEN MUST ver Motivo Vacaciones y Observación viaje en esa fila de Cargas

## MODIFIED Requirements

### Requirement: Grilla y XLS (detalle)

(Previously: detail columns without motivo/observación.)

`GET /novedades/grilla` row payloads MUST include optional **`motivo_sin_produccion`** and **`observacion_sin_produccion`** (null when absent).

`GET /novedades/export.xlsx` detail sheet(s) MUST include columns **motivo** and **observacion** (human-readable motivo label or raw value consistently with other exports; empty when null), in addition to existing detail columns. Resumen sheet (when date range produces two sheets) MUST NOT be required to add these columns.

#### Scenario: Export incluye motivo

- GIVEN una carga con motivo Enfermedad
- WHEN se descarga `export.xlsx` (sin o con fechas)
- THEN la hoja de detalle MUST incluir columnas motivo y observación
- AND esa fila MUST reflejar Enfermedad y su observación

### Requirement: Pantalla Capital Humano

(Previously: period selector, text filter, no Motivo select / Con novedad.)

In addition to existing controls, the Capital Humano toolbar MUST show the Motivo select and the **Con novedad** button as defined in Requirement “Motivos sin producción en Capital Humano”. The `GET /novedades/capital-humano` response MUST expose per-row data sufficient for the UI to highlight professionals (e.g. which motivos are present among that professional’s cargas in the period).

#### Scenario: Controles visibles

- GIVEN admin en Capital Humano
- WHEN mira la toolbar
- THEN MUST ver select Motivo y botón Con novedad
- AND el filtro de texto MUST seguir siendo solo legajo/nombre
