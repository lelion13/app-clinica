# Exploration: Export liquidación XLS — Capital Humano

## Context

Capital Humano already exports:
- `export-capital.xlsx` (aggregated totals)
- `export-capital-bonos.xlsx` (with bono columns)
- `export.xlsx` (detail cargas)

`concepto_liquidacion` exists on `novedades_servicio` but was deferred for Excel liquidación (see archive `capital-humano-grilla-actualizar`).

## Goal

New download **Descargar liquidación** producing rows:
`empresa | legajo | monto | concepto`
driven by servicio conceptos for cargas, with production and ajustes merged in without changing existing exports or grid behavior.

## Constraints

- Do not break existing endpoints/UI downloads.
- Closed period only.
- Fail closed if any carga service lacks `concepto_liquidacion`.
