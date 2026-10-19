# Proposal: limpiar-ui-obsoleta

## Intent

Eliminar del menú Distribución y del código las capacidades obsoletas **Ocupación semanal**, **Agenda** (reservas) y **Estadística**, sin afectar las pantallas que sí se usan.

## Scope

### In Scope
- Quitar ítems de navegación y páginas/rutas asociadas.
- Redirect `/ocupacion-semanal`, `/agenda`, `/estadisticas` → Home.
- Eliminar routers/services/schemas/tests exclusivos: bookings, weekly-assignments, stats.
- Migración Alembic: drop tablas/datos solo si el grafo de uso lo confirma (p. ej. `bookings`, `room_weekly_assignments`).
- Actualizar OpenSpec `distribucion` (quitar requisitos Estadística / referencias a Ocupación semanal y Agenda bookings) + runbook.

### Out of Scope
- Cambiar Profesionales (queda; posible change futuro).
- Tocar Ocupación sync, Agenda ocupación, Indicadores, Consultorios, Ubicaciones, Novedades.
- Soft-drop / restore automático (backup = operador pre-deploy).

## Approach

1. Inventario de referencias FE/BE; eliminar solo lo exclusivo.
2. FE: navigation + routes + delete pages; redirects.
3. BE: unregister routers; delete dead modules; migration drop.
4. Specs + tests + runbook; smoke de pantallas que quedan.

## Affected Areas

| Area | Impact |
|------|--------|
| `frontend/src/config/navigation.js`, `main.jsx` | Menú + routes + redirects |
| `WeeklyOccupancyPage`, `AgendaPage`, `EstadisticasPage` | Delete |
| `backend/.../bookings*`, `weekly_assignments*`, `stats*` | Delete |
| Alembic `0033_…` | Drop tables |
| `openspec/specs/distribucion/spec.md`, runbook | Sync |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Borrar API compartida (professionals, rooms, hours) | Med | Checklist de grep; no tocar esas rutas |
| FK / migration order | Med | Drop bookings/assignments only; keep professionals |
| Spec/archive contradictorio | Low | REMOVED + MODIFIED en delta; anti-ambigüedad |

## Rollback Plan

Revert PR + restore DB from backup pre-deploy si ya corrió drop.

## Dependencies

- Backup operador antes de `alembic upgrade` en VPS.

## Success Criteria

- [ ] Menú Distribución sin Ocupación semanal / Agenda / Estadística.
- [ ] URLs viejas redirigen a Home.
- [ ] Pantallas restantes OK (Ocupación, Agenda ocupación, Indicadores, Profesionales, Consultorios).
- [ ] Endpoints `/bookings`, `/weekly-assignments`, `/stats` ausentes.
- [ ] Tablas exclusivas dropeadas tras verificación de no-uso.
