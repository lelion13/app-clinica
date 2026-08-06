# Exploration: indicadores-ocupacion

## Current State

- Sync ocupación en DB (`ocupacion_horario_activo`) + mapeo `consulting_room_id_agenda`.
- Horario operativo: `room_operating_hours` (weekday JS 0=dom…6=sáb, alineado con bookings).
- UI **Estadística** `/estadisticas` + `stats_service` calculan % con **bookings** ÷ operating hours (recharts Pie). **Distinto** de este change (sync/agendas).
- Agenda ocupación ya materializa bloques por día/weekday; lógica de dia/horas reutilizable.

## Affected Areas

- `backend/app/services/distribucion/` — nuevo servicio de indicadores (o módulo dedicado)
- `backend/app/api/routers/distribucion.py` — GET summary (+ filter-options si hace falta)
- `backend/app/schemas/` — response pie + horas + lista sin horario
- `frontend/src/config/navigation.js`, `main.jsx`
- `frontend/src/pages/` — `IndicadoresOcupacionPage.jsx` (recharts, patrón `EstadisticasPage`)
- `backend/tests/` — cálculo % / exclusiones
- `docs/runbook.md`

## Approaches

1. **Endpoint dedicado sync-based** — Calcula para un `date` + filtros; no toca `stats_service` de bookings.
   - Pros: sin mezclar semánticas; clear RBAC
   - Cons: algo de lógica de intervalos duplicada vs agenda
   - Effort: Medium

2. **Extender `/stats`** con `source=sync|bookings`
   - Pros: un dashboard
   - Cons: ambigüedad con change `dashboard-estadisticas`; user eligió menú aparte (Q6=A)
   - Effort: Medium–High

## Recommendation

Approach **1**. Reutilizar helpers de weekday/hora de agenda ocupación; Pie con recharts como Estadística.

## Risks

- % >100% (Q9/Q10) puede confundir → mostrar horas absolutas al lado.
- Rooms sin horario excluidos de torta pero visibles en aviso (Q5).
- Filtro médico/especialidad deja denominador alto → % bajo esperado (documentar).

## Ready for Proposal

Yes.
