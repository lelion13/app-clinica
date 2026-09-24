# Exploration: novedades-descarga-parcial-modulos

## Intent

Capital Humano: button **Descarga parcial de módulo** (after Descargar liquidación), closed period only. Modal with date from/to (within period) → grid of CH-like rows filtered by dates, **cargas only**, expandable Detalle inline, Cancel + Download Excel.

## Current State

- CH page: `NovedadesXlsPage.jsx`; liquidación after Importe a descontar; closed-only.
- Main grid columns: legajo, name, total cargas, ajustes, total producción, total general + Detalle/Agregar importe.
- Detalle today: separate modal (cargas + producción + ajustes).
- Aggregates from full period via `build_capital_humano_rows` / `build_grid_rows` (`fecha_realizacion` on carga items).

## Survey status

CLOSED (Q1–Q21). Ready for proposal + delta spec.
