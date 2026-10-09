# Proposal: novedades-capital-humano-ajuste-mas-menos

## Intent

Capital Humano needs a second Excel import next to **Importe a descontar** that creates adjustments with **signed** amounts: negative rows discount, positive (or unsigned) rows add. Reuse the same closed-period, all-or-nothing, waterfill, and annul-lot UX, without replacing the existing discount-only import.

## Scope

### In Scope
- Button **Ajuste +/-** immediately right of Importe a descontar / Anular descuento (before Descargar liquidación); with active lot → **Anular Ajuste +/-**.
- Excel headers exact: `Legajo`, `Nombre y Apellido`, `Sector`, `Monto` (signed).
- Import `admin`/`rrhh`, closed period only; re-import of this flow requires annulling **this** lot first.
- Independent lot from descuento: both lots MAY coexist on the same period.
- Negatives: same rules as Importe a descontar (`importe = -abs(Monto)`, waterfill, cap cargas+producción, total general must not go negative).
- Positives: same waterfill across services, **no** amount/total cap; `importe = +abs(Monto)`.
- Comentario: `Legajo - Nombre y Apellido - Sector - {importe signed}`, truncate 500.
- Todo-o-nada + centered modal with **all** errors.
- Liquidación: keep existing `servicio_id` → concepto mapping for created adjustments.

### Out of Scope
- Changing Importe a descontar behavior.
- Changing manual **Agregar importe**.
- Downloadable template.
- Import on open period.
- Validating Nombre/Sector against catalog.

## Approach

1. Migration: nullable lote id for this import (e.g. `ajuste_mas_menos_lote_id` UUID), distinct from `descuento_lote_id`.
2. Service: mirror descuento import parse/validate/waterfill; branch on Monto sign for importe, caps, and total-general check.
3. API: import multipart, anular by this lote, status “has Ajuste +/- lot”.
4. UI: second toggle button + file picker + shared-style error modal.

## Affected Areas

| Area | Impact |
|------|--------|
| `models/novedades.py` + Alembic | New lote column |
| `services/novedades/` import + CH | New/reuse waterfill |
| `api/routers/novedades.py` | New endpoints or parallel routes |
| `NovedadesXlsPage.jsx` | Button + wire-up |
| `docs/runbook.md` | Ops note |
| `openspec/specs/novedades/spec.md` | Delta → merge on archive |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Confundir lotes Anular | Med | Labels distintos; columnas lote separadas |
| Waterfill positivo mal interpretado | Med | Spec scenarios: fill by cargas desc, remainder to last, no cap |
| Doble import accidental | Low | Re-import blocked until Anular Ajuste +/- |

## Rollback Plan

Revert migration/code; annul lot in UI soft-deletes active Ajuste +/- adjustments.

## Dependencies

- Existing Importe a descontar (waterfill, grilla CH, soft-delete ajustes).
- Liquidación `servicio_id` mapping already in place.

## Success Criteria

- [ ] Signed Excel creates +/− adjustments with waterfill rules per sign.
- [ ] Descuento lot and Ajuste +/- lot can both be active; each Anular is selective.
- [ ] Any row error → zero rows from this import + full error modal.
- [ ] Importe a descontar and Agregar importe unchanged.
