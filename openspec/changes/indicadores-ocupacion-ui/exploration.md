# Exploration: indicadores-ocupacion-ui

## Current State

`IndicadoresOcupacionPage.jsx`:
- Filtros: día (date), ubicación, consultorio, especialidad, médico.
- Opciones especialidad/médico desde `GET .../agenda/filter-options` (compartido con Agenda ocupación).
- KPI cards + torta Recharts (Ocupado/Libre) sin horas en etiquetas de segmento.
- Sin tops; sin modo mes.

`list_filter_options` (`agenda_ocupacion.py`):
- `especialidad` = unión de `payload.especialidad` + `especialidad_agenda` (derivada).
- `medico` = `row.medico` (columna derivada o payload).

`compute_indicadores` (`indicadores_ocupacion.py`):
- Un solo `date`; denom = hours del weekday; numerador = sync mapeado ese día.
- Filtro especialidad matchea `especialidad` **o** `especialidad_agenda`.
- Respuesta: occupied/enabled/free/percent + rooms_* ; sin tops ni period.

Stable spec § Indicadores ocupación (archive `2026-10-03-indicadores-ocupacion`).

## Affected Areas

- `frontend/src/pages/IndicadoresOcupacionPage.jsx`
- `backend/app/services/distribucion/indicadores_ocupacion.py`
- `backend/app/services/distribucion/agenda_ocupacion.py` (filter-options + match especialidad/medico en events)
- `backend/app/schemas/distribucion.py`
- `backend/app/api/routers/distribucion.py`
- `backend/tests/test_indicadores_ocupacion.py` (+ filter-options / agenda match tests)
- `frontend` Agenda ocupación (consume mismos filter-options / match)
- `docs/runbook.md`
- `openspec/specs/distribucion/spec.md` (merge on archive)

## Approaches

1. **Extender API indicadores** (period day|month + tops en misma response) + ajustar filter-options/match compartidos — **elegido**.
2. Endpoint tops separado — más round-trips; innecesario para v1.
3. Solo frontend mes (N llamadas diarias) — lento e inconsistente.

## Recommendation

Approach 1. Query `period=day|month` + `date` o `month=YYYY-MM`; tops en response; pie labels en UI.

## Risks

- Agenda ocupación pierde opciones de `especialidad_agenda` en el select (aceptado Q5/Q6).
- Mes = loop de días puede ser costoso; MUST optimizar (sumar hours por weekday × count, sync scan una vez).
- % > 100% sigue posible (igual que hoy).

## Ready for Proposal

Yes.
