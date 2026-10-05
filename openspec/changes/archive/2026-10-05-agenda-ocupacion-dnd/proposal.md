# Proposal: agenda-ocupacion-dnd

## Intent

Permitir en **Agenda ocupación** reasignar agendas por drag-and-drop entre consultorios y **Sin consultorio**, con validación de horario del box y sin solapes, respetando filtros actuales.

## Scope

### In Scope
- DnD **solo cambio de columna** (horario del bloque fijo, del sync).
- Destinos: Sin consultorio ↔ room y room ↔ room.
- Persistencia al soltar vía API (remap `id_agenda` completo).
- Validación server-side: para **cada** weekday con bloques de esa agenda en sync, el intervalo debe:
  - estar cubierto por `room_operating_hours` del room destino ese weekday, y
  - no solapar otra agenda ya mapeada a ese room (en esos horarios/días).
- Confirmación modal al “robar” agenda de otro room (`confirm_move`).
- Confirmación modal al desasignar (→ Sin consultorio); sin validar horario/solape.
- Rechazo: modal con motivo detallado; bloque vuelve a origen.
- Filtros actuales se respetan (columnas visibles = destinos dropeables).
- Roles `admin`|`operador`.

### Out of Scope
- Cambiar horas del sync / drag vertical / resize.
- Override de mapeo por fecha suelta.
- Endurecer modal Agendas de Consultorios (sigue igual, Q10).
- Sync Ocupación, Indicadores, Estadística.
- Multi-select / mover varias agendas a la vez.

## Approach

1. Backend: endpoint de reassign (+ unassign) con validación horario+solape multi-weekday; reutilizar `confirm_move` / delete mapeo.
2. Frontend: DnD en grilla Agenda; confirm modals; error modal; refresh events tras éxito.
3. Tests: happy path, fuera de horario, solape, confirm_move, unassign; nota runbook.
4. Delta spec: UI Agenda deja de ser “solo lectura” para mapeo vía DnD; reglas de validación del path DnD.

## Affected Areas

| Area | Impact |
|------|--------|
| `AgendaOcupacionPage.jsx` | DnD + modals |
| `room_agenda_map` / nuevo service validate | Reassign + rules |
| router distribucion o consulting_rooms | Endpoint |
| tests + runbook + specs | verify/docs |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Reglas DnD ≠ Consultorios Agendas | Med | Documentar; Q10 acepta divergencia |
| False positive solape (misma agenda multi-franja) | Med | Excluir el propio `id_agenda` del check |
| UX drag vs click detalle | Med | Threshold drag distance; click sigue abriendo modal |
| Perf validación | Low | Un scan sync + hours por request |

## Rollback Plan

Revert PR; UI vuelve a solo lectura; endpoint nuevo se deja de llamar. Mapa `id_agenda`→room intacto.

## Dependencies

- Snapshot sync `ocupacion_horario_activo`, `room_operating_hours`, mapa `consulting_room_id_agenda`.
- Events API y filtros Agenda existentes.

## Success Criteria

- [ ] Drag Sin consultorio → room (y room↔room) persiste si pasa horario+sin solape en todos los weekdays de la agenda.
- [ ] Drop inválido: modal detalle + sin persistir.
- [ ] Robo: confirm; Unassign: confirm sin validar horario.
- [ ] Filtros vigentes; sin cambio de hora por drag.
- [ ] Tests backend de validación + smoke UI.
