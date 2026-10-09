# Proposal: novedades-indices-modulos

## Intent

Dar a **admin** una pantalla **Índices** bajo Novedades con contadores por **período** (servicio y profesional), y estructurar **`horas` en el catálogo de módulos** para que Índices sume duración de módulos cargados + horas de novedades — sin parsear la descripción.

## Scope

### In Scope
- Menú Novedades: ítem **Índices** al final; visible solo `admin`; ruta `/novedades/indices`.
- API/UI Índices solo `admin`.
- Selector de período (abierto o cerrado); sin período → sin datos.
- Sección **Por servicio**: horas (módulos + novedades), monto (cargas + ajustes con `servicio_id`), profesionales, cantidad de asignaciones. Sin producción por servicio.
- Sección **Por profesional**: horas (módulos + novedades), cantidad de módulos, producción monto + cantidad (reglas CH).
- Catálogo **módulo.horas**: entero ≥ 1; obligatorio en alta y edición; migración deja existentes en NULL.
- Filas solo con actividad; orden por nombre A→Z.

### Out of Scope
- Parseo de horas desde descripción del módulo.
- Export Excel/CSV de Índices.
- Producción atribuida a servicio.
- Roles `rrhh` / `jefe_medico` en Índices.
- Columna `horas` en plantilla/import Excel de módulos (deferred).

## Approach

1. Migration nullable `horas` on `novedades_modulo`; wire Param create/edit + schemas.
2. Índices aggregation: assignments contribute `coalesce(modulo.horas, 0)` + net novedad hours.
3. Admin page + navigation.

## Affected Areas

| Area | Impact |
|------|--------|
| Alembic + `NovedadesModulo` | New column |
| schemas/masters/Param UI módulos | Modified |
| `indices` service + page | New/Modified |
| `docs/runbook.md` | Note |
| `openspec/specs/novedades/spec.md` | Delta on archive |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Módulos legacy sin horas | Med | NULL → 0 en Índices; obligar en próxima edición |
| Confundir horas módulo vs novedad | Low | Labels claros en UI Índices |

## Rollback Plan

Revert migration/code; Índices/menú se quitan con el revert.

## Dependencies

- Períodos, cargas, ajustes, snapshot producción CH, ABM módulos Param.

## Success Criteria

- [ ] Solo admin ve/llama Índices.
- [ ] Alta/edición módulo exige `horas` entero ≥ 1.
- [ ] Índices Horas = módulos (coalesce) + novedades netas.
- [ ] Existentes migran con `horas` NULL.
