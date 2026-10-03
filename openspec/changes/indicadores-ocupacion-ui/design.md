# Design: indicadores-ocupacion-ui

## Technical Approach

Ajustar filter-options/match a payload-only; extender `compute_indicadores` con `period` + tops; actualizar UI Indicadores (modo Día/Mes, torta labels, panel tops).

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Query `period=day\|month` + `date` o `month` | Explícito; evita ambigüedad |
| Tops en misma response | Un fetch; coherente con filtros |
| Mes: un scan sync + hours por weekday×count | Evita N queries por día |
| Match payload en agenda_ocupacion e indicadores | Q6; una regla compartida helper |
| Labels pie en frontend (Recharts) | No requiere backend extra |

## API

### `GET /distribucion/ocupacion/indicadores`

| Param | Uso |
|-------|-----|
| `period` | `day` (default) \| `month` |
| `date` | obligatorio si period=day (`YYYY-MM-DD`) |
| `month` | obligatorio si period=month (`YYYY-MM`) |
| `location_id`, `room_id`, `especialidad`, `medico` | como hoy |

Response extends current fields:

```json
{
  "period": "month",
  "date": null,
  "month": "2026-10",
  "occupied_hours": 0,
  "enabled_hours": 0,
  "free_hours": 0,
  "occupancy_percent": null,
  "rooms_included": 0,
  "rooms_in_pie": 0,
  "rooms_without_hours": [],
  "rooms_without_agenda": 0,
  "top_especialidad": [
    { "label": "CLINICA", "hours": 12.5, "percent_box": 25.0, "percent_occupied": 40.0 }
  ],
  "top_medico": [
    { "label": "Sin médico", "hours": 1.0, "percent_box": 2.0, "percent_occupied": 3.2 }
  ]
}
```

`percent_*` null si denom 0. Top length ≤ 10, sort hours desc.

### Month enabled_hours

For each included room, for each calendar day in month: add operating hours for that day's JS weekday. Rooms with 0 hours all month contribute to without_hours logic analogous to day (document in apply: rooms with no hours on any day of month vs pie — prefer: room enters pie if has any hours in month).

### Month occupied_hours

Reuse day-overlap logic for each day in month (or equivalent interval intersection with [month_start, month_end+1)). Group by payload especialidad/medico for tops **after** filters.

### filter-options

```python
if fields["especialidad"]: especialidades.add(...)  # payload only
# remove especialidad_agenda from set
if payload medico: medicos.add(...)  # from raw payload, not only row.medico
```

### Match helpers

```python
def match_especialidad_payload(esp, selected): ...  # only esp
def match_medico_payload(medico_payload, selected): ...
```

Use in indicadores + agenda events.

## UI

```
[ Día | Mes ]  [date | month]  Ubicación  Consultorio  Especialidad  Médico
KPIs...
[ Pie (labels h + %) ]  [ Top especialidad ]  [ Top médico ]
```

Mobile: stack pie then tops. Labels pie: `Ocupado: {h}h ({%}%)`.

## File Changes

| File | Change |
|------|--------|
| `schemas/distribucion.py` | period fields, TopItem, lists |
| `indicadores_ocupacion.py` | month + tops + payload match |
| `agenda_ocupacion.py` | filter-options + events match |
| `distribucion.py` router | query params |
| `IndicadoresOcupacionPage.jsx` | mode, pie labels, tops |
| tests | filter-options, match, month, tops |
| `docs/runbook.md` | note |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Month CPU | weekday multiplicity for hours; single ocupacion load |
| Agenda UX change | runbook + tests |

## Open Questions

None — survey closed.
