# Proposal: novedades-capital-humano-grilla-totales

## Intent

Show a footer on the Capital Humano grid with sums of the four numeric columns for the currently visible rows.

## Scope

### In Scope
- Footer row: sum `monto_cargas`, `monto_ajustes`, `monto_bonos`, `monto_total` over `visibleRows`.
- Empty first columns (legajo/profesional) and acciones; empty grid → `$0,00`.
- Spec + runbook.

### Out of Scope
- Backend / API totals.
- XLS exports.
- Solo bonos modal / Detalle.

## Approach

Client-side sum in `NovedadesXlsPage.jsx` (`tfoot`).

## Risks

Low — display-only; filter already defines `visibleRows`.

## Success Criteria

- [ ] Footer sums match sum of visible numeric cells.
- [ ] Filter narrows footer totals.
- [ ] No rows → footer `$0,00`; XLS unchanged.
