# Archive Report: novedades-descarga-parcial-modulos

## Change Summary
- **Change Name:** `novedades-descarga-parcial-modulos`
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-09-24

## Delivered
1. Capital Humano: **Descarga parcial de módulos** after liquidación (closed period only).
2. Modal fechas + grilla agregada + Detalle accordion + Excel `descarga-parcial-modulos_{desde}_{hasta}.xlsx`.
3. API: `fecha_desde`/`fecha_hasta` on `/grilla` and `/export.xlsx`; 2 sheets Resumen+Detalle when both set; `legajo` on `GridRowResponse`.
4. Tests + runbook note.

## Specs synced
| Domain | Action | Details |
|--------|--------|---------|
| `novedades` | Updated | ADDED: Descarga parcial de módulos; MODIFIED: Grilla y XLS (detalle) date params + 2-sheet export |

## Verification
User-tested OK (2026-09-24).
