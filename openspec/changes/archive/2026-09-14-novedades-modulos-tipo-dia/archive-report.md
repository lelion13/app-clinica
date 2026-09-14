# Archive Report: novedades-modulos-tipo-dia

## Change Summary
- **Change Name:** `novedades-modulos-tipo-dia`
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-09-14

## Delivered
1. Replaced module boolean `sadofe` with exclusive `tipo_dia` (`semana` | `sadofe` | `valor_unico`).
2. Migration backfill: false→semana, true→sadofe; API drops `sadofe`.
3. Param: three exclusive checks; Carga filter includes valor_unico any day.
4. Excel plantilla/import column `tipo_dia` (empty→semana; invalid→all-or-nothing).

## Specs synced
| Domain | Action | Details |
|--------|--------|---------|
| `novedades` | Updated | Modified Servicios y módulos, Filtro módulos; Plantilla; Added Tipo día + Carga masiva (restored) |

## Verification
User-tested OK (2026-09-14).
