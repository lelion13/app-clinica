# Archive Report: novedades-capital-humano-motivo-sin-produccion

## Change Summary
- **Change Name:** `novedades-capital-humano-motivo-sin-produccion`
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-09-30

## Delivered
1. Capital Humano: select Motivo (Todos / Vacaciones / Enfermedad) + highlight de filas (un color).
2. Botón **Con novedad** → modal lista plana de cargas con `motivo_sin_produccion` (respeta select).
3. Detalle Cargas + `export.xlsx`: columnas Motivo / Observación.
4. API: `motivo_sin_produccion` / `observacion_sin_produccion` en `GridRowResponse`; `motivos_sin_produccion` en filas capital-humano.
5. Tests + runbook.

## Specs synced
| Domain | Action | Details |
|--------|--------|---------|
| `novedades` | Updated | ADDED: Motivos sin producción en CH; Motivo y observación en Detalle Cargas. MODIFIED: Grilla y XLS (detalle); Pantalla Capital Humano; Detalle unificado (cross-ref). |

## Verification
Implemented and user requested archive (2026-09-30). Runbook already documented under the change name.
