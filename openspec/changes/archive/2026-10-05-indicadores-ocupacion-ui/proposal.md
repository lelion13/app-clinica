# Proposal: indicadores-ocupacion-ui

## Intent

Mejorar Indicadores ocupación: filtros desde payload puro, período día/mes, torta con horas+%, tops por especialidad/médico, y alinear la columna **médico** del sync Ocupación con `medico_responsable_equipo`.

## Scope

### In Scope
- `filter-options` compartido: especialidad = solo `payload.especialidad`; médico = solo `payload.medico_responsable_equipo` (fallback `payload.medico`).
- Match de filtros (Indicadores + Agenda): solo esos campos payload.
- Sync Ocupación: columna `medico` ← `medico_responsable_equipo` (no resto de `nombre_agenda`).
- UI modo **Día | Mes**; mes agrega occupied/enabled como suma del mes.
- Torta: etiquetas/leyenda con horas y %.
- Panel al costado: Top 10 especialidad + Top 10 médico (horas, % box, % ocupado); vacíos → “Sin especialidad” / “Sin médico”.
- API indicadores extendida (period + tops).

### Out of Scope
- Cambiar fórmula base (sync÷box) o Estadística.
- Validar agendas vs horarios del box.
- Multi-select filtros.
- Export Excel.

## Approach

1. Ajustar `list_filter_options` + match especialidad/medico en agenda/indicadores.
2. En sync (`horarios_activos`): `medico` desde `medico_responsable_equipo`; split solo para tipo/especialidad_agenda.
3. Extender `compute_indicadores` para `period=day|month` y tops top-10.
4. Rehacer layout UI: período, torta+labels, columnas tops.

## Affected Areas

| Area | Impact |
|------|--------|
| `horarios_activos.py` | Fuente columna `medico` |
| `indicadores_ocupacion.py` + schemas + router | period, tops |
| `agenda_ocupacion.py` | filter-options + match |
| `IndicadoresOcupacionPage.jsx` | UI |
| Agenda ocupación page | opciones/match filtros |
| tests + runbook + specs | verify/docs |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Perf mes | Med | Agregar hours por weekday×días; un pass sync |
| Regresión Agenda filtros | Med | Tests match payload-only; nota runbook |
| Datos viejos en DB | High | Re-sync Actualizar tras deploy |
| % > 100 en tops | Low | Misma regla que torta; mostrar valores |

## Rollback Plan

Revert PR; restaurar medico desde split nombre_agenda; filter-options/match previos; UI/API día-only sin tops.

## Dependencies

- Spec estable Indicadores + mapeo agenda↔room + `room_operating_hours`.
- Campo `medico_responsable_equipo` en API externa de horarios activos.

## Success Criteria

- [x] Selects especialidad/médico solo valores payload (compartido).
- [x] Columna Ocupación `medico` = `medico_responsable_equipo` tras Actualizar.
- [x] Modo Mes calcula suma del mes; Día igual que hoy.
- [x] Torta muestra horas y %; tops 10 con horas + 2 %.
- [x] Tests backend del área (+ smoke UI pendiente).
