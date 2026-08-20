# Delta: novedades

## ADDED Requirements

### Requirement: Importar bonos resumen en Capital Humano

Capital Humano MUST offer **Importar bonos** to `admin`/`rrhh` only. The user MUST select a **single period** before import. The backend MUST call the configured external resumen API with `fecha_desde` = period `fecha_inicio` and `fecha_hasta` = period `fecha_fin`, using the same Bearer token as Novedades professional sync. Results MUST be persisted per period. Match MUST be by API `profesional` → catalog `CODPROF` (string/trim). Each dynamic column MUST be the full option `centro|servicio|semana|horario`. Duplicate rows for the same professional+option MUST sum `cantidad`. Unknown CODPROF MUST be ignored and counted in the summary. On success the UI MUST show a summary modal (received / matched / solo-bonos / columns / ignored) and refresh the grid.

While the period is **open**, re-import MUST **replace** the period’s bonos snapshot. While the period is **closed**, import MUST be rejected (frozen). If the period lacks valid start/end dates, the API MUST return 422 without calling the external service. If the external call fails, the system MUST NOT modify the existing snapshot and MUST surface an error modal.

#### Scenario: Import con período abierto

- GIVEN período open con fechas 2026-07-01..2026-07-31
- AND admin selecciona ese período
- WHEN pulsa Importar bonos
- THEN el backend MUST llamar el API con esas fechas
- AND MUST persistir cantidades matcheadas por CODPROF
- AND la grilla MUST mostrar columnas dinámicas a la derecha

#### Scenario: Re-import reemplaza

- GIVEN período open con snapshot previo
- WHEN se importa de nuevo con éxito
- THEN el snapshot anterior del período MUST ser reemplazado

#### Scenario: Período cerrado congela

- GIVEN período closed con snapshot
- WHEN se intenta Importar bonos
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

The main Capital Humano grid MUST remain **one row per professional** with cargas/ajustes activity. For the selected period filter, it MUST append dynamic bonos quantity columns for options present in that period’s snapshot. Professionals that have bonos but **no** cargas/ajustes MUST NOT appear as rows in the main grid.

#### Scenario: Una fila

- GIVEN profesional P con cargas y bonos en dos opciones
- WHEN se lista Capital Humano del período
- THEN MUST haber una sola fila de P con ambas columnas de cantidad

### Requirement: Modal solo bonos

Capital Humano MUST provide a control that opens a **modal** listing catalog professionals that have persisted bonos for the period and have neither cargas nor ajustes in that Capital Humano scope. Roles: `admin`/`rrhh`.

#### Scenario: Solo bonos en modal

- GIVEN profesional Q con bonos y sin cargas/ajustes en el período
- WHEN admin abre el modal Solo bonos
- THEN MUST ver a Q
- AND Q MUST NOT aparecer en la grilla principal

### Requirement: XLS con bonos

Capital Humano MUST offer a third download **XLS con bonos** (aggregated row per professional plus dynamic bonos columns). Existing aggregated and detail XLS MUST remain unchanged. In this change, XLS downloads MUST remain available regardless of period open/closed (testing exception).

#### Scenario: Tercer XLS

- GIVEN snapshot de bonos en el período
- WHEN admin descarga XLS con bonos
- THEN el archivo MUST incluir columnas de opciones y cantidades

## MODIFIED Requirements

### Requirement: Pantalla Capital Humano

(Previously: grilla agregada, ajustes, Detalle, dos XLS.)

In addition: Importar bonos (period-required), dynamic bonos columns from persisted snapshot, Solo bonos modal, and a third XLS-with-bonos download, per the ADDED requirements above.

---

## Archive note (2026-08-20)

Requirements **Columnas de bonos**, **Modal solo bonos**, and **XLS con bonos** as written above describe the **original** intent of this change. The stable spec (`openspec/specs/novedades/spec.md`) holds the **final** behavior after:

- `2026-08-20-capital-humano-bonos-servicios-especiales` (promoción DEA/DEP/CAP/CAI)
- `2026-08-20-novedades-produccion-valor-bonos` (subtotales + cleanup huérfanas)

Only **Importar bonos resumen** was missing from the stable spec and was merged at archive time.
