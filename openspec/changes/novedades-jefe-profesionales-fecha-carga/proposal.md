# Proposal: Jefe gestiona profesionales de su servicio + fecha de realización

## Intent

1. Permitir que `jefe_medico` **agregue o quite** profesionales asociados **solo** a los servicios que tiene asignados (hoy eso es exclusivo de admin/rrhh).
2. Exigir, al cargar un módulo o una novedad, el **día en que se realizó** (dato de negocio distinto de la fecha de alta), con UI de calendario/date picker, y que ese dato viaje a grilla/XLS.

## Scope

### In Scope
- API + UI para que jefe (y probablemente admin) gestione `profesional↔servicio` con scope por servicios del jefe.
- Campo de fecha de realización en asignaciones de módulo y novedades (create + listados + export).
- Búsqueda de profesionales tipo **typeahead** (filtrar al tipear, mostrar matches), reutilizando el patrón de `ProfessionalCombobox`.
- Validaciones y RBAC alineados a specs de Novedades.
- Migración Alembic + actualización de docs/runbook breve.
- Delta specs al cerrar el change.

### Out of Scope
- Sync con API externa de profesionales (sábana MySQL/otro sistema).
- Cambiar catálogo global de `professionals` (alta de persona nueva en el maestro).
- Liquidación, PDF, emails.
- Rediseño completo de Parametrización.

## Approach

Extender el dominio Novedades existente: guards scoped en `profesional-servicios`; nueva columna date en tablas de carga; date input en Carga; columnas en grilla/XLS. Detalle de UI y reglas de validación se cierran en `decisions.md` (survey).

## Affected Areas

| Area | Impact |
|------|--------|
| API `profesional-servicios` | RBAC jefe scoped |
| Models/schemas cargas | `fecha_realizacion` |
| Carga UI + grid + XLS | Campo + columnas |
| Param / nav | Superficie para jefe (según Q) |
| Specs `novedades` | Delta |

## Risks

| Risk | Mitigation |
|------|------------|
| Soft-delete de vínculo con cargas abiertas | Decidir en survey (bloquear vs permitir) |
| Fecha fuera del período | Regla explícita en survey |
| Jefe ve Param completa | Tabs/rutas filtradas por rol |

## Rollback

Revert migración (nullable/backfill cuidadoso) + feature flags no necesarios; ocultar UI y endpoints nuevos.

## Success Criteria

- [ ] Jefe puede asociar/desasociar profesionales solo en sus servicios; fuera de alcance → 403
- [ ] Admin/rrhh siguen pudiendo gestionar asociaciones (alcance global)
- [ ] Carga de módulo y novedad exige fecha de realización; aparece en grilla Carga y XLS
- [ ] Tests RBAC + validación de fecha

**Estado:** IMPLEMENTADO (2026-07-29) — pendiente verify manual / archive.
