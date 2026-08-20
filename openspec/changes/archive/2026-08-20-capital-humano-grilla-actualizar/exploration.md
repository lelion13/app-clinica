# Exploration: capital-humano-grilla-actualizar

## Topic

Reordenar **Capital Humano**: período (default open) + **Actualizar** (import bonos) + grilla de totales por profesional + Detalle unificado. Concepto liquidación / Excel / cierre → change posterior.

## Current State

- `/novedades/xls`: período, Importar bonos, Solo bonos, XLS, grilla 1 fila/profesional con columnas dinámicas de bonos.
- Import: `POST .../bonos/import`; valorización Producción; elegibilidad DEA/DEP/CAP/CAI.
- `concepto_liquidacion` en servicios Param aún no agrupa CH.

## Decisions (closed)

Ver `decisions.md`. Resumen: Actualizar=import bonos; sin botón Importar bonos; Solo bonos queda; grilla totales fijos + ajustes; Detalle unificado; Excel out.

## Affected Areas

- `NovedadesXlsPage.jsx`
- Posible extensión detalle en `capital_humano` / schemas
- Spec novedades + runbook

## Risks

- Detalle más cargado.
- Botones Excel legacy hasta el change de export.
