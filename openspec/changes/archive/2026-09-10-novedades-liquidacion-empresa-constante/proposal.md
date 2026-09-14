# Proposal: novedades-liquidacion-empresa-constante

## Intent

In **Descargar liquidación**, column `empresa` MUST always be numeric `1`, without changing how montos are built or allocated.

## Scope

### In Scope
- Output `empresa=1` (int) on liquidación XLS / `LiquidacionRow`.
- Update specs, tests, runbook.

### Out of Scope
- Other Capital Humano exports.
- Changing `empresa_from_concepto` / `empresa_from_prefix` allocation rules.
- Renaming the column.

## Approach

Keep internal CHI/CMG bucketing; assign `empresa=1` when emitting rows for the file.

## Success Criteria

- [x] Every liquidación XLS row has numeric empresa `1`.
- [x] Production/carga split behavior unchanged.
- [x] Other exports untouched.
