# Proposal: agenda-ocupacion-segun-dia

## Intent

Permitir asignar/desasignar agendas a consultorios **por weekday**, para que en Agenda ocupación solo se confirme el día del calendario, y en Consultorios se complete el resto de días pendientes sin pisar otros rooms.

## Scope

### In Scope
- Persistencia mapa `(id_agenda, weekday)` → `room_id` + migración desde mapa 1:1 actual.
- **Agenda ocupación:** assign/unassign solo el weekday del día seleccionado; listar solo agendas con bloque ese día; validar horario/solape solo ese día; columnas rooms orden numérico; scroll H + auto-scroll al drag; Sin consultorio sticky si tiene ítems.
- **Consultorios → Agendas:** assign solo días aún Sin consultorio (todo-o-nada + modal conflicto); unassign de ese room (parcial = un día / full = todos los días en ese room); labels full vs parcial.
- Roles actuales; tests + runbook.

### Out of Scope
- Override por fecha calendario (solo weekday).
- Cambiar horas sync / drag vertical.
- Indicadores / Estadística / sync Ocupación (salvo que lean el mapa — adaptar resolución por weekday).
- Nuevos roles.

## Approach

1. Migración Alembic: clave compuesta + expandir filas existentes a todos los weekdays sync del `id_agenda`.
2. Backend: reassign/unassign y modal Agendas con scope weekday; events `resource_id` por día.
3. Frontend AO: filtro por día, DnD weekday, orden/scroll/sticky.
4. Frontend Consultorios: labels y unassign día; assign restante todo-o-nada.

## Affected Areas

| Area | Impact |
|------|--------|
| `consulting_room_id_agenda` + Alembic | PK/mapa por weekday |
| `agenda_reassign.py`, `room_agenda_map.py`, events | API + validación |
| `AgendaOcupacionPage` | DnD día, orden, scroll |
| UI Consultorios Agendas | assign/unassign/labels |
| tests + `docs/runbook.md` + delta `distribucion` | verify |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Indicadores/events asumen 1 room/agenda | Med | Resolver room por weekday del evento |
| Migración incompleta (sin sync weekday) | Med | Expandir solo weekdays presentes en sync; doc |
| UX sticky/scroll vs DnD | Med | Smoke + auto-scroll borde |

## Rollback Plan

Revert PR + migración down (colapsar a un room por `id_agenda` si rollback controlado; si no, restore backup). UI vuelve a mapa global.

## Dependencies

- Sync `ocupacion_horario_activo`, `room_operating_hours`, change DnD previo.

## Success Criteria

- [ ] AO lunes asigna solo lunes; martes queda Sin consultorio hasta martes.
- [ ] Consultorios assign solo días libres; conflicto → modal, 0 cambios.
- [ ] Orden C1…Cn; scroll H; auto-scroll al drag; Sin consultorio sticky con ítems.
- [ ] Lista Consultorios: full sin sufijo; parcial `nombre - día` desasociable por día.
- [ ] Migración: mapas previos = todos los días de la agenda en ese room.
