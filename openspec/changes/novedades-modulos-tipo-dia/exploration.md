# Exploration: novedades-modulos-tipo-dia

## Current State

- Módulo: boolean `sadofe` (default false = Semana).
- Carga: combo filtra por `fecha_realizacion` — Semana (lun–vie no feriado) vs SADOFE (sáb/dom/feriado). UI-only.
- Param: check SADOFE en alta/edición; Excel import columna `sadofe` Sí/No.
- Consumers of `sadofe`: Param UI, Carga filter, modulos_import, schemas/API — all in this app.

## Intent

Replace exclusive day-type with three options: **semana** | **sadofe** | **valor_unico**. Valor único appears on any date. Migrate existing rows without breaking cargas.

## Approaches

| Option | Pros | Cons |
|--------|------|------|
| **A** Single `tipo_dia` enum | Clear exclusivity; clean API | Migration + FE/import update |
| B Keep booleans | — | Fragile exclusivity |

**Chosen: A** (survey).

## Ready for Proposal

Yes.
