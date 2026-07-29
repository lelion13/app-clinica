# Proposal: Jefe gestiona profesionales + fecha de realización

## Intent

1. `jefe_medico` (y admin/rrhh) gestionan asociaciones profesional↔servicio con alcance correcto.
2. Cargas exigen **fecha de realización** (calendario), visible en grilla/XLS, editable con período abierto.

## Scope (entregado)

### In Scope
- Mis profesionales + RBAC scoped/global
- `fecha_realizacion` + validación + export
- Typeahead, labels, alert modal, UX período no iniciado

### Out of Scope
- Sync API externa de profesionales
- Liquidación / PDF / emails

## Success Criteria

- [x] Jefe asocia/desasocia solo en sus servicios; admin/rrhh globales
- [x] Fecha realización requerida, validada, en grilla/XLS
- [x] Typeahead + AlertModal + manejo período futuro en UI
- [x] Docs + aprendizajes de fallas en `implementation-notes.md`

**Estado:** ARCHIVED 2026-07-29 → `openspec/changes/archive/2026-07-29-novedades-jefe-profesionales-fecha-carga/`  
Spec estable: `openspec/specs/novedades/spec.md`
