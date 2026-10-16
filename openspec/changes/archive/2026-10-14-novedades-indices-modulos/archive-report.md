# Archive Report: novedades-indices-modulos

## Change Summary
- **Change Name:** `novedades-indices-modulos`
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-10-14
- **Branch:** `feature/novedades-indices-modulos`

## Delivered
1. Menú Novedades → **Índices** (solo `admin`, último ítem); ruta `/novedades/indices`.
2. `GET /novedades/indices` admin-only; contadores por período (servicio + profesional).
3. **Horas** = Σ `coalesce(módulo.horas,0)` por asignación + horas netas de novedades.
4. Catálogo **módulo.horas** (rev `0031_modulo_horas`): nullable en migración; obligatorio ≥ 1 en alta/edición Param + API.
5. Import Excel módulos sin cambio (horas queda NULL si se crea por import).
6. Unit tests (`test_indices.py`) + runbook.

## Specs synced
| Domain | Action | Details |
|--------|--------|---------|
| `novedades` | Updated | ADDED: Navegación Índices; Pantalla Índices; Horas en catálogo; Índices por servicio; Índices por profesional. MODIFIED: Servicios y módulos (`horas` en create/update/list). |

## Drift check
User confirmed feature works in production path. Implementation matched delta (API/UI/migration/runbook). No blocking gaps before archive.

## Verification
Implemented on `feature/novedades-indices-modulos`; smoke OK (user 2026-10-14). Unit tests for hours helpers passed at apply time.
