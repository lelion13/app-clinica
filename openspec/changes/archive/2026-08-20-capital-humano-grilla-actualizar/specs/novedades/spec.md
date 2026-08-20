# Delta: novedades

## MODIFIED Requirements

### Requirement: Pantalla Capital Humano

The Capital Humano page (admin/rrhh) MUST present, at the top: a **period selector** that defaults to the **open** period when one exists, and an **Actualizar** button.

**Actualizar** MUST run the existing bonos import for the selected period (same persistence rules: replace snapshot when open; reject when closed) and then refresh the grid. The dedicated **Importar bonos** button MUST be removed. **Solo bonos** MUST remain.

On entry, the grid MUST show **already persisted** data for the selected period (cargas/ajustes + last bonos snapshot if any). **Actualizar** MUST be disabled when the selected period is **closed** (persisted data still visible).

The main grid MUST show **one row per professional** with fixed columns: legajo, name, total cargas (jefe modules/novedades), ajustes, total producción (valorized imported bonos), total general (`cargas + ajustes + producción`), plus actions. Dynamic per-option bonos columns MUST NOT appear on the main grid.

Row eligibility MUST remain: professionals with cargas and/or adjustments, or bonos-only with option `servicio` in `DEA|DEP|CAP|CAI`. Others with only non-special bonos MUST appear only in Solo bonos.

Text filter (legajo/name) and banner for options missing Producción tariffs MUST remain.

Grouping/ordering by `concepto_liquidacion` is **out of scope** for this screen change (Excel change later).

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
- AND la grilla MUST mostrar el snapshot persistido

#### Scenario: Columnas fijas

- GIVEN profesionales en grilla con bonos valorizados
- WHEN se lista Capital Humano
- THEN MUST ver Total cargas, Ajustes, Total producción, Total general
- AND MUST NOT ver columnas dinámicas por opción de bono en la grilla principal

### Requirement: Ajustes de Capital Humano

Creating an adjustment MUST remain available from the **main grid** action (e.g. agregar importe) without requiring opening Detalle. The Detalle modal MUST also show the adjustment **history** for that professional/period.

#### Scenario: Alta desde grilla

- GIVEN profesional en grilla y período seleccionado
- WHEN admin agrega un ajuste desde la acción de grilla
- THEN MUST persistirse
- AND montos de la fila MUST actualizarse

### Requirement: Importar bonos resumen en Capital Humano

The import behavior (API, match CODPROF, replace when open, freeze when closed, summary modal, orphan cleanup) MUST remain. The UI entry point MUST be the **Actualizar** button on Capital Humano instead of a separate Importar bonos button.

#### Scenario: Entry point Actualizar

- GIVEN período open
- WHEN admin pulsa Actualizar
- THEN MUST ejecutarse el mismo flujo de import que antes vía Importar bonos

## ADDED Requirements

### Requirement: Detalle unificado Capital Humano

The **Detalle** action MUST open a modal showing, for the selected professional and period: (1) carga items (módulos/novedades), (2) producción/bonos breakdown (quantities and subtotals per option as available), and (3) adjustment history. Adding a new adjustment MAY remain only on the grid action (not required inside Detalle).

#### Scenario: Detalle completo

- GIVEN profesional con cargas, bonos y ajustes en el período
- WHEN admin abre Detalle
- THEN MUST ver las tres secciones (cargas, producción, historial de ajustes)
