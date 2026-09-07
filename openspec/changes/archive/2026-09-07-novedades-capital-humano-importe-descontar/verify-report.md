# Verify Report: novedades-capital-humano-importe-descontar

## Status
PASS (user-verified in production after migration)

## Checks
- Automated: backend pytest suite green at apply time (`166 passed`, including `test_importe_descontar` + liquidación `servicio_id`).
- Ops: prod 500 on Capital Humano fixed by `alembic upgrade head` → `0025_ajuste_descuento_lote` (column `descuento_lote_id`).
- Manual (user, 2026-09-07): Importe a descontar / Anular / grilla Capital Humano OK en `clinica.lionapp.cloud`.

## Notes
- Deploy of model without migration caused 500 on `GET /capital-humano` and status endpoint; restart backend not required after migrate.
