# Archive — novedades-sincro-profesionales

- **Closed:** 2026-07-30
- **Status:** Implemented; OpenSpec change archived by owner request
- **Main specs synced:** `openspec/specs/novedades/spec.md` (catálogo Novedades, sync HTTP, limpieza, Mis profesionales / carga / vínculos actualizados)
- **Note:** Formal verify-report optional; covered by unit tests (`test_novedades_prof_sync.py`) + runbook + `implementation-notes.md` (L1–L7)

## Contents

- proposal, exploration, decisions (Q1–Q13), design, tasks (all `[x]`)
- specs/novedades (delta)
- **implementation-notes.md** — entregables, decisiones, aprendizajes L1–L7, deploy checklist

## Product delivered (one line)

Catálogo Novedades sync HTTP (`CODPROF`) aparte de Distribución; sync en Param + Mis prof.; inactivos sin carga; Limpiar hard-delete en Param; migración `0008` destructiva en transaccional.

## Ops reminder

Backup → pull/up → `alembic upgrade head` → set `NOVEDADES_PROF_SYNC_*` → sync → reasociar. Token solo en env; rotar si se expuso.
