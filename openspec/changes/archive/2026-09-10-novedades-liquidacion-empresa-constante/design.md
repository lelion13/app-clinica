# Design: novedades-liquidacion-empresa-constante

## Approach

In `build_liquidacion_rows`, after aggregating with internal CHI/CMG keys, emit:

```python
LiquidacionRow(empresa=1, legajo=..., monto=..., concepto=...)
```

`empresa_from_concepto` / `empresa_from_prefix` remain for allocation only. XLS already writes `row.empresa` as cell value (int → numeric).

## Files

| File | Change |
|------|--------|
| `liquidacion_export.py` | `LiquidacionRow.empresa: int`; emit `1` |
| `test_liquidacion_export.py` | Assert `empresa == 1` |
| delta + runbook | Document |

## Sort

Sort by `(legajo, concepto)` (empresa constant) or keep `(empresa, legajo, concepto)` — equivalent when empresa is always 1.
