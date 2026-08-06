# Proposal: Agenda ocupación (calendario sync)

## Intent

Mostrar en calendario read-only los horarios activos persistidos por sync, con filtros, sin mezclar con reservas (`/agenda`).

## Scope

### In Scope

- Menú **Agenda ocupación** → `/agenda-ocupacion` (admin/operador).
- Backend: `GET .../ocupacion/agenda/events?start=&end=` + filtros; materializa bloques de la ventana.
- Filtros: dominio (label ubicación o id), tipo, especialidad (OR agenda), médico, día.
- Frontend: FullCalendar (día/semana/mes), bloque título=`medico`, click=popover detalle; un color.
- Tests materialización + filtros; docs runbook breve.

### Out of Scope

- Sync en esta pantalla (sigue en Ocupación).
- Crear/editar bookings o filas sync.
- Cambios a `/agenda`, Ocupación semanal, Novedades.
- Colores por dominio/tipo.

## Approach

API BFF materializa eventos desde `ocupacion_horario_activo` para `[start,end)`: filas con `dia` válido cuyo `[fecha_desde,fecha_hasta]` solapa la ventana; aplica filtros query; resuelve label ubicación vía `locations.id_dominio`. UI reutiliza FullCalendar como Agenda, sin formularios de reserva.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `frontend/src/config/navigation.js` | Modified | Ítem menú |
| `frontend/src/main.jsx` | Modified | Ruta |
| `frontend/src/pages/` | New | AgendaOcupacionPage |
| `backend/app/api/routers/distribucion.py` | Modified | Endpoint events |
| `backend/app/services/distribucion/` | New/Mod | Materialización |
| `backend/app/schemas/distribucion.py` | Modified | Event schemas |
| `backend/tests/` | New | Tests agenda events |
| `docs/runbook.md` | Modified | Nota pantalla |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Ventana mes + muchos eventos | Med | Filtros; paginar después si hace falta |
| `dia` inconsistente en API | Med | Normalizar ES; excluir inválidos |
| Ubicación sin match id_dominio | Low | Fallback al número (Q14=C) |

## Rollback Plan

Revertir deploy front/back. Sin migración nueva (usa tablas existentes).

## Dependencies

- Snapshot sync poblado (`ocupacion_horario_activo`).
- `locations.id_dominio` para labels (placeholders OK).

## Success Criteria

- [ ] Menú muestra Agenda ocupación; `/agenda` intacta.
- [ ] Calendario pinta bloques solo en ventana visible con solape de fechas.
- [ ] Filtros A–E aplican; especialidad OR; sin dia no pinta.
- [ ] Popover con detalle; solo lectura.
- [ ] Tests backend de materialización.

## Decisions

Ver `decisions.md` (Q1–Q15). Survey CLOSED.
