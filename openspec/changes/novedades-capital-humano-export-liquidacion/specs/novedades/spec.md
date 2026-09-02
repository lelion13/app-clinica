# Delta Spec: novedades-capital-humano-export-liquidacion

## ADDED Requirements

### Requirement: Export liquidación XLS (Capital Humano)

Capital Humano MUST offer a **Descargar liquidación** control for `admin`/`rrhh` that downloads an `.xlsx` with exactly these columns, in order: **empresa**, **legajo**, **monto**, **concepto**.

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
- `monto` = sum of carga values for that concepto, plus allocated production and ajustes (see below), preserving system decimal precision

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
