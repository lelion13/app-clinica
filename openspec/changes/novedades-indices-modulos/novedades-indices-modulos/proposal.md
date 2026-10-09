# Proposal: novedades-indices-modulos

## Intent

Dar a **admin** una pantalla **Índices** bajo Novedades para ver, por **período**, contadores agregados de actividad de módulos/novedades/producción — por servicio y por profesional — sin export y sin inventar horas de módulo desde la descripción.

## Scope

### In Scope
- Menú Novedades: ítem **Índices** al final; visible solo `admin`; ruta `/novedades/indices`.
- API/UI solo `admin` (403/oculto para otros roles).
- Selector de período (abierto o cerrado); sin período → sin datos.
- Sección **Por servicio**: horas (novedades netas), monto (cargas + ajustes con `servicio_id`), profesionales distintos con cargas, cantidad de asignaciones de módulo. Sin producción por servicio.
- Sección **Por profesional**: horas (novedades netas), cantidad de módulos, producción monto + cantidad (mismas reglas CH).
- Filas solo con actividad; orden por nombre A→Z.
- Soft-deleted cargas/ajustes excluidos (comportamiento estándar).

### Out of Scope
- Horas derivadas de duración de módulo / parseo de descripción.
- Export Excel/CSV.
- Producción atribuida a servicio.
- Roles `rrhh` / `jefe_medico`.
- Atributo estructurado `horas` en catálogo de módulos (posible change futuro).

## Approach

1. Backend endpoint(s) agregados por `periodo_id` reutilizando fuentes de grilla CH / cargas / bonos snapshot.
2. Página React mobile-first con selector de período + dos tablas apiladas.
3. Wire navigation + route guard admin-only.

## Affected Areas

| Area | Impact |
|------|--------|
| `frontend/.../navigation` + Home/Router | New item + route |
| `frontend` page Índices | New |
| `backend` router + service índices | New |
| `openspec/specs/novedades/spec.md` | Delta on archive |
| `docs/runbook.md` | Short note |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Confundir “horas” con duración de módulo | Med | Copy UI: “Horas (novedades)” |
| Monto por servicio ≠ total CH del profesional | Med | Spec/runbook explícitos |
| Cantidad producción mal definida | Med | Reusar valorización/filtros CH |

## Rollback Plan

Quitar ruta/menú y endpoints; sin migración de datos prevista.

## Dependencies

- Períodos, cargas, ajustes, snapshot bonos/prácticas/internaciones, reglas elegibilidad bonos CH.

## Success Criteria

- [ ] Solo admin ve y llama Índices.
- [ ] Métricas coinciden con las definiciones de `decisions.md` para un período de prueba.
- [ ] Sin período no muestra filas inventadas.
