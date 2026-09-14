# Delta Spec: novedades-liquidacion-empresa-constante

## MODIFIED Requirements

### Requirement: Filas de liquidación desde cargas

(Previously: `empresa` = CHI if concepto > 100 else CMG.)

Each distinct `(legajo, concepto)` from cargas MUST produce (after merges) one output row with:
- `concepto` = that `concepto_liquidacion`
- `empresa` = numeric **`1`** (constant for all rows in this export)
- `legajo` = professional legajo (string as stored)
- `monto` = sum of carga values for that concepto, plus allocated production and ajustes, preserving system decimal precision

Internal allocation of production by CHI/CMG buckets (from concepto thresholds and `centro`/`sucursal` prefixes) MUST remain unchanged; only the exported `empresa` cell value changes.

#### Scenario: Profesional multi-servicio

- GIVEN profesional con cargas en servicio concepto 50 y servicio concepto 150
- WHEN exporta liquidación
- THEN MUST haber dos filas con conceptos 50 y 150
- AND ambas MUST tener empresa = 1 (numérico)

#### Scenario: Servicio sin concepto bloquea

- GIVEN al menos una carga en servicio sin `concepto_liquidacion`
- WHEN exporta liquidación
- THEN MUST fallar
- AND el mensaje MUST indicar el/los nombre(s) de servicio sin concepto

### Requirement: Solo producción sin cargas

(Previously: fixed-concepto rows carried empresa CMG/CHI derived from centro.)

Fixed-concepto rows (90/91/122/123) MUST still be chosen using the existing empresa/servicio special mapping for **which conceptos appear**, but the exported `empresa` column MUST be numeric **`1`**.

#### Scenario: Solo DEA CMG

- GIVEN profesional sin cargas con bono DEA en centro CMG y producción valorizada
- WHEN exporta
- THEN MUST existir fila concepto=90 con el monto correspondiente
- AND empresa MUST ser 1
