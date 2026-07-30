# Delta: novedades

## ADDED Requirements

### Requirement: LEGAJO en sync de profesionales Novedades

HTTP sync of `novedades_profesional` MUST map optional field `LEGAJO` (aliases `legajo`) as a **string**, trimming outer spaces and preserving leading zeros, max length 40. Missing or blank LEGAJO MUST store `null` without failing the row. Sync MUST continue successfully when LEGAJO is absent.

#### Scenario: LEGAJO con ceros a la izquierda

- GIVEN response remoto con `CODPROF` "032" y `LEGAJO` " 05100"
- WHEN corre sync
- THEN el profesional MUST persistir `legajo` = "05100"

#### Scenario: LEGAJO ausente

- GIVEN fila remota sin `LEGAJO`
- WHEN corre sync
- THEN el upsert MUST completar con `legajo` null
- AND el resto de campos MUST actualizarse normalmente

### Requirement: Pantalla Capital Humano

The former **Generación archivo XLS** nav entry MUST be labeled **Capital Humano** and remain restricted to `admin`/`rrhh`. The page MUST show **one row per professional** with columns: legajo, name, monto cargas, monto ajustes, monto total. Rows MUST appear only when the professional has cargas and/or adjustments in the active filter scope (period ± optional service). Filter/sort MUST follow the same UX patterns as the Carga grid (period, service, text search including legajo/name).

Total cargas MUST be the sum of module + novedad valores in the filtered period (and only that service when filtered). Total = cargas ± persisted adjustments. Adjustments MUST be allowed when the period is **closed**.

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

The system MUST persist create-only signed adjustments (`novedades_ajuste_capital`) with non-zero `importe` and required non-blank `comentario`. UI MUST open a modal from the ajustes column showing history and a create form. Edit/delete of adjustments MUST NOT be offered in this change. Scope of listed/created adjustments MUST match the current period filter and optional service filter.

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

Capital Humano MUST offer **two** downloads: aggregated Capital Humano XLS (`GET /novedades/export-capital.xlsx`) and the existing detail XLS (`GET /novedades/export.xlsx`). Both MUST honor the same filters as the grid and require `admin`/`rrhh`.

#### Scenario: Export agregada

- GIVEN filas visibles en Capital Humano
- WHEN descarga export-capital
- THEN el XLS MUST contener una fila por profesional con legajo, nombre y montos

## MODIFIED Requirements

### Requirement: Sincronización HTTP de profesionales

(Previously: CODPROF, NOMBRES, CODPROV only.)

In addition to prior sync rules, each upsert MUST refresh `legajo` from remote `LEGAJO` when present (string trim, leading zeros preserved). Absence of LEGAJO MUST NOT fail the sync row.

#### Scenario: Actualiza legajo en re-sync

- GIVEN profesional local con `legajo` null
- AND response exitoso incluye LEGAJO "05100"
- WHEN corre sync
- THEN `legajo` MUST quedar "05100"
