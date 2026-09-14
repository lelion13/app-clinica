# Exploration: novedades-liquidacion-empresa-constante

## Current State

`export-liquidacion.xlsx`: column `empresa` = `CHI` if `concepto > 100` else `CMG`. Internal production bucketing uses `empresa_from_prefix` (SC→CHI) and `empresa_from_concepto` for allocation — separate from the written cell.

## Intent

Write numeric `1` in every `empresa` cell. Do not change allocation/build logic. Only this export.

## Recommendation

Keep `empresa_from_*` for internal split; set `LiquidacionRow.empresa = 1` (int) when building output / XLS rows.
