# Exploration: novedades-capital-humano-grilla-totales

## Current State

Capital Humano main grid (`NovedadesXlsPage`): columns Legajo, Profesional, Total cargas, Ajustes, Total producción, Total general, Acciones. Client filter/sort via `visibleRows`. No footer totals. XLS exports unchanged and out of scope.

## Intent

Footer row summing the four numeric columns for **visible** rows only.

## Recommendation

**UI-only** — `useMemo` sums over `visibleRows`; `<tfoot>` always rendered (`$0,00` when empty). No API/backend/XLS changes.

## Survey

See `decisions.md`.
