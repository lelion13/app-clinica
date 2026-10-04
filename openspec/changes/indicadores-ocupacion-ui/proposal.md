# Proposal: indicadores-ocupacion-ui

## Intent

Mejorar Indicadores ocupación: filtros desde payload puro, período día/mes, torta con horas+%, y tops por especialidad/médico al costado.

## Scope

### In Scope
- `filter-options` compartido: especialidad = solo `payload.especialidad`; médico = solo `payload.medico`.
- Match de filtros (Indicadores + Agenda): solo esos campos payload.
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
2. Extender `compute_indicadores` para `period=day|month` y tops top-10.
3. Rehacer layout UI: período, torta+labels, columnas tops.

## Affected Areas

| Area | Impact |
|------|--------|
| `indicadores_ocupacion.py` + schemas + router | period, tops |
| `agenda_ocupacion.py` | filter-options + match |
| `IndicadoresOcupacionPage.jsx` | UI |
| Agenda ocupación page | opciones/match filtros |
| tests + runbook | verify/docs |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Perf mes | Med | Agregar hours por weekday×días; un pass sync |
| Regresión Agenda filtros | Med | Tests match payload-only; nota runbook |
| % > 100 en tops | Low | Misma regla que torta; mostrar valores |

## Rollback Plan

Revert PR; restaurar filter-options/match y UI/API día-only sin tops.

## Dependencies

- Spec estable Indicadores + mapeo agenda↔room + `room_operating_hours`.

## Success Criteria

- [ ] Selects especialidad/médico solo valores payload (compartido).
- [ ] Modo Mes calcula suma del mes; Día igual que hoy.
- [ ] Torta muestra horas y %; tops 10 con horas + 2 %.
- [ ] Tests backend del área + smoke UI.
