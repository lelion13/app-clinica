# Decisions — novedades-jefe-profesionales-fecha-carga

**Estado:** CLOSED + ARCHIVED (2026-07-29)  
**Change:** `novedades-jefe-profesionales-fecha-carga`

| # | Tema | Decisión | Notas |
|---|------|----------|-------|
| Q1 | Catálogo al asociar (jefe) | **B** | Cualquier profesional activo; typeahead; no listar ya asociados al servicio |
| Q2 | UI superficie | **B** | Menú Novedades → “Mis profesionales”; Param sigue para admin/rrhh |
| Q3 | Quitar con cargas | **A** | Soft-delete vínculo siempre; cargas históricas OK |
| Q4 | Quién ve Mis profesionales | **C** | jefe + admin + rrhh (admin/rrhh todos los servicios) |
| Q5 | Semántica fecha | **A** | Día de **realización** |
| Q6 | Validación fecha | **D** | ∈ [inicio, fin] del período **y** ≤ hoy |
| Q7 | Futuro | **por Q6** | “hoy” = calendario `BUSINESS_TIMEZONE` |
| Q8 | Grilla / XLS | **A** | Fecha realización + Fecha carga |
| Q9 | Editar fecha | **B** | Editable con período abierto (admin/jefe scoped) |
| R12 | Typeahead | **A** | Reuse `ProfessionalCombobox` |
| R13 | Labels + período futuro | **A** | Labels alineados; si no hay días válidos → aviso (no min>max) |
| R14 | Alertas | **A** | `AlertModal` + OK |
| L1 | Deploy | — | Siempre migrar tras deploy (F1) |
| L2 | Guards roster | — | `assert_can_manage_profesional_servicio` ≠ `assert_can_load_servicio` (F3) |

## Matriz RBAC (final)

| Capacidad | admin | jefe_medico | rrhh | operador |
|-----------|-------|-------------|------|----------|
| Mis profesionales | sí (todos) | sí (sus servicios) | sí (todos) | no |
| Param tab profesional↔servicio | sí | no | sí | no |
| Cargar / editar fecha (período abierto) | sí | sí (scoped) | no | no |
| Grilla + XLS | sí | no | sí | no |

Detalle de fallas y mitigaciones: `implementation-notes.md`.
