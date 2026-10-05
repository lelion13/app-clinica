# Design: indicadores-ocupacion-ui

## Technical Approach

Ajustar filter-options/match a payload-only; sync Ocupación con `medico` ← `medico_responsable_equipo`; extender `compute_indicadores` con `period` + tops; actualizar UI Indicadores (modo Día/Mes, torta labels, panel tops).

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Query `period=day\|month` + `date` o `month` | Explícito; evita ambigüedad |
| Tops en misma response | Un fetch; coherente con filtros |
| Mes: un scan sync + hours por weekday×count | Evita N queries por día |
| Match payload en agenda_ocupacion e indicadores | Q6; una regla compartida helper |
| `medico` sync = `medico_responsable_equipo` | Q8; nombre_agenda parte 3 no es el médico real (p. ej. CONSULTORIOS) |
| Labels pie en frontend (Recharts) | No requiere backend extra |

## Sync Ocupación (`horarios_activos._raw_to_model`)

```python
tipo, especialidad_agenda, _ = _split_nombre_agenda(payload.get("nombre_agenda"))
medico = _as_str(payload.get("medico_responsable_equipo"))  # columna DB + UI
```

`filter-options` / match / tops leen `medico_payload` = `medico_responsable_equipo` (fallback legado `payload.medico`).

## API

### `GET /distribucion/ocupacion/indicadores`

| Param | Uso |
|-------|-----|
| `period` | `day` (default) \| `month` |
| `date` | obligatorio si period=day (`YYYY-MM-DD`) |
| `month` | obligatorio si period=month (`YYYY-MM`) |
| `location_id`, `room_id`, `especialidad`, `medico` | como hoy |

Response extends current fields with `period`, `month`, `top_especialidad`, `top_medico` (`IndicadoresTopItem`: label, hours, percent_box, percent_occupied).

### Month aggregation

- **enabled:** count de cada JS weekday en el mes × horas del room ese weekday.
- **occupied:** por cada bloque sync, ocurrencias de su `dia` en el mes dentro de `[fecha_desde, fecha_hasta]` × duración del bloque.
- Room entra a la torta si tiene enabled > 0 en el período.

## UI

```
[ Día | Mes ]  [date | month]  Ubicación  Consultorio  Especialidad  Médico
KPIs...
[ Donut (% centro + labels internos + chips) ]  [ Top especialidad ]  [ Top médico ]
```

Torta: donut Recharts; % ocupación al centro; horas/% dentro del segmento; chips debajo con texto completo (evita labels externos cortados).

## File Changes

| File | Change |
|------|--------|
| `horarios_activos.py` | medico ← medico_responsable_equipo |
| `schemas/distribucion.py` | period fields, TopItem, lists |
| `indicadores_ocupacion.py` | month + tops + payload match |
| `agenda_ocupacion.py` | filter-options + events match + medico_payload |
| `distribucion.py` router | query params |
| `IndicadoresOcupacionPage.jsx` | mode, pie labels, tops |
| tests | sync medico, filter-options, month, tops |
| `docs/runbook.md` + specs | note + delta |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Month CPU | weekday multiplicity for hours; single ocupacion load |
| Agenda UX change | runbook + tests |
| Snapshot DB viejo | Actualizar tras deploy |

## Open Questions

None — survey Q1–Q8 closed.
