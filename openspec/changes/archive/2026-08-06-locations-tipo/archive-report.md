# Archive report — locations-tipo

Archivado: 2026-08-06  
Mode: openspec (documentación retroactiva de código ya implementado)

## Specs synced

| Domain | Action | Details |
|--------|--------|---------|
| distribucion | Merged into main `openspec/specs/distribucion/spec.md` | Ubicación `(id_dominio, tipo)`; split `nombre_agenda` con fallback `-` |

## Archive contents

- proposal.md
- design.md
- decisions.md
- tasks.md (todas [x])
- specs/distribucion/spec.md (delta)
- archive-report.md (este archivo)

## Ops

- Migración: `0016_locations_tipo`
- Tras deploy: `alembic upgrade head` → editar `PENDIENTE-*` en Ubicaciones → **Actualizar** Ocupación si hubo fix de split
