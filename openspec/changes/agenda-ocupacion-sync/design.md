# Design: agenda-ocupacion-sync

## Technical Approach

Backend materializa eventos FullCalendar desde snapshot JSONB. Frontend solo pinta + filtra vía query params. Sin sync en esta pantalla.

## Architecture Decisions

| Decisión | Rationale |
|----------|-----------|
| `GET .../ocupacion/agenda/events` | Q15=B; payload acotado a ventana |
| Materializar en service Python | Reglas de dia/fechas testables sin FC |
| Map dia ES → weekday 0–6 (lun=0…dom=6 alineado a datos API) | API usa `lunes`…`domingo` |
| BUSINESS_TIMEZONE para dates naive→aware | Consistente con consultorios |
| Join locations por id_dominio en memoria | Pocas ubicaciones; simple |
| Filtros query CSV repetible (`tipo=ART&tipo=SC`) | Multi-select UI |
| Endpoint `.../agenda/filter-options` | Distincts + labels dominio sin bajar 7k al client |

## Flow

```
datesSet / filter change
  → GET events?start&end&filters
  → SELECT ocupacion (+ locations)
  → filter solape + filtros + dia válido
  → expand cada fila a fechas en ventana
  → JSON events[]
  → FullCalendar
click event → popover (extended props)
```

## API

### GET `/api/v1/distribucion/ocupacion/agenda/events`

Query:

- `start`, `end` (required): ISO date `YYYY-MM-DD` o datetime
- `id_dominio`, `tipo`, `especialidad`, `medico`, `dia`: opcionales, multi

Response:

```json
{
  "events": [
    {
      "id": "rowId:YYYY-MM-DD",
      "title": "MEDICO",
      "start": "2026-08-03T09:00:00",
      "end": "2026-08-03T12:00:00",
      "extended": { "...detalle..." }
    }
  ]
}
```

### GET `/api/v1/distribucion/ocupacion/agenda/filter-options`

Distincts desde snapshot (+ location names). Auth igual.

## Files

| Path | Action |
|------|--------|
| `backend/app/services/distribucion/agenda_ocupacion.py` | New |
| `backend/app/schemas/distribucion.py` | Modify |
| `backend/app/api/routers/distribucion.py` | Modify |
| `backend/tests/test_agenda_ocupacion.py` | New |
| `frontend/src/pages/AgendaOcupacionPage.jsx` | New |
| `frontend/src/config/navigation.js` | Modify |
| `frontend/src/main.jsx` | Modify |
| `docs/runbook.md` | Modify |

## Out of scope

Migraciones; sync; bookings; colores por categoría.
