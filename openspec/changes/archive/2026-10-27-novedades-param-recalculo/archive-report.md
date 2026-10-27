# Archive Report: novedades-param-recalculo

## Change Summary
- **Change Name:** `novedades-param-recalculo`
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-10-27
- **Branch:** `medicos`

## Delivered
1. **Recálculo** (Param, after Feriados): preview/apply horas y/o módulos; período abierto/cerrado; bloqueo sin cambios; plus especialista = carga; soft-delete excluido.
2. Rev **`0035_novedad_valor`**: snapshot `novedades_novedad.valor` (create/grid/export/CH/recalc).
3. **Valores Extras** (Índices, admin): modal filtro/búsqueda/expand/checkboxes; PDF reportlab (chrome recepción, 1 PDF / N páginas).
4. Tests: `test_recalculo.py`, `test_valores_extras.py`; runbook actualizado; `reportlab` + `pdf-header-band.png`.

## Specs synced
| Domain | Action | Details |
|--------|--------|---------|
| `novedades` | Updated | ADDED: Recálculo (pestaña, importes, preview, reglas), valor persistido, Valores Extras, Export PDF. MODIFIED: Servicios y módulos (tab Recálculo); Pantalla Índices (Valores Extras). |

## Decisions
Q1–Q9 Recálculo + VE-Q1–Q12 Valores Extras/PDF closed in `decisions.md`.

## Verification
See `verify-report.md` (PASS). Recálculo confirmed in production path by user; Valores Extras + PDF implemented and smoke-tested locally before archive.

## Engram lineage (topic keys)
- `sdd/novedades-param-recalculo/proposal`
- `sdd/novedades-param-recalculo/apply-progress`
- `sdd/novedades-param-recalculo/valores-extras`
- `sdd/novedades-param-recalculo/archive-report` (this)
