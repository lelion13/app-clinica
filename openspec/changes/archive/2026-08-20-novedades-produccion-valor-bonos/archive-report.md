# Archive report: 2026-08-20-capital-humano-bonos-servicios-especiales + 2026-08-20-novedades-produccion-valor-bonos

**Date:** 2026-08-20  
**Order:** servicios-especiales first (promotion + UI sin servicio), then produccion-valor-bonos (tarifas + valorización + cleanup).

## Specs synced

| Domain | Action | Details |
|--------|--------|---------|
| `novedades` | Modified | Servicios y módulos (+ tab Producción) |
| `novedades` | Modified | Pantalla Capital Humano (sin selector servicio; promoción especiales; total con bonos) |
| `novedades` | Modified | Exportaciones XLS duales (`monto_total` con bonos) |
| `novedades` | Added | Columnas de bonos (cantidad + subtotal; promoción DEA/DEP/CAP/CAI) |
| `novedades` | Added | Modal solo bonos (excluye promovidos) |
| `novedades` | Added | XLS con bonos (cantidad + subtotal) |
| `novedades` | Added | Tarifas Producción (valor bonos) |
| `novedades` | Added | Valorización de bonos en Capital Humano |
| `novedades` | Added | Limpieza de opciones de bono huérfanas |
| `openspec/specs/README.md` | Updated | origins table |

## Archive paths

- `openspec/changes/archive/2026-08-20-capital-humano-bonos-servicios-especiales/`
- `openspec/changes/archive/2026-08-20-novedades-produccion-valor-bonos/`

## Contents each

proposal, design, decisions, exploration, specs/, tasks, implementation-notes (learnings F*), verify-report

## Migrations

- none (servicios-especiales)
- `0021_produccion_tarifa` (produccion-valor-bonos)

## Learnings captured

See `implementation-notes.md` in each archive:

- **servicios-especiales:** orden de fórmula `monto_total`; `opción.servicio` ≠ maestro Servicios; UI vs contrato API; tres tests de elegibilidad.
- **produccion-valor-bonos:** colisión `editProduccion`; build `recharts` ajeno; cleanup catálogo vs snapshot; combobox vs checkboxes; naming Producción.

## Still open (related)

- `capital-humano-bonos-resumen` — import/snapshot ADDED requirement still lives in that active change; stable spec now includes downstream behavior. Archive that change next to merge Importar bonos into main.

## Source of truth

`openspec/specs/novedades/spec.md`

## SDD cycle

Both changes planned → implemented → documented (learnings) → verified (PASS) → archived.
