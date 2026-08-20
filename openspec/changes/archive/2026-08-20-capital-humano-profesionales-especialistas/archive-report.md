# Archive report: 2026-08-20-capital-humano-profesionales-especialistas

**Date:** 2026-08-20  
**Archived to:** `openspec/changes/archive/2026-08-20-capital-humano-profesionales-especialistas/`

## Specs synced

| Domain | Action | Details |
|--------|--------|---------|
| `novedades` | Modified | Catálogo (+ `es_especialista`); Sync Param vs Mis profesionales |
| `novedades` | Added | Profesionales especialistas |
| `novedades` | Added | Plus 20% en módulos de especialistas |
| `novedades` | Modified | Detalle unificado (+ indicador especialista) |
| `openspec/specs/README.md` | Updated | origins |

## Migration

- `0022_especialista_valor` (≤32 chars; idempotent after truncated-revision failure)

## Learnings

See `implementation-notes.md` F1–F4 (alembic revision length, query flag sync, CODPROF match, historical valores).

## Source of truth

`openspec/specs/novedades/spec.md`
