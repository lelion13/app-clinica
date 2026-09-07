# Archive Report: novedades-capital-humano-importe-descontar

## Change Summary
- **Change Name:** `novedades-capital-humano-importe-descontar`
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-09-07

## Delivered Capabilities
1. Botón **Importe a descontar** / **Anular descuento** (antes de Descargar liquidación); solo período cerrado; `admin`/`rrhh`.
2. Import Excel columnas exactas `Legajo`, `Nombre y Apellido`, `Sector`, `Monto`; importe `-abs(Monto)`; comentario truncado 500.
3. Lote `descuento_lote_id` (rev `0025_ajuste_descuento_lote`); Anular solo el lote; re-import exige anular.
4. Waterfill multi-servicio (mayor cargas primero; resto dentro de cargas+producción al último); solo-prod → ajuste sin servicio.
5. Todo-o-nada + modal con todos los errores.
6. Liquidación: ajustes con `servicio_id` van al concepto del servicio.

## Verification
- User-tested OK in production (2026-09-07) after `alembic upgrade head`.
- Docs: `docs/runbook.md` updated.
