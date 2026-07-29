# Archive — novedades-jefe-profesionales-fecha-carga

- **Closed:** 2026-07-29
- **Status:** Implemented in app; OpenSpec change archived by owner request
- **Main specs synced:**
  - `openspec/specs/novedades/spec.md` (updated: Mis profesionales, fecha_realizacion, grilla/XLS columns, Alertas UI)
- **Note:** Formal verify-report was optional at archive time; behavior covered by unit tests + runbook + production learnings in `implementation-notes.md`.

## Contents

- proposal, exploration, decisions, design, tasks
- specs/novedades (delta)
- **implementation-notes.md** — entregables, decisiones, **fallas F1–F5** (deploy sin Alembic, date picker min>max, RBAC RRHH, AlertModal, Alembic id ≤32)

## Product delivered

1. Mis profesionales (`/novedades/mis-profesionales`) — admin/rrhh/jefe scoped; typeahead; soft-delete link always OK
2. `fecha_realizacion` (Alembic `0007_fecha_realizacion`) — in period ∩ ≤ today; editable while open; grid + XLS both dates
3. UX — AlertModal, ProfessionalCombobox, empty date range when period not started

## Ops reminder

Post-deploy Novedades: **always** `alembic upgrade head` after backend image with new revisions (see F1 in implementation-notes).
