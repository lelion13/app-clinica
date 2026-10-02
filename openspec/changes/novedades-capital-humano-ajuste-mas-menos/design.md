# Design: novedades-capital-humano-ajuste-mas-menos

## Overview

Mirror `importe_descontar` as a parallel Capital Humano Excel import with signed `Monto`. Persist adjustments under a separate lot column so discount and Ajuste +/- lots can coexist and annul independently.

## Architecture

```
UI (NovedadesXlsPage)
  → GET  /capital-humano/ajuste-mas-menos/status
  → POST /capital-humano/ajuste-mas-menos          (multipart)
  → POST /capital-humano/ajuste-mas-menos/anular
       → services/novedades/ajuste_mas_menos.py
            → parse Excel (same headers)
            → validate vs CH grid
            → waterfill (reuse importe_descontar helpers)
            → insert NovedadesAjusteCapital(ajuste_mas_menos_lote_id=…)
```

## Data Model

- Add nullable indexed `ajuste_mas_menos_lote_id` `String(36)` on `novedades_ajuste_capital`.
- Keep `descuento_lote_id` unchanged; an adjustment belongs to at most one of the two lot types (or neither for manual).

Migration: `0029_ajuste_mas_menos_lote` revising `0028_servicio_especialista`.

## Sign / waterfill rules

Reuse `_waterfill` from `importe_descontar` (returns negative partials). Then:

| Monto | Persist | Cap / total check | Allocation |
|-------|---------|-------------------|------------|
| < 0 | `-abs` | Same as descontar | Use `_waterfill` as-is |
| > 0 | `+abs` | None | Negate each `_waterfill` amount |
| 0 / empty | error | — | — |

Solo producción: single adjustment `servicio_id=null` with signed full amount.

## API

Schemas parallel to ImporteDescontar:
- `AjusteMasMenosStatusResponse` (`has_ajuste`, `lote_id`)
- `AjusteMasMenosImportResponse` (`created`, `lote_id`)
- `AjusteMasMenosAnularResponse` (`deleted`)

Auth: `require_admin_or_rrhh`. Closed period required (409 if open).

## Frontend

- State/handlers mirrored from descuento (`hasAjuste`, busy, errors modal).
- Button immediately after Importe a descontar / Anular descuento.
- Labels: **Ajuste +/-** / **Anular Ajuste +/-**.

## Testing

- Unit: signed waterfill transform (+), parse `+500`, comment with positive amount.
- Rely on existing descontar tests for base `_waterfill` negatives.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Reuse `descuento_lote_id` with type flag | Spec requires independent coexist + selective Anular |
| Refactor shared import module now | Out of scope; private helper import is enough |
| Cap positives | Rejected in Q3 |
