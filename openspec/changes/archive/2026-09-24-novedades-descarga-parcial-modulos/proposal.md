# Proposal: novedades-descarga-parcial-modulos

## Intent

Allow `admin`/`rrhh` on Capital Humano to review and download **module/novedad cargas** for a **date range inside a closed period**, without producción/ajustes — via modal preview + Excel (resumen + detalle).

## Scope

### In Scope
- Button **Descarga parcial de módulos** after **Descargar liquidación**; enabled only when selected period is **closed**.
- Modal: `fecha desde` / `fecha hasta` (empty on open; UI `min`/`max` = period bounds; require `desde ≤ hasta`).
- Auto-load grid when both dates valid: columns legajo · nombre · total cargas (sum of `valor`) + Detalle.
- Rows only if ≥1 carga with `fecha_realizacion` in range (modules + novedades).
- Detalle: expand one row at a time under the row (indent); same carga columns as CH Detalle section; no producción/ajustes; no text filter/footer.
- Download enabled only with valid dates and ≥1 row; file `descarga-parcial-modulos_{desde}_{hasta}.xlsx`.
- Extend `GET /novedades/grilla` + `GET /novedades/export.xlsx` with optional `fecha_desde`/`fecha_hasta` (filter `fecha_realizacion`, inclusive). When both present on export → sheets **Resumen** + **Detalle**; without dates → current single-sheet behavior.

### Out of Scope
- API requiring closed period or validating dates against period bounds (UI-only).
- Producción, ajustes, liquidación, importe a descontar.
- New dedicated backup-style endpoints.
- `jefe_medico` access.

## Approach

1. Backend: add date filters to `build_grid_rows` / grilla + `export_xlsx_bytes`; when both dates set, add Resumen sheet (legajo, nombre, total cargas) then Detalle.
2. Frontend modal on `NovedadesXlsPage.jsx`: call `/grilla` with dates, aggregate by professional client-side; expand uses filtered items; download via existing export URL with dates + custom filename.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `NovedadesXlsPage.jsx` | Modified | Button + modal + expand + download |
| `export_xls.py` + router | Modified | Date filters; 2-sheet export when dates set |
| `openspec/specs/novedades` | Modified | Delta requirements |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Breaking existing single-sheet export | Med | 2 sheets only when both date params present |
| Large ranges / many rows | Low | Same pagination limits as grilla today; reuse query |

## Rollback Plan

Revert FE button/modal and date-filter branches in export/grilla; restore prior export behavior.

## Dependencies

- Closed period available in Capital Humano (existing).
- Survey Q1–Q21 closed (`decisions.md`).

## Success Criteria

- [ ] Button visible only for closed period, after Descargar liquidación.
- [ ] Modal filters by `fecha_realizacion`; grid shows cargas-only totals; accordion Detalle.
- [ ] Excel 2 sheets with expected filename; without dates export unchanged.
